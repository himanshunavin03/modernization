"""Phase-2 contracts: agent interpretations stay separate from deterministic KG facts."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


EvidenceProvenance = Literal["COMPILER_PROVEN", "PROJECT_PARTIAL", "SYNTHETIC_FALLBACK", "STRUCTURAL_ONLY"]
InterpretationOrigin = Literal["DETERMINISTIC_FACT", "AGENT_REASONING"]


class EvidenceReference(BaseModel):
    node_id: str
    source_path: str
    line_start: int = 0
    line_end: int = 0
    provenance: EvidenceProvenance


class ConfidenceAssessment(BaseModel):
    level: Literal["HIGH", "MEDIUM", "LOW"]
    provenance: list[EvidenceProvenance]
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


class EvidenceBackedItem(BaseModel):
    name: str
    evidence: list[EvidenceReference]
    confidence: ConfidenceAssessment
    origin: InterpretationOrigin = "DETERMINISTIC_FACT"


class BusinessModule(EvidenceBackedItem):
    pass


class BusinessCapability(EvidenceBackedItem):
    pass


class BusinessRule(EvidenceBackedItem):
    pass


class DomainConcept(EvidenceBackedItem):
    pass


class Dependency(EvidenceBackedItem):
    pass


class UserWorkflow(EvidenceBackedItem):
    ui_surface: str
    backend_mapping: Literal["UNRESOLVED", "NOT_APPLICABLE"]


class UISurface(EvidenceBackedItem):
    kind: str


class AgentReasoningSubmission(BaseModel):
    """Provider-neutral payload authored by the active Codex or Copilot chat agent."""
    model_config = ConfigDict(extra="forbid")
    application_purpose: BusinessCapability
    business_modules: list[BusinessModule] = Field(default_factory=list)
    business_capabilities: list[BusinessCapability] = Field(default_factory=list)
    user_workflows: list[UserWorkflow] = Field(default_factory=list)
    business_rules: list[BusinessRule] = Field(default_factory=list)
    domain_concepts: list[DomainConcept] = Field(default_factory=list)
    ui_surfaces: list[UISurface] = Field(default_factory=list)
    dependencies: list[Dependency] = Field(default_factory=list)
    best_razor_demo_candidate: str | None = None
    razor_demo_capability: BusinessCapability | None = None
    razor_demo_workflow: UserWorkflow | None = None
    best_angular_demo_candidate: str | None = None
    angular_demo_capability: BusinessCapability | None = None
    angular_demo_workflow: UserWorkflow | None = None


class ApplicationUnderstanding(BaseModel):
    project_id: str
    status: Literal["COMPLETE"]
    application_purpose: str
    kg_metrics: dict[str, int]
    limitations: list[str]
    business_modules: list[BusinessModule]
    business_capabilities: list[BusinessCapability]
    user_workflows: list[UserWorkflow]
    business_rules: list[BusinessRule]
    ui_surfaces: list[UISurface]
    domain_concepts: list[DomainConcept]
    dependencies: list[Dependency]
    best_razor_demo_candidate: str | None
    razor_demo_capability: BusinessCapability | None = None
    razor_demo_workflow: UserWorkflow | None = None
    best_angular_demo_candidate: str | None
    angular_demo_capability: BusinessCapability | None = None
    angular_demo_workflow: UserWorkflow | None = None
    agent_reasoning: AgentReasoningSubmission
