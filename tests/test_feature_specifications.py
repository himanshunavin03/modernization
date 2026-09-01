import json
from pathlib import Path

from polaris_modernization.feature_specifications.workflow import generate_feature_specifications


BUSINESS = Path("artifacts/business-features/runs/legacy-dashboard-complete-application-demo-v1-2026-09-01-145336-704667")
STORIES = Path("artifacts/stories/runs/legacy-dashboard-complete-application-demo-v1-2026-09-01-105453-078418")
AC = Path("artifacts/acceptance-criteria/runs/legacy-dashboard-complete-application-demo-v1-2026-09-01-112024-635713")


def test_generates_five_paired_specs_with_complete_parent_coverage(tmp_path):
    result = generate_feature_specifications(BUSINESS, STORIES, AC, tmp_path / "specs")
    assert len(result["specifications"]) == 5
    assert len(list((tmp_path / "specs/latest").glob("feature-*.md"))) == 6  # Five Features plus index.
    feature_json = [x for x in (tmp_path / "specs/latest").glob("feature-*.json") if x.name not in {"feature-specification-index.json", "feature-specification-validation.json", "feature-specification-quality-review.json"}]
    assert len(feature_json) == 5
    assert result["validation"]["stories_represented"] == 12
    assert result["validation"]["acceptance_criteria_represented"] == 14


def test_markdown_json_parity_and_safety(tmp_path):
    result = generate_feature_specifications(BUSINESS, STORIES, AC, tmp_path / "specs")
    for spec in result["specifications"]:
        markdown = (tmp_path / "specs/latest" / f"{spec['feature_id']}.md").read_text()
        stored = json.loads((tmp_path / "specs/latest" / f"{spec['feature_id']}.json").read_text())
        assert stored["feature_id"] in markdown and stored["feature_name"] in markdown
        assert all(x["story_id"] in markdown for x in stored["stories"])
        assert all(x["acceptance_criterion_id"] in markdown for x in stored["acceptance_criteria"])
        assert stored["target_design"]["url"] is None
        assert not any(term.lower() in markdown.lower() for term in ("Roslyn", "Tree-sitter", "package hash", "parser warning", "KG diagnostic", "opaque dependency"))


def test_no_invention_and_poc_completeness(tmp_path):
    result = generate_feature_specifications(BUSINESS, STORIES, AC, tmp_path / "specs")
    poc = next(x for x in result["specifications"] if x["feature_id"] == "feature-operational-dashboard-insights")
    assert len(poc["stories"]) == 3
    assert len([x for x in poc["stories"] if x["story_id"] in {"story-operational-dashboard-insights-open-operational-dashboard", "story-operational-dashboard-insights-view-tenant-aware-dashboard-summary"}]) == 2
    assert len([x for x in poc["acceptance_criteria"] if x["story_id"] in {"story-operational-dashboard-insights-open-operational-dashboard", "story-operational-dashboard-insights-view-tenant-aware-dashboard-summary"}]) == 4
    assert all(x["security_context"].startswith("Feature-specific access") for x in result["specifications"])
