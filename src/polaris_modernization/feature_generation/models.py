"""Contracts for provider-free, evidence-backed Feature generation."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from polaris_modernization.application_understanding.models import ConfidenceAssessment, EvidenceReference


ApiMappingStatus = Literal["PROVEN", "UNRESOLVED", "DYNAMIC", "EXTERNAL", "NO_BACKEND_ROUTE", "NOT_APPLICABLE"]


class ApplicationUnderstandingReference(BaseModel):
    object_type: Literal["module", "capability", "workflow", "ui_surface", "domain_concept", "business_rule", "dependency"]
    name: str


class ApiContractReference(BaseModel):
    workflow: str
    status: ApiMappingStatus


class FeatureEvidencePackage(BaseModel):
    package_id: str
    package_hash: str
    kg_run_id: str
    application_understanding_run_id: str
    module: str
    objects: dict[str, list[dict]]
    evidence: list[EvidenceReference]
    confidence: ConfidenceAssessment


class FeatureCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    feature_id: str
    title: str
    business_outcome: str
    description: str
    module: str
    business_capabilities: list[str]
    actors_personas: list[str] = Field(default_factory=list)
    workflows: list[str]
    ui_surfaces: list[str] = Field(default_factory=list)
    domain_concepts: list[str] = Field(default_factory=list)
    business_rules: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    api_contracts: list[ApiContractReference] = Field(default_factory=list)
    source_evidence: list[EvidenceReference]
    kg_evidence: list[str]
    application_understanding_evidence: list[ApplicationUnderstandingReference]
    evidence_package_ids: list[str]
    confidence: ConfidenceAssessment
    provenance: Literal["AGENT_REASONING"] = "AGENT_REASONING"
    modernization_scope: list[Literal["UI_MODERNIZATION", "FRONTEND_WORKFLOW_MODERNIZATION", "SHARED_REUSABLE_UI", "API_INTEGRATION_PRESERVATION", "EXTERNAL_INTEGRATION", "CROSS_CUTTING_FUNCTIONALITY"]]
    modernization_priority: Literal["HIGH", "MEDIUM", "LOW"]
    modernization_rationale: str
    limitations: list[str] = Field(default_factory=list)


class PocFeatureSelection(BaseModel):
    feature_ids: list[str]
    razor_feature_id: str
    razor_surface: str
    angularjs_feature_id: str
    angularjs_surface: str
    rationale: str


class FeatureReasoningSubmission(BaseModel):
    model_config = ConfigDict(extra="forbid")
    kg_run_id: str
    application_understanding_run_id: str
    evidence_package_manifest_hash: str
    features: list[FeatureCandidate]
    poc_selection: PocFeatureSelection


class FeatureCatalog(BaseModel):
    project_id: str
    kg_run_id: str
    application_understanding_run_id: str
    feature_run_id: str
    readiness: Literal["FEATURES_READY", "FEATURES_READY_WITH_LIMITATIONS", "FEATURES_NOT_READY"]
    features: list[FeatureCandidate]
    poc_selection: PocFeatureSelection
    quality_review: dict
    limitations: list[str]
    next_action: str
