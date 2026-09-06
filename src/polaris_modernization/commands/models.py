"""Command metadata and errors shared by every adapter."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class CommandDefinition:
    name: str
    category: str
    purpose: str
    operation: str
    argument: str | None = None
    argument_required: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CommandResult:
    command: str
    status: str
    data: dict[str, Any] = field(default_factory=dict)
    message: str = ""
    next_commands: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class CommandError(ValueError):
    """A command cannot be parsed or safely executed."""


class FeatureNotFoundError(CommandError):
    pass


class AmbiguousFeatureError(CommandError):
    def __init__(self, query: str, candidates: list[dict[str, Any]]) -> None:
        self.query = query
        self.candidates = candidates
        names = ", ".join(item["feature_id"] for item in candidates)
        super().__init__(f"Feature '{query}' is ambiguous: {names}. Run /list-features.")


class PrerequisiteError(CommandError):
    def __init__(self, message: str, next_commands: list[str]) -> None:
        self.next_commands = next_commands
        super().__init__(message)
