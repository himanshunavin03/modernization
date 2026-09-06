"""Reusable modernization operation contracts and registry."""

from .angular import AngularFeatureModernizationOperation
from .context import ModernizationContextBuilder
from .ids import ANGULAR_FEATURE_OPERATION_ID
from .models import ModernizationFeatureContext, ModernizationOperation, OperationReadiness
from .registry import ModernizationOperationRegistry, default_operation_registry

__all__ = [
    "ANGULAR_FEATURE_OPERATION_ID",
    "AngularFeatureModernizationOperation",
    "ModernizationContextBuilder",
    "ModernizationFeatureContext",
    "ModernizationOperation",
    "ModernizationOperationRegistry",
    "OperationReadiness",
    "default_operation_registry",
]
