import json
from pathlib import Path

import pytest

from polaris_modernization.application_understanding.providers import MockReasoningProvider
from polaris_modernization.application_understanding.models import BusinessCapability, ConfidenceAssessment, EvidenceReference, ReasoningResult
from polaris_modernization.application_understanding.retrieval import build_evidence_packages, load_approved_graph
from polaris_modernization.application_understanding.workflow import run_application_understanding


def kg(tmp_path, ready=True):
    root=tmp_path/'kg'; root.mkdir()
    graph={"nodes":[
        {"id":"p:RazorView:Dashboard","label":"RazorView","name":"src/Web/Views/Dashboard/Index.cshtml","evidence":[{"source_path":"src/Web/Views/Dashboard/Index.cshtml","line_start":1,"line_end":2,"extraction_method":"tree-sitter","confidence":1}]},
        {"id":"p:AngularController:DashboardController","label":"AngularController","name":"DashboardController","evidence":[{"source_path":"src/Web/content/app/components/dashboard/controller.js","line_start":1,"line_end":2,"extraction_method":"tree-sitter","confidence":1}]},
        {"id":"p:Route:dashboard","label":"Route","name":"dashboard","evidence":[{"source_path":"src/Web/content/app/app.js","line_start":1,"line_end":2,"extraction_method":"tree-sitter","confidence":1}]},
        {"id":"p:ApiCall:/api/x","label":"ApiCall","name":"/api/x","evidence":[{"source_path":"src/Web/content/app/components/dashboard/service.js","line_start":1,"line_end":2,"extraction_method":"tree-sitter","confidence":1}]},
    ],"edges":[{"source":"p:Route:dashboard","target":"p:AngularController:DashboardController","type":"DEPENDS_ON","evidence":[{}]}]}
    (root/'knowledge-graph.json').write_text(json.dumps(graph)); (root/'knowledge-graph-validation.json').write_text(json.dumps({"valid":True})); (root/'graph-run-status.json').write_text(json.dumps({"project_id":"p","scope":{"extraction_warning_count":0}})); (root/'kg-readiness-analysis.md').write_text("KG_READINESS_STATUS: READY_WITH_EXPLAINED_LIMITATIONS" if ready else "KG_READINESS_STATUS: NOT_READY")
    return root


def test_not_ready_kg_cannot_proceed(tmp_path):
    with pytest.raises(ValueError,match="not approved"):
        load_approved_graph(kg(tmp_path,False))


def test_evidence_packages_are_deterministic_and_hash_stable(tmp_path):
    graph=load_approved_graph(kg(tmp_path))["graph"]
    assert [item.package_hash for item in build_evidence_packages(graph)] == [item.package_hash for item in build_evidence_packages(graph)]


def test_mock_provider_and_artifacts_keep_api_mapping_unresolved(tmp_path):
    result=run_application_understanding(kg(tmp_path),tmp_path/'out',MockReasoningProvider())
    assert result['understanding'].status == 'COMPLETE'
    assert result['token_usage']['llm_provider_used'] == 'MOCK'
    assert result['understanding'].user_workflows[0].backend_mapping == 'UNRESOLVED'
    assert (tmp_path/'out/latest/application-understanding.json').is_file()


def test_none_provider_is_framework_only_and_records_tokens(tmp_path):
    result=run_application_understanding(kg(tmp_path),tmp_path/'out')
    assert result['understanding'].status == 'FRAMEWORK_ONLY'
    assert result['token_usage']['llm_calls'] == 0
    assert result['token_usage']['approx_input_tokens'] == 0


def test_unsupported_ai_claim_without_package_evidence_is_rejected(tmp_path):
    class UnsafeProvider:
        name = "TEST"
        def reason(self, packages):
            return ReasoningResult(claims=[BusinessCapability(name="unsupported", origin="AI_INTERPRETATION", evidence=[EvidenceReference(node_id="missing", source_path="x", provenance="STRUCTURAL_ONLY")], confidence=ConfidenceAssessment(level="LOW", provenance=["STRUCTURAL_ONLY"], rationale="test"))])
    with pytest.raises(ValueError, match="Unsupported AI claim"):
        run_application_understanding(kg(tmp_path), tmp_path / "out", UnsafeProvider())


def test_reasoning_results_are_cached_by_stable_package_hash(tmp_path):
    output = tmp_path / "out"
    first = run_application_understanding(kg(tmp_path), output, MockReasoningProvider())
    second = run_application_understanding(tmp_path / "kg", output, MockReasoningProvider())
    assert first["token_usage"]["cache_hit"] is False
    assert second["token_usage"]["cache_hit"] is True
    assert second["token_usage"]["llm_calls"] == 0
