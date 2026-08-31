import json

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
