"""Deterministic retrieval of compact Feature evidence from an approved AU run."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import re

from polaris_modernization.application_understanding.models import ConfidenceAssessment, EvidenceReference
from polaris_modernization.feature_generation.models import FeatureEvidencePackage


COLLECTIONS = {
    "modules": "business_modules",
    "capabilities": "business_capabilities",
    "workflows": "user_workflows",
    "ui_surfaces": "ui_surfaces",
    "domain_concepts": "domain_concepts",
    "business_rules": "business_rules",
    "dependencies": "dependencies",
}


def _read_json(path: Path) -> object:
    if not path.is_file():
        raise ValueError(f"Required approved Application Understanding artifact is missing: {path.name}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_approved_application_understanding(root: Path) -> dict:
    understanding = _read_json(root / "application-understanding.json")
    validation = _read_json(root / "agent-reasoning-validation.json")
    manifest = _read_json(root / "evidence-package-manifest.json")
    packages = _read_json(root / "evidence-packages.json")
    token_usage = _read_json(root / "token-usage.json")
    run_id = root.name
    if understanding.get("status") != "COMPLETE" or understanding.get("readiness") not in {
        "APPLICATION_UNDERSTANDING_READY", "APPLICATION_UNDERSTANDING_READY_WITH_LIMITATIONS",
    }:
        raise ValueError("Application Understanding is not approved for Feature generation.")
    if not validation.get("valid") or any(validation.get(key) != "PASS" for key in ("package_hash_validation", "provenance_validation", "claim_validation")):
        raise ValueError("Application Understanding validation is not approved for Feature generation.")
    if validation.get("kg_run_id") != understanding.get("kg_run_id") or manifest.get("kg_run_id") != understanding.get("kg_run_id"):
        raise ValueError("Application Understanding artifacts reference different KG runs.")
    actual_packages = {item["package_id"]: item["package_hash"] for item in packages}
    if manifest.get("packages") != actual_packages:
        raise ValueError("Application Understanding evidence package hashes are stale or incomplete.")
    encoded = json.dumps(actual_packages, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if manifest.get("manifest_hash") != sha256(encoded).hexdigest():
        raise ValueError("Application Understanding evidence manifest hash is invalid.")
    if token_usage.get("external_llm_api_calls") != 0:
        raise ValueError("Interactive Application Understanding unexpectedly records external LLM API calls.")
    return {
        "understanding": understanding,
        "validation": validation,
        "manifest": manifest,
        "packages": packages,
        "run_id": run_id,
        "kg_run_id": understanding["kg_run_id"],
    }


def _tokens(value: str) -> set[str]:
    expanded = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", value).lower()
    tokens = {token for token in re.findall(r"[a-z0-9]+", expanded) if len(token) > 3 and token not in {"manage", "management", "current", "route"}}
    return tokens | {token[:-1] for token in tokens if token.endswith("s") and len(token) > 4}


def _is_related(item: dict, seeds: set[str], seed_tokens: set[str]) -> bool:
    name = item.get("name", "")
    related = set(item.get("related_items", []))
    if name in seeds or related & seeds:
        return True
    return bool((_tokens(name) | _tokens(item.get("ui_surface", ""))) & seed_tokens)


def _references(objects: dict[str, list[dict]]) -> list[EvidenceReference]:
    values: dict[tuple, EvidenceReference] = {}
    for items in objects.values():
        for item in items:
            for evidence in item.get("evidence", []):
                reference = EvidenceReference.model_validate(evidence)
                key = (reference.node_id, reference.source_path, reference.line_start, reference.line_end, reference.provenance)
                values[key] = reference
    return sorted(values.values(), key=lambda item: (item.source_path, item.line_start, item.node_id))


def build_feature_evidence_packages(approved: dict) -> list[FeatureEvidencePackage]:
    understanding = approved["understanding"]
    results: list[FeatureEvidencePackage] = []
    for module in understanding["business_modules"]:
        seeds = {module["name"], *module.get("related_items", [])}
        selected_capabilities: list[dict] = []
        while True:
            additions = [
                item for item in understanding["business_capabilities"]
                if item not in selected_capabilities and (item["name"] in seeds or set(item.get("related_items", [])) & seeds)
            ]
            if not additions:
                break
            selected_capabilities.extend(additions)
            for item in additions:
                seeds.update({item["name"], *item.get("related_items", [])})
        seed_tokens = set().union(*(_tokens(value) for value in seeds))
        objects: dict[str, list[dict]] = {"modules": [module]}
        for output_name, source_name in COLLECTIONS.items():
            if output_name == "modules":
                continue
            objects[output_name] = selected_capabilities if output_name == "capabilities" else [item for item in understanding[source_name] if _is_related(item, seeds, seed_tokens)]
        references = _references(objects)
        provenance = sorted({item.provenance for item in references})
        confidence = ConfidenceAssessment(
            level="HIGH" if references and all(item.provenance in {"COMPILER_PROVEN", "PROJECT_PARTIAL", "STRUCTURAL_ONLY"} for item in references) else "MEDIUM",
            provenance=provenance,
            rationale="Deterministic subset of validated Application Understanding evidence.",
        )
        payload = {
            "kg_run_id": approved["kg_run_id"], "application_understanding_run_id": approved["run_id"],
            "module": module["name"], "objects": objects,
            "evidence": [item.model_dump(mode="json") for item in references],
        }
        digest = sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
        package_id = "feature-module:" + re.sub(r"[^a-z0-9]+", "-", module["name"].lower()).strip("-")
        results.append(FeatureEvidencePackage(
            package_id=package_id, package_hash=digest, kg_run_id=approved["kg_run_id"],
            application_understanding_run_id=approved["run_id"], module=module["name"],
            objects=objects, evidence=references, confidence=confidence,
        ))
    return sorted(results, key=lambda item: item.package_id)
