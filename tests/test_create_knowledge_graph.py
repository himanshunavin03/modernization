import hashlib
import json
from pathlib import Path

import pytest

from polaris_modernization import knowledge_graph_agent as agent


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "roslyn-semantic"


def fixture_hashes() -> dict[Path, str]:
    return {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in FIXTURE.rglob("*") if path.is_file()}


def test_graph_only_success_writes_customer_status_without_changing_source(tmp_path):
    before = fixture_hashes()
    result = agent.create_knowledge_graph(FIXTURE, "semantic-agent", "default", tmp_path)
    after = fixture_hashes()

    assert result["overall_status"] == "succeeded"
    assert after == before
    assert (tmp_path / "semantic-agent" / "knowledge-graph.json").exists()
    assert (tmp_path / "semantic-agent" / "graph-run-summary.md").exists()
    assert result["neo4j"]["status"] == "skipped"
    assert [stage["name"] for stage in result["stages"]] == [
        "validate_input", "analyze_source", "validate_graph", "load_neo4j", "produce_run_status", "preserve_review_artifacts"
    ]
    assert (tmp_path / "knowledge-graph" / "latest" / "knowledge-graph.json").exists()
    assert (tmp_path / "knowledge-graph" / "latest" / "knowledge-graph-validation.json").exists()


def test_missing_source_path_returns_failed_status_artifact(tmp_path):
    result = agent.create_knowledge_graph(tmp_path / "missing", "missing-source", "default", tmp_path)

    assert result["overall_status"] == "failed"
    assert result["stages"] == [{"name": "validate_input", "status": "failed", "message": "--source-root must exist and be a directory."}]
    assert (tmp_path / "missing-source" / "graph-run-status.json").exists()


@pytest.mark.parametrize("project_id", ["", " ", "../other", "other/project", "."])
def test_empty_or_unsafe_project_id_fails_before_writing(project_id, tmp_path):
    result = agent.create_knowledge_graph(FIXTURE, project_id, "default", tmp_path)

    assert result["overall_status"] == "failed"
    assert result["stages"][0]["name"] == "validate_input"
    assert result["stages"][0]["status"] == "failed"
    assert not any(tmp_path.iterdir())


def test_status_artifact_has_required_customer_fields(tmp_path):
    result = agent.create_knowledge_graph(FIXTURE, "status-shape", "default", tmp_path)
    status = json.loads(Path(result["artifact_paths"]["graph_run_status"]).read_text(encoding="utf-8"))

    assert {"project_id", "source_root", "started_at", "ended_at", "overall_status", "stages", "counts", "roslyn", "neo4j", "artifact_paths", "neo4j_browser_url", "next_actions"} <= status.keys()
    assert {"file_count", "fact_count", "node_count", "edge_count", "warning_count", "extraction_warning_count", "review_warning_count"} <= status["counts"].keys()
    assert status["neo4j_browser_url"] == "http://localhost:7474"
    assert "local-only" not in Path(result["artifact_paths"]["graph_run_status"]).read_text(encoding="utf-8")


def test_status_warning_and_scope_counts_match_graph_metadata(tmp_path):
    result = agent.create_knowledge_graph(FIXTURE, "status-consistency", "default", tmp_path)
    status = json.loads(Path(result["artifact_paths"]["graph_run_status"]).read_text(encoding="utf-8"))
    graph = json.loads(Path(result["artifact_paths"]["knowledge_graph"]).read_text(encoding="utf-8"))

    assert status["counts"]["warning_count"] == len(graph["warnings"])
    assert status["counts"]["extraction_warning_count"] == graph["metadata"]["extraction_warning_count"]
    assert status["counts"]["review_warning_count"] == graph["metadata"]["review_warning_count"]
    assert status["counts"]["warning_count"] == status["counts"]["extraction_warning_count"] + status["counts"]["review_warning_count"]
    assert status["scope"]["selected_file_count"] == graph["metadata"]["selected_file_count"]
    assert status["scope"]["selected_file_count"] == sum(node["label"] == "File" for node in graph["nodes"])


def test_neo4j_load_failure_is_controlled_without_any_delete(monkeypatch, tmp_path):
    class Driver:
        def close(self):
            pass

    class FailingLoader:
        def __init__(self, driver):
            self.driver = driver

        def load(self, graph, project_id):
            raise RuntimeError("offline")

        def clear_project(self, *args):
            raise AssertionError("The workflow must not clear any project.")

    monkeypatch.setenv("NEO4J_URI", "bolt://localhost:7687")
    monkeypatch.setenv("NEO4J_USERNAME", "neo4j")
    monkeypatch.setenv("NEO4J_PASSWORD", "local-only")
    monkeypatch.setattr(agent, "connect", lambda *args: Driver())
    monkeypatch.setattr(agent, "Neo4jLoader", FailingLoader)

    result = agent.create_knowledge_graph(FIXTURE, "neo4j-failure", "default", tmp_path, load_neo4j=True)

    load_stage = next(stage for stage in result["stages"] if stage["name"] == "load_neo4j")
    assert result["overall_status"] == "failed"
    assert load_stage["status"] == "failed"
    assert result["neo4j"]["message"] == "Connection or load failed; no delete operation was attempted."
