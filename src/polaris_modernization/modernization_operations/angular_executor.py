"""Deterministic adapter for adding an artifact-defined feature to an Angular workspace."""
from __future__ import annotations

from polaris_modernization.modernization_generation.angular_feature import generate_angular_feature

from .models import ModernizationFeatureContext


def execute_angular_feature(context: ModernizationFeatureContext) -> dict[str, object]:
    return generate_angular_feature(context)
