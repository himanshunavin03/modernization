"""Compact structured contracts for design and architecture decisions."""
from __future__ import annotations

from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field


class DesignSpecification(BaseModel):
    model_config = ConfigDict(extra="forbid")
    provider: str
    source_reference: str | None = None
    status: Literal["NOT_PROVIDED", "AVAILABLE", "FIGMA_CONNECTOR_NOT_IMPLEMENTED"]
    screens: list[str] = Field(default_factory=list)
    components: list[str] = Field(default_factory=list)
    responsive_rules: list[str] = Field(default_factory=list)
    design_tokens: dict[str, str] = Field(default_factory=dict)
    unresolved_design_items: list[str] = Field(default_factory=list)
    traceability: list[str] = Field(default_factory=list)


class DesignProvider(Protocol):
    provider_type: str

    def can_handle(self, provider_type: str) -> bool: ...
    def analyze(self, source_reference: str | None) -> DesignSpecification: ...


class NoDesignProvider:
    provider_type = "NONE"

    def can_handle(self, provider_type: str) -> bool:
        return provider_type.upper() in {"", "NONE"}

    def analyze(self, source_reference: str | None = None) -> DesignSpecification:
        return DesignSpecification(provider="NONE", status="NOT_PROVIDED")


class FigmaDesignProvider:
    provider_type = "FIGMA"

    def can_handle(self, provider_type: str) -> bool:
        return provider_type.upper() == self.provider_type

    def analyze(self, source_reference: str | None) -> DesignSpecification:
        return DesignSpecification(
            provider=self.provider_type,
            source_reference=source_reference,
            status="FIGMA_CONNECTOR_NOT_IMPLEMENTED",
            unresolved_design_items=["A Figma connector is required before design content can be analyzed."],
            traceability=[source_reference] if source_reference else [],
        )


class ArchitectureDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    category: str
    technology: str
    status: Literal["USE", "DO_NOT_USE", "EVALUATE", "NOT_APPLICABLE"]
    decision: str
    rationale: str
    requirement_refs: list[str]
    story_refs: list[str]
    api_refs: list[str]
    design_refs: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    alternatives: list[str] = Field(default_factory=list)
    adr_required: bool = False


class ArchitectureRecommendation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    feature_id: str
    target_platform: str
    target_framework: str
    framework_version: str
    decisions: list[ArchitectureDecision]
    limitations: list[str]
    traceability: dict[str, list[str]]


class ArchitectureValidation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: Literal["ARCHITECTURE_READY", "ARCHITECTURE_READY_WITH_LIMITATIONS", "ARCHITECTURE_BLOCKED"]
    checks: dict[str, bool]
    warnings: list[str]
    blockers: list[str]
