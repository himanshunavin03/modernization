import hashlib
from pathlib import Path

from polaris_modernization import cli
from polaris_modernization.graph.normalizer import normalize
from polaris_modernization.isolated_extraction import ExtractionResult
from polaris_modernization.models import Evidence, Fact


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "generic-graph"


def scoped_profile():
    return {
        "scope_id": "selected-flow",
        "scope_name": "Selected modernization flow",
        "scope_description": "A customer-approved subset.",
        "scope_type": "selected_modernization_flow",
        "include_paths": ["services/alpha.js"],
    }


def fake_success(payload):
    return ExtractionResult([])


def test_full_profile_graphs_every_audited_file(tmp_path):
    result = cli.analyze(FIXTURE, "full-scope", "default", tmp_path)

    file_nodes = [node for node in result["graph"]["nodes"] if node["label"] == "File"]
    assert len(file_nodes) == len(result["inventory"])
    assert result["graph"]["metadata"]["scope_type"] == "full_application"


def test_selected_scope_keeps_audit_inventory_but_limits_graph_files(monkeypatch, tmp_path):
    default = cli.load_profile("default")
    monkeypatch.setattr(cli, "load_profile", lambda name: default if name == "default" else scoped_profile())
    monkeypatch.setattr(cli, "extract_file", fake_success)
    before = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in FIXTURE.rglob("*") if path.is_file()}

    result = cli.analyze(FIXTURE, "selected-scope", "selected", tmp_path)

    after = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in FIXTURE.rglob("*") if path.is_file()}
    file_nodes = [node for node in result["graph"]["nodes"] if node["label"] == "File"]
    alpha = next(item for item in result["inventory"] if item["source_path"] == "services/alpha.js")
    beta = next(item for item in result["inventory"] if item["source_path"] == "services/beta.js")
    assert after == before
    assert len(result["inventory"]) > len(file_nodes) == 1
    assert alpha["extraction_status"] == "in_scope_succeeded"
    assert beta["extraction_status"] == "out_of_scope"
    assert result["graph"]["metadata"]["coverage_status"] == "scope_complete"


def test_in_scope_failure_prevents_scope_complete(monkeypatch, tmp_path):
    default = cli.load_profile("default")
    monkeypatch.setattr(cli, "load_profile", lambda name: default if name == "default" else scoped_profile())
    monkeypatch.setattr(cli, "extract_file", lambda payload: ExtractionResult([], {
        "source_path": payload["source_path"], "language": payload["language"], "extractor": payload["language"],
        "failure_category": "abnormal_exit", "diagnostic": "Extraction worker exited with code 139.", "status": "skipped",
    }))

    result = cli.analyze(FIXTURE, "failed-scope", "selected", tmp_path)

    assert result["analysis_status"] == "failed"
    assert result["graph"]["metadata"]["coverage_status"] == "scope_partial_with_extraction_failures"


def test_out_of_scope_semantic_reference_uses_boundary_node():
    evidence = Evidence("scope", "selected.cs", 1, 1, "roslyn", 1.0, "hash").to_dict()
    graph = normalize("scope", [{"source_path": "selected.cs", "source_hash": "hash"}], [])
    facts = [
        {"project_id": "scope", "kind": "controller", "name": "SelectedController", "properties": {"identity": "global::Selected.Controller"}, "evidence": {**evidence, "resolution_status": "proven"}},
        {"project_id": "scope", "kind": "action", "name": "Get", "properties": {"identity": "global::Selected.Controller.Get()", "owner_identity": "global::Selected.Controller", "return_type_identity": "global::Outside.Dto"}, "evidence": {**evidence, "resolution_status": "proven"}},
    ]

    cli.merge_roslyn(graph, facts, "scope", {"global::Outside.Dto": "outside.cs"})

    boundary = next(node for node in graph["nodes"] if node["label"] == "OutOfScopeReference")
    assert boundary["properties"]["source_path"] == "outside.cs"
    assert any(edge["type"] == "DEPENDS_ON_OUT_OF_SCOPE" and edge["target"] == boundary["id"] for edge in graph["edges"])
    assert not any(node["label"] == "Type" and node["properties"].get("identity") == "global::Outside.Dto" for node in graph["nodes"])


def test_selected_scope_filters_out_of_scope_roslyn_facts(monkeypatch, tmp_path):
    default = cli.load_profile("default")
    monkeypatch.setattr(cli, "load_profile", lambda name: default if name == "default" else scoped_profile())
    monkeypatch.setattr(cli, "extract_file", fake_success)
    evidence = Evidence("selected-roslyn", "services/alpha.js", 1, 1, "roslyn", 1.0, "hash").to_dict()
    outside_evidence = Evidence("selected-roslyn", "services/beta.js", 1, 1, "roslyn", 1.0, "hash").to_dict()
    monkeypatch.setattr(cli, "enrich", lambda *_: {
        "project_id": "selected-roslyn",
        "warnings": [],
        "facts": [
            {"project_id": "selected-roslyn", "kind": "controller", "name": "SelectedController", "properties": {"identity": "global::Selected.Controller"}, "evidence": {**evidence, "resolution_status": "proven"}},
            {"project_id": "selected-roslyn", "kind": "controller", "name": "OutsideController", "properties": {"identity": "global::Outside.Controller"}, "evidence": {**outside_evidence, "resolution_status": "proven"}},
        ],
    })

    result = cli.analyze(FIXTURE, "selected-roslyn", "selected", tmp_path, enable_roslyn=True)

    identities = {node["properties"].get("identity") for node in result["graph"]["nodes"]}
    assert "global::Selected.Controller" in identities
    assert "global::Outside.Controller" not in identities
