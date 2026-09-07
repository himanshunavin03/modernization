"""Reusable command interface over Polaris operations."""

from .artifacts import (
    ArchitectureResolution,
    ArchitectureSelectionResolver,
    TechnicalTaskResolution,
    TechnicalTaskResolver,
)
from .registry import CommandRegistry, default_registry


def __getattr__(name: str):
    """Load the orchestration service lazily to avoid package import cycles."""
    if name == "CommandService":
        from .service import CommandService
        return CommandService
    raise AttributeError(name)

__all__ = [
    "ArchitectureResolution",
    "ArchitectureSelectionResolver",
    "TechnicalTaskResolution",
    "TechnicalTaskResolver",
    "CommandRegistry",
    "CommandService",
    "default_registry",
]
