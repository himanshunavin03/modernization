"""Write deterministic artifacts only to the caller-selected output directory."""

from __future__ import annotations

import json
from pathlib import Path

from polaris_modernization.models import Fact


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_summary(path: Path, inventory: list[dict[str, str]], facts: list[Fact], graph: dict, extraction_warnings: list[dict] | None = None) -> None:
    extraction_warnings = extraction_warnings or []
    lines = [
        "# Dashboard Deterministic Extraction Summary",
        "",
        f"- Inventory files: {len(inventory)}",
        f"- Deterministic facts: {len(facts)}",
        f"- Graph nodes: {len(graph['nodes'])}",
        f"- Graph edges: {len(graph['edges'])}",
        f"- Extraction warnings: {len(extraction_warnings)}",
        f"- Total graph warnings: {len(graph['warnings'])}",
        "- Parser: Tree-sitter JavaScript, HTML, and C# only.",
        "",
        "## Needs Review",
        "",
        "- Razor directives are not modeled beyond file classification because this POC uses the Tree-sitter HTML grammar, not a Razor grammar.",
        "- Dynamic JavaScript URL expressions are emitted as source expressions, not resolved API endpoints.",
        "- Only the configured dashboard source scope was inspected; no behavior outside it is represented.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
