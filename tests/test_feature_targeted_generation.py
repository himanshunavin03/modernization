import json
from pathlib import Path

import pytest

from polaris_modernization.feature_targeted_generation import (
    FeatureLineageError,
    generate_targeted_acceptance_criteria,
    generate_targeted_stories,
    resolve_approved_feature,
)


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def approved_context(tmp_path: Path) -> tuple[Path, dict]:
    root = tmp_path / "repository"
    feature = {"feature_id": "feature-alpha", "slug": "alpha", "name": "Alpha Directory", "spec_path": "artifacts/feature-specifications/latest/feature-alpha.json"}
    contract = {
        "feature_id": "feature-alpha", "status": "FEATURE_SCOPE_READY",
        "functional_requirements": [
            {"id": "FR-01", "title": "Review Alpha Directory", "description": "Users can review alpha records.", "source_capability_ids": ["cap-list"], "interaction_semantics": [{"interaction_type": "ACTION", "label": "Show records", "observable_result": "the record collection is displayed"}]},
            {"id": "FR-02", "title": "Create Alpha", "description": "Users can create an alpha record.", "source_capability_ids": ["cap-create"], "interaction_semantics": [{"interaction_type": "ACTION", "label": "Add record", "observable_result": "the new record is displayed"}]},
        ],
        "capability_api_contracts": [
            {"contract_id": "API-01", "method": "GET", "route": "/api/alphas", "requirement_ids": ["FR-01"]},
            {"contract_id": "API-02", "method": "POST", "route": "/api/alphas", "requirement_ids": ["FR-02"]},
        ],
        "capability_dispositions": [
            {"capability_id": "cap-list", "scope_status": "INCLUDED", "downstream_refs": ["FR-01"]},
            {"capability_id": "cap-create", "scope_status": "INCLUDED", "downstream_refs": ["FR-02"]},
        ],
    }
    latest = root / "artifacts/feature-specifications/latest/feature-alpha.json"
    write_json(latest, contract)
    scope = root / "artifacts/feature-specifications/runs/capability-scope-fixture"
    write_json(scope / "feature-alpha.json", contract)
    write_json(root / "artifacts/feature-specifications/latest/capability-coverage.json", {
        "capabilities": [
            {"capability_id": "cap-list", "qualifiers": ["FIXED_ORDER"]},
            {"capability_id": "cap-create", "qualifiers": ["TENANT_SCOPED"]},
        ],
    })
    write_json(root / "artifacts/knowledge-graph/latest/review-metadata.json", {"run_id": "kg-final", "validation": {"valid": True}})
    return root, feature


def test_targeted_generation_uses_current_feature_contract_and_preserves_global_artifacts(tmp_path: Path) -> None:
    root, feature = approved_context(tmp_path)
    global_story = root / "artifacts/stories/latest/story-catalog.json"
    write_json(global_story, {"global": "unchanged"})
    context = resolve_approved_feature(root, feature)

    stories = generate_targeted_stories(context, root / "artifacts/stories")
    criteria = generate_targeted_acceptance_criteria(context, stories["path"], root / "artifacts/acceptance-criteria")

    assert stories["validation"]["fr_without_story_coverage"] == []
    assert {item["functional_requirement_ids"][0] for item in stories["stories"]} == {"FR-01", "FR-02"}
    assert "fixed ordering" in stories["stories"][0]["business_outcome"]
    assert stories["lineage"]["feature_run"] == "capability-scope-fixture"
    assert stories["lineage"]["canonical_upstream_kg_run"] == "kg-final"
    assert criteria["validation"]["stories_without_ac"] == []
    assert criteria["lineage"]["story_run"] == stories["run_id"]
    assert json.loads(global_story.read_text(encoding="utf-8")) == {"global": "unchanged"}
    status = json.loads((criteria["path"] / "downstream-status.json").read_text(encoding="utf-8"))
    assert status == {"stories": "CURRENT", "acceptance_criteria": "CURRENT", "technical_tasks": "STALE_REGENERATION_REQUIRED", "angular": "STALE_REGENERATION_REQUIRED", "playwright": "STALE_REGENERATION_REQUIRED"}


def test_stale_or_unarchived_feature_contract_cannot_fall_back_to_global_business_features(tmp_path: Path) -> None:
    root, feature = approved_context(tmp_path)
    (root / "artifacts/feature-specifications/runs/capability-scope-fixture/feature-alpha.json").unlink()
    write_json(root / "artifacts/business-features/latest/business-feature-catalog.json", {"stale": True})

    with pytest.raises(FeatureLineageError, match="matching immutable scope-refresh run"):
        resolve_approved_feature(root, feature)


def test_targeted_acceptance_criteria_are_observable_and_not_title_restatements(tmp_path: Path) -> None:
    root, feature = approved_context(tmp_path)
    contract_path = root / feature["spec_path"]
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    contract["functional_requirements"][0]["interaction_semantics"] = [{"interaction_type": "ACTION", "label": "Fetch next records", "observable_result": "additional records are displayed"}]
    write_json(contract_path, contract)
    write_json(root / "artifacts/feature-specifications/runs/capability-scope-fixture/feature-alpha.json", contract)
    context = resolve_approved_feature(root, feature)
    stories = generate_targeted_stories(context, root / "artifacts/stories")
    criteria = generate_targeted_acceptance_criteria(context, stories["path"], root / "artifacts/acceptance-criteria")
    first = criteria["criteria"][0]
    assert first["when"] == 'the user selects "Fetch next records"'
    assert first["then"] == "additional records are displayed"
    assert criteria["validation"]["tautological_ac"] == []
    assert criteria["validation"]["non_observable_outcome"] == []
