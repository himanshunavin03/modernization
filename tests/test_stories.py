from hashlib import sha256
import json
from pathlib import Path

import pytest

from polaris_modernization.stories.retrieval import build_story_packages, load_approved_business_features
from polaris_modernization.stories.workflow import UnsupportedStoryClaimsError, expected_story_id, prepare_story_generation, validate_and_persist_stories


REF = {"node_id": "kg:dashboard", "source_path": "src/Web/dashboard.js", "line_start": 1, "line_end": 2, "provenance": "STRUCTURAL_ONLY"}
CONF = {"level": "HIGH", "provenance": ["STRUCTURAL_ONLY"], "rationale": "fixture evidence"}
LOW = {"level": "LOW", "provenance": ["STRUCTURAL_ONLY"], "rationale": "No approved persona evidence."}


def approved_business_features(tmp_path):
    root = tmp_path / "business-feature-run"
    root.mkdir()
    feature = {
        "feature_id": "feature-dashboard", "feature_name": "Dashboard Insights", "short_business_summary": "Dashboard information",
        "business_capabilities": ["View insights"], "functional_module": "Dashboard", "feature_status": "APPROVED_ENRICHED", "confidence": CONF,
        "business_value": [{"text": "The Feature appears to support access to dashboard information.", "classification": "INFERRED_BUSINESS_VALUE", "evidence": [REF], "confidence": CONF}],
        "actors": [], "actor_evidence_limitation": "No actor is proven.",
        "workflows": [{"name": "Load dashboard", "business_trigger": "Navigation", "actor": None, "business_steps": ["Open"], "expected_outcome": "Dashboard available", "supporting_ui": ["DashboardView"], "api_status": "PROVEN", "evidence": [REF], "confidence": CONF}],
        "domain_concepts": [], "business_rules": [], "dependencies": [{"name": "Dashboard data", "dependency_type": "TECHNICAL", "description": "Existing contract", "evidence": [REF]}],
        "api_integration": {"proven": 1, "unresolved": 0, "dynamic": 0, "external": 0, "no_backend_route": 0, "relationships": [{"workflow": "Load dashboard", "status": "PROVEN"}], "paths": [{"workflow": "Load dashboard", "status": "PROVEN", "frontend_source": "src/Web/dashboard.js", "api_contract": "GET /api/dashboard", "backend_endpoint": "GET /api/dashboard"}], "business_readable_limitation": "None"},
        "open_questions": [{"question_id": "Q1", "question": "Which information is most important?", "reason": "Priority is not proven.", "evidence": [REF], "confidence": CONF}],
        "story_decomposition_guidance": [{"boundary": "View dashboard summary", "workflows": ["Load dashboard"], "rationale": "One coherent interaction."}],
        "source_evidence": [REF], "kg_evidence": ["kg:dashboard"], "evidence_package_id": "business-feature:feature-dashboard",
    }
    catalog = {"project_id": "fixture", "kg_run_id": "kg-run", "application_understanding_run_id": "au-run", "feature_run_id": "feature-run", "business_feature_run_id": root.name, "readiness": "BUSINESS_FEATURES_READY_WITH_LIMITATIONS", "business_features": [feature]}
    (root / "business-feature-catalog.json").write_text(json.dumps(catalog))
    package_map = {"business-feature:feature-dashboard": "hash"}
    manifest_hash = sha256(json.dumps(package_map, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    (root / "business-feature-evidence-manifest.json").write_text(json.dumps({"manifest_hash": manifest_hash, "hash_validation": "PASS", "packages": package_map}))
    (root / "business-feature-validation.json").write_text(json.dumps({"valid": True, "provenance_validation": "PASS", "business_feature_validation": "PASS", "business_quality_validation": "PASS"}))
    (root / "provenance.json").write_text(json.dumps({"kg_run_id": "kg-run", "application_understanding_run_id": "au-run", "feature_run_id": "feature-run", "business_feature_run_id": root.name}))
    (root / "token-usage.json").write_text(json.dumps({"external_llm_api_calls": 0}))
    (root / "poc-business-feature.md").write_text("# Dashboard Insights\n\n**Feature ID:** `feature-dashboard`\n")
    return root


def submission(root):
    approved = load_approved_business_features(root)
    package = build_story_packages(approved)[0]
    package_map = {package.package_id: package.package_hash}
    manifest_hash = sha256(json.dumps(package_map, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    title = "View Dashboard Summary"
    story = {
        "story_id": expected_story_id("feature-dashboard", title), "story_key_candidate": expected_story_id("feature-dashboard", title).upper().replace("-", "_"), "title": title,
        "parent_feature_id": "feature-dashboard", "parent_feature_name": "Dashboard Insights", "business_capability": "View insights",
        "story_statement": "As a user of the existing application, I want to view dashboard information, so that I can access the existing summary.",
        "actor": "user of the existing application", "actor_confidence": LOW, "business_goal": "View dashboard information",
        "business_value": package.business_value[0]["text"], "business_value_status": "INFERRED_BUSINESS_VALUE", "description": "Represents the approved dashboard workflow.",
        "workflow_refs": ["Load dashboard"], "workflow_boundary": package.boundary, "workflow_boundary_rationale": package.boundary_rationale,
        "ui_surface_refs": package.ui_surfaces, "domain_concept_refs": [], "business_rule_refs": ["NO_EVIDENCE_BACKED_BUSINESS_RULE"], "dependency_refs": ["Dashboard data"],
        "api_contract_refs": [item.model_dump(mode="json") for item in package.api_relationships], "api_mapping_status": ["PROVEN"],
        "source_evidence": [item.model_dump(mode="json") for item in package.source_evidence], "kg_evidence": ["kg:dashboard"], "application_understanding_evidence": [package.source_evidence[0].node_id],
        "feature_evidence": ["feature-dashboard"], "business_feature_evidence": ["business-feature:feature-dashboard"], "story_evidence_package_id": package.package_id,
        "confidence": CONF, "provenance": "AGENT_REASONING",
        "current_state_behavior": {"text": "The existing dashboard presents supported information.", "classification": "PROVEN", "evidence": [package.source_evidence[0].model_dump(mode="json")], "confidence": CONF},
        "modernization_relevance": {"text": "Preserve this behavior in the target frontend.", "classification": "MODERNIZATION_CONCERN", "evidence": [package.source_evidence[0].model_dump(mode="json")], "confidence": CONF},
        "in_scope": ["Approved dashboard workflow"], "out_of_scope": ["Backend redesign"], "assumptions": [], "open_questions": ["Q1"], "limitations": ["Actor is generic because no persona is approved."],
        "story_priority": "HIGH", "priority_rationale": "Approved POC behavior.", "poc_relevance": "Demonstrates an evidence-backed dashboard interaction.",
        "invest_assessment": {"independent_enough": True, "negotiable": True, "valuable": True, "estimable_conceptually": True, "small_and_coherent": True, "testable_in_principle": True, "issues": []},
        "story_points": "UNESTIMATED",
    }
    return {"kg_run_id": "kg-run", "application_understanding_run_id": "au-run", "feature_run_id": "feature-run", "business_feature_run_id": root.name, "evidence_package_manifest_hash": manifest_hash, "stories": [story], "poc_story_ids": [story["story_id"]]}


def write_payload(tmp_path, payload):
    path = tmp_path / "agent.json"
    path.write_text(json.dumps(payload))
    return path


def test_packages_are_stable_and_prepare_is_provider_free(tmp_path):
    root = approved_business_features(tmp_path)
    approved = load_approved_business_features(root)
    assert [item.package_hash for item in build_story_packages(approved)] == [item.package_hash for item in build_story_packages(approved)]
    prepared = prepare_story_generation(root, tmp_path / "out")
    assert json.loads((prepared["path"] / "preparation.json").read_text())["external_llm_api_calls"] == 0


def test_valid_story_persists_without_acceptance_criteria(tmp_path):
    root = approved_business_features(tmp_path)
    result = validate_and_persist_stories(root, tmp_path / "out", write_payload(tmp_path, submission(root)))
    assert result["quality"]["story_validation"] == "PASS"
    assert (tmp_path / "out/latest/story-catalog.json").is_file()
    assert "acceptance_criteria" not in json.loads((tmp_path / "out/latest/story-catalog.json").read_text())["stories"][0]


@pytest.mark.parametrize("mutation,match", [
    (lambda story: story.update(actor="Administrator"), "actor"),
    (lambda story: story.update(title="Migrate Dashboard Controller"), "stable ID|Technical-artifact"),
    (lambda story: story.update(api_mapping_status=["UNRESOLVED"]), "API mapping"),
    (lambda story: story.update(open_questions=[]), "open questions"),
])
def test_unsafe_story_claims_are_rejected(tmp_path, mutation, match):
    root = approved_business_features(tmp_path)
    payload = submission(root)
    mutation(payload["stories"][0])
    with pytest.raises(UnsupportedStoryClaimsError, match=match):
        validate_and_persist_stories(root, tmp_path / "out", write_payload(tmp_path, payload))


def test_reusable_story_engine_has_no_application_specific_conditions():
    code = (Path(__file__).parents[1] / "src/polaris_modernization/stories").read_text() if False else ""
    for path in (Path(__file__).parents[1] / "src/polaris_modernization/stories").glob("*.py"):
        code += path.read_text()
    assert "HealthClinic" not in code and "MyHealth" not in code
