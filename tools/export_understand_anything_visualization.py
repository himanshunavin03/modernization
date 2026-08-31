"""Export the canonical Polaris graph as a read-only Understand Anything viewer copy."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

PROJECT_ID = "healthclinic-dashboard-scope-demo-v3"
DISCLAIMER = (
    "Evidence-backed legacy modernization graph. Tree-sitter/Roslyn source of truth. "
    "Review warnings remain visible. No LLM inference. Legacy AngularJS 1.x is the "
    "legacy client-side code; Target Angular 22 is the modernization target."
)
LAYER_DEFINITIONS = (
    ("legacy-ui-modernization", "Legacy UI modernization scope", "Legacy Razor and AngularJS records eligible for UI modernization."),
    ("backend-api-contract", "Backend API and contract", "Read-only API controllers, actions, endpoints, and contracts."),
    ("repository-data-access", "Repository and data-access flow", "Read-only repositories and proven EF/LINQ operations."),
    ("domain-dto-model", "Domain DTO/entity model", "Read-only DTO and domain model records."),
    ("dbcontext-dependency", "DbContext/database dependency", "Read-only DbContext dependency records."),
    ("legacy-razor-mvc-shell", "Legacy ASP.NET MVC/Razor shell", "Proven MVC controllers, Razor views, layouts, partials, and UI controls."),
    ("legacy-angularjs-client-flow", "Legacy AngularJS 1.x client-side flow", "Proven AngularJS modules, controllers, routes, templates, directives, and services."),
    ("api-integration-flow", "API and integration flow", "Proven API-call and external integration records."),
    ("csharp-domain-semantic-model", "C# domain and semantic model", "Proven C# namespaces, types, methods, and related source records."),
    ("project-supporting-records", "Project/supporting graph records", "Project, support, and remaining evidence-backed graph records."),
)


def read_graph(path: Path, project_id: str = PROJECT_ID) -> dict:
    graph = json.loads(path.read_text(encoding="utf-8"))
    metadata = graph.get("metadata", {})
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    if metadata.get("coverage_status") != "scope_complete":
        raise ValueError("Visualization requires scope_complete coverage.")
    if metadata.get("extraction_warning_count") != 0:
        raise ValueError("Visualization requires zero extraction warnings.")
    if not project_id or any(item.get("project_id") != project_id for item in [*nodes, *edges]):
        raise ValueError("Visualization requires only the approved project ID.")
    return graph


def source_path(item: dict) -> str:
    evidence = item.get("evidence", [])
    return next((record.get("source_path", "") for record in evidence if record.get("source_path")), "")


def viewer_type(label: str) -> str:
    if label == "File":
        return "file"
    if label in {"Controller", "Type", "DTO"}:
        return "class"
    if label in {"Action", "Method"}:
        return "function"
    if label in {"AngularModule", "Namespace"}:
        return "module"
    if label in {"ApiCall", "Route", "Endpoint"}:
        return "endpoint"
    return "concept"


def viewer_edge_type(edge_type: str) -> str:
    return {
        "CALLS_API": "calls",
        "CONFIGURES_ROUTE": "routes",
        "CONTAINS": "contains",
        "CONTAINS_CONTROL": "contains",
        "DECLARES": "contains",
        "DEPENDS_ON": "depends_on",
        "DEPENDS_ON_OUT_OF_SCOPE": "depends_on",
        "EXPOSES": "exports",
        "HAS_PROPERTY": "contains",
        "HOSTS": "contains",
        "IMPORTS": "imports",
        "INVOKES": "calls",
        "PROTECTS": "configures",
        "RETURNS_TYPE": "related",
        "USES_TEMPLATE": "routes",
    }.get(edge_type, "related")


def node_summary(node: dict, review_warnings: list[dict]) -> str:
    evidence = node.get("evidence", [])
    locations = []
    for record in evidence:
        path = record.get("source_path", "")
        if not path:
            continue
        start = record.get("line_start")
        end = record.get("line_end")
        location = path if start is None else f"{path}:L{start}" + (f"-L{end}" if end and end != start else "")
        locations.append(location)
    evidence_text = "; ".join(dict.fromkeys(locations)) or "No source-path evidence recorded."
    warning_text = "; ".join(warning.get("message", "") for warning in review_warnings) or "None."
    return (
        f"Evidence-backed Polaris node. Original label: {node['label']}. "
        f"Evidence: {evidence_text}. Review warnings: {warning_text}"
    )


def layer_id_for(node: dict, relationship_types: set[str]) -> str:
    """Classify each canonical node once using only labels, paths, and graph edges."""
    label = node["label"]
    path = source_path(node).replace("\\", "/").lower()

    if path.startswith("src/myhealth.api/") or node.get("properties", {}).get("modernization_role") == "preserve_backend":
        return "backend-api-contract"
    if "repositories/" in path or label == "DataQuery": return "repository-data-access"
    if path.startswith("src/myhealth.model/"): return "domain-dto-model"
    if path.endswith("myhealthcontext.cs"): return "dbcontext-dependency"
    if node.get("properties", {}).get("modernization_role") == "transform_ui": return "legacy-ui-modernization"

    if label == "ApiCall" or (label == "ExternalReference" and "CALLS_API" in relationship_types):
        return "api-integration-flow"
    if (
        path.startswith("src/myhealth.web/content/app/")
        or label in {"AngularModule", "AngularController", "AngularService", "AngularDirective", "Route", "Template"}
    ):
        return "legacy-angularjs-client-flow"
    if label in {"Namespace", "Type", "Method"}:
        return "csharp-domain-semantic-model"
    if (
        path.startswith("src/myhealth.web/views/")
        or path.startswith("src/myhealth.web/controllers/")
        or label in {"RazorView", "PartialView", "Layout", "UIControl", "ClientComponent", "Controller", "Action", "AuthorizationPolicy"}
    ):
        return "legacy-razor-mvc-shell"
    if path.endswith(".cs"):
        return "csharp-domain-semantic-model"
    return "project-supporting-records"


def build_layers(graph: dict, relationship_types_by_node: dict[str, set[str]]) -> list[dict]:
    nodes_by_layer = {layer_id: [] for layer_id, _, _ in LAYER_DEFINITIONS}
    for node in graph["nodes"]:
        nodes_by_layer[layer_id_for(node, relationship_types_by_node[node["id"]])].append(node["id"])
    return [
        {"id": layer_id, "name": name, "description": description, "nodeIds": node_ids}
        for layer_id, name, description in LAYER_DEFINITIONS
        if (node_ids := sorted(nodes_by_layer[layer_id]))
    ]


def build_tour(graph: dict) -> list[dict]:
    """Return only tour steps whose existing canonical nodes can be demonstrated."""
    nodes = graph["nodes"]

    def ids_for(predicate) -> list[str]:
        return sorted(node["id"] for node in nodes if predicate(node))

    steps = []
    shell_ids = ids_for(lambda node: node["label"] in {"Controller", "RazorView"} and "Dashboard" in node["name"])
    if shell_ids:
        steps.append({"order": 1, "title": "Razor/MVC Dashboard shell", "description": "Proven Dashboard MVC controller and Razor-view records.", "nodeIds": shell_ids})

    angular_ids = ids_for(lambda node: node["label"] in {"AngularModule", "Route", "UIControl"} and node["name"] in {"moduleName", "dashboard", "ui-view"})
    if angular_ids:
        steps.append({"order": 2, "title": "Legacy AngularJS 1.x Dashboard route/ui-view", "description": "Proven Legacy AngularJS 1.x route, module, and ui-view records.", "nodeIds": angular_ids})

    api_ids = ids_for(lambda node: node["label"] in {"AngularService", "ApiCall"} and (node["name"] == "dashboardService" or node["label"] == "ApiCall"))
    if api_ids:
        steps.append({"order": 3, "title": "Dashboard API service flow", "description": "Proven dashboard service and API-call records.", "nodeIds": api_ids})
    return steps

def export(graph: dict, output_root: Path, project_id: str = PROJECT_ID) -> Path:
    warnings_by_path: dict[str, list[dict]] = defaultdict(list)
    relationship_types_by_node: dict[str, set[str]] = defaultdict(set)
    for warning in graph.get("warnings", []):
        warnings_by_path[warning.get("source_path", "")].append(warning)
    for edge in graph["edges"]:
        relationship_types_by_node[edge["source"]].add(edge["type"])
        relationship_types_by_node[edge["target"]].add(edge["type"])

    nodes = []
    for node in graph["nodes"]:
        path = source_path(node)
        review_warnings = warnings_by_path.get(path, [])
        nodes.append({
            "id": node["id"],
            "type": viewer_type(node["label"]),
            "name": node["name"],
            "filePath": path,
            "summary": node_summary(node, review_warnings),
            "tags": [
                f"polaris-label:{node['label']}",
                *[f"polaris-relationship:{edge_type}" for edge_type in sorted(relationship_types_by_node[node['id']])],
                "evidence-backed",
                "no-llm-inference",
            ],
            "complexity": "moderate",
            "polarisProjectId": project_id,
            "polarisLabel": node["label"],
            "polarisEvidence": node.get("evidence", []),
            "polarisProperties": node.get("properties", {}),
            "polarisReviewWarnings": review_warnings,
        })

    edges = [{
        "source": edge["source"],
        "target": edge["target"],
        "type": viewer_edge_type(edge["type"]),
        "direction": "forward",
        "weight": 1,
        "polarisProjectId": project_id,
        "polarisRelationshipType": edge["type"],
        "polarisEvidence": edge.get("evidence", []),
        "polarisProperties": edge.get("properties", {}),
    } for edge in graph["edges"]]

    visualization = {
        "version": "1.0.0",
        "kind": "codebase",
        "project": {
            "name": "Polaris HealthClinic Dashboard modernization POC",
            "description": DISCLAIMER,
            "languages": ["C#", "Razor", "JavaScript"],
            "frameworks": ["Legacy ASP.NET MVC/Razor UI", "Legacy AngularJS 1.x client-side code", "Target Angular 22 application"],
            "analyzedAt": "2026-08-30T18:35:01.946232Z",
            "gitCommitHash": "polaris-canonical-graph",
        },
        "nodes": nodes,
        "edges": edges,
        "layers": build_layers(graph, relationship_types_by_node),
        "tour": build_tour(graph),
        "polarisVisualization": {
            "disclaimer": DISCLAIMER,
            "project_id": project_id,
            "canonical_counts": {"nodes": len(graph["nodes"]), "edges": len(graph["edges"]), "warnings": len(graph.get("warnings", []))},
            "review_warnings": graph.get("warnings", []),
            "source_of_truth": "Tree-sitter/Roslyn canonical knowledge-graph.json and project-scoped Neo4j data.",
        },
    }
    target = output_root / ".ua" / "knowledge-graph.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(visualization, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graph", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--project-id", default=PROJECT_ID)
    args = parser.parse_args()
    graph = read_graph(args.graph, args.project_id)
    target = export(graph, args.output, args.project_id)
    print(target)


if __name__ == "__main__":
    main()
