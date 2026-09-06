"""Artifact navigation, Feature resolution, and persisted command state."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import re
import tempfile
from typing import Any

from .models import AmbiguousFeatureError, FeatureNotFoundError


def _read(path: Path, default: Any = None) -> Any:
    if not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")


def _relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def _write_json_atomic(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True) + "\n")
        temporary = Path(stream.name)
    temporary.replace(path)


@dataclass(frozen=True)
class ArtifactPaths:
    repository_root: Path

    @property
    def artifacts(self) -> Path:
        return self.repository_root / "artifacts"

    @property
    def specifications(self) -> Path:
        return self.artifacts / "feature-specifications" / "latest"

    @property
    def command_root(self) -> Path:
        return self.artifacts / "commands"

    @property
    def feature_index(self) -> Path:
        return self.command_root / "feature-index.json"

    @property
    def modernization_state(self) -> Path:
        return self.command_root / "modernization-state.json"


class FeatureIndex:
    def __init__(self, paths: ArtifactPaths) -> None:
        self.paths = paths

    def build(self, *, persist: bool = True) -> dict[str, Any]:
        source_path = self.paths.specifications / "feature-specification-index.json"
        source = _read(source_path)
        if not source or not isinstance(source.get("features"), list):
            raise FeatureNotFoundError("No Feature index is available. Run /generate-features.")
        api_catalog = _read(self.paths.specifications / "feature-api-contracts.json", {})
        api_by_feature = {
            item.get("feature_id"): item.get("contracts", [])
            for item in api_catalog.get("features", [])
        }
        architecture = _read(self.paths.artifacts / "architecture" / "latest" / "architecture.json", {})
        architecture_selection = architecture.get("selection", {})
        task_plan = _read(self.paths.artifacts / "technical-tasks" / "latest" / "technical-tasks.json", {})
        generation = _read(self.paths.artifacts / "modernization" / "latest" / "generation-manifest.json", {})
        generation_validation = _read(self.paths.artifacts / "modernization" / "latest" / "generation-validation.json", {})
        persisted = _read(self.paths.modernization_state, {"features": {}})
        persisted_features = persisted.get("features", {})
        rows: list[dict[str, Any]] = []
        source_hashes: dict[str, str] = {}
        for summary in source["features"]:
            feature_id = summary["feature_id"]
            spec_path = self.paths.specifications / f"{feature_id}.json"
            specification = _read(spec_path, {})
            source_hashes[_relative(spec_path, self.paths.repository_root)] = sha256(spec_path.read_bytes()).hexdigest() if spec_path.is_file() else "MISSING"
            stories = [item.get("story_id") for item in specification.get("stories", []) if item.get("story_id")]
            criteria = [item.get("acceptance_criterion_id") for item in specification.get("acceptance_criteria", []) if item.get("acceptance_criterion_id")]
            contracts = api_by_feature.get(feature_id, [])
            task_ids = [item["task_id"] for item in task_plan.get("tasks", [])] if task_plan.get("feature_id") == feature_id else []
            modernization_operation = task_plan.get("modernization_operation") if task_plan.get("feature_id") == feature_id else None
            implementation_paths = generation.get("generated_files", []) if generation.get("feature_id") == feature_id else []
            test_paths = [item["file"] for item in generation.get("generated_tests", [])] if generation.get("feature_id") == feature_id else []
            if feature_id in persisted_features:
                status = persisted_features[feature_id]["status"]
            elif implementation_paths and generation_validation.get("status") == "PASS":
                status = "IMPLEMENTED"
            elif task_ids:
                status = "READY"
            else:
                status = "NOT_STARTED"
            architecture_selected = bool(
                architecture_selection.get("feature_id") == feature_id
                and architecture.get("architecture_lock", {}).get("status") == "LOCKED"
            )
            selected_decisions = architecture_selection.get("decisions", []) if architecture_selected else []
            rows.append({
                "feature_id": feature_id,
                "slug": feature_id.removeprefix("feature-"),
                "name": summary["feature_name"],
                "spec_path": _relative(spec_path, self.paths.repository_root),
                "story_ids": stories,
                "acceptance_criteria_ids": criteria,
                "api_contract_ids": [item["contract_id"] for item in contracts if item.get("contract_id")],
                "technical_task_ids": task_ids,
                "modernization_operation": modernization_operation,
                "architecture_selected": architecture_selected,
                "architecture_decision_ids": [item["id"] for item in selected_decisions if item.get("id")],
                "adr_ids": list(dict.fromkeys(item["adr_ref"] for item in selected_decisions if item.get("adr_ref"))),
                "modernization_status": status,
                "implementation_paths": implementation_paths,
                "test_paths": test_paths,
            })
        result = {
            "schema_version": 1,
            "source_index": _relative(source_path, self.paths.repository_root),
            "source_run_id": source.get("feature_specification_run_id"),
            "source_hashes": source_hashes,
            "features": rows,
        }
        if persist:
            _write_json_atomic(self.paths.feature_index, result)
        return result

    def resolve(self, query: str, index: dict[str, Any] | None = None) -> dict[str, Any]:
        index = index or self.build()
        normalized = _slug(query).removeprefix("feature-")
        matches = [
            item for item in index["features"]
            if normalized in {
                _slug(item["feature_id"]).removeprefix("feature-"),
                _slug(item["slug"]),
                _slug(item["name"]),
            }
        ]
        if not matches:
            raise FeatureNotFoundError(f"Feature '{query}' was not found. Run /list-features.")
        if len(matches) > 1:
            raise AmbiguousFeatureError(query, matches)
        return matches[0]

    def resolve_story(self, story_id: str, index: dict[str, Any] | None = None) -> tuple[dict[str, Any], str]:
        index = index or self.build()
        matches = [(feature, candidate) for feature in index["features"] for candidate in feature["story_ids"] if candidate.casefold() == story_id.casefold()]
        if not matches:
            raise FeatureNotFoundError(f"Story '{story_id}' was not found. Run /list-features.")
        if len(matches) > 1:
            raise AmbiguousFeatureError(story_id, [feature for feature, _ in matches])
        return matches[0]


class ModernizationState:
    def __init__(self, paths: ArtifactPaths) -> None:
        self.paths = paths

    def load(self) -> dict[str, Any]:
        return _read(self.paths.modernization_state, {"schema_version": 1, "features": {}})

    def set(self, feature_id: str, status: str, operation: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
        state = self.load()
        state.setdefault("features", {})[feature_id] = {"status": status, "operation": operation, "details": details or {}}
        _write_json_atomic(self.paths.modernization_state, state)
        return state
