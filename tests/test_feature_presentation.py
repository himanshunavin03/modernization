import json
from pathlib import Path

from polaris_modernization.feature_specifications.presentation import refine_feature_presentations


SOURCE = Path("artifacts/feature-specifications/runs/legacy-dashboard-complete-application-demo-v1-2026-09-01-114638-016471")


def test_refinement_preserves_machine_contract_and_complete_mapping(tmp_path):
    result = refine_feature_presentations(SOURCE, tmp_path / "out")
    assert result["validation"]["features"] == 5
    assert result["validation"]["stories"] == 12
    assert result["validation"]["acceptance_criteria"] == 14
    assert result["validation"]["story_semantic_equivalence"] == "PASS"
    for source_json in SOURCE.glob("feature-*.json"):
        if source_json.name in {"feature-specification-index.json", "feature-specification-validation.json", "feature-specification-quality-review.json"}: continue
        assert source_json.read_bytes() == (tmp_path / "out/latest" / source_json.name).read_bytes()


def test_professional_markdown_filter_and_quality(tmp_path):
    result = refine_feature_presentations(SOURCE, tmp_path / "out")
    assert result["validation"]["minimum_score"] >= 9
    assert result["validation"]["internal_diagnostic_noise"] == 0
    assert result["validation"]["rendering_defects"] == 0
    dashboard = (tmp_path / "out/latest/feature-operational-dashboard-insights.md").read_text()
    assert "As an application user," in dashboard
    assert "## Stakeholder Summary" in dashboard
    assert "Target Architecture is pending" in dashboard
    assert ".;" not in dashboard
    assert "approved current-state context" not in dashboard.lower()


def test_mapping_is_semantically_auditable(tmp_path):
    refine_feature_presentations(SOURCE, tmp_path / "out")
    mapping = json.loads((tmp_path / "out/latest/feature-presentation-mapping.json").read_text())["mappings"]
    assert len([x for x in mapping if x["source_type"] == "STORY"]) == 12
    assert len([x for x in mapping if x["source_type"] == "ACCEPTANCE_CRITERION"]) == 14
    assert all(x["semantic_equivalence_status"] == "SEMANTICALLY_EQUIVALENT" for x in mapping)
