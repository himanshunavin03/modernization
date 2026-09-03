"""Existing-UI-driven Angular modernization generation."""

from .models import ExistingUiSpecification, GenerationManifest
from .workflow import generate_angular_hero

__all__ = ["ExistingUiSpecification", "GenerationManifest", "generate_angular_hero"]
