import inspect
from hashlib import sha256
import json

import pytest

from polaris_modernization.application_understanding.models import AgentReasoningSubmission
from polaris_modernization.application_understanding.providers import (
    AzureOpenAIHeadlessProvider, BedrockHeadlessProvider, headless_provider_from_environment,
)
from polaris_modernization.application_understanding.retrieval import build_evidence_packages, load_approved_graph
from polaris_modernization.application_understanding.workflow import (
    UnsupportedAgentClaimsError, prepare_application_understanding,
    validate_and_persist_application_understanding,
)
from polaris_modernization.knowledge_graph_agent import create_knowledge_graph


def kg(tmp_path, ready=True):
    root = tmp_path / "kg"
    root.mkdir()
    graph = {"nodes": [
        {"id": "p:RazorView:Dashboard", "label": "RazorView", "name": "src/Web/Views/Dashboard/Index.cshtml", "evidence": [{"source_path": "src/Web/Views/Dashboard/Index.cshtml", "line_start": 1, "line_end": 2, "extraction_method": "tree-sitter", "confidence": 1}]},
        {"id": "p:AngularController:DashboardController", "label": "AngularController", "name": "DashboardController", "evidence": [{"source_path": "src/Web/content/app/components/dashboard/controller.js", "line_start": 1, "line_end": 2, "extraction_method": "tree-sitter", "confidence": 1}]},
        {"id": "p:Route:dashboard", "label": "Route", "name": "dashboard", "evidence": [{"source_path": "src/Web/content/app/app.js", "line_start": 1, "line_end": 2, "extraction_method": "tree-sitter", "confidence": 1}]},
        {"id": "p:ApiCall:/api/x", "label": "ApiCall", "name": "/api/x", "evidence": [{"source_path": "src/Web/content/app/components/dashboard/service.js", "line_start": 1, "line_end": 2, "extraction_method": "tree-sitter", "confidence": 1}]},
        {"id": "p:Endpoint:GET /api/x", "label": "Endpoint", "name": "GET /api/x", "evidence": [{"source_path": "src/Api/XController.cs", "line_start": 10, "line_end": 12, "extraction_method": "framework-analyzer", "confidence": 1}]},
    ], "edges": [
        {"source": "p:Route:dashboard", "target": "p:AngularController:DashboardController", "type": "DEPENDS_ON", "evidence": [{}]},
        {"source": "p:ApiCall:/api/x", "target": "p:Endpoint:GET /api/x", "type": "IMPLEMENTED_BY", "evidence": [{}]},
    ]}
    (root / "knowledge-graph.json").write_text(json.dumps(graph))
    (root / "knowledge-graph-validation.json").write_text(json.dumps({"valid": True}))
    (root / "graph-run-status.json").write_text(json.dumps({"project_id": "p", "scope": {"extraction_warning_count": 0}}))
    (root / "kg-readiness-analysis.md").write_text("KG_READINESS_STATUS: READY_WITH_EXPLAINED_LIMITATIONS" if ready else "KG_READINESS_STATUS: NOT_READY")
    return root


def agent_item(reference, name="Evidence-backed dashboard capability"):
    return {"name": name, "origin": "AGENT_REASONING", "evidence": [reference], "confidence": {"level": "LOW", "provenance": [reference["provenance"]], "rationale": "Only package evidence was used."}}


def valid_submission(packages):
    evidence = [item for package in packages for item in package.evidence]
    razor = next(item for item in evidence if item.source_path.endswith("Index.cshtml")).model_dump(mode="json")
    angular = next(item for item in evidence if item.source_path.endswith("controller.js")).model_dump(mode="json")
    route = next(item for item in evidence if item.source_path.endswith("app.js")).model_dump(mode="json")
    purpose = agent_item(razor, "Dashboard-oriented web application")
    workflow = {**agent_item(route, "Dashboard route workflow"), "ui_surface": "dashboard", "backend_mapping": "UNRESOLVED"}
    return {
        "kg_run_id": "LEGACY_TEST_RUN",
        "evidence_package_manifest_hash": sha256(json.dumps(
            {item.package_id: item.package_hash for item in packages},
            sort_keys=True, separators=(",", ":"),
        ).encode("utf-8")).hexdigest(),
        "application_purpose": purpose,
        "primary_application_type": "Hybrid server-rendered and client-side web application",
        "technical_composition": ["ASP.NET MVC/Razor", "AngularJS 1.x", "ASP.NET Web API"],
        "major_user_facing_areas": ["Dashboard"],
        "major_backend_areas": ["API"],
        "business_modules": [agent_item(razor, "Dashboard module")],
        "business_capabilities": [agent_item(angular, "Dashboard client interaction")],
        "user_workflows": [workflow],
        "business_rules": [], "domain_concepts": [], "ui_surfaces": [], "dependencies": [],
        "best_razor_demo_candidate": "src/Web/Views/Dashboard/Index.cshtml",
        "razor_demo_capability": agent_item(razor, "Dashboard shell capability"),
        "razor_demo_workflow": workflow,
        "best_angular_demo_candidate": "DashboardController",
        "angular_demo_capability": agent_item(angular, "Dashboard controller capability"),
        "angular_demo_workflow": workflow,
    }


def test_not_ready_kg_cannot_prepare(tmp_path):
    with pytest.raises(ValueError, match="not approved"):
        prepare_application_understanding(kg(tmp_path, False), tmp_path / "out")


def test_evidence_packages_are_deterministic_and_hash_stable(tmp_path):
    graph = load_approved_graph(kg(tmp_path))["graph"]
    assert [item.package_hash for item in build_evidence_packages(graph)] == [item.package_hash for item in build_evidence_packages(graph)]


