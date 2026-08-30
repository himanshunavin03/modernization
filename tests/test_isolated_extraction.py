import hashlib
import json
from pathlib import Path
import subprocess

import pytest

from polaris_modernization import cli
from polaris_modernization import knowledge_graph_agent as agent
from polaris_modernization.isolated_extraction import ExtractionResult, LOCAL_SOURCE_DIRECTORY, extract_file


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "generic-graph"
SEMANTIC_FIXTURE = ROOT / "tests" / "fixtures" / "roslyn-semantic"


def request(source_path: str = "good.js") -> dict[str, str]:
    return {
        "source_root": str(FIXTURE),
        "source_path": source_path,
        "source_hash": "hash",
        "project_id": "isolated-test",
        "language": "javascript",
    }


def fact_payload() -> dict:
    return {
        "status": "succeeded",
        "facts": [{
            "kind": "api_call",
            "name": "/api/test",
            "properties": {},
            "evidence": {
                "project_id": "isolated-test",
                "source_path": "good.js",
                "line_start": 1,
                "line_end": 1,
                "extraction_method": "tree-sitter",
                "confidence": 1.0,
                "source_hash": "hash",
            },
        }],
    }


def test_worker_bootstrap_extracts_normal_fixture_without_parent_pythonpath(monkeypatch):
    source_path = FIXTURE / "services" / "alpha.js"
    monkeypatch.delenv("PYTHONPATH", raising=False)

    result = extract_file({
        "source_root": str(FIXTURE),
        "source_path": "services/alpha.js",
        "source_hash": hashlib.sha256(source_path.read_bytes()).hexdigest(),
        "project_id": "clean-checkout",
        "language": "javascript",
    })

    assert result.warning is None
    assert result.facts
    assert LOCAL_SOURCE_DIRECTORY.joinpath("polaris_modernization").is_dir()


def test_worker_abnormal_exit_isolated_while_another_file_succeeds(monkeypatch):
    def run_worker(*args, **kwargs):
        source_path = json.loads(kwargs["input"])["source_path"]
        if source_path == "bad.js":
            return subprocess.CompletedProcess(args[0], 139, "", "")
        return subprocess.CompletedProcess(args[0], 0, json.dumps(fact_payload()), "")

    monkeypatch.setattr("polaris_modernization.isolated_extraction.subprocess.run", run_worker)

    failed = extract_file(request("bad.js"))
    succeeded = extract_file(request())

    assert failed.warning and failed.warning["failure_category"] == "abnormal_exit"
    assert not failed.facts
    assert succeeded.warning is None
    assert succeeded.facts[0].name == "/api/test"


def test_worker_import_failure_has_distinct_safe_category(monkeypatch):
    monkeypatch.setattr(
        "polaris_modernization.isolated_extraction.subprocess.run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args[0], 1, "", "ModuleNotFoundError: No module named 'polaris_modernization'"),
    )

    result = extract_file(request())

    assert result.warning
    assert result.warning["failure_category"] == "worker_startup_failed"
    assert result.warning["diagnostic"] == "Extraction worker could not import the analyzer package."


@pytest.mark.parametrize("worker", [
    lambda *args, **kwargs: (_ for _ in ()).throw(subprocess.TimeoutExpired(args[0], 30)),
    lambda *args, **kwargs: subprocess.CompletedProcess(args[0], 0, "not-json", ""),
])
def test_worker_timeout_or_invalid_output_becomes_safe_warning(monkeypatch, worker):
    monkeypatch.setattr("polaris_modernization.isolated_extraction.subprocess.run", worker)

    result = extract_file(request())

    assert result.facts == []
    assert result.warning
    assert result.warning["status"] == "skipped"
    assert result.warning["failure_category"] in {"timeout", "invalid_worker_output"}
    assert "good.js" not in result.warning["diagnostic"]


def test_partial_run_writes_artifacts_and_preserves_fixture(monkeypatch, tmp_path):
    before = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in FIXTURE.rglob("*") if path.is_file()}
    calls = 0

    def isolated_result(payload):
        nonlocal calls
        calls += 1
        if calls == 1:
            return ExtractionResult([], {
                "source_path": payload["source_path"], "language": payload["language"], "extractor": payload["language"],
                "failure_category": "abnormal_exit", "diagnostic": "Extraction worker exited with code 139.", "status": "skipped",
            })
        return ExtractionResult([])

    monkeypatch.setattr(cli, "extract_file", isolated_result)
    result = agent.create_knowledge_graph(FIXTURE, "partial-run", "default", tmp_path, load_neo4j=True)
    after = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in FIXTURE.rglob("*") if path.is_file()}
    status = json.loads((tmp_path / "partial-run" / "graph-run-status.json").read_text(encoding="utf-8"))
    inventory = json.loads((tmp_path / "partial-run" / "source-inventory.json").read_text(encoding="utf-8"))

    assert after == before
    assert result["overall_status"] == "succeeded_with_warnings"
    assert status["counts"]["extraction_warning_count"] == 1
    assert status["neo4j"]["status"] == "blocked"
    assert any(item["extraction_status"] == "failed_isolated" for item in inventory["files"])
    assert (tmp_path / "partial-run" / "knowledge-graph.json").exists()
    assert "Extraction warnings: 1" in (tmp_path / "partial-run" / "analysis-summary.md").read_text(encoding="utf-8")
    assert "Extraction warnings: 1" in (tmp_path / "partial-run" / "graph-run-summary.md").read_text(encoding="utf-8")


def test_all_files_failed_returns_failed_status_and_artifacts(monkeypatch, tmp_path):
    def isolated_failure(payload):
        return ExtractionResult([], {
            "source_path": payload["source_path"], "language": payload["language"], "extractor": payload["language"],
            "failure_category": "abnormal_exit", "diagnostic": "Extraction worker exited with code 139.", "status": "skipped",
        })

    monkeypatch.setattr(cli, "extract_file", isolated_failure)
    result = agent.create_knowledge_graph(SEMANTIC_FIXTURE, "all-failed", "default", tmp_path)

    assert result["overall_status"] == "failed"
    assert next(stage for stage in result["stages"] if stage["name"] == "analyze_source")["status"] == "failed"
    assert (tmp_path / "all-failed" / "knowledge-graph.json").exists()
    assert (tmp_path / "all-failed" / "graph-run-status.json").exists()
