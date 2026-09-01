from hashlib import sha256
import json

import pytest

from polaris_modernization.business_features.retrieval import build_business_feature_packages, load_approved_features
from polaris_modernization.business_features.workflow import UnsupportedBusinessClaimsError, prepare_business_feature_enrichment, validate_and_persist_business_features


REF = {"node_id": "kg:dashboard", "source_path": "src/Web/dashboard.js", "line_start": 1, "line_end": 2, "provenance": "STRUCTURAL_ONLY"}
CONF = {"level": "HIGH", "provenance": ["STRUCTURAL_ONLY"], "rationale": "fixture evidence"}


def approved_features(tmp_path):
    root = tmp_path / "feature-run"
    root.mkdir()
    feature = {
        "feature_id": "feature-dashboard", "title": "Dashboard Insights", "business_outcome": "View dashboard", "description": "Dashboard",
        "module": "Dashboard", "business_capabilities": ["View insights"], "actors_personas": [], "workflows": ["Load dashboard"],
        "ui_surfaces": ["DashboardController"], "domain_concepts": [], "business_rules": [], "dependencies": [],
        "api_contracts": [{"workflow": "Load dashboard", "status": "PROVEN"}], "source_evidence": [REF], "kg_evidence": ["kg:dashboard"],
        "application_understanding_evidence": [], "evidence_package_ids": ["feature-module:dashboard"], "confidence": CONF,
        "provenance": "AGENT_REASONING", "modernization_scope": ["UI_MODERNIZATION"], "modernization_priority": "HIGH", "modernization_rationale": "POC", "limitations": [],
    }
    catalog = {"project_id": "fixture", "kg_run_id": "kg-run", "application_understanding_run_id": "au-run", "feature_run_id": "feature-run", "readiness": "FEATURES_READY_WITH_LIMITATIONS", "features": [feature], "poc_selection": {"feature_ids": ["feature-dashboard"]}, "quality_review": {}, "limitations": [], "next_action": "GENERATE_STORIES"}
    (root / "feature-catalog.json").write_text(json.dumps(catalog))
    package_map = {"feature-module:dashboard": "package-hash"}
    manifest_hash = sha256(json.dumps(package_map, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    (root / "feature-evidence-package-manifest.json").write_text(json.dumps({"kg_run_id": "kg-run", "application_understanding_run_id": "au-run", "manifest_hash": manifest_hash, "packages": package_map}))
    workflow_evidence = [
        {"node_id": "kg:ApiCall:GET /api/dashboard", "source_path": "src/Web/dashboard.js", "line_start": 1, "line_end": 2, "provenance": "STRUCTURAL_ONLY"},
        {"node_id": "kg:Endpoint:GET /api/dashboard", "source_path": "src/Api/DashboardController.cs", "line_start": 3, "line_end": 4, "provenance": "STRUCTURAL_ONLY"},
    ]
    (root / "feature-evidence-packages.json").write_text(json.dumps([{"package_id": "feature-module:dashboard", "package_hash": "package-hash", "objects": {"workflows": [{"name": "Load dashboard", "evidence": workflow_evidence}]}}]))
    (root / "feature-validation.json").write_text(json.dumps({"valid": True, "package_hash_validation": "PASS", "provenance_validation": "PASS", "feature_validation": "PASS"}))
    (root / "provenance.json").write_text(json.dumps({"kg_run_id": "kg-run", "application_understanding_run_id": "au-run", "feature_run_id": "feature-run"}))
    (root / "token-usage.json").write_text(json.dumps({"external_llm_api_calls": 0}))
    return root


def statement(text, classification="PROVEN"):
    return {"text": text, "classification": classification, "evidence": [REF], "confidence": CONF}


def submission(approved, packages):
    package_map = {item.package_id: item.package_hash for item in packages}
    manifest_hash = sha256(json.dumps(package_map, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    spec = {
        "feature_id": "feature-dashboard", "feature_name": "Dashboard Insights", "short_business_summary": "Dashboard information", "business_capabilities": ["View insights"], "functional_module": "Dashboard", "feature_status": "APPROVED_ENRICHED", "confidence": CONF,
        "executive_description": ["The feature presents dashboard information.", "It belongs to the approved dashboard area."],
        "current_objective": statement("Present dashboard information."), "modernization_objective": statement("Preserve the workflow in the target frontend.", "MODERNIZATION_CONCERN"),
        "business_value": [statement("May improve access to dashboard information.", "INFERRED_BUSINESS_VALUE")], "actors": [], "actor_evidence_limitation": "No actor is proven.",
        "capability_details": [{"name": "View insights", "contribution": "Presents insights", "workflows": ["Load dashboard"], "evidence": [REF]}],
        "current_business_functionality": [statement("Loads dashboard information.")],
        "workflows": [{"name": "Load dashboard", "business_trigger": "Dashboard navigation", "actor": None, "business_steps": ["Open dashboard", "Load information"], "expected_outcome": "Dashboard information is available", "supporting_ui": ["DashboardController"], "api_status": "PROVEN", "evidence": [REF], "confidence": CONF}],
        "business_rules": [], "no_business_rules_marker": "NO_EVIDENCE_BACKED_BUSINESS_RULES_IDENTIFIED", "domain_concepts": [],
        "information_involved": [statement("Dashboard information is exchanged.")], "dependencies": [],
        "api_integration": {"proven": 1, "unresolved": 0, "dynamic": 0, "external": 0, "no_backend_route": 0, "relationships": [{"workflow": "Load dashboard", "status": "PROVEN"}], "business_readable_limitation": "No unresolved relationship."},
        "current_user_experience": [statement("A dashboard client surface presents the feature.")], "evidence_backed_limitations": [],
        "modernization_concerns": [statement("The legacy client requires migration.", "MODERNIZATION_CONCERN")],
        "in_scope": [statement("Preserve the dashboard workflow.")], "out_of_scope": [statement("Backend redesign is excluded.")], "assumptions": [],
        "open_questions": [{"question_id": "Q1", "question": "Which dashboard information is most important to stakeholders?", "reason": "Priority is not proven.", "evidence": [REF], "confidence": CONF}],
        "risks_and_limitations": [statement("Only approved behavior can be preserved.", "BUSINESS_ANALYSIS_LIMITATION")],
        "success_indicators": [statement("The approved workflow remains available in the target frontend.", "MODERNIZATION_SUCCESS_INDICATOR")],
        "story_decomposition_guidance": [{"boundary": "Present dashboard", "workflows": ["Load dashboard"], "rationale": "One approved workflow boundary."}],
        "source_evidence": [REF], "kg_evidence": ["kg:dashboard"], "evidence_package_id": "business-feature:feature-dashboard",
    }
    return {"kg_run_id": "kg-run", "application_understanding_run_id": "au-run", "feature_run_id": "feature-run", "evidence_package_manifest_hash": manifest_hash, "business_features": [spec]}


def test_packages_are_stable_and_prepare_uses_no_external_llm(tmp_path):
    approved = load_approved_features(approved_features(tmp_path))
    assert [item.package_hash for item in build_business_feature_packages(approved)] == [item.package_hash for item in build_business_feature_packages(approved)]
    prepared = prepare_business_feature_enrichment(tmp_path / "feature-run", tmp_path / "out")
    assert json.loads((prepared["path"] / "preparation.json").read_text())["external_llm_api_calls"] == 0


def test_valid_enrichment_preserves_identity_and_persists(tmp_path):
    root = approved_features(tmp_path)
    approved = load_approved_features(root)
    packages = build_business_feature_packages(approved)
    path = tmp_path / "agent.json"
    path.write_text(json.dumps(submission(approved, packages)))
    result = validate_and_persist_business_features(root, tmp_path / "out", path)
    assert result["quality"]["feature_ids_preserved"] is True
    assert (tmp_path / "out/latest/poc-business-feature.md").is_file()


def test_stale_hash_and_api_upgrade_are_rejected(tmp_path):
    root = approved_features(tmp_path)
    approved = load_approved_features(root)
    packages = build_business_feature_packages(approved)
    payload = submission(approved, packages)
    payload["evidence_package_manifest_hash"] = "stale"
    path = tmp_path / "agent.json"
    path.write_text(json.dumps(payload))
    with pytest.raises(UnsupportedBusinessClaimsError, match="manifest"):
        validate_and_persist_business_features(root, tmp_path / "out", path)
    payload = submission(approved, packages)
    payload["business_features"][0]["api_integration"]["relationships"][0]["status"] = "UNRESOLVED"
    path.write_text(json.dumps(payload))
    with pytest.raises(UnsupportedBusinessClaimsError, match="API status"):
        validate_and_persist_business_features(root, tmp_path / "out", path)


def test_fabricated_actor_and_unlabeled_assumption_are_rejected(tmp_path):
    root = approved_features(tmp_path)
    approved = load_approved_features(root)
    packages = build_business_feature_packages(approved)
    payload = submission(approved, packages)
    payload["business_features"][0]["actors"] = [{"name": "Administrator", "role": "Admin", "supporting_workflows": ["Load dashboard"], "evidence": [REF], "confidence": CONF}]
    path = tmp_path / "agent.json"
    path.write_text(json.dumps(payload))
    with pytest.raises(UnsupportedBusinessClaimsError, match="actors"):
        validate_and_persist_business_features(root, tmp_path / "out", path)
    payload = submission(approved, packages)
    payload["business_features"][0]["assumptions"] = [statement("Assumed behavior", "PROVEN")]
    path.write_text(json.dumps(payload))
    with pytest.raises(UnsupportedBusinessClaimsError, match="Assumptions"):
        validate_and_persist_business_features(root, tmp_path / "out", path)


def test_fabricated_kpi_is_rejected(tmp_path):
    root = approved_features(tmp_path)
    approved = load_approved_features(root)
    packages = build_business_feature_packages(approved)
    payload = submission(approved, packages)
    payload["business_features"][0]["success_indicators"][0]["text"] = "Increase productivity by 30%."
    path = tmp_path / "agent.json"
    path.write_text(json.dumps(payload))
    with pytest.raises(UnsupportedBusinessClaimsError, match="KPIs"):
        validate_and_persist_business_features(root, tmp_path / "out", path)
