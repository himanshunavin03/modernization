"""Structured contracts for evidence-backed Acceptance Criteria."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from polaris_modernization.application_understanding.models import ConfidenceAssessment, EvidenceReference
from polaris_modernization.business_features.models import ApiRelationshipPath, TraceableStatement


CriterionType = Literal["CORE_BEHAVIOR", "BUSINESS_RULE", "DATA_PRESENTATION", "DATA_INTERACTION", "NAVIGATION", "API_CONTRACT", "TENANT_CONTEXT", "ERROR_OR_EDGE_BEHAVIOR", "MODERNIZATION_PRESERVATION"]
EvidenceStatus = Literal["PROVEN", "SUPPORTED_WITH_LIMITATION", "REQUIRES_STAKEHOLDER_CLARIFICATION"]
ApiStatus = Literal["PROVEN", "UNRESOLVED", "DYNAMIC", "EXTERNAL", "NO_BACKEND_ROUTE"]


class AcceptanceEvidencePackage(BaseModel):
    package_id: str
    package_hash: str
    kg_run_id: str
    application_understanding_run_id: str
    feature_run_id: str
    business_feature_run_id: str
    story_run_id: str
    story: dict


class AcceptanceCriterion(BaseModel):
    model_config = ConfigDict(extra="forbid")
    acceptance_criterion_id: str
    story_id: str
    parent_feature_id: str
    title: str
    criterion_type: CriterionType
    given: str
    when: str
    then: str
    business_condition: str
    observable_outcome: str
    workflow_refs: list[str]
    ui_surface_refs: list[str]
    domain_concept_refs: list[str]
    business_rule_refs: list[str]
    dependency_refs: list[str]
    api_contract_refs: list[ApiRelationshipPath]
    api_mapping_status: list[ApiStatus]
    source_evidence: list[EvidenceReference]
    kg_evidence: list[str]
    application_understanding_evidence: list[str]
    feature_evidence: list[str]
    business_feature_evidence: list[str]
    story_evidence: list[str]
    acceptance_evidence_package_id: str
    confidence: ConfidenceAssessment
    provenance: Literal["AGENT_REASONING"]
    evidence_status: EvidenceStatus
    assumptions: list[TraceableStatement] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    modernization_preservation_required: bool
    stakeholder_validation_required: bool


class AcceptanceReasoningSubmission(BaseModel):
    model_config = ConfigDict(extra="forbid")
    kg_run_id: str
    application_understanding_run_id: str
    feature_run_id: str
    business_feature_run_id: str
    story_run_id: str
    evidence_package_manifest_hash: str
    acceptance_criteria: list[AcceptanceCriterion]


class AcceptanceCatalog(BaseModel):
    project_id: str
    kg_run_id: str
    application_understanding_run_id: str
    feature_run_id: str
    business_feature_run_id: str
    story_run_id: str
    acceptance_criteria_run_id: str
    readiness: Literal["ACCEPTANCE_CRITERIA_READY", "ACCEPTANCE_CRITERIA_READY_WITH_LIMITATIONS", "ACCEPTANCE_CRITERIA_NOT_READY"]
    acceptance_criteria: list[AcceptanceCriterion]
    coverage: dict
    quality_review: dict
    limitations: list[str]
    next_action: str
