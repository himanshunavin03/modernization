"""Scope configuration reader. It parses only this controlled POC YAML shape."""

from __future__ import annotations

from pathlib import Path


def default_config_path() -> Path:
    return Path(__file__).resolve().parents[2] / "config" / "poc-scope.yaml"


def load_scope(scope: str, config_path: Path | None = None) -> list[str]:
    """Return configured paths without interpreting reference source text."""
    config_path = config_path or default_config_path()
    active_scope = False
    paths: list[str] = []

    for raw_line in config_path.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        if stripped == f"{scope}:":
            active_scope = True
            continue
        if active_scope and stripped.endswith(":") and stripped != "paths:":
            break
        if active_scope and stripped.startswith("- "):
            paths.append(stripped[2:].strip())

    if not paths:
        raise ValueError(f"Scope '{scope}' was not found in {config_path}")
    return paths
