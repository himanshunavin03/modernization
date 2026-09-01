import json
import inspect

import pytest
from langchain_core.messages import AIMessage

from polaris_modernization.application_understanding.models import BusinessCapability, ConfidenceAssessment, EvidenceReference, ReasoningResult
from polaris_modernization.application_understanding.providers import (
    AzureOpenAIReasoningProvider, BedrockReasoningProvider, MockReasoningProvider,
    OpenAIReasoningProvider, ProviderConfigurationError, provider_from_environment,
)
from polaris_modernization.application_understanding.retrieval import build_evidence_packages, load_approved_graph
from polaris_modernization.application_understanding.workflow import run_application_understanding
from polaris_modernization.knowledge_graph_agent import create_knowledge_graph


def kg(tmp_path, ready=True):
    root = tmp_path / "kg"
    root.mkdir()
    graph = {"nodes": [
        {"id": "p:RazorView:Dashboard", "label": "RazorView", "name": "src/Web/Views/Dashboard/Index.cshtml", "evidence": [{"source_path": "src/Web/Views/Dashboard/Index.cshtml", "line_start": 1, "line_end": 2, "extraction_method": "tree-sitter", "confidence": 1}]},
        {"id": "p:AngularController:DashboardController", "label": "AngularController", "name": "DashboardController", "evidence": [{"source_path": "src/Web/content/app/components/dashboard/controller.js", "line_start": 1, "line_end": 2, "extraction_method": "tree-sitter", "confidence": 1}]},
        {"id": "p:Route:dashboard", "label": "Route", "name": "dashboard", "evidence": [{"source_path": "src/Web/content/app/app.js", "line_start": 1, "line_end": 2, "extraction_method": "tree-sitter", "confidence": 1}]},
        {"id": "p:ApiCall:/api/x", "label": "ApiCall", "name": "/api/x", "evidence": [{"source_path": "src/Web/content/app/components/dashboard/service.js", "line_start": 1, "line_end": 2, "extraction_method": "tree-sitter", "confidence": 1}]},
    ], "edges": [{"source": "p:Route:dashboard", "target": "p:AngularController:DashboardController", "type": "DEPENDS_ON", "evidence": [{}]}]}
    (root / "knowledge-graph.json").write_text(json.dumps(graph))
    (root / "knowledge-graph-validation.json").write_text(json.dumps({"valid": True}))
    (root / "graph-run-status.json").write_text(json.dumps({"project_id": "p", "scope": {"extraction_warning_count": 0}}))
    (root / "kg-readiness-analysis.md").write_text("KG_READINESS_STATUS: READY_WITH_EXPLAINED_LIMITATIONS" if ready else "KG_READINESS_STATUS: NOT_READY")
    return root


def claim(node_id, source_path):
    return BusinessCapability(
        name="Evidence-backed dashboard capability", origin="AI_INTERPRETATION",
        evidence=[EvidenceReference(node_id=node_id, source_path=source_path, provenance="STRUCTURAL_ONLY")],
        confidence=ConfidenceAssessment(level="LOW", provenance=["STRUCTURAL_ONLY"], rationale="Fixture evidence."),
    )


class FakeStructuredRunnable:
    def __init__(self, response):
        self.response = response
        self.calls = 0

    def invoke(self, messages):
        self.calls += 1
        return self.response


def test_not_ready_kg_cannot_proceed(tmp_path):
    with pytest.raises(ValueError, match="not approved"):
        load_approved_graph(kg(tmp_path, False))


def test_evidence_packages_are_deterministic_and_hash_stable(tmp_path):
    graph = load_approved_graph(kg(tmp_path))["graph"]
    assert [item.package_hash for item in build_evidence_packages(graph)] == [item.package_hash for item in build_evidence_packages(graph)]


def test_knowledge_graph_creation_has_no_reasoning_provider_dependency():
    assert "provider_from_environment" not in inspect.getsource(create_knowledge_graph)
    assert "OpenAI" not in inspect.getsource(create_knowledge_graph)


def test_mock_provider_and_artifacts_keep_api_mapping_unresolved(tmp_path):
    result = run_application_understanding(kg(tmp_path), tmp_path / "out", MockReasoningProvider())
    assert result["understanding"].status == "COMPLETE"
    assert result["token_usage"]["llm_provider_used"] == "MOCK"
    assert result["understanding"].user_workflows[0].backend_mapping == "UNRESOLVED"
    assert (tmp_path / "out/latest/application-understanding.json").is_file()


def test_none_provider_is_framework_only_and_records_zero_tokens(tmp_path):
    result = run_application_understanding(kg(tmp_path), tmp_path / "out")
    assert result["understanding"].status == "FRAMEWORK_ONLY"
    assert result["token_usage"]["llm_calls"] == 0
    assert result["token_usage"]["total_tokens"] == 0


