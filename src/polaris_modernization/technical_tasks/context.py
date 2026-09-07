"""Resolve the current approved Feature contract for technical planning."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path


class TechnicalTaskContextError(ValueError):
    """The current Feature contract or its downstream lineage is inconsistent."""


def _read(path: Path) -> dict:
    if not path.is_file():
        raise TechnicalTaskContextError(f"Required approved artifact is missing: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _normalise_api(contract: dict) -> dict:
    metadata = contract.get("metadata") or [{}]
    detail = metadata[0]
    return {
        "api_id": contract.get("api_id") or contract["contract_id"],
        "method": contract["method"],
        "endpoint": contract.get("endpoint") or contract["route"],
        "path_parameters": [
            item if isinstance(item, dict) else {"name": item, "location": "Path", "description": f"{item} path parameter"}
            for item in detail.get("path_parameters", contract.get("path_parameters", []))
        ],
        "query_parameters": [
            item if isinstance(item, dict) else {"name": item, "location": "Query", "description": f"{item} query parameter"}
            for item in detail.get("query_parameters", contract.get("query_parameters", []))
        ],
        "request_model": detail.get("request_type", contract.get("request_model")),
        "response_model": detail.get("response_type", contract.get("response_model")),
        "response_description": contract.get("response_description") or detail.get("response_type") or "Approved response contract",
        "purpose": contract.get("purpose") or f"Preserve the approved {contract['method']} {contract.get('route', contract.get('endpoint'))} contract.",
        "requirement_ids": contract.get("requirement_ids", []),
        "traceability": {
            "source_capability_ids": contract.get("source_capability_ids", []),
            "endpoint_node_ids": list(dict.fromkeys(item.get("node_id") for item in metadata if item.get("node_id"))),
        },
    }


def resolve_feature_context(specification_root: Path, feature_id: str) -> dict:
    """Prefer the active per-Feature contract, retaining the historical bundle fallback."""
    feature_path = specification_root / f"{feature_id}.json"
    feature = _read(feature_path)
    current_shape = all(key in feature for key in (
        "functional_requirements", "stories", "acceptance_criteria", "capability_api_contracts",
    ))
    if not current_shape:
        bundle = _read(specification_root / "jira-quality.json")
        legacy = next((item for item in bundle["features"] if item["feature_id"] == feature_id), None)
        if not legacy:
            raise TechnicalTaskContextError(f"Unknown approved Feature: {feature_id}")
        stories = legacy["stories"]
        return {
            "feature": legacy,
            "requirements": list({item["id"]: item for story in stories for item in story["functional_requirement_refs"]}.values()),
            "stories": stories,
            "acceptance_criteria": [item for story in stories for item in story["acceptance_criteria"]],
            "api_contracts": list({item["api_id"]: item for story in stories for item in story["api_dependencies"]}.values()),
            "lineage": {"feature_contract": str(feature_path), "feature_contract_hash": _digest(feature_path), "mode": "CONSOLIDATED"},
        }

    lineage = feature.get("generation_lineage") or feature.get("traceability") or {}
    required_lineage = ("feature_run", "story_run", "acceptance_criteria_run", "kg_run_id")
    missing = [key for key in required_lineage if not lineage.get(key)]
    if missing:
        raise TechnicalTaskContextError(f"Current Feature lineage is incomplete: {missing}")
    repository_root = specification_root.parents[2]
    story_root = repository_root / "artifacts" / "stories" / "features" / feature_id / "latest"
    ac_root = repository_root / "artifacts" / "acceptance-criteria" / "features" / feature_id / "latest"
    story_lineage = _read(story_root / "story-lineage.json")
    ac_lineage = _read(ac_root / "acceptance-lineage.json")
    comparisons = {
        "feature_lineage": bool(lineage.get("feature_run")),
        "story_lineage": story_lineage.get("story_run") == lineage["story_run"] and story_lineage.get("feature_run") == lineage["feature_run"],
        "acceptance_criteria_lineage": ac_lineage.get("acceptance_criteria_run") == lineage["acceptance_criteria_run"] and ac_lineage.get("story_run") == lineage["story_run"],
        "feature_specification_lineage": feature.get("traceability", {}).get("story_run") == lineage["story_run"] and feature.get("traceability", {}).get("acceptance_criteria_run") == lineage["acceptance_criteria_run"],
    }
    if not all(comparisons.values()):
        raise TechnicalTaskContextError(f"Current Feature lineage validation failed: {comparisons}")

    requirements = feature["functional_requirements"]
    stories = [{
        **item,
        "summary": item.get("summary") or item.get("title"),
        "functional_requirement_refs": item.get("functional_requirement_refs") or [
            {"id": ref} for ref in item.get("functional_requirement_ids", [])
        ],
    } for item in feature["stories"]]
    criteria = [{
        **item,
        "id": item.get("id") or f"AC-{index:03d}",
        "authoritative_ac_ref": item.get("authoritative_ac_ref") or item["acceptance_criterion_id"],
    } for index, item in enumerate(feature["acceptance_criteria"], 1)]
    return {
        "feature": {**feature, "feature_name": feature["feature_name"]},
        "requirements": requirements,
        "stories": stories,
        "acceptance_criteria": criteria,
        "api_contracts": [_normalise_api(item) for item in feature["capability_api_contracts"]],
        "lineage": {
            **lineage,
            "feature_contract": str(feature_path.relative_to(repository_root)),
            "feature_contract_hash": _digest(feature_path),
            "mode": "CURRENT_FEATURE",
            "checks": comparisons,
        },
    }
