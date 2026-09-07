"""Typed technical task delivery contracts."""
from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TechnicalTaskCategory(StrEnum):
    SCAFFOLD = "SCAFFOLD"
    ROUTING = "ROUTING"
    UI = "UI"
    STATE = "STATE"
    API = "API"
    INTEGRATION = "INTEGRATION"
    BFF = "BFF"
    GATEWAY = "GATEWAY"
    SECURITY_CONTEXT = "SECURITY_CONTEXT"
    SHARED_COMPONENT = "SHARED_COMPONENT"
    DESIGN_SYSTEM = "DESIGN_SYSTEM"
    ACCESSIBILITY = "ACCESSIBILITY"
    OBSERVABILITY = "OBSERVABILITY"
    TEST = "TEST"
    CONFIGURATION = "CONFIGURATION"


class TechnicalTaskModel(BaseModel):
    model_config = ConfigDict(extra="forbid")
    task_id: str
    feature_id: str
    title: str
    objective: str
    category: TechnicalTaskCategory
    description: str
    implementation_requirements: list[str]
    architecture_decision_refs: list[str]
    adr_refs: list[str]
    functional_requirement_refs: list[str] = Field(default_factory=list)
    story_refs: list[str] = Field(default_factory=list)
    acceptance_criteria_refs: list[str] = Field(default_factory=list)
    api_refs: list[str] = Field(default_factory=list)
    design_refs: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    validation_requirements: list[str]
    deliverables: list[str]
    status: Literal["PLANNED"] = "PLANNED"
    implementation_status: Literal["IMPLEMENTED", "PARTIALLY_IMPLEMENTED", "NOT_IMPLEMENTED", "BLOCKED"] = "NOT_IMPLEMENTED"
    implementation_evidence: list[str] = Field(default_factory=list)
    implementation_assessment: str = "Implementation has not been assessed."
    implementation_order: int
    blocking: bool = False
    open_questions: list[str] = Field(default_factory=list)
    traceability: list[str]


class TechnicalTaskPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    project_id: str
    feature_id: str
    feature_name: str | None = None
    modernization_operation: dict | None = None
    status: Literal["TECHNICAL_TASKS_READY"] = "TECHNICAL_TASKS_READY"
    architecture_selection_ref: str
    architecture_selection_hash: str
    architecture_lock_status: Literal["LOCKED"]
    design: dict
    requirements: list[dict]
    stories: list[dict]
    acceptance_criteria: list[dict]
    existing_api_contracts: list[dict]
    tasks: list[TechnicalTaskModel]
    validation: dict
    traceability: dict
    workflow: dict
    lineage: dict = Field(default_factory=dict)
