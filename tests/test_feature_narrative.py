import json
from pathlib import Path

from polaris_modernization.feature_specifications.narrative import synthesize_feature_narratives

SOURCE=Path("artifacts/feature-specifications/runs/legacy-dashboard-complete-application-demo-v1-2026-09-01-114638-016471")

def test_narrative_synthesis_groups_and_traces_all_contracts(tmp_path):
    result=synthesize_feature_narratives(SOURCE,tmp_path/"out");v=result["validation"]
    assert (v["features"],v["stories"],v["authoritative_acceptance_criteria"])==(5,12,14)
    assert v["untraceable_narrative_statements"]==0 and v["semantic_duplication_rate"]<=10
    assert v["minimum_score"]>=9

def test_customer_documents_use_eight_sections_and_preserve_json(tmp_path):
    synthesize_feature_narratives(SOURCE,tmp_path/"out")
    for source in SOURCE.glob("feature-*.json"):
        if source.name.startswith("feature-specification-"): continue
        assert source.read_bytes()==(tmp_path/"out/latest"/source.name).read_bytes()
    md=(tmp_path/"out/latest/feature-operational-dashboard-insights.md").read_text()
    assert "## 1. Feature Summary" in md and "## 8. Review & Approval" in md
    assert "Trigger:" not in md and "Interaction:" not in md and "Outcome:" not in md

def test_narrative_artifacts_cover_comprehension_and_traceability(tmp_path):
    synthesize_feature_narratives(SOURCE,tmp_path/"out")
    root=tmp_path/"out/latest"
    assert len(json.loads((root/"feature-narrative-model.json").read_text())["features"])==5
    assert json.loads((root/"feature-narrative-validation.json").read_text())["customer_comprehension_review"]=="PASS"
