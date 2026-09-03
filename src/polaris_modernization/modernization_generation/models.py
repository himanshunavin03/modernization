"""Typed contracts for UI reconstruction and generated delivery evidence."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ExistingUiSpecification(BaseModel):
    model_config = ConfigDict(extra="forbid")
    feature_id: str
    source_mode: Literal["EXISTING_APPLICATION_UI"] = "EXISTING_APPLICATION_UI"
    surfaces: list[dict]
    regions: list[dict]
    controls: list[dict]
    visible_text: list[dict]
    navigation: list[dict]
    interactions: list[dict]
    layouts: list[dict]
    styles: list[dict]
    css_classes: list[dict]
    assets: list[dict]
    data_bindings: list[dict]
    api_relationships: list[dict]
    responsive_behavior: list[dict]
    shared_elements: list[dict]
    unresolved_visual_details: list[dict] = Field(default_factory=list)
    source_traceability: list[str]


class TaskExecutionStatus(BaseModel):
    model_config = ConfigDict(extra="forbid")
    task_id: str
    status: Literal["IMPLEMENTED", "PARTIALLY_IMPLEMENTED", "DEFERRED", "NOT_APPLICABLE"]
    detail: str
    generated_file_refs: list[str] = Field(default_factory=list)


class GenerationManifest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    project_id: str
    feature_id: str
    source_ui_mode: Literal["EXISTING_APPLICATION_UI"]
    figma_for_generation: Literal["DISABLED"] = "DISABLED"
    architecture_selection_ref: str
    technical_task_ref: str
    generated_workspace: str
    generated_files: list[str]
    generated_components: list[dict]
    generated_services: list[dict]
    generated_routes: list[dict]
    generated_models: list[dict]
    generated_tests: list[dict]
    preserved_api_contracts: list[dict]
    reused_assets: list[dict]
    task_statuses: list[TaskExecutionStatus]
    unresolved_items: list[dict]
    generation_timestamp: str
    generator: dict
    build_status: Literal["NOT_YET_EXECUTED"] = "NOT_YET_EXECUTED"
    generated_test_status: Literal["NOT_YET_EXECUTED"] = "NOT_YET_EXECUTED"


class PepValidationContract(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: Literal["NOT_STARTED"] = "NOT_STARTED"
    attempt: dict | None = None
    failure: dict | None = None
    context: dict | None = None
    diagnosis: dict | None = None
    repair: dict | None = None
    revalidation: dict | None = None
    next_stage: Literal["BUILD_TEST_PEP_AND_FINAL_TRACEABILITY"] = "BUILD_TEST_PEP_AND_FINAL_TRACEABILITY"


class PepAttempt(BaseModel):
    model_config = ConfigDict(extra="forbid")
    attempt_id: str
    stage: str
    command: str
    status: Literal["PASS", "FAIL"]
    timestamp: str


class PepFailure(BaseModel):
    model_config = ConfigDict(extra="forbid")
    failure_id: str
    attempt_id: str
    category: str
    layer: str
    summary: str
    relevant_error: str
    affected_files: list[str]
    context: dict


class PepDiagnosis(BaseModel):
    model_config = ConfigDict(extra="forbid")
    diagnosis_id: str
    failure_id: str
    root_cause: str
    confidence: Literal["HIGH", "MEDIUM", "LOW"]
    evidence: list[str]
    candidate_repairs: list[dict]
    selected_repair: str
    rationale: str


class PepRepair(BaseModel):
    model_config = ConfigDict(extra="forbid")
    repair_id: str
    diagnosis_id: str
    files_changed: list[str]
    description: str
    scope: str
    architecture_impact: str
    requirement_impact: str


class PepRevalidation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    repair_id: str
    command: str
    result: Literal["PASS", "FAIL"]
    new_failure_id: str | None = None


class PepRun(BaseModel):
    model_config = ConfigDict(extra="forbid")
    project_id: str
    feature_id: str
    status: Literal["IN_PROGRESS", "PASS", "BLOCKED"]
    attempts: list[PepAttempt]
    failures: list[PepFailure]
    diagnoses: list[PepDiagnosis]
    repairs: list[PepRepair]
    revalidations: list[PepRevalidation]
