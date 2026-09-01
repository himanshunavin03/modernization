import json
from pathlib import Path

from polaris_modernization.cli import analyze


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "framework-contract"


def test_framework_registry_emits_endpoint_contracts_and_proven_mapping(tmp_path):
    result = analyze(FIXTURE, "contracts", "default", tmp_path)
    facts = [fact.to_dict() for fact in result["facts"]]
    endpoints = [fact for fact in facts if fact["kind"] == "endpoint"]
    assert any(item["name"] == "GET /api/orders/{id}" and item["properties"]["response_type"] == "OrderDto" for item in endpoints)
    assert any(item["name"] == "POST /api/orders" for item in endpoints)
    assert any(item["kind"] == "api_mapping" and item["properties"]["status"] == "PROVEN" for item in facts)
    graph = json.loads((result["output"] / "knowledge-graph.json").read_text())
    assert any(edge["type"] == "IMPLEMENTED_BY" for edge in graph["edges"])


def test_razor_model_and_action_relationships_are_evidence_backed(tmp_path):
    result = analyze(FIXTURE, "contracts", "default", tmp_path)
    graph = result["graph"]
    assert any(edge["type"] == "USES_VIEW_MODEL" for edge in graph["edges"])
    assert any(edge["type"] == "CALLS_ACTION" for edge in graph["edges"])
    assert all(edge["evidence"] for edge in graph["edges"])


def test_dynamic_angular_url_is_not_mapped(tmp_path):
    result = analyze(FIXTURE, "contracts", "default", tmp_path)
    assert any("Dynamic AngularJS API URL" in item["message"] for item in result["warnings"])
    assert all("+ id" not in fact.name for fact in result["facts"] if fact.kind == "api_mapping")
