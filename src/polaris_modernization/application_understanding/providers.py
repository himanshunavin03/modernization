"""Optional headless enterprise providers; interactive agent mode never uses these."""
from __future__ import annotations

import os
from typing import Protocol

from langchain_core.runnables import Runnable

from polaris_modernization.application_understanding.models import AgentReasoningSubmission


class ProviderConfigurationError(RuntimeError):
    """A requested headless provider cannot be used in the current environment."""


class HeadlessReasoningProvider(Protocol):
    name: str
    model: str

    def structured_runnable(self) -> Runnable: ...


class AzureOpenAIHeadlessProvider:
    name = "AZURE_OPENAI"

    def __init__(self, endpoint: str, deployment: str, api_version: str):
        self.model = deployment
        self._endpoint = endpoint
        self._api_version = api_version

    def structured_runnable(self) -> Runnable:
        try:
            from langchain_openai import AzureChatOpenAI
        except ImportError as error:
            raise ProviderConfigurationError("Azure OpenAI headless mode requires `pip install -e \".[azure-openai]\"`.") from error
        return AzureChatOpenAI(azure_endpoint=self._endpoint, azure_deployment=self.model, api_version=self._api_version, temperature=0).with_structured_output(AgentReasoningSubmission)


class BedrockHeadlessProvider:
    name = "BEDROCK"

    def __init__(self, model: str, region: str):
        self.model = model
        self._region = region

    def structured_runnable(self) -> Runnable:
        try:
            from langchain_aws import ChatBedrockConverse
        except ImportError as error:
            raise ProviderConfigurationError("Bedrock headless mode requires `pip install -e \".[bedrock]\"`.") from error
        return ChatBedrockConverse(model_id=self.model, region_name=self._region).with_structured_output(AgentReasoningSubmission)


def headless_provider_from_environment() -> HeadlessReasoningProvider | None:
    """Future server-side selection; never called by interactive Codex/Copilot workflows."""
    selected = os.getenv("POLARIS_HEADLESS_LLM_PROVIDER", "").strip().lower()
    if selected and selected not in {"azure", "bedrock"}:
        raise ProviderConfigurationError("POLARIS_HEADLESS_LLM_PROVIDER must be one of: azure, bedrock.")
    if selected in {"", "azure"} and all(os.getenv(name) for name in ("AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY", "AZURE_OPENAI_DEPLOYMENT")):
        return AzureOpenAIHeadlessProvider(os.environ["AZURE_OPENAI_ENDPOINT"], os.environ["AZURE_OPENAI_DEPLOYMENT"], os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21"))
    if selected in {"", "bedrock"} and os.getenv("AWS_REGION") and os.getenv("POLARIS_BEDROCK_MODEL_ID"):
        return BedrockHeadlessProvider(os.environ["POLARIS_BEDROCK_MODEL_ID"], os.environ["AWS_REGION"])
    return None
