import json
from pathlib import Path

import pytest

from tools.export_understand_anything_visualization import PROJECT_ID, export, read_graph


def canonical_graph():
    evidence = [{"project_id": PROJECT_ID, "source_path": "src/dashboard.js", "line_start": 1}]
    return {
        "metadata": {"coverage_status": "scope_complete", "extraction_warning_count": 0},
        "nodes": [{"id": f"{PROJECT_ID}:File:dashboard.js", "project_id": PROJECT_ID, "label": "File", "name": "dashboard.js", "evidence": evidence, "properties": {}}],
        "edges": [{"project_id": PROJECT_ID, "source": f"{PROJECT_ID}:File:dashboard.js", "target": f"{PROJECT_ID}:File:dashboard.js", "type": "CALLS_API", "evidence": [], "properties": {}}],
        "warnings": [{"source_path": "src/dashboard.js", "message": "review only"}],
    }


def test_export_preserves_canonical_counts_and_evidence(tmp_path):
    target = export(canonical_graph(), tmp_path)
    result = json.loads(target.read_text(encoding="utf-8"))

    assert target == tmp_path / ".ua" / "knowledge-graph.json"
    assert len(result["nodes"]) == 1
    assert len(result["edges"]) == 1
    assert result["nodes"][0]["polarisLabel"] == "File"
    assert result["nodes"][0]["polarisEvidence"][0]["source_path"] == "src/dashboard.js"
    assert result["nodes"][0]["polarisReviewWarnings"][0]["message"] == "review only"
    assert "src/dashboard.js:L1" in result["nodes"][0]["summary"]
    assert "review only" in result["nodes"][0]["summary"]
    assert "polaris-relationship:CALLS_API" in result["nodes"][0]["tags"]
    assert result["polarisVisualization"]["canonical_counts"] == {"nodes": 1, "edges": 1, "warnings": 1}
    assert "No LLM inference" in result["polarisVisualization"]["disclaimer"]
    assert result["layers"]
    assert result["layers"][0]["nodeIds"] == [f"{PROJECT_ID}:File:dashboard.js"]


def test_export_assigns_every_node_to_one_existing_non_empty_layer(tmp_path):
    graph = canonical_graph()
    graph["nodes"] = [
        {"id": f"{PROJECT_ID}:RazorView:dashboard", "project_id": PROJECT_ID, "label": "RazorView", "name": "Dashboard", "evidence": [{"source_path": "src/MyHealth.Web/Views/Dashboard/Index.cshtml"}], "properties": {}},
        {"id": f"{PROJECT_ID}:AngularModule:module", "project_id": PROJECT_ID, "label": "AngularModule", "name": "moduleName", "evidence": [{"source_path": "src/MyHealth.Web/content/app/app.module.js"}], "properties": {}},
        {"id": f"{PROJECT_ID}:ApiCall:dashboard", "project_id": PROJECT_ID, "label": "ApiCall", "name": "/api/dashboard", "evidence": [{"source_path": "src/MyHealth.Web/content/app/dashboardService.js"}], "properties": {}},
        {"id": f"{PROJECT_ID}:Type:patient", "project_id": PROJECT_ID, "label": "Type", "name": "Patient", "evidence": [{"source_path": "src/MyHealth.Domain/Patient.cs"}], "properties": {}},
        {"id": f"{PROJECT_ID}:Project:scope", "project_id": PROJECT_ID, "label": "Project", "name": PROJECT_ID, "evidence": [], "properties": {}},
    ]
    graph["edges"] = []
    result = json.loads(export(graph, tmp_path).read_text(encoding="utf-8"))

    layer_node_ids = [node_id for layer in result["layers"] for node_id in layer["nodeIds"]]
    exported_node_ids = {node["id"] for node in result["nodes"]}
    assert result["layers"]
    assert len(layer_node_ids) == len(exported_node_ids)
    assert len(layer_node_ids) == len(set(layer_node_ids))
    assert set(layer_node_ids) == exported_node_ids
    assert {layer["id"] for layer in result["layers"]} == {
        "legacy-razor-mvc-shell",
        "legacy-angularjs-client-flow",
        "api-integration-flow",
        "csharp-domain-semantic-model",
        "project-supporting-records",
    }


def test_approved_canonical_graph_counts_and_tour_are_preserved(tmp_path):
    canonical_path = Path(__file__).parents[1] / "artifacts" / PROJECT_ID / "knowledge-graph.json"
    graph = read_graph(canonical_path)
    result = json.loads(export(graph, tmp_path).read_text(encoding="utf-8"))

    assert (len(result["nodes"]), len(result["edges"])) == (123, 169)
    assert result["polarisVisualization"]["canonical_counts"] == {"nodes": 123, "edges": 169, "warnings": 27}
    layer_node_ids = [node_id for layer in result["layers"] for node_id in layer["nodeIds"]]
    assert len(layer_node_ids) == 123
    assert len(set(layer_node_ids)) == 123
    assert set(layer_node_ids) == {node["id"] for node in result["nodes"]}
    assert [step["title"] for step in result["tour"]] == [
        "Razor/MVC Dashboard shell",
        "Legacy AngularJS 1.x Dashboard route/ui-view",
        "Dashboard API service flow",
    ]


@pytest.mark.parametrize("metadata", [
    {"coverage_status": "scope_partial_with_extraction_failures", "extraction_warning_count": 0},
    {"coverage_status": "scope_complete", "extraction_warning_count": 1},
])
def test_read_graph_rejects_ineligible_visualization_input(tmp_path, metadata):
    graph = canonical_graph()
    graph["metadata"] = metadata
    path = tmp_path / "knowledge-graph.json"
    path.write_text(json.dumps(graph), encoding="utf-8")

    with pytest.raises(ValueError):
        read_graph(path)


def test_read_graph_rejects_other_project_id(tmp_path):
    graph = canonical_graph()
    graph["nodes"][0]["project_id"] = "other-project"
    path = tmp_path / "knowledge-graph.json"
    path.write_text(json.dumps(graph), encoding="utf-8")

    with pytest.raises(ValueError):
        read_graph(path)
