"""Provider-neutral, structured LangChain reasoning with environment-only credentials."""
from __future__ import annotations

import json
import os
from typing import Any, Protocol

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import Runnable

from polaris_modernization.application_understanding.models import EvidencePackage, ReasoningResult


class ProviderConfigurationError(RuntimeError):
    """A requested provider cannot be used in the current local environment."""


class ReasoningProvider(Protocol):
    name: str
    model: str | None

    def reason(self, package: EvidencePackage) -> ReasoningResult: ...


def _compact_payload(package: EvidencePackage) -> dict[str, Any]:
    """Keep model input bounded to one evidence package and never include source text."""
    return {
        "package_id": package.package_id,
        "package_hash": package.package_hash,
        "cluster_type": package.cluster_type,
        "title": package.title,
        "node_ids": package.node_ids,
        "relationships": [
            {"type": edge.get("type"), "source": edge.get("source"), "target": edge.get("target")}
            for edge in package.relationships
        ],
        "evidence": [reference.model_dump(mode="json") for reference in package.evidence],
        "unresolved_relationships": package.unresolved_relationships,
        "confidence": package.confidence.model_dump(mode="json"),
    }


_SYSTEM_PROMPT = """You analyze one compact, evidence-backed application knowledge-graph package.
Return only the requested structured result. Do not infer behavior absent from the package.
Every AI interpretation must use one or more supplied evidence references and only supplied node IDs.
Do not invent backend endpoint mappings. If the package says BACKEND_MAPPING=UNRESOLVED, preserve it.
Do not claim compiler proof when package provenance is partial, fallback, or structural only.
Use AI_INTERPRETATION origins for model-generated items. Source text is unavailable by design."""


def _usage(raw: Any) -> tuple[int, int]:
    metadata = getattr(raw, "usage_metadata", None) or getattr(raw, "response_metadata", {}).get("token_usage", {})
    if not isinstance(metadata, dict):
        return 0, 0
    return int(metadata.get("input_tokens", metadata.get("prompt_tokens", 0)) or 0), int(metadata.get("output_tokens", metadata.get("completion_tokens", 0)) or 0)


class StructuredRunnableReasoningProvider:
    """Adapts a LangChain structured-output runnable without coupling the workflow to a vendor."""

    def __init__(self, name: str, model: str | None, runnable: Runnable):
        self.name = name
        self.model = model
        self.runnable = runnable

    def reason(self, package: EvidencePackage) -> ReasoningResult:
        response = self.runnable.invoke([
            SystemMessage(content=_SYSTEM_PROMPT),
            HumanMessage(content=json.dumps(_compact_payload(package), sort_keys=True, separators=(",", ":"))),
        ])
        parsed = response.get("parsed") if isinstance(response, dict) and "parsed" in response else response
        if parsed is None:
            raise ValueError("Provider returned no structured application-understanding result.")
        result = parsed if isinstance(parsed, ReasoningResult) else ReasoningResult.model_validate(parsed)
        raw = response.get("raw") if isinstance(response, dict) else None
        input_tokens, output_tokens = _usage(raw)
        return result.model_copy(update={"input_tokens": input_tokens, "output_tokens": output_tokens})


class OpenAIReasoningProvider:
    """Local-demo OpenAI provider, constructed lazily so credentials never reach the workflow."""

    name = "OPENAI"

    def __init__(self, model: str, runnable: Runnable | None = None):
        self.model = model
        self._runnable = runnable

    def _structured_runnable(self) -> Runnable:
        if self._runnable is not None:
            return self._runnable
        try:
            from langchain_openai import ChatOpenAI
        except ImportError as error:
            raise ProviderConfigurationError("OpenAI provider requires `pip install -e \".[openai]\"`.") from error
        return ChatOpenAI(model=self.model, temperature=0).with_structured_output(ReasoningResult, include_raw=True)

    def reason(self, package: EvidencePackage) -> ReasoningResult:
        return StructuredRunnableReasoningProvider(self.name, self.model, self._structured_runnable()).reason(package)


