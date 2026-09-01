"""Provider-neutral LangChain reasoning boundary with no credentials in the workflow."""
from __future__ import annotations

import os
from typing import Protocol

from langchain_core.runnables import Runnable

from polaris_modernization.application_understanding.models import EvidencePackage, ReasoningResult


class ReasoningProvider(Protocol):
    name: str

    def reason(self, packages: list[EvidencePackage]) -> ReasoningResult: ...


class MockReasoningProvider:
    """Test-only deterministic provider. It intentionally creates no business claims."""
    name = "MOCK"

    def reason(self, packages: list[EvidencePackage]) -> ReasoningResult:
        payload = "\n".join(package.model_dump_json() for package in packages)
        return ReasoningResult(input_tokens=(len(payload) + 3) // 4, output_tokens=0)


class RunnableReasoningProvider:
    """Adapter for a future credentialed LangChain runnable returning `ReasoningResult`."""
    name = "LANGCHAIN"

    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    def reason(self, packages: list[EvidencePackage]) -> ReasoningResult:
        result = self.runnable.invoke([package.model_dump(mode="json") for package in packages])
        return result if isinstance(result, ReasoningResult) else ReasoningResult.model_validate(result)


def provider_from_environment() -> ReasoningProvider | None:
    """Construct a configured enterprise provider lazily; secrets remain in the environment."""
    if all(os.getenv(name) for name in ("AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY", "AZURE_OPENAI_DEPLOYMENT")):
        from langchain_openai import AzureChatOpenAI
        return RunnableReasoningProvider(AzureChatOpenAI(azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"], api_key=os.environ["AZURE_OPENAI_API_KEY"], azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT"], api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21")))
    if os.getenv("AWS_REGION") and os.getenv("POLARIS_BEDROCK_MODEL_ID"):
        from langchain_aws import ChatBedrockConverse
        return RunnableReasoningProvider(ChatBedrockConverse(model_id=os.environ["POLARIS_BEDROCK_MODEL_ID"], region_name=os.environ["AWS_REGION"]))
    return None


def provider_configuration_help() -> list[str]:
    return ["Azure OpenAI: AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_DEPLOYMENT (optional AZURE_OPENAI_API_VERSION).", "AWS Bedrock: AWS_REGION and POLARIS_BEDROCK_MODEL_ID; credentials use the standard AWS credential chain."]
