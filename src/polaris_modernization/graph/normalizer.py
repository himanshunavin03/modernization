"""Normalize deterministic facts into an evidence-bearing graph JSON document."""

from __future__ import annotations

from collections import defaultdict

from polaris_modernization.models import Fact


KIND_TO_LABEL = {
    "razor_view": "RazorView",
    "layout": "Layout",
    "partial_view": "PartialView",
    "script_asset": "ScriptAsset",
    "style_asset": "StyleAsset",
    "controller": "Controller",
    "action": "Action",
    "authorization_policy": "AuthorizationPolicy",
    "angular_module": "AngularModule",
    "route": "Route",
    "angular_controller": "AngularController",
    "angular_service": "AngularService",
    "angular_directive": "AngularDirective",
    "client_component": "ClientComponent",
    "chart": "Chart",
    "ui_control": "UIControl",
    "api_call": "ApiCall",
    "opaque_source": "OpaqueSource",
    "conservative_source": "ConservativeSource",
}


def normalize(project_id: str, inventory: list[dict], facts: list[Fact], metadata: dict | None = None) -> dict:
    nodes: dict[str, dict] = {}
    edges: dict[tuple[str, str, str], dict] = {}

    def add_node(label: str, name: str, evidence: dict, properties: dict | None = None) -> str:
        node_id = f"{project_id}:{label}:{name}"
        if node_id not in nodes:
            nodes[node_id] = {"id": node_id, "project_id": project_id, "label": label, "name": name, "properties": properties or {}, "evidence": []}
        nodes[node_id]["evidence"].append(evidence)
        return node_id

    def add_edge(edge_type: str, source: str, target: str, evidence: dict, properties: dict | None = None) -> None:
        key = (edge_type, source, target)
        if key not in edges:
            edges[key] = {"project_id": project_id, "type": edge_type, "source": source, "target": target, "properties": properties or {}, "evidence": []}
        edges[key]["evidence"].append(evidence)

    application_evidence = {"project_id": project_id, "source_path": "", "line_start": 0, "line_end": 0, "extraction_method": "tree-sitter", "confidence": 1.0, "source_hash": ""}
    application = add_node("Project", project_id, application_evidence)
    file_nodes: dict[str, str] = {}
    for file_entry in inventory:
        evidence = {"project_id": project_id,
            "source_path": file_entry["source_path"],
            "line_start": 1,
            "line_end": 1,
            "extraction_method": "tree-sitter",
            "confidence": 1.0,
            "source_hash": file_entry["source_hash"],
        }
        file_nodes[file_entry["source_path"]] = add_node("File", file_entry["source_path"], evidence)
        add_edge("CONTAINS", application, file_nodes[file_entry["source_path"]], evidence)

    controllers: dict[str, str] = {}
    modules_by_file: dict[str, str] = {}
    views_by_stem: dict[str, str] = {}
    pending_routes: list[tuple[str, Fact]] = []
    pending_actions: list[tuple[str, Fact]] = []
    pending_returns: list[Fact] = []
    owners_by_file: dict[str, list[str]] = defaultdict(list)
    warnings: list[dict] = []

    for fact in facts:
        evidence = fact.evidence.to_dict()
        file_node = file_nodes[evidence["source_path"]]
        if fact.kind == "returns_view":
            pending_returns.append(fact)
            continue
        label = KIND_TO_LABEL.get(fact.kind)
        if label is None:
            if fact.kind == "import":
                target = add_node("ExternalReference", fact.name, evidence)
                add_edge("IMPORTS", file_node, target, evidence)
            continue
        node = add_node(label, fact.name, evidence, fact.properties)
        add_edge("DECLARES", file_node, node, evidence)
        if fact.kind in {"razor_view", "layout", "partial_view", "script_asset", "style_asset", "client_component", "ui_control"}:
            add_edge("HOSTS", file_node, node, evidence)
        if fact.kind in {"client_component", "ui_control"}:
            add_edge("CONTAINS_CONTROL", file_node, node, evidence)
        if fact.kind == "controller":
            controllers[fact.name] = node
        if fact.kind == "angular_module":
            modules_by_file[evidence["source_path"]] = node
        if fact.kind == "razor_view":
            views_by_stem[fact.name.rsplit("/", 1)[-1].split(".", 1)[0]] = node
        if fact.kind == "authorization_policy":
            controller = controllers.get(str(fact.properties.get("controller")))
            if controller:
                add_edge("PROTECTS", node, controller, evidence)
        if fact.kind == "action":
            pending_actions.append((node, fact))
        if fact.kind in {"angular_service", "angular_controller", "angular_directive"}:
            owners_by_file[evidence["source_path"]].append(node)
        if fact.kind == "route":
            pending_routes.append((node, fact))
        if fact.kind == "api_call":
            owners = owners_by_file[evidence["source_path"]]
            source = owners[0] if len(owners) == 1 else file_node
            add_edge("CALLS_API", source, node, evidence, {"ownership": "proven" if len(owners) == 1 else "unresolved"})
            if len(owners) != 1:
                warnings.append({"source_path": evidence["source_path"], "message": "API call owner was not uniquely proven; attached to File."})

    for action_node, action_fact in pending_actions:
        controller = controllers.get(str(action_fact.properties.get("controller")))
        if controller:
            add_edge("DECLARES", controller, action_node, action_fact.evidence.to_dict())
    for return_fact in pending_returns:
        action = next((item for item, fact in pending_actions if fact.name == return_fact.name and fact.properties.get("controller") == return_fact.properties.get("controller")), None)
        view_name = return_fact.properties.get("view_name")
        if action and isinstance(view_name, str) and view_name in views_by_stem:
            add_edge("RETURNS", action, views_by_stem[view_name], return_fact.evidence.to_dict())
        elif return_fact.properties.get("unresolved"):
            warnings.append({"source_path": return_fact.evidence.source_path, "message": return_fact.properties["unresolved"]})

    for route_node, route_fact in pending_routes:
        module = modules_by_file.get(route_fact.evidence.source_path)
        if module:
            add_edge("CONFIGURES_ROUTE", module, route_node, route_fact.evidence.to_dict())
        template = route_fact.properties.get("template")
        if isinstance(template, str):
            template_node = add_node("Template", template, route_fact.evidence.to_dict())
            add_edge("USES_TEMPLATE", route_node, template_node, route_fact.evidence.to_dict())
        controller_name = route_fact.properties.get("controller")
        if isinstance(controller_name, str):
            controller_node = add_node("AngularController", controller_name, route_fact.evidence.to_dict())
            add_edge("DEPENDS_ON", route_node, controller_node, route_fact.evidence.to_dict())

    return {
        "nodes": sorted(nodes.values(), key=lambda item: item["id"]),
        "edges": sorted(edges.values(), key=lambda item: (item["type"], item["source"], item["target"])),
        "warnings": warnings,
        "metadata": metadata or {},
    }
