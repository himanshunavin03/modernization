"""Structured Phase 2 contracts; AI claims remain separate from KG facts."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class EvidenceReference(BaseModel):
    node_id: str
    source_path: str
    line_start: int = 0
    line_end: int = 0
    provenance: Literal["COMPILER_PROVEN", "PROJECT_PARTIAL", "SYNTHETIC_FALLBACK", "STRUCTURAL_ONLY"]


class ConfidenceAssessment(BaseModel):
    level: Literal["HIGH", "MEDIUM", "LOW"]
    provenance: list[str]
    rationale: str


class EvidencePackage(BaseModel):
    package_id: str
    package_hash: str
    cluster_type: Literal["RAZOR", "ANGULAR", "ROUTE"]
    title: str
    node_ids: list[str]
    relationships: list[dict]
    evidence: list[EvidenceReference]
    unresolved_relationships: list[str] = Field(default_factory=list)
    confidence: ConfidenceAssessment


class BusinessModule(BaseModel):
    name: str
    evidence: list[EvidenceReference]
    confidence: ConfidenceAssessment
    origin: Literal["DETERMINISTIC_FACT", "AI_INTERPRETATION"] = "DETERMINISTIC_FACT"


class BusinessCapability(BaseModel):
    name: str
    evidence: list[EvidenceReference]
    confidence: ConfidenceAssessment
    origin: Literal["DETERMINISTIC_FACT", "AI_INTERPRETATION"]


class UserWorkflow(BaseModel):
    name: str
    ui_surface: str
    backend_mapping: Literal["UNRESOLVED", "NOT_APPLICABLE"]
    evidence: list[EvidenceReference]
    confidence: ConfidenceAssessment
    origin: Literal["DETERMINISTIC_FACT", "AI_INTERPRETATION"] = "DETERMINISTIC_FACT"


class BusinessRule(BaseModel):
    name: str
    evidence: list[EvidenceReference]
    confidence: ConfidenceAssessment
    origin: Literal["AI_INTERPRETATION"]


class UISurface(BaseModel):
    name: str
    kind: str
    evidence: list[EvidenceReference]
    confidence: ConfidenceAssessment


class ApplicationUnderstanding(BaseModel):
    project_id: str
    status: Literal["COMPLETE", "FRAMEWORK_ONLY"]
    application_purpose: str
    kg_metrics: dict[str, int]
    limitations: list[str]
    business_modules: list[BusinessModule]
    business_capabilities: list[BusinessCapability]
    user_workflows: list[UserWorkflow]
    business_rules: list[BusinessRule]
    ui_surfaces: list[UISurface]
    domain_concepts: list[BusinessModule]
    dependencies: list[str]
    best_razor_demo_candidate: str | None
    best_angular_demo_candidate: str | None
    ai_interpretations: list[BusinessCapability] = Field(default_factory=list)


class ReasoningResult(BaseModel):
    claims: list[BusinessCapability] = Field(default_factory=list)
    input_tokens: int = 0
    output_tokens: int = 0
