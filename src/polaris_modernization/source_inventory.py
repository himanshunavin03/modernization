"""Inventory only configured source paths and calculate immutable evidence hashes."""

from __future__ import annotations

import hashlib
from pathlib import Path


def source_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_inventory(source_root: Path, profile: dict) -> tuple[list[dict], list[str]]:
    source_root = source_root.resolve()
    if not source_root.is_dir():
        raise ValueError(f"Source root does not exist: {source_root}")

    from polaris_modernization.project_discovery import discover_files
    extensions = profile.get("supported_extensions", {})
    includes = [item.rstrip("/") for item in profile.get("include_paths", [])]
    warnings = []
    for include in includes:
        if not (source_root / include).exists(): warnings.append(f"Configured path not found: {include}")
    files = []
    for file_path in discover_files(source_root, set(profile.get("excluded_directories", []))):
        relative_path = file_path.relative_to(source_root).as_posix()
        selected = not includes or any(relative_path == item or relative_path.startswith(f"{item}/") for item in includes)
        files.append({"source_path": relative_path, "source_hash": source_hash(file_path), "language": extensions.get(file_path.suffix.lower()), "supported": file_path.suffix.lower() in extensions, "selected_for_extraction": selected})
    if not any(item["supported"] for item in files): raise ValueError("No supported source files found")
    return files, warnings
