"""Normalize deterministic facts into an evidence-bearing graph JSON document."""

from __future__ import annotations

from collections import defaultdict

from polaris_modernization.models import Fact


def _qualified_name(owner: object, function: object) -> str:
    return f"{owner}.{function}" if owner and function else str(function or "")


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
    "ui_action": "UIAction",
    "ui_validation": "UIValidation",
    "ui_selection": "UISelection",
    "ui_condition": "UICondition",
    "validation_condition": "ValidationCondition",
    "state_mutation": "StateMutation",
    "collection_mutation": "CollectionMutation",
    "navigation": "Navigation",
    "confirmation": "Confirmation",
    "frontend_function": "FrontendFunction",
    "frontend_invocation": "FrontendInvocation",
    "backend_invocation": "BackendInvocation",
    "backend_handler": "BackendHandler",
    "persistence_operation": "PersistenceOperation",
    "api_call": "ApiCall",
    "endpoint": "Endpoint",
    "view_model": "Type",
    "opaque_source": "OpaqueSource",
    "conservative_source": "ConservativeSource",
    "type": "Type",
    "property": "Property",
    "method": "Method",
    "function": "Function",
}


def normalize(project_id: str, inventory: list[dict], facts: list[Fact], metadata: dict | None = None) -> dict:
    nodes: dict[str, dict] = {}
    edges: dict[tuple[str, str, str], dict] = {}

    def add_node(label: str, name: str, evidence: dict, properties: dict | None = None, identity: str | None = None) -> str:
        node_id = f"{project_id}:{label}:{identity or name}"
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
    pending_framework: list[Fact] = []
    pending_ui_actions: list[tuple[str, Fact]] = []
    pending_ui_semantics: list[tuple[str, Fact]] = []
    pending_invocations: list[tuple[str, Fact]] = []
    pending_backend_invocations: list[tuple[str, Fact]] = []
    pending_methods: list[tuple[str, Fact]] = []
    containers_by_file: dict[tuple[str, str], str] = {}
    owners_by_file: dict[str, list[str]] = defaultdict(list)
    warnings: list[dict] = []
    methods_by_route: dict[str, set[str]] = defaultdict(set)
    for fact in facts:
        if fact.kind == "api_call":
            route = str(fact.properties.get("normalized_route_template") or fact.properties.get("normalized_route") or fact.name).rstrip("/")
            methods_by_route[route].add(str(fact.properties.get("http_method") or "GET").upper())

    for fact in facts:
        evidence = fact.evidence.to_dict()
        file_node = file_nodes[evidence["source_path"]]
        if fact.kind == "returns_view":
            pending_returns.append(fact)
            continue
        if fact.kind in {"api_mapping", "razor_model", "razor_action"}:
            pending_framework.append(fact)
            continue
        label = KIND_TO_LABEL.get(fact.kind)
        if label is None:
            if fact.kind == "import":
                target = add_node("ExternalReference", fact.name, evidence)
                add_edge("IMPORTS", file_node, target, evidence)
            continue
        node_name = fact.name
        if fact.kind == "api_call":
            route = str(fact.properties.get("normalized_route_template") or fact.properties.get("normalized_route") or fact.name).rstrip("/")
            if len(methods_by_route[route]) > 1:
                node_name = f"{str(fact.properties.get('http_method') or 'GET').upper()} {route}"
        structural_identity = None
        if fact.kind == "method":
            structural_identity = str(fact.properties.get("structural_identity") or (
                f"{fact.properties.get('owner') or fact.properties.get('controller') or 'unknown'}."
                f"{fact.name}/{fact.properties.get('arity', 0)}@{evidence['source_path']}"
            ))
        node = add_node(label, node_name, evidence, fact.properties, structural_identity)
        add_edge("DECLARES", file_node, node, evidence)
        if fact.kind in {"razor_view", "layout", "partial_view", "script_asset", "style_asset", "client_component", "ui_control", "ui_action", "ui_validation", "ui_selection", "ui_condition", "validation_condition"}:
            add_edge("HOSTS", file_node, node, evidence)
        if fact.kind in {"client_component", "ui_control", "ui_action", "ui_validation", "ui_selection", "ui_condition", "validation_condition"}:
            add_edge("CONTAINS_CONTROL", file_node, node, evidence)
        if fact.kind == "controller":
            controllers[fact.name] = node
            containers_by_file[(evidence["source_path"], str(fact.properties.get("container_identity") or fact.name))] = node
            if fact.name.endswith("Controller"):
                controllers[fact.name.removesuffix("Controller")] = node
        if fact.kind == "type":
            containers_by_file[(evidence["source_path"], str(fact.properties.get("container_identity") or fact.name))] = node
        if fact.kind == "method":
            pending_methods.append((node, fact))
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
        if fact.kind == "ui_action":
            pending_ui_actions.append((node, fact))
        if fact.kind in {"state_mutation", "collection_mutation", "navigation", "confirmation"}:
            pending_ui_semantics.append((node, fact))
        if fact.kind == "frontend_invocation":
            pending_invocations.append((node, fact))
        if fact.kind == "backend_invocation":
            pending_backend_invocations.append((node, fact))
        if fact.kind == "api_call":
            owners = owners_by_file[evidence["source_path"]]
            function_name = fact.properties.get("function_name")
            qualified = _qualified_name(fact.properties.get("service"), function_name)
            source = next((item["id"] for item in nodes.values() if item["label"] == "FrontendFunction" and item["name"] == qualified), None)
            source = source or (owners[0] if len(owners) == 1 else file_node)
            add_edge("CALLS_API", source, node, evidence, {"ownership": "proven" if len(owners) == 1 else "unresolved"})
            if len(owners) == 1 and owners[0] != source:
                add_edge("CALLS_API", owners[0], node, evidence, {"ownership": "proven", "compatibility": "service-level"})
            if len(owners) != 1:
                warnings.append({"source_path": evidence["source_path"], "message": "API call owner was not uniquely proven; attached to File."})

    functions = [item for item in nodes.values() if item["label"] == "FrontendFunction"]
    for action_node, action_fact in pending_ui_actions:
        handler = action_fact.properties.get("handler")
        candidates = [item for item in functions if item["properties"].get("function_name") == handler]
        action_parts = action_fact.evidence.source_path.split("/")
        domain = action_parts[action_parts.index("components") + 1] if "components" in action_parts and action_parts.index("components") + 1 < len(action_parts) else None
        scoped = [item for item in candidates if domain and f"/{domain}/" in f"/{item['evidence'][0]['source_path']}/"]
        routed_controllers = {
            str(route_fact.properties.get("controller", "")).casefold()
            for _, route_fact in pending_routes
            if isinstance(route_fact.properties.get("template"), str)
            and action_fact.evidence.source_path.endswith(str(route_fact.properties["template"]).lstrip("/"))
        }
        preferred = [item for item in scoped if str(item["properties"].get("owner", "")).casefold() in routed_controllers]
        preferred = preferred or [item for item in scoped if "/controllers/" in f"/{item['evidence'][0]['source_path']}/" or str(item["properties"].get("owner", "")).lower().endswith("controller")]
        resolved = preferred or scoped or candidates
        if len(resolved) == 1:
            add_edge("TRIGGERS", action_node, resolved[0]["id"], action_fact.evidence.to_dict(), {"status": "PROVEN"})
    for semantic_node, semantic_fact in pending_ui_semantics:
        owner = _qualified_name(semantic_fact.properties.get("owner"), semantic_fact.properties.get("function_name"))
        function = next((item for item in functions if item["name"] == owner), None)
        if function:
            edge_type = {"state_mutation": "MUTATES", "collection_mutation": "MUTATES_COLLECTION", "navigation": "NAVIGATES", "confirmation": "REQUIRES_CONFIRMATION"}[semantic_fact.kind]
            add_edge(edge_type, function["id"], semantic_node, semantic_fact.evidence.to_dict(), {"status": "PROVEN"})
    for _, invocation_fact in pending_invocations:
        caller_name = _qualified_name(invocation_fact.properties.get("caller_owner"), invocation_fact.properties.get("caller"))
        target_name = _qualified_name(invocation_fact.properties.get("target_owner"), invocation_fact.properties.get("target_function"))
        caller = next((item["id"] for item in functions if item["name"] == caller_name), None)
        target = next((item["id"] for item in functions if item["name"].casefold() == target_name.casefold()), None)
        if caller and target:
            add_edge("INVOKES", caller, target, invocation_fact.evidence.to_dict(), {"status": "PROVEN"})
    backend_handlers = [item for item in nodes.values() if item["label"] == "BackendHandler"]
    persistence_nodes = [item for item in nodes.values() if item["label"] == "PersistenceOperation"]
    for endpoint in (item for item in nodes.values() if item["label"] == "Endpoint"):
        arity = len(endpoint["properties"].get("parameters", []))
        qualified = f"{_qualified_name(endpoint['properties'].get('controller'), endpoint['properties'].get('action'))}/{arity}"
        action = next((item for item in backend_handlers if item["name"] == qualified), None)
        if action:
            add_edge("HANDLED_BY", endpoint["id"], action["id"], endpoint["evidence"][0], {"status": "PROVEN"})
    for _, invocation_fact in pending_backend_invocations:
        caller_name = f"{_qualified_name(invocation_fact.properties.get('caller_owner'), invocation_fact.properties.get('caller'))}/{invocation_fact.properties.get('caller_arity', 0)}"
        caller = next((item for item in backend_handlers if item["name"] == caller_name), None)
        hint = str(invocation_fact.properties.get("target_owner_hint", "")).casefold()
        target = next((item for item in backend_handlers if item["properties"].get("function_name") == invocation_fact.properties.get("target_function") and item["properties"].get("arity") == invocation_fact.properties.get("target_arity") and hint in str(item["properties"].get("owner", "")).casefold()), None)
        if caller and target:
            add_edge("INVOKES", caller["id"], target["id"], invocation_fact.evidence.to_dict(), {"status": "PROVEN"})
    for operation in persistence_nodes:
        qualified = f"{_qualified_name(operation['properties'].get('repository'), operation['properties'].get('handler'))}/{operation['properties'].get('handler_arity', 0)}"
        handler = next((item for item in backend_handlers if item["name"] == qualified), None)
        if handler:
            add_edge("PERFORMS", handler["id"], operation["id"], operation["evidence"][0], {"status": "PROVEN"})

    for action_node, action_fact in pending_actions:
        controller = containers_by_file.get((action_fact.evidence.source_path, str(action_fact.properties.get("container_identity") or action_fact.properties.get("controller"))))
        if controller:
            add_edge("DECLARES", controller, action_node, action_fact.evidence.to_dict())
    for method_node, method_fact in pending_methods:
        owner = containers_by_file.get((method_fact.evidence.source_path, str(
            method_fact.properties.get("container_identity")
            or method_fact.properties.get("owner")
            or method_fact.properties.get("controller")
        )))
        if owner:
            add_edge("DECLARES", owner, method_node, method_fact.evidence.to_dict())
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

    endpoint_nodes = {node["name"]: node["id"] for node in nodes.values() if node["label"] == "Endpoint"}
    api_nodes = {node["name"]: node["id"] for node in nodes.values() if node["label"] == "ApiCall"}
    for fact in pending_framework:
        evidence = fact.evidence.to_dict()
        if fact.kind == "api_mapping":
            proof = fact.properties.get("proof", {})
            operation_route = str(proof.get("frontend_template") or proof.get("frontend_route") or fact.name).rstrip("/")
            operation_name = f"{str(proof.get('frontend_http_method') or 'GET').upper()} {operation_route}"
            call = api_nodes.get(operation_name) or api_nodes.get(fact.name)
            endpoint = endpoint_nodes.get(str(fact.properties.get("endpoint")))
            if call and endpoint and fact.properties.get("status") == "PROVEN":
                add_edge("IMPLEMENTED_BY", call, endpoint, evidence, {
                    "status": "PROVEN",
                    "detail_status": fact.properties.get("detail_status"),
                    "resolution": fact.properties.get("resolution"),
                    "confidence": fact.properties.get("confidence"),
                    "frontend_call_id": fact.properties.get("frontend_call_id"),
                    "backend_endpoint_id": fact.properties.get("backend_endpoint_id"),
                    "proof": fact.properties.get("proof"),
                    "resolver_version": fact.properties.get("resolver_version"),
                })
        elif fact.kind == "razor_model":
            view = next((node["id"] for node in nodes.values() if node["label"] == "RazorView" and node["name"] == fact.name), None)
            if view:
                model = add_node("Type", str(fact.properties["model"]), evidence)
                add_edge("USES_VIEW_MODEL", view, model, evidence)
        elif fact.kind == "razor_action":
            view = next((node["id"] for node in nodes.values() if node["label"] == "RazorView" and node["name"] == fact.name), None)
            action = controllers.get(str(fact.properties["controller"]))
            if view and action:
                add_edge("CALLS_ACTION", view, action, evidence, {"action": fact.properties["action"]})

    return {
        "nodes": sorted(nodes.values(), key=lambda item: item["id"]),
        "edges": sorted(edges.values(), key=lambda item: (item["type"], item["source"], item["target"])),
        "warnings": warnings,
        "metadata": metadata or {},
    }
