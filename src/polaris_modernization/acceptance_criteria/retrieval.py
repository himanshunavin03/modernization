"""Load an approved Story run and build deterministic AC evidence packages."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

from polaris_modernization.acceptance_criteria.models import AcceptanceEvidencePackage


def _read(path: Path) -> object:
    if not path.is_file():
        raise ValueError(f"Required approved Story artifact is missing: {path.name}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_approved_stories(root: Path) -> dict:
    catalog = _read(root / "story-catalog.json")
    validation = _read(root / "story-validation.json")
    manifest = _read(root / "story-evidence-manifest.json")
    packages = _read(root / "story-evidence-packages.json")
    questions = _read(root / "story-open-questions.json")
    poc = _read(root / "poc-story-selection.json")
    provenance = _read(root / "provenance.json")
    token_usage = _read(root / "token-usage.json")
    run_id = root.name
    if catalog.get("story_run_id") != run_id or catalog.get("readiness") not in {"STORIES_READY", "STORIES_READY_WITH_LIMITATIONS"}:
        raise ValueError("Story catalog is not approved for Acceptance Criteria generation.")
    if not validation.get("valid") or any(validation.get(key) != "PASS" for key in ("package_hash_validation", "provenance_validation", "story_validation", "story_quality_validation")):
        raise ValueError("Story validation is not approved for Acceptance Criteria generation.")
    lineage_keys = ("kg_run_id", "application_understanding_run_id", "feature_run_id", "business_feature_run_id", "story_run_id")
    if tuple(catalog[key] for key in lineage_keys) != tuple(provenance.get(key) for key in lineage_keys):
        raise ValueError("Story provenance does not match the catalog lineage.")
    package_map = {item["package_id"]: item["package_hash"] for item in packages}
    encoded = json.dumps(package_map, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if manifest.get("packages") != package_map or manifest.get("manifest_hash") != sha256(encoded).hexdigest() or manifest.get("hash_validation") != "PASS":
        raise ValueError("Story evidence manifest is stale or invalid.")
    if token_usage.get("external_llm_api_calls") != 0:
        raise ValueError("Approved Story run records external LLM API calls.")
    return {"catalog": catalog, "validation": validation, "manifest": manifest, "packages": packages, "questions": questions, "poc": poc, "run_id": run_id}


def build_acceptance_packages(approved: dict) -> list[AcceptanceEvidencePackage]:
    catalog = approved["catalog"]
    result = []
    for story in catalog["stories"]:
        payload = {
            "kg_run_id": catalog["kg_run_id"], "application_understanding_run_id": catalog["application_understanding_run_id"],
            "feature_run_id": catalog["feature_run_id"], "business_feature_run_id": catalog["business_feature_run_id"],
            "story_run_id": approved["run_id"], "story": story,
        }
        digest = sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
        result.append(AcceptanceEvidencePackage(package_id=f"acceptance-evidence:{story['story_id']}", package_hash=digest, **payload))
    return sorted(result, key=lambda item: item.package_id)
