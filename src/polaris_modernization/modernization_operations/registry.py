"""Target-stack operation registry with no application-specific dispatch."""
from __future__ import annotations

from collections.abc import Iterable

from polaris_modernization.commands.models import CommandError

from .angular import AngularFeatureModernizationOperation
from .angular_executor import execute_angular_feature
from .models import ModernizationOperation


class ModernizationOperationRegistry:
    def __init__(self, operations: Iterable[ModernizationOperation] = ()) -> None:
        self._operations = {operation.operation_id: operation for operation in operations}

    def register(self, operation: ModernizationOperation) -> None:
        self._operations[operation.operation_id] = operation

    def get(self, operation_id: str) -> ModernizationOperation:
        try:
            return self._operations[operation_id]
        except KeyError as exc:
            raise CommandError(f"Unknown modernization operation '{operation_id}'.") from exc

    def contains(self, operation_id: str) -> bool:
        return operation_id in self._operations


def default_operation_registry() -> ModernizationOperationRegistry:
    return ModernizationOperationRegistry([AngularFeatureModernizationOperation(execute_angular_feature)])
