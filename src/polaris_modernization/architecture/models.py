"""Typed contracts for enterprise design and architecture decisions."""
from __future__ import annotations

from enum import StrEnum
from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field


class DecisionStatus(StrEnum):
    SELECTED = "SELECTED"
    RECOMMENDED = "RECOMMENDED"
    EVALUATED_ALTERNATIVE = "EVALUATED_ALTERNATIVE"
    NOT_SELECTED = "NOT_SELECTED"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    REQUIRES_CLARIFICATION = "REQUIRES_CLARIFICATION"


class SelectionSource(StrEnum):
    POLARIS_POC_DEFAULT = "POLARIS_POC_DEFAULT"
    POLARIS_RECOMMENDATION = "POLARIS_RECOMMENDATION"
    CUSTOMER_OVERRIDE = "CUSTOMER_OVERRIDE"
    ENTERPRISE_POLICY = "ENTERPRISE_POLICY"


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
    status: DecisionStatus
    decision: str
    rationale: str
    benefits: list[str]
    tradeoffs: list[str]
    selection_conditions: list[str]
    rejection_reason: str | None = None
    requirement_refs: list[str]
    feature_refs: list[str]
    story_refs: list[str]
    api_refs: list[str]
    design_refs: list[str] = Field(default_factory=list)
    adr_ref: str | None = None
    machine_traceability: dict[str, str]


class ArchitectureRecommendation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    feature_id: str
    target_platform: str
    target_framework: str
    framework_version: str
    decisions: list[ArchitectureDecision]
    limitations: list[str]
    traceability: dict[str, list[str]]


class ArchitectureSelection(BaseModel):
    model_config = ConfigDict(extra="forbid")
    feature_id: str
    status: Literal["ARCHITECTURE_SELECTED"] = "ARCHITECTURE_SELECTED"
    selection_source: SelectionSource
    recommendation_ref: str
    decisions: list[ArchitectureDecision]
    selected_decision_ids: list[str]
    recommended_decision_ids: list[str]
    alternative_decision_ids: list[str]
    clarification_decision_ids: list[str]
    existing_api_contracts: list[dict]
    target_integration_topology: list[str]
    downstream_source_of_truth: bool = True


class ArchitectureValidation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: Literal["ARCHITECTURE_READY", "ARCHITECTURE_READY_WITH_LIMITATIONS", "ARCHITECTURE_BLOCKED"]
    checks: dict[str, bool]
    warnings: list[str]
    blockers: list[str]


class ArchitectureLock(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: Literal["LOCKED", "NOT_LOCKED"]
    selection_source: SelectionSource
    selection_hash: str | None = None
    locked_after_validation: bool
