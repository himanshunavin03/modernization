"""Inventory only configured source paths and calculate immutable evidence hashes."""

from __future__ import annotations

import hashlib
from pathlib import Path


def source_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_inventory(source_root: Path, configured_paths: list[str]) -> list[dict[str, str]]:
    source_root = source_root.resolve()
    if not source_root.is_dir():
        raise ValueError(f"Source root does not exist: {source_root}")

    files: dict[str, dict[str, str]] = {}
    for configured_path in configured_paths:
        candidate = (source_root / configured_path).resolve()
        if source_root not in candidate.parents and candidate != source_root:
            raise ValueError(f"Configured path escapes source root: {configured_path}")
        if not candidate.exists():
            continue
        candidates = candidate.rglob("*") if candidate.is_dir() else [candidate]
        for file_path in candidates:
            if file_path.is_file():
                relative_path = file_path.relative_to(source_root).as_posix()
                files[relative_path] = {
                    "source_path": relative_path,
                    "source_hash": source_hash(file_path),
                }
    return [files[path] for path in sorted(files)]
