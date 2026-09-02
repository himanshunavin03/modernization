import json
from pathlib import Path

from polaris_modernization.feature_specifications.narrative import synthesize_feature_narratives


SOURCE = Path("artifacts/feature-specifications/runs/legacy-dashboard-complete-application-demo-v1-2026-09-01-230757-788124")
KG = Path("artifacts/knowledge-graph/runs/legacy-dashboard-complete-application-demo-v1-2026-09-02-050627")
APP = Path("source/HealthClinic.biz")


def _generate(tmp_path: Path) -> tuple[dict, list[dict]]:
    result = synthesize_feature_narratives(SOURCE, tmp_path / "out", KG, APP)
    artifact = json.loads((tmp_path / "out/latest/jira-quality.json").read_text(encoding="utf-8"))
    return result, artifact["features"]


def test_jira_delivery_preserves_frozen_counts_and_traceability(tmp_path):
    result, features = _generate(tmp_path)
    stories = [story for feature in features for story in feature["stories"]]
    criteria = [criterion for story in stories for criterion in story["acceptance_criteria"]]
    assert (len(features), len(stories), len(criteria)) == (5, 12, 14)
    assert result["validation"]["jira_story_models"] == 12
    assert all(story["traceability"]["authoritative_story_ref"] for story in stories)
    assert all(criterion["authoritative_ac_ref"] for criterion in criteria)
    assert all(api["traceability"]["source_interaction_ids"] for story in stories for api in story["api_dependencies"])


def test_quality_gates_are_explainable_and_ac_are_testable(tmp_path):
    result, features = _generate(tmp_path)
    validation = result["validation"]
    stories = [story for feature in features for story in feature["stories"]]
    criteria = [criterion for story in stories for criterion in story["acceptance_criteria"]]
    assert validation["invest_validated_stories"] == 12
    assert validation["invest_pass"] + validation["invest_warning"] + validation["invest_needs_review"] == 12
    assert validation["ready_stories"] + validation["needs_clarification_stories"] == 12
    assert validation["blocked_stories"] == 0
    assert (validation["ac_total"], validation["ac_testability_pass"]) == (14, 14)
    assert validation["ac_testability_warning"] == validation["ac_needs_clarification"] == 0
    assert validation["circular_human_ac"] == validation["vague_human_ac"] == 0
    assert all(set(item["quality"]["checks"]) == {"precondition_present", "trigger_present", "observable_result_present", "vague_result", "circular_result"} for item in criteria)


def test_dashboard_split_recommendation_does_not_mutate_story_catalog(tmp_path):
    _, features = _generate(tmp_path)
    dashboard = next(feature for feature in features if feature["feature_id"] == "feature-operational-dashboard-insights")
    assert len(dashboard["stories"]) == 3
    yearly = next(story for story in dashboard["stories"] if story["summary"] == "Access Yearly Operational Reports")
    recommendation = yearly["quality"]["split_recommendation"]
    assert recommendation["status"] == "SPLIT_RECOMMENDATION"
    assert recommendation["suggested_summaries"] == ["View Yearly Expense Information", "View Yearly Patient Information"]
    dependencies = {(api["method"], api["endpoint"]) for api in yearly["api_dependencies"]}
    assert {
        ("GET", "/api/reports/expenses/{year}"),
        ("GET", "/api/reports/patients/{year}"),
    } <= dependencies
    assert yearly["readiness"]["status"] == "NEEDS_CLARIFICATION"
    assert len(yearly["acceptance_criteria"]) == 1


def test_human_story_packages_are_clean_and_clinic_safe(tmp_path):
    _, features = _generate(tmp_path)
    root = tmp_path / "out/latest"
    markdown = "\n".join((root / f"{feature['feature_id']}.md").read_text(encoding="utf-8") for feature in features)
    assert "#### Story Readiness" in markdown
    assert "#### Functional Requirements" in markdown
    assert "#### Acceptance Criteria" in markdown
    assert "INVEST" not in markdown
    clinic = (root / "feature-clinic-appointment-experience.md").read_text(encoding="utf-8").lower()
    for unsupported in ("create appointment", "update appointment", "cancel appointment", "reschedule appointment"):
        assert unsupported not in clinic
