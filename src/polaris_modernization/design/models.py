"""Normalized design contracts; no provider response is exposed downstream."""
from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class DesignMode(StrEnum):
    NONE = "NONE"
    FIXTURE = "FIXTURE"
    LIVE = "LIVE"


class DesignStatus(StrEnum):
    NOT_PROVIDED = "NOT_PROVIDED"
    AVAILABLE = "AVAILABLE"
    PARTIAL = "PARTIAL"
    UNAVAILABLE = "UNAVAILABLE"
    UNAUTHORIZED = "UNAUTHORIZED"
    INVALID = "INVALID"


class DesignErrorCode(StrEnum):
    AUTH_NOT_CONFIGURED = "FIGMA_AUTH_NOT_CONFIGURED"
    ACCESS_DENIED = "FIGMA_ACCESS_DENIED"
    DOCUMENT_UNAVAILABLE = "FIGMA_DOCUMENT_UNAVAILABLE"
    INVALID_URL = "FIGMA_INVALID_URL"
    NETWORK_ERROR = "FIGMA_NETWORK_ERROR"
    RESPONSE_INVALID = "FIGMA_RESPONSE_INVALID"


class DesignRequirementLink(BaseModel):
    model_config = ConfigDict(extra="forbid")
    design_ref: str
    requirement_ref: str
    relationship: Literal["SUPPORTS", "CONFLICTS"]
    description: str


class DesignRequirementConflict(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: Literal["DESIGN_REQUIREMENT_CONFLICT"] = "DESIGN_REQUIREMENT_CONFLICT"
    design_reference: str
    requirement_reference: str
    conflict_description: str
    required_clarification: str


class DesignSpecification(BaseModel):
    model_config = ConfigDict(extra="forbid")
    provider: Literal["NO_DESIGN", "FIGMA"]
    mode: DesignMode
    status: DesignStatus
    source_reference: str | None = None
    document_name: str | None = None
    error_code: DesignErrorCode | None = None
    pages: list[dict] = Field(default_factory=list)
    screens: list[dict] = Field(default_factory=list)
    components: list[dict] = Field(default_factory=list)
    component_instances: list[dict] = Field(default_factory=list)
    layouts: list[dict] = Field(default_factory=list)
    controls: list[dict] = Field(default_factory=list)
    typography: list[dict] = Field(default_factory=list)
    colors: list[dict] = Field(default_factory=list)
    design_tokens: list[dict] = Field(default_factory=list)
    spacing: list[dict] = Field(default_factory=list)
    assets: list[dict] = Field(default_factory=list)
    responsive_hints: list[dict] = Field(default_factory=list)
    interactions: list[dict] = Field(default_factory=list)
    navigation_hints: list[dict] = Field(default_factory=list)
    unresolved_items: list[str] = Field(default_factory=list)
    requirement_links: list[DesignRequirementLink] = Field(default_factory=list)
    conflicts: list[DesignRequirementConflict] = Field(default_factory=list)
    traceability: list[str] = Field(default_factory=list)


class FigmaReference(BaseModel):
    model_config = ConfigDict(extra="forbid")
    provider: Literal["FIGMA"] = "FIGMA"
    file_key: str
    node_id: str | None = None
    normalized_reference: str
