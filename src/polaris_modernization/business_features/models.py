"""Structured contracts for evidence-backed Business Feature specifications."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from polaris_modernization.application_understanding.models import ConfidenceAssessment, EvidenceReference
from polaris_modernization.feature_generation.models import ApiContractReference


ClaimClassification = Literal[
    "PROVEN", "INFERRED_BUSINESS_VALUE", "MODERNIZATION_CONCERN", "ASSUMPTION",
    "BUSINESS_ANALYSIS_LIMITATION", "TECHNICAL_MODERNIZATION_RISK", "MODERNIZATION_SUCCESS_INDICATOR",
]


class TraceableStatement(BaseModel):
    text: str
    classification: ClaimClassification
    evidence: list[EvidenceReference] = Field(default_factory=list)
    confidence: ConfidenceAssessment


class ActorSpecification(BaseModel):
    name: str
    role: str
    supporting_workflows: list[str]
    evidence: list[EvidenceReference]
    confidence: ConfidenceAssessment


class CapabilitySpecification(BaseModel):
    name: str
    contribution: str
    workflows: list[str]
    evidence: list[EvidenceReference]


class WorkflowSpecification(BaseModel):
    name: str
    business_trigger: str
    actor: str | None = None
    business_steps: list[str]
    expected_outcome: str
    supporting_ui: list[str]
    api_status: Literal["PROVEN", "UNRESOLVED", "DYNAMIC", "EXTERNAL", "NO_BACKEND_ROUTE", "NOT_APPLICABLE"]
    evidence: list[EvidenceReference]
    confidence: ConfidenceAssessment


class BusinessRuleSpecification(BaseModel):
    rule_id: str
    source_rule: str
    description: str
    triggering_condition: str
    expected_behavior: str
    related_workflow: str | None = None
    evidence: list[EvidenceReference]
    confidence: ConfidenceAssessment


class DomainConceptSpecification(BaseModel):
    name: str
    business_meaning: str
    role_in_feature: str
    evidence: list[EvidenceReference]


class DependencySpecification(BaseModel):
    name: str
    dependency_type: Literal["BUSINESS_FUNCTIONAL", "TECHNICAL"]
    description: str
    evidence: list[EvidenceReference]


class OpenQuestion(BaseModel):
    question_id: str
    question: str
    reason: str
    evidence: list[EvidenceReference]
    confidence: ConfidenceAssessment


class StoryBoundary(BaseModel):
    boundary: str
    workflows: list[str]
    rationale: str


class ApiIntegrationProfile(BaseModel):
    proven: int
    unresolved: int
    dynamic: int
    external: int
    no_backend_route: int
    relationships: list[ApiContractReference]
    business_readable_limitation: str
    paths: list["ApiRelationshipPath"] = Field(default_factory=list)


class ApiRelationshipPath(BaseModel):
    workflow: str
    status: Literal["PROVEN", "UNRESOLVED", "DYNAMIC", "EXTERNAL", "NO_BACKEND_ROUTE"]
    frontend_source: str
    api_contract: str
    backend_endpoint: str


class BusinessFeatureEvidencePackage(BaseModel):
    package_id: str
    package_hash: str
    kg_run_id: str
    application_understanding_run_id: str
    feature_run_id: str
    feature: dict
    upstream_feature_evidence_packages: dict[str, str]
    evidence: list[EvidenceReference]


class BusinessFeatureSpecification(BaseModel):
    model_config = ConfigDict(extra="forbid")
    feature_id: str
    feature_name: str
    short_business_summary: str
    business_capabilities: list[str]
    functional_module: str
    feature_status: Literal["APPROVED_ENRICHED"]
    confidence: ConfidenceAssessment
    executive_description: list[str] = Field(min_length=2, max_length=4)
    current_objective: TraceableStatement
    modernization_objective: TraceableStatement
    business_value: list[TraceableStatement]
    actors: list[ActorSpecification] = Field(default_factory=list)
    actor_evidence_limitation: str
    capability_details: list[CapabilitySpecification]
    current_business_functionality: list[TraceableStatement]
    workflows: list[WorkflowSpecification]
    business_rules: list[BusinessRuleSpecification] = Field(default_factory=list)
    no_business_rules_marker: Literal["NO_EVIDENCE_BACKED_BUSINESS_RULES_IDENTIFIED"] | None = None
    domain_concepts: list[DomainConceptSpecification] = Field(default_factory=list)
    information_involved: list[TraceableStatement]
    dependencies: list[DependencySpecification] = Field(default_factory=list)
    api_integration: ApiIntegrationProfile
    current_user_experience: list[TraceableStatement]
    evidence_backed_limitations: list[TraceableStatement]
    modernization_concerns: list[TraceableStatement]
    in_scope: list[TraceableStatement]
    out_of_scope: list[TraceableStatement]
    assumptions: list[TraceableStatement] = Field(default_factory=list)
    open_questions: list[OpenQuestion]
    risks_and_limitations: list[TraceableStatement]
    success_indicators: list[TraceableStatement]
    story_decomposition_guidance: list[StoryBoundary]
    source_evidence: list[EvidenceReference]
    kg_evidence: list[str]
    evidence_package_id: str


class BusinessFeatureReasoningSubmission(BaseModel):
    model_config = ConfigDict(extra="forbid")
    kg_run_id: str
    application_understanding_run_id: str
    feature_run_id: str
    evidence_package_manifest_hash: str
    business_features: list[BusinessFeatureSpecification]


class BusinessFeatureCatalog(BaseModel):
    project_id: str
    kg_run_id: str
    application_understanding_run_id: str
    feature_run_id: str
    business_feature_run_id: str
    readiness: Literal["BUSINESS_FEATURES_READY", "BUSINESS_FEATURES_READY_WITH_LIMITATIONS", "BUSINESS_FEATURES_NOT_READY"]
    business_features: list[BusinessFeatureSpecification]
    limitations: list[str]
    quality_review: dict
    next_action: str
    capability_coverage: dict = Field(default_factory=dict)
