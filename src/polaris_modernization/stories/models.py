"""Structured contracts for evidence-backed Jira-style Stories."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from polaris_modernization.application_understanding.models import ConfidenceAssessment, EvidenceReference
from polaris_modernization.business_features.models import ApiRelationshipPath, TraceableStatement


ApiStatus = Literal["PROVEN", "UNRESOLVED", "DYNAMIC", "EXTERNAL", "NO_BACKEND_ROUTE"]


class StoryEvidencePackage(BaseModel):
    package_id: str
    package_hash: str
    kg_run_id: str
    application_understanding_run_id: str
    feature_run_id: str
    business_feature_run_id: str
    parent_feature_id: str
    parent_feature_name: str
    boundary: str
    boundary_rationale: str
    business_capabilities: list[str]
    workflows: list[dict]
    ui_surfaces: list[str]
    domain_concepts: list[str]
    business_rules: list[str]
    dependencies: list[str]
    api_relationships: list[ApiRelationshipPath]
    open_questions: list[dict]
    business_value: list[dict]
    source_evidence: list[EvidenceReference]
    kg_evidence: list[str]
    business_feature_evidence: str


class InvestAssessment(BaseModel):
    independent_enough: bool
    negotiable: bool
    valuable: bool
    estimable_conceptually: bool
    small_and_coherent: bool
    testable_in_principle: bool
    issues: list[str] = Field(default_factory=list)


class StoryCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    story_id: str
    story_key_candidate: str
    title: str
    parent_feature_id: str
    parent_feature_name: str
    business_capability: str
    story_statement: str
    actor: str
    actor_confidence: ConfidenceAssessment
    business_goal: str
    business_value: str
    business_value_status: Literal["PROVEN", "INFERRED_BUSINESS_VALUE"]
    description: str
    workflow_refs: list[str]
    workflow_boundary: str
    workflow_boundary_rationale: str
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
    story_evidence_package_id: str
    confidence: ConfidenceAssessment
    provenance: Literal["AGENT_REASONING"]
    current_state_behavior: TraceableStatement
    modernization_relevance: TraceableStatement
    in_scope: list[str]
    out_of_scope: list[str]
    assumptions: list[TraceableStatement] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    story_priority: Literal["HIGH", "MEDIUM", "LOW"]
    priority_rationale: str
    poc_relevance: str
    invest_assessment: InvestAssessment
    story_points: Literal["UNESTIMATED"] = "UNESTIMATED"


class StoryReasoningSubmission(BaseModel):
    model_config = ConfigDict(extra="forbid")
    kg_run_id: str
    application_understanding_run_id: str
    feature_run_id: str
    business_feature_run_id: str
    evidence_package_manifest_hash: str
    stories: list[StoryCandidate]
    poc_story_ids: list[str]


class StoryCatalog(BaseModel):
    project_id: str
    kg_run_id: str
    application_understanding_run_id: str
    feature_run_id: str
    business_feature_run_id: str
    story_run_id: str
    readiness: Literal["STORIES_READY", "STORIES_READY_WITH_LIMITATIONS", "STORIES_NOT_READY"]
    stories: list[StoryCandidate]
    poc_story_ids: list[str]
    coverage: dict
    quality_review: dict
    limitations: list[str]
    next_action: str
