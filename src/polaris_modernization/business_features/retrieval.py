"""Read approved Feature artifacts and produce one compact package per Feature."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

from polaris_modernization.application_understanding.models import EvidenceReference
from polaris_modernization.business_features.models import BusinessFeatureEvidencePackage


def _read(path: Path) -> object:
    if not path.is_file():
        raise ValueError(f"Required approved Feature artifact is missing: {path.name}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_approved_features(root: Path) -> dict:
    catalog = _read(root / "feature-catalog.json")
    validation = _read(root / "feature-validation.json")
    manifest = _read(root / "feature-evidence-package-manifest.json")
    packages = _read(root / "feature-evidence-packages.json")
    provenance = _read(root / "provenance.json")
    token_usage = _read(root / "token-usage.json")
    run_id = root.name
    if catalog.get("feature_run_id") != run_id or catalog.get("readiness") not in {"FEATURES_READY", "FEATURES_READY_WITH_LIMITATIONS"}:
        raise ValueError("Feature catalog is not approved for Business Feature enrichment.")
    if not validation.get("valid") or any(validation.get(key) != "PASS" for key in ("package_hash_validation", "provenance_validation", "feature_validation")):
        raise ValueError("Feature validation is not approved for enrichment.")
    lineage = (catalog["kg_run_id"], catalog["application_understanding_run_id"], run_id)
    if lineage != (provenance.get("kg_run_id"), provenance.get("application_understanding_run_id"), provenance.get("feature_run_id")):
        raise ValueError("Feature provenance does not match the catalog lineage.")
    if manifest.get("kg_run_id") != lineage[0] or manifest.get("application_understanding_run_id") != lineage[1]:
        raise ValueError("Feature evidence manifest has stale upstream lineage.")
    package_map = {item["package_id"]: item["package_hash"] for item in packages}
    encoded = json.dumps(package_map, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if manifest.get("packages") != package_map or manifest.get("manifest_hash") != sha256(encoded).hexdigest():
        raise ValueError("Feature evidence manifest is stale or invalid.")
    if token_usage.get("external_llm_api_calls") != 0:
        raise ValueError("Approved interactive Feature run unexpectedly records external LLM API calls.")
    return {"catalog": catalog, "validation": validation, "manifest": manifest, "packages": packages, "run_id": run_id}


def build_business_feature_packages(approved: dict) -> list[BusinessFeatureEvidencePackage]:
    catalog = approved["catalog"]
    package_hashes = approved["manifest"]["packages"]
    result = []
    for feature in catalog["features"]:
        selected_hashes = {package_id: package_hashes[package_id] for package_id in feature["evidence_package_ids"]}
        payload = {
            "kg_run_id": catalog["kg_run_id"], "application_understanding_run_id": catalog["application_understanding_run_id"],
            "feature_run_id": approved["run_id"], "feature": feature,
            "upstream_feature_evidence_packages": selected_hashes,
        }
        digest = sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
        result.append(BusinessFeatureEvidencePackage(
            package_id=f"business-feature:{feature['feature_id']}", package_hash=digest,
            kg_run_id=catalog["kg_run_id"], application_understanding_run_id=catalog["application_understanding_run_id"],
            feature_run_id=approved["run_id"], feature=feature, upstream_feature_evidence_packages=selected_hashes,
            evidence=[EvidenceReference.model_validate(item) for item in feature["source_evidence"]],
        ))
    return sorted(result, key=lambda item: item.package_id)