def test_interactive_preparation_requires_no_openai_key(monkeypatch, tmp_path):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    prepared = prepare_application_understanding(kg(tmp_path), tmp_path / "out")
    assert (prepared["path"] / "evidence-packages.json").is_file()
    assert (prepared["path"] / "agent-reasoning-schema.json").is_file()
    assert json.loads((prepared["path"] / "preparation.json").read_text())["external_llm_calls"] == 0


def test_knowledge_graph_creation_has_no_agent_or_provider_dependency():
    source = inspect.getsource(create_knowledge_graph)
    assert "provider" not in source.lower()
    assert "agent_reasoning" not in source.lower()


def test_valid_agent_submission_is_validated_and_persisted(tmp_path):
    root = kg(tmp_path)
    packages = build_evidence_packages(load_approved_graph(root)["graph"])
    result_path = tmp_path / "agent.json"
    result_path.write_text(json.dumps(valid_submission(packages)))
    result = validate_and_persist_application_understanding(root, tmp_path / "out", result_path)
    assert result["understanding"].status == "COMPLETE"
    assert result["understanding"].user_workflows[-1].backend_mapping == "UNRESOLVED"
    assert (tmp_path / "out/latest/application-understanding.json").is_file()
    assert json.loads((tmp_path / "out/latest/agent-reasoning-validation.json").read_text())["valid"] is True
    assert result["understanding"].kg_run_id == "LEGACY_TEST_RUN"
    assert result["understanding"].business_modules[0].evidence_package_ids
    assert all(item.evidence_package_ids for item in result["understanding"].ui_surfaces)


def test_proven_api_workflow_requires_implemented_by_evidence(tmp_path):
    root = kg(tmp_path)
    packages = build_evidence_packages(load_approved_graph(root)["graph"])
    payload = valid_submission(packages)
    references = [reference.model_dump(mode="json") for package in packages if package.cluster_type == "API" for reference in package.evidence]
    call = next(reference for reference in references if reference["node_id"] == "p:ApiCall:/api/x")
    endpoint = next(reference for reference in references if reference["node_id"] == "p:Endpoint:GET /api/x")
    payload["user_workflows"][0]["evidence"] = [call, endpoint]
    payload["user_workflows"][0]["backend_mapping"] = "PROVEN"
    path = tmp_path / "proven.json"
    path.write_text(json.dumps(payload))
    result = validate_and_persist_application_understanding(root, tmp_path / "out", path)
    assert result["understanding"].user_workflows[-1].backend_mapping == "PROVEN"
    payload = valid_submission(packages)
    payload["user_workflows"][0]["backend_mapping"] = "PROVEN"
    path.write_text(json.dumps(payload))
    with pytest.raises(UnsupportedAgentClaimsError, match="IMPLEMENTED_BY"):
        validate_and_persist_application_understanding(root, tmp_path / "out", path)


def test_stale_package_hashes_are_rejected(tmp_path):
    root = kg(tmp_path)
    packages = build_evidence_packages(load_approved_graph(root)["graph"])
    payload = valid_submission(packages)
    payload["evidence_package_manifest_hash"] = "stale"
    path = tmp_path / "stale.json"
    path.write_text(json.dumps(payload))
    with pytest.raises(UnsupportedAgentClaimsError, match="manifest hash"):
        validate_and_persist_application_understanding(root, tmp_path / "out", path)


def test_malformed_agent_submission_is_rejected(tmp_path):
    path = tmp_path / "agent.json"
    path.write_text(json.dumps({"unexpected": "payload"}))
    with pytest.raises(Exception):
        validate_and_persist_application_understanding(kg(tmp_path), tmp_path / "out", path)


def test_unsupported_agent_claim_and_invented_api_mapping_are_rejected(tmp_path):
    root = kg(tmp_path)
    packages = build_evidence_packages(load_approved_graph(root)["graph"])
    payload = valid_submission(packages)
    payload["business_capabilities"][0]["evidence"][0]["node_id"] = "missing"
    path = tmp_path / "unsupported.json"
    path.write_text(json.dumps(payload))
    with pytest.raises(UnsupportedAgentClaimsError):
        validate_and_persist_application_understanding(root, tmp_path / "out", path)
    payload = valid_submission(packages)
    payload["user_workflows"][0]["backend_mapping"] = "MAPPED"
    path.write_text(json.dumps(payload))
    with pytest.raises(Exception):
        validate_and_persist_application_understanding(root, tmp_path / "out", path)


def test_headless_enterprise_boundaries_remain_optional(monkeypatch):
    monkeypatch.setenv("POLARIS_HEADLESS_LLM_PROVIDER", "azure")
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://example.invalid")
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "test-only-secret")
    monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "deployment")
    assert isinstance(headless_provider_from_environment(), AzureOpenAIHeadlessProvider)
    monkeypatch.setenv("POLARIS_HEADLESS_LLM_PROVIDER", "bedrock")
    monkeypatch.setenv("AWS_REGION", "ca-central-1")
    monkeypatch.setenv("POLARIS_BEDROCK_MODEL_ID", "model")
    assert isinstance(headless_provider_from_environment(), BedrockHeadlessProvider)


def test_submission_schema_requires_agent_reasoning_origin(tmp_path):
    packages = build_evidence_packages(load_approved_graph(kg(tmp_path))["graph"])
    payload = valid_submission(packages)
    payload["application_purpose"]["origin"] = "DETERMINISTIC_FACT"
    with pytest.raises(UnsupportedAgentClaimsError):
        path = tmp_path / "origin.json"
        path.write_text(json.dumps(payload))
        validate_and_persist_application_understanding(tmp_path / "kg", tmp_path / "out", path)
