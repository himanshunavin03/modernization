"""Process isolation for native Tree-sitter extraction."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

from polaris_modernization.models import Evidence, Fact

WORKER_TIMEOUT_SECONDS = 30


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
        )
    except subprocess.TimeoutExpired:
        return _warning(request, "timeout", "Extraction worker exceeded the allowed time.")
    except OSError:
        return _warning(request, "worker_start_failed", "Extraction worker could not be started.")

    if completed.returncode != 0:
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
