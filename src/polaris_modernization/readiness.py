"""Separate deterministic pipeline execution from Knowledge Graph readiness."""
from __future__ import annotations


def readiness(pipeline_status: str, *, analyzer_defects: int = 0, unknowns: int = 0, integrity_valid: bool = True, explained_limitations: int = 0) -> str:
    if pipeline_status != "SUCCESS" or not integrity_valid or analyzer_defects or unknowns:
        return "NOT_READY"
    return "READY_WITH_EXPLAINED_LIMITATIONS" if explained_limitations else "READY"