class AzureOpenAIReasoningProvider(OpenAIReasoningProvider):
    name = "AZURE_OPENAI"

    def __init__(self, endpoint: str, deployment: str, api_version: str):
        super().__init__(deployment)
        self._endpoint = endpoint
        self._api_version = api_version

    def _structured_runnable(self) -> Runnable:
        try:
            from langchain_openai import AzureChatOpenAI
        except ImportError as error:
            raise ProviderConfigurationError("Azure OpenAI provider requires `pip install -e \".[azure-openai]\"`.") from error
        return AzureChatOpenAI(azure_endpoint=self._endpoint, azure_deployment=self.model, api_version=self._api_version, temperature=0).with_structured_output(ReasoningResult, include_raw=True)


class BedrockReasoningProvider:
    name = "BEDROCK"

    def __init__(self, model: str, region: str):
        self.model = model
        self._region = region

    def reason(self, package: EvidencePackage) -> ReasoningResult:
        try:
            from langchain_aws import ChatBedrockConverse
        except ImportError as error:
            raise ProviderConfigurationError("Bedrock provider requires `pip install -e \".[bedrock]\"`.") from error
        runnable = ChatBedrockConverse(model_id=self.model, region_name=self._region).with_structured_output(ReasoningResult, include_raw=True)
        return StructuredRunnableReasoningProvider(self.name, self.model, runnable).reason(package)


class MockReasoningProvider:
    """Test-only deterministic provider. It intentionally creates no business claims."""
    name = "MOCK"
    model = None

    def reason(self, package: EvidencePackage) -> ReasoningResult:
        return ReasoningResult(input_tokens=(len(json.dumps(_compact_payload(package))) + 3) // 4)


def provider_from_environment() -> ReasoningProvider | None:
    """Select only the explicitly requested provider, or a fully configured provider."""
    selected = os.getenv("POLARIS_LLM_PROVIDER", "").strip().lower()
    if selected and selected not in {"openai", "azure", "bedrock"}:
        raise ProviderConfigurationError("POLARIS_LLM_PROVIDER must be one of: openai, azure, bedrock.")
    if selected == "openai" and os.getenv("OPENAI_API_KEY"):
        return OpenAIReasoningProvider(os.getenv("POLARIS_OPENAI_MODEL", "gpt-4o-mini"))
    if selected == "azure" and all(os.getenv(name) for name in ("AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY", "AZURE_OPENAI_DEPLOYMENT")):
        return AzureOpenAIReasoningProvider(os.environ["AZURE_OPENAI_ENDPOINT"], os.environ["AZURE_OPENAI_DEPLOYMENT"], os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21"))
    if selected == "bedrock" and os.getenv("AWS_REGION") and os.getenv("POLARIS_BEDROCK_MODEL_ID"):
        return BedrockReasoningProvider(os.environ["POLARIS_BEDROCK_MODEL_ID"], os.environ["AWS_REGION"])
    if not selected:
        if all(os.getenv(name) for name in ("AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY", "AZURE_OPENAI_DEPLOYMENT")):
            return AzureOpenAIReasoningProvider(os.environ["AZURE_OPENAI_ENDPOINT"], os.environ["AZURE_OPENAI_DEPLOYMENT"], os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21"))
        if os.getenv("AWS_REGION") and os.getenv("POLARIS_BEDROCK_MODEL_ID"):
            return BedrockReasoningProvider(os.environ["POLARIS_BEDROCK_MODEL_ID"], os.environ["AWS_REGION"])
        if os.getenv("OPENAI_API_KEY"):
            return OpenAIReasoningProvider(os.getenv("POLARIS_OPENAI_MODEL", "gpt-4o-mini"))
    return None


def provider_configuration_help() -> list[str]:
    return [
        "OpenAI local demo: POLARIS_LLM_PROVIDER=openai, OPENAI_API_KEY, and optional POLARIS_OPENAI_MODEL (default gpt-4o-mini).",
        "Azure OpenAI: POLARIS_LLM_PROVIDER=azure, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, and AZURE_OPENAI_DEPLOYMENT.",
        "AWS Bedrock: POLARIS_LLM_PROVIDER=bedrock, AWS_REGION, and POLARIS_BEDROCK_MODEL_ID; credentials use the standard AWS credential chain.",
    ]
