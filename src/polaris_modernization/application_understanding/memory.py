"""Future project-memory boundary; it never writes source KG facts."""
from __future__ import annotations
from typing import Protocol


class ProjectMemoryStore(Protocol):
    def record_workflow_state(self, project_id: str, state: dict) -> None: ...


class NullProjectMemoryStore:
    def record_workflow_state(self, project_id: str, state: dict) -> None:
        return None
