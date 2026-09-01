from hashlib import sha256
import json

import pytest

from polaris_modernization.feature_generation.retrieval import build_feature_evidence_packages, load_approved_application_understanding
from polaris_modernization.feature_generation.workflow import (
    UnsupportedFeatureClaimsError, prepare_feature_generation, validate_and_persist_features,
)


def evidence(node, path):
    return {"node_id": node, "source_path": path, "line_start": 1, "line_end": 2, "provenance": "STRUCTURAL_ONLY"}


def item(name, node, path, related=None):
    return {"name": name, "description": name, "related_items": related or [], "evidence_package_ids": ["upstream"], "evidence": [evidence(node, path)], "confidence": {"level": "HIGH", "provenance": ["STRUCTURAL_ONLY"], "rationale": "fixture"}, "origin": "AGENT_REASONING"}


def approved_au(tmp_path):
    root = tmp_path / "au-run"
    root.mkdir()
    module = {**item("Dashboard", "n:module", "Views/Dashboard.cshtml", ["Dashboard capability"]), "module_type": "FUNCTIONAL"}
    capability = item("Dashboard capability", "n:cap", "dashboard.js", ["Dashboard"])
    workflow = {**item("Load dashboard", "n:call", "service.js", ["Dashboard capability"]), "ui_surface": "DashboardController", "backend_mapping": "PROVEN"}
    surface = {**item("DashboardController", "n:ui", "dashboard.js"), "kind": "AngularController"}
    understanding = {
        "project_id": "fixture", "kg_run_id": "kg-approved", "status": "COMPLETE", "readiness": "APPLICATION_UNDERSTANDING_READY_WITH_LIMITATIONS",
        "application_purpose": "Fixture", "primary_application_type": "Web", "technical_composition": [], "major_user_facing_areas": [], "major_backend_areas": [],
        "kg_metrics": {}, "limitations": [], "api_mapping_summary": {}, "business_modules": [module], "business_capabilities": [capability],
        "user_workflows": [workflow], "business_rules": [], "ui_surfaces": [surface], "domain_concepts": [], "dependencies": [],
        "best_razor_demo_candidate": "Views/Dashboard.cshtml", "best_angular_demo_candidate": "DashboardController", "agent_reasoning": {},
    }
    (root / "application-understanding.json").write_text(json.dumps(understanding))
    validation = {"valid": True, "kg_run_id": "kg-approved", "package_hash_validation": "PASS", "provenance_validation": "PASS", "claim_validation": "PASS"}
    (root / "agent-reasoning-validation.json").write_text(json.dumps(validation))
    upstream = [{"package_id": "upstream", "package_hash": "hash"}]
    (root / "evidence-packages.json").write_text(json.dumps(upstream))
    package_map = {"upstream": "hash"}
    manifest_hash = sha256(json.dumps(package_map, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    (root / "evidence-package-manifest.json").write_text(json.dumps({"kg_run_id": "kg-approved", "manifest_hash": manifest_hash, "packages": package_map}))
    (root / "token-usage.json").write_text(json.dumps({"external_llm_api_calls": 0}))
    return root


def submission(approved, packages):
    package = packages[0]
    manifest = {item.package_id: item.package_hash for item in packages}
    manifest_hash = sha256(json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    refs = {ref.node_id: ref.model_dump(mode="json") for ref in package.evidence}
    feature = {
        "feature_id": "feature-dashboard", "title": "Dashboard insights", "business_outcome": "View dashboard information", "description": "Dashboard outcome",
        "module": "Dashboard", "business_capabilities": ["Dashboard capability"], "actors_personas": [], "workflows": ["Load dashboard"],
        "ui_surfaces": ["DashboardController"], "domain_concepts": [], "business_rules": [], "dependencies": [],
        "api_contracts": [{"workflow": "Load dashboard", "status": "PROVEN"}],
        "source_evidence": [refs["n:call"]], "kg_evidence": ["n:call"],
        "application_understanding_evidence": [{"object_type": "capability", "name": "Dashboard capability"}, {"object_type": "workflow", "name": "Load dashboard"}],
        "evidence_package_ids": [package.package_id], "confidence": {"level": "HIGH", "provenance": ["STRUCTURAL_ONLY"], "rationale": "fixture"},
        "provenance": "AGENT_REASONING", "modernization_scope": ["UI_MODERNIZATION", "API_INTEGRATION_PRESERVATION"], "modernization_priority": "HIGH",
        "modernization_rationale": "POC", "limitations": [],
    }
    return {
        "kg_run_id": "kg-approved", "application_understanding_run_id": approved["run_id"], "evidence_package_manifest_hash": manifest_hash,
        "features": [feature], "poc_selection": {"feature_ids": ["feature-dashboard"], "razor_feature_id": "feature-dashboard", "razor_surface": "Views/Dashboard.cshtml", "angularjs_feature_id": "feature-dashboard", "angularjs_surface": "DashboardController", "rationale": "same capability"},
    }


def test_feature_packages_are_deterministic_and_bound_to_upstream(tmp_path):
    approved = load_approved_application_understanding(approved_au(tmp_path))
    first = build_feature_evidence_packages(approved)
    second = build_feature_evidence_packages(approved)
    assert [item.package_hash for item in first] == [item.package_hash for item in second]
    assert all(item.kg_run_id == "kg-approved" and item.application_understanding_run_id == "au-run" for item in first)
    assert any(item["name"] == "DashboardController" for item in first[0].objects["ui_surfaces"])


def test_prepare_uses_no_external_llm(tmp_path):
    result = prepare_feature_generation(approved_au(tmp_path), tmp_path / "features")
    assert json.loads((result["path"] / "preparation.json").read_text())["external_llm_api_calls"] == 0


def test_valid_features_persist_with_provenance_and_poc(tmp_path):
    root = approved_au(tmp_path)
    approved = load_approved_application_understanding(root)
    packages = build_feature_evidence_packages(approved)
    path = tmp_path / "agent.json"
    path.write_text(json.dumps(submission(approved, packages)))
    result = validate_and_persist_features(root, tmp_path / "features", path)
    assert result["catalog"].readiness == "FEATURES_READY"
    assert result["catalog"].kg_run_id == "kg-approved"
    assert (tmp_path / "features/latest/feature-catalog.json").is_file()
    assert (tmp_path / "features/latest/feature-reasoning.json").is_file()


def test_stale_hash_and_api_status_promotion_are_rejected(tmp_path):
    root = approved_au(tmp_path)
    approved = load_approved_application_understanding(root)
    packages = build_feature_evidence_packages(approved)
    payload = submission(approved, packages)
    payload["evidence_package_manifest_hash"] = "stale"
    path = tmp_path / "agent.json"
    path.write_text(json.dumps(payload))
    with pytest.raises(UnsupportedFeatureClaimsError, match="manifest"):
        validate_and_persist_features(root, tmp_path / "features", path)
    payload = submission(approved, packages)
    payload["features"][0]["api_contracts"][0]["status"] = "UNRESOLVED"
    path.write_text(json.dumps(payload))
    with pytest.raises(UnsupportedFeatureClaimsError, match="API mapping"):
        validate_and_persist_features(root, tmp_path / "features", path)


def test_duplicate_and_untraceable_features_are_rejected(tmp_path):
    root = approved_au(tmp_path)
    approved = load_approved_application_understanding(root)
    packages = build_feature_evidence_packages(approved)
    payload = submission(approved, packages)
    payload["features"].append(payload["features"][0])
    path = tmp_path / "agent.json"
    path.write_text(json.dumps(payload))
    with pytest.raises(UnsupportedFeatureClaimsError, match="Duplicate"):
        validate_and_persist_features(root, tmp_path / "features", path)
