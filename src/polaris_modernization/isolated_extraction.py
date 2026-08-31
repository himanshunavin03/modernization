"""Process isolation for native Tree-sitter extraction."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

from polaris_modernization.models import Evidence, Fact

WORKER_TIMEOUT_SECONDS = 30
LOCAL_SOURCE_DIRECTORY = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = LOCAL_SOURCE_DIRECTORY.parent


@dataclass(frozen=True)
class ExtractionResult:
    facts: list[Fact]
    warning: dict[str, str] | None = None


def _warning(request: dict[str, str], category: str, diagnostic: str) -> ExtractionResult:
    return ExtractionResult([], {
        "source_path": request["source_path"],
        "language": request.get("language", "unknown"),
        "extractor": request.get("language", "unknown"),
        "failure_category": category,
        "diagnostic": diagnostic,
        "status": "skipped",
    })


def _fact(payload: dict[str, Any]) -> Fact:
    return Fact(
        kind=str(payload["kind"]),
        name=str(payload["name"]),
        properties=dict(payload.get("properties", {})),
        evidence=Evidence(**payload["evidence"]),
    )


def _worker_environment() -> dict[str, str]:
    environment = os.environ.copy()
    existing_pythonpath = environment.get("PYTHONPATH")
    environment["PYTHONPATH"] = str(LOCAL_SOURCE_DIRECTORY) if not existing_pythonpath else f"{LOCAL_SOURCE_DIRECTORY}{os.pathsep}{existing_pythonpath}"
    return environment


def _worker_cwd() -> str | None:
    return str(REPOSITORY_ROOT) if (REPOSITORY_ROOT / "pyproject.toml").is_file() else None


def _is_import_failure(stderr: str) -> bool:
    return "polaris_modernization" in stderr and ("ModuleNotFoundError" in stderr or "No module named" in stderr)


def extract_file(request: dict[str, str], timeout: int = WORKER_TIMEOUT_SECONDS) -> ExtractionResult:
    """Run one extractor in a child process and return only validated fact data."""
    try:
        completed = subprocess.run(
            [sys.executable, "-m", "polaris_modernization.isolated_extraction"],
            input=json.dumps(request),
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
            env=_worker_environment(),
            cwd=_worker_cwd(),
        )
    except subprocess.TimeoutExpired:
        return _warning(request, "timeout", "Extraction worker exceeded the allowed time.")
    except OSError:
        return _warning(request, "worker_start_failed", "Extraction worker could not be started.")

    if completed.returncode != 0:
        if _is_import_failure(completed.stderr):
            return _warning(request, "worker_startup_failed", "Extraction worker could not import the analyzer package.")
        # The native parser died before it could return facts. Preserve the supported
        # source file as opaque evidence rather than claiming syntax/semantic facts.
        if completed.returncode == 3221225477:
            return ExtractionResult([Fact("opaque_source", request["source_path"], Evidence(request["project_id"], request["source_path"], 1, 1, "opaque-fallback", 0.0, request["source_hash"]), {"classification": "native_parser_fallback", "worker_exit_code": completed.returncode})])
        return _warning(request, "abnormal_exit", f"Extraction worker exited with code {completed.returncode}.")
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return _warning(request, "invalid_worker_output", "Extraction worker returned invalid structured output.")
    if payload.get("status") != "succeeded":
        return _warning(request, "python_extraction_error", "Extraction worker reported a Python extraction error.")
    try:
        return ExtractionResult([_fact(item) for item in payload["facts"]])
    except (KeyError, TypeError, ValueError):
        return _warning(request, "invalid_worker_output", "Extraction worker returned invalid fact data.")


def _worker(request: dict[str, str]) -> dict[str, Any]:
    root = Path(request["source_root"])
    source_path = root / request["source_path"]
    from polaris_modernization.tree_sitter_extractors.registry import extractor_for

    extractor = extractor_for(source_path)
    if extractor is None:
        raise ValueError("No extractor is available for the requested file.")
    facts = extractor.extract(source_path, root, request["source_hash"], request["project_id"])
    return {"status": "succeeded", "facts": [fact.to_dict() for fact in facts]}


def main() -> None:
    try:
        request = json.loads(sys.stdin.read())
        print(json.dumps(_worker(request), separators=(",", ":")))
    except Exception:
        # Do not emit source content or Python tracebacks from the isolated worker.
        print(json.dumps({"status": "error"}, separators=(",", ":")))


if __name__ == "__main__":
    main()
