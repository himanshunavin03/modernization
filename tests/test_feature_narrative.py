import json
from pathlib import Path

from polaris_modernization.feature_specifications.narrative import synthesize_feature_narratives

SOURCE=Path("artifacts/feature-specifications/runs/legacy-dashboard-complete-application-demo-v1-2026-09-01-121948-351008")
KG=Path("artifacts/knowledge-graph/runs/legacy-dashboard-complete-application-demo-v1-2026-09-01-034128")
APP=Path("source/HealthClinic.biz")

def test_narrative_synthesis_groups_and_traces_all_contracts(tmp_path):
    result=synthesize_feature_narratives(SOURCE,tmp_path/"out",KG,APP);v=result["validation"]
    assert (v["features"],v["stories"],v["authoritative_acceptance_criteria"])==(5,12,14)
    assert v["untraceable_narrative_statements"]==0 and v["semantic_duplication_rate"]<=10
    assert v["minimum_score"]>=9

def test_customer_documents_use_eight_sections_and_preserve_json(tmp_path):
    synthesize_feature_narratives(SOURCE,tmp_path/"out",KG,APP)
    feature_ids=[item["feature_id"] for item in json.loads((SOURCE/"feature-specification-index.json").read_text())["features"]]
    for source in (SOURCE/f"{feature_id}.json" for feature_id in feature_ids):
        assert source.read_bytes()==(tmp_path/"out/latest"/source.name).read_bytes()
    md=(tmp_path/"out/latest/feature-operational-dashboard-insights.md").read_text()
    assert "## 1. Feature Summary" in md and "## 5. Existing Backend Integration" in md and "## 8. Review & Approval" in md
    assert "Trigger:" not in md and "Interaction:" not in md and "Outcome:" not in md

def test_narrative_artifacts_cover_comprehension_and_traceability(tmp_path):
    synthesize_feature_narratives(SOURCE,tmp_path/"out",KG,APP)
    root=tmp_path/"out/latest"
    assert len(json.loads((root/"feature-narrative-model.json").read_text())["features"])==5
    assert json.loads((root/"feature-narrative-validation.json").read_text())["customer_comprehension_review"]=="PASS"


def test_api_contracts_are_evidence_backed_and_preserve_status(tmp_path):
    result=synthesize_feature_narratives(SOURCE,tmp_path/"out",KG,APP)
    root=tmp_path/"out/latest"
    artifact=json.loads((root/"feature-api-contracts.json").read_text())
    coverage=json.loads((root/"feature-api-contract-coverage.json").read_text())
    contracts=[item for feature in artifact["features"] for item in feature["contracts"]]
    assert coverage["totals"]["feature_relevant_api_contracts"]==11
    assert (coverage["totals"]["proven"],coverage["totals"]["dynamic"],coverage["totals"]["unresolved"],coverage["totals"]["external"])==(8,2,1,0)
    assert all(item["backend"]["http_method"]=="GET" for item in contracts if item["relationship"]["status"]=="PROVEN")
    assert all(not item["backend"]["http_method"] for item in contracts if item["relationship"]["status"]!="PROVEN")
    assert result["validation"]["untraceable_api_contract_fields"]==0
    assert coverage["totals"]["traceable_api_contract_fields"]>0
    assert artifact["baseline"]["backend_endpoint_facts"]==58 and artifact["baseline"]["frontend_api_call_facts"]==44


def test_language_gate_rejects_previous_defect_patterns(tmp_path):
    synthesize_feature_narratives(SOURCE,tmp_path/"out",KG,APP)
    root=tmp_path/"out/latest"
    markdown="\n".join(path.read_text(encoding="utf-8") for path in root.glob("feature-*.md") if "index" not in path.name)
    validation=json.loads((root/"feature-narrative-validation.json").read_text())
    assert "I can use access" not in markdown
    assert "I want access" not in markdown
    assert "experience is available. A" not in markdown
    assert validation["broken_verb_constructions"]==0
    assert validation["concatenated_outcome_fragments"]==0
    assert validation["story_coherence_defects"]==0 and validation["ac_coherence_defects"]==0


def test_machine_contracts_and_provenance_remain_exact(tmp_path):
    result=synthesize_feature_narratives(SOURCE,tmp_path/"out",KG,APP)
    root=tmp_path/"out/latest"
    feature_ids=[item["feature_id"] for item in json.loads((SOURCE/"feature-specification-index.json").read_text())["features"]]
    for source in (SOURCE/f"{feature_id}.json" for feature_id in feature_ids):
        assert source.read_bytes()==(root/source.name).read_bytes()
    provenance=json.loads((root/"provenance.json").read_text())
    assert provenance["kg_run_id"]==KG.name
    assert provenance["source_feature_narrative_run_id"]==SOURCE.name
    assert provenance["modernization_feature_specification_run_id"]==result["run_id"]


def test_feature_relative_api_classification_and_candidates(tmp_path):
    synthesize_feature_narratives(SOURCE,tmp_path/"out",KG,APP)
    root=tmp_path/"out/latest"
    matrix=json.loads((root/"feature-api-coverage-matrix.json").read_text())
    rows={item["feature_id"]:item for item in matrix["features"]}
    doctor=rows["feature-doctor-directory-management"]
    user=rows["feature-user-access-context"]
    assert doctor["counts"]["SUPPORTING_SHARED_API"]==1
    assert doctor["counts"]["UNRESOLVED_PRIMARY_INTERACTION"]>=1
    assert doctor["counts"]["DYNAMIC_PRIMARY_INTERACTION"]>=1
    assert user["counts"]["PRIMARY_BUSINESS_API"]>=1
    candidates=[candidate for row in rows.values() for interaction in row["interactions"] for candidate in interaction["candidate_endpoints"]]
    assert candidates and all(item["promotion_status"]=="NOT_PROVEN_NO_FRONTEND_MAPPING" for item in candidates)


def test_customer_markdown_separates_primary_supporting_and_unresolved(tmp_path):
    synthesize_feature_narratives(SOURCE,tmp_path/"out",KG,APP)
    root=tmp_path/"out/latest"
    doctor=(root/"feature-doctor-directory-management.md").read_text(encoding="utf-8")
    user=(root/"feature-user-access-context.md").read_text(encoding="utf-8")
    assert "### Supporting / Shared APIs" in doctor
    assert "does not provide the Feature's primary business data" in doctor
    assert "### Unresolved or Dynamic Integrations" in doctor
    assert "Candidate Existing Backend Contract" in doctor
    assert "### Primary Business APIs" in user
