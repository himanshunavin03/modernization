"""Generic, recursive project-file discovery for read-only source roots."""
from pathlib import Path

def discover_files(source_root: Path, excluded_directories: set[str]) -> list[Path]:
    if not source_root.is_dir():
        raise ValueError(f"Source root does not exist: {source_root}")
    return sorted(
        (path for path in source_root.rglob("*") if path.is_file() and not any(part in excluded_directories for part in path.relative_to(source_root).parts)),
        key=lambda path: path.as_posix(),
    )
