import hashlib
import json
import shutil
from pathlib import Path

import pytest

from polaris_modernization.cli import analyze, merge_roslyn


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "roslyn-semantic"


def evidence(path="ShipmentGatewayController.cs"):
    return {"project_id": "semantic-demo", "source_path": path, "line_start": 1, "line_end": 1,
            "column_start": 1, "column_end": 1, "source_hash": "fixture", "extractor": "roslyn",
            "confidence": 1.0, "resolution_status": "proven", "diagnostic": None}


def fact(kind, name, identity, **properties):
    return {"kind": kind, "name": name, "project_id": "semantic-demo", "evidence": evidence(),
            "properties": {"identity": identity, **properties}}


def test_semantic_graph_relationships_are_project_scoped():
    controller = "global::Sample.Shipments.ShipmentGatewayController"
    action = "global::Sample.Shipments.ShipmentGatewayController.Fetch(string)"
    status = "global::Sample.Shipments.ShipmentGatewayController.Status()"
    dto = "global::Sample.Shipments.ShipmentSummary"
    graph = {"nodes": [], "edges": [], "warnings": []}
    merge_roslyn(graph, [
        fact("controller", "ShipmentGatewayController", controller),
        fact("action", "Fetch", action, owner_identity=controller, return_type_identity=dto),
        fact("action", "Status", status, owner_identity=controller, return_type_identity="global::System.String"),
        fact("dto", "ShipmentSummary", dto),
        fact("endpoint", "Fetch GET", f"{action}:GET:api/shipments/{{trackingCode}}", owner_identity=action, route_template="api/shipments/{trackingCode}", verb="GET"),
        fact("authorization_policy", "AuthorizeAttribute", f"{action}:auth", owner_identity=action, owner_kind="action", policy="shipments.read"),
        fact("property", "TrackingCode", f"{dto}.TrackingCode", owner_identity=dto, type_identity="global::System.String"),
        fact("method", "BuildSummary", f"{controller}.BuildSummary(string)", owner_identity=controller),
        fact("invocation", "BuildSummary", f"{action}:invoke", owner_identity=action, target_identity=f"{controller}.BuildSummary(string)"),
    ], "semantic-demo")
    assert {edge["type"] for edge in graph["edges"]} >= {"DECLARES", "EXPOSES", "RETURNS_TYPE", "HAS_PROPERTY", "INVOKES", "PROTECTED_BY"}
    labels_by_id = {node["id"]: node["label"] for node in graph["nodes"]}
    returned_by_action = {edge["source"]: labels_by_id[edge["target"]] for edge in graph["edges"] if edge["type"] == "RETURNS_TYPE"}
    action_nodes = {node["name"]: node["id"] for node in graph["nodes"] if node["label"] == "Action"}
    assert returned_by_action[action_nodes["Fetch"]] == "DTO"
    assert returned_by_action[action_nodes["Status"]] == "Type"
    assert all(node["project_id"] == "semantic-demo" for node in graph["nodes"])
    assert all(edge["project_id"] == "semantic-demo" for edge in graph["edges"])


def test_analysis_never_changes_semantic_fixture(monkeypatch, tmp_path):
    before = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in FIXTURE.rglob("*.cs")}
    monkeypatch.setattr("polaris_modernization.roslyn_bridge.shutil.which", lambda _: None)
    analyze(FIXTURE, "unchanged-fixture", "default", tmp_path, enable_roslyn=True)
    after = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in FIXTURE.rglob("*.cs")}
    assert before == after


@pytest.mark.skipif(shutil.which("dotnet") is None, reason=".NET SDK is not installed")
def test_roslyn_fixture_produces_evidence_backed_graph(tmp_path):
    before = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in FIXTURE.rglob("*.cs")}
    result = analyze(FIXTURE, "semantic-fixture", "default", tmp_path, enable_roslyn=True)
    roslyn = json.loads((result["output"] / "roslyn-semantic.json").read_text(encoding="utf-8"))
    after = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in FIXTURE.rglob("*.cs")}
    kinds = {item["kind"] for item in roslyn["facts"]}
    edges = {item["type"] for item in result["graph"]["edges"]}
    assert roslyn["project_id"] == "semantic-fixture"
    assert before == after
    assert {"namespace", "controller", "action", "dto", "property", "endpoint", "authorization_policy", "invocation"} <= kinds
    assert {"DECLARES", "EXPOSES", "RETURNS_TYPE", "HAS_PROPERTY", "INVOKES", "PROTECTED_BY"} <= edges
    assert any(item["properties"].get("route_template") == "api/shipments/{trackingCode}" for item in roslyn["facts"] if item["kind"] == "endpoint")
    labels_by_id = {node["id"]: node["label"] for node in result["graph"]["nodes"]}
    action_nodes = {node["name"]: node["id"] for node in result["graph"]["nodes"] if node["label"] == "Action"}
    returned_by_action = {edge["source"]: labels_by_id[edge["target"]] for edge in result["graph"]["edges"] if edge["type"] == "RETURNS_TYPE"}
    assert returned_by_action[action_nodes["Fetch"]] == "DTO"
    assert returned_by_action[action_nodes["Status"]] == "Type"
