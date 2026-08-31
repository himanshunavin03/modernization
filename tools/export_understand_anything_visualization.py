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


def read_graph(path: Path) -> dict:
    graph = json.loads(path.read_text(encoding="utf-8"))
    metadata = graph.get("metadata", {})
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    if metadata.get("coverage_status") != "scope_complete":
        raise ValueError("Visualization requires scope_complete coverage.")
    if metadata.get("extraction_warning_count") != 0:
        raise ValueError("Visualization requires zero extraction warnings.")
    if any(item.get("project_id") != PROJECT_ID for item in [*nodes, *edges]):
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

def export(graph: dict, output_root: Path) -> Path:
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
            "polarisProjectId": PROJECT_ID,
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
        "polarisProjectId": PROJECT_ID,
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
        "layers": [],
        "tour": [],
        "polarisVisualization": {
            "disclaimer": DISCLAIMER,
            "project_id": PROJECT_ID,
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
    args = parser.parse_args()
    graph = read_graph(args.graph)
    target = export(graph, args.output)
    print(target)


if __name__ == "__main__":
    main()
