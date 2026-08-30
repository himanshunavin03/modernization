"""Evidence-first data models shared by extractors and graph normalization."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class Evidence:
    project_id: str
    source_path: str
    line_start: int
    line_end: int
    extraction_method: str
    confidence: float
    source_hash: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class Fact:
    kind: str
    name: str
    evidence: Evidence
    properties: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "kind": self.kind,
            "name": self.name,
            "properties": self.properties,
            "evidence": self.evidence.to_dict(),
        }
