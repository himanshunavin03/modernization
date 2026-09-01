"""Load one approved Business Feature run and build deterministic Story packages."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import re

from polaris_modernization.application_understanding.models import EvidenceReference
from polaris_modernization.business_features.models import ApiRelationshipPath
from polaris_modernization.stories.models import StoryEvidencePackage


def _read(path: Path) -> object:
    if not path.is_file():
        raise ValueError(f"Required approved Business Feature artifact is missing: {path.name}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_approved_business_features(root: Path) -> dict:
    catalog = _read(root / "business-feature-catalog.json")
    validation = _read(root / "business-feature-validation.json")
    manifest = _read(root / "business-feature-evidence-manifest.json")
    provenance = _read(root / "provenance.json")
    token_usage = _read(root / "token-usage.json")
    poc_path = root / "poc-business-feature.md"
    if not poc_path.is_file():
        raise ValueError("Required approved Business Feature artifact is missing: poc-business-feature.md")
    poc_match = re.search(r"\*\*Feature ID:\*\* `([^`]+)`", poc_path.read_text(encoding="utf-8"))
    if not poc_match:
        raise ValueError("Approved POC Business Feature does not identify its Feature ID.")
    poc_feature_id = poc_match.group(1)
    run_id = root.name
    if catalog.get("business_feature_run_id") != run_id or catalog.get("readiness") not in {"BUSINESS_FEATURES_READY", "BUSINESS_FEATURES_READY_WITH_LIMITATIONS"}:
        raise ValueError("Business Feature catalog is not approved for Story generation.")
    if not validation.get("valid") or any(validation.get(key) != "PASS" for key in ("provenance_validation", "business_feature_validation", "business_quality_validation")):
        raise ValueError("Business Feature validation is not approved for Story generation.")
    lineage = (catalog["kg_run_id"], catalog["application_understanding_run_id"], catalog["feature_run_id"], run_id)
    actual = tuple(provenance.get(key) for key in ("kg_run_id", "application_understanding_run_id", "feature_run_id", "business_feature_run_id"))
    if lineage != actual:
        raise ValueError("Business Feature provenance does not match catalog lineage.")
    package_map = manifest.get("packages", {})
    encoded = json.dumps(package_map, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if manifest.get("manifest_hash") != sha256(encoded).hexdigest() or manifest.get("hash_validation") != "PASS":
        raise ValueError("Business Feature evidence manifest is stale or invalid.")
    if token_usage.get("external_llm_api_calls") != 0:
        raise ValueError("Approved Business Feature run records external LLM API calls.")
    if poc_feature_id not in {item["feature_id"] for item in catalog["business_features"]}:
        raise ValueError("Approved POC Business Feature is not present in the catalog.")
    return {"catalog": catalog, "validation": validation, "manifest": manifest, "run_id": run_id, "poc_feature_id": poc_feature_id}


def stable_slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _evidence(value: object) -> list[dict]:
    found: dict[tuple, dict] = {}
    def visit(item: object) -> None:
        if isinstance(item, dict):
            if {"node_id", "source_path", "line_start", "line_end", "provenance"} <= item.keys():
                key = (item["node_id"], item["source_path"], item["line_start"], item["line_end"], item["provenance"])
                found[key] = {key_name: item[key_name] for key_name in ("node_id", "source_path", "line_start", "line_end", "provenance")}
            for child in item.values():
                visit(child)
        elif isinstance(item, list):
            for child in item:
                visit(child)
    visit(value)
    return [found[key] for key in sorted(found)]


def build_story_packages(approved: dict) -> list[StoryEvidencePackage]:
    catalog = approved["catalog"]
    packages: list[StoryEvidencePackage] = []
    for feature in catalog["business_features"]:
        workflows = {item["name"]: item for item in feature["workflows"]}
        for boundary in feature["story_decomposition_guidance"]:
            selected = [workflows[name] for name in boundary["workflows"]]
            ui = sorted({name for workflow in selected for name in workflow["supporting_ui"]})
            api = [item for item in feature["api_integration"].get("paths", []) if item["workflow"] in boundary["workflows"]]
            source_evidence = _evidence({"feature": feature, "workflows": selected})
            payload = {
                "kg_run_id": catalog["kg_run_id"], "application_understanding_run_id": catalog["application_understanding_run_id"],
                "feature_run_id": catalog["feature_run_id"], "business_feature_run_id": approved["run_id"],
                "parent_feature_id": feature["feature_id"], "parent_feature_name": feature["feature_name"],
                "boundary": boundary["boundary"], "boundary_rationale": boundary["rationale"],
                "business_capabilities": feature["business_capabilities"], "workflows": selected, "ui_surfaces": ui,
                "domain_concepts": [item["name"] for item in feature["domain_concepts"]],
                "business_rules": [item["rule_id"] for item in feature["business_rules"]],
                "dependencies": [item["name"] for item in feature["dependencies"]], "api_relationships": api,
                "open_questions": feature["open_questions"], "business_value": feature["business_value"],
                "source_evidence": source_evidence, "kg_evidence": feature["kg_evidence"],
                "business_feature_evidence": feature["evidence_package_id"],
            }
            digest = sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
            package_id = f"story-evidence:{feature['feature_id']}:{stable_slug(boundary['boundary'])}"
            packages.append(StoryEvidencePackage(
                package_id=package_id, package_hash=digest,
                api_relationships=[ApiRelationshipPath.model_validate(item) for item in api],
                source_evidence=[EvidenceReference.model_validate(item) for item in source_evidence],
                **{key: value for key, value in payload.items() if key not in {"api_relationships", "source_evidence"}},
            ))
    return sorted(packages, key=lambda item: item.package_id)