def test_explicit_openai_without_key_waits_without_llm(monkeypatch, tmp_path):
    for name in ("OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY", "AZURE_OPENAI_DEPLOYMENT", "AWS_REGION", "POLARIS_BEDROCK_MODEL_ID"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("POLARIS_LLM_PROVIDER", "openai")
    assert provider_from_environment() is None
    result = run_application_understanding(kg(tmp_path), tmp_path / "out", waiting_for_provider=True)
    assert result["understanding"].status == "WAITING_FOR_PROVIDER_CONFIGURATION"
    assert result["token_usage"]["llm_calls"] == 0


def test_provider_selection_is_explicit_and_preserves_enterprise_paths(monkeypatch):
    monkeypatch.setenv("POLARIS_LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-only-secret")
    monkeypatch.setenv("POLARIS_OPENAI_MODEL", "test-model")
    assert isinstance(provider_from_environment(), OpenAIReasoningProvider)
    monkeypatch.setenv("POLARIS_LLM_PROVIDER", "azure")
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://example.invalid")
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "test-only-secret")
    monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "deployment")
    assert isinstance(provider_from_environment(), AzureOpenAIReasoningProvider)
    monkeypatch.setenv("POLARIS_LLM_PROVIDER", "bedrock")
    monkeypatch.setenv("AWS_REGION", "ca-central-1")
    monkeypatch.setenv("POLARIS_BEDROCK_MODEL_ID", "model")
    assert isinstance(provider_from_environment(), BedrockReasoningProvider)
    monkeypatch.setenv("POLARIS_LLM_PROVIDER", "unknown")
    with pytest.raises(ProviderConfigurationError):
        provider_from_environment()


def test_unselected_provider_preserves_existing_enterprise_precedence(monkeypatch):
    monkeypatch.delenv("POLARIS_LLM_PROVIDER", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "test-only-secret")
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://example.invalid")
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "test-only-secret")
    monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "deployment")
    assert isinstance(provider_from_environment(), AzureOpenAIReasoningProvider)


def test_mocked_openai_response_is_structured_and_captures_actual_usage(tmp_path):
    package = build_evidence_packages(load_approved_graph(kg(tmp_path))["graph"])[0]
    response = {"parsed": ReasoningResult(claims=[claim(package.node_ids[0], package.evidence[0].source_path)]), "raw": AIMessage(content="", usage_metadata={"input_tokens": 19, "output_tokens": 7, "total_tokens": 26})}
    runnable = FakeStructuredRunnable(response)
    provider = OpenAIReasoningProvider("test-model", runnable)
    result = provider.reason(package)
    assert result.claims[0].origin == "AI_INTERPRETATION"
    assert (result.input_tokens, result.output_tokens) == (19, 7)
    assert runnable.calls == 1


def test_malformed_openai_response_is_rejected(tmp_path):
    package = build_evidence_packages(load_approved_graph(kg(tmp_path))["graph"])[0]
    provider = OpenAIReasoningProvider("test-model", FakeStructuredRunnable({"parsed": {"claims": "not-a-list"}, "raw": AIMessage(content="")}))
    with pytest.raises(Exception):
        provider.reason(package)


def test_unsupported_ai_claim_without_package_evidence_is_rejected(tmp_path):
    class UnsafeProvider:
        name = "TEST"
        model = "test"
        def reason(self, package):
            return ReasoningResult(claims=[claim("missing", "x")])
    with pytest.raises(ValueError, match="package-scoped KG evidence"):
        run_application_understanding(kg(tmp_path), tmp_path / "out", UnsafeProvider())


def test_reasoning_results_are_cached_per_stable_package_hash(tmp_path):
    output = tmp_path / "out"
    first = run_application_understanding(kg(tmp_path), output, MockReasoningProvider())
    second = run_application_understanding(tmp_path / "kg", output, MockReasoningProvider())
    assert first["token_usage"]["cache_misses"] == len(first["packages"])
    assert second["token_usage"]["cache_hits"] == len(second["packages"])
    assert second["token_usage"]["llm_calls"] == 0


def test_no_secret_is_persisted_in_application_understanding_artifacts(monkeypatch, tmp_path):
    secret = "test-only-secret"
    monkeypatch.setenv("OPENAI_API_KEY", secret)
    result = run_application_understanding(kg(tmp_path), tmp_path / "out", MockReasoningProvider())
    text = "\n".join(path.read_text(encoding="utf-8") for path in result["path"].iterdir() if path.is_file())
    assert secret not in text
