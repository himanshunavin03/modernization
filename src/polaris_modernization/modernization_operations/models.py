"""Contracts shared by modernization-operation registries and adapters."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Protocol


@dataclass(frozen=True)
class ModernizationFeatureContext:
    repository_root: str
    project_id: str
    feature: dict[str, Any]
    feature_specification: dict[str, Any]
    technical_task_plan: dict[str, Any]
    architecture_selection: dict[str, Any]
    architecture_source: str
    api_contracts: list[dict[str, Any]]
    ui_evidence: dict[str, Any]
    design_source: str
    design_input: dict[str, Any]
    modernization_state: dict[str, Any]


@dataclass(frozen=True)
class OperationReadiness:
    status: str
    operation_id: str
    target: str
    blockers: tuple[str, ...] = ()


OperationExecutor = Callable[[ModernizationFeatureContext], dict[str, Any]]


class ModernizationOperation(Protocol):
    operation_id: str
    target: str

    def validate(self, context: ModernizationFeatureContext) -> OperationReadiness: ...

    def execute(self, context: ModernizationFeatureContext) -> dict[str, Any]: ...
