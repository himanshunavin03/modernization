"""Provider-neutral LangChain reasoning boundary with no credentials in the workflow."""
from __future__ import annotations

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
