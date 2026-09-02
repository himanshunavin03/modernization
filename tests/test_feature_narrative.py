import json
from pathlib import Path

from polaris_modernization.feature_specifications.narrative import synthesize_feature_narratives

SOURCE=Path("artifacts/feature-specifications/runs/legacy-dashboard-complete-application-demo-v1-2026-09-01-230757-788124")
KG=Path("artifacts/knowledge-graph/runs/legacy-dashboard-complete-application-demo-v1-2026-09-02-050627")
APP=Path("source/HealthClinic.biz")

def test_narrative_synthesis_groups_and_traces_all_contracts(tmp_path):
    result=synthesize_feature_narratives(SOURCE,tmp_path/"out",KG,APP);v=result["validation"]
    assert (v["features"],v["stories"],v["authoritative_acceptance_criteria"])==(5,12,14)
    assert v["untraceable_narrative_statements"]==0 and v["semantic_duplication_rate"]<=10
    assert v["minimum_score"]>=8
    assert v["final_feature_specification_readiness"]=="FINAL_FEATURE_SPECIFICATIONS_READY_WITH_LIMITATIONS"

def test_customer_documents_are_jira_ready_and_preserve_json(tmp_path):
    synthesize_feature_narratives(SOURCE,tmp_path/"out",KG,APP)
    feature_ids=[item["feature_id"] for item in json.loads((SOURCE/"feature-specification-index.json").read_text())["features"]]
    for source in (SOURCE/f"{feature_id}.json" for feature_id in feature_ids):
        assert source.read_bytes()==(tmp_path/"out/latest"/source.name).read_bytes()
    md=(tmp_path/"out/latest/feature-operational-dashboard-insights.md").read_text()
    assert "## 1. Feature Overview" in md and "## 2. Functional Requirements" in md and "## 5. API Requirements" in md
    assert "## 3. User Stories" in md and "## 4. Acceptance Criteria" in md
    assert "Definition of Done" in md and "Review and Approval" in md

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
    assert (coverage["totals"]["proven"],coverage["totals"]["dynamic"],coverage["totals"]["unresolved"],coverage["totals"]["external"])==(11,0,0,0)
    assert all(item["backend"]["http_method"]=="GET" for item in contracts if item["relationship"]["status"]=="PROVEN")
    assert all(not item["backend"]["http_method"] for item in contracts if item["relationship"]["status"]!="PROVEN")
    assert result["validation"]["untraceable_api_contract_fields"]==0
    assert coverage["totals"]["traceable_api_contract_fields"]>0
    assert artifact["baseline"]["backend_endpoint_facts"]==58 and artifact["baseline"]["frontend_api_call_facts"]==33


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


def test_feature_relative_api_classification_preserves_final_resolution(tmp_path):
    synthesize_feature_narratives(SOURCE,tmp_path/"out",KG,APP)
    root=tmp_path/"out/latest"
    matrix=json.loads((root/"feature-api-coverage-matrix.json").read_text())
    rows={item["feature_id"]:item for item in matrix["features"]}
    doctor=rows["feature-doctor-directory-management"]
    user=rows["feature-user-access-context"]
    assert doctor["counts"]["SUPPORTING_SHARED_API"]==1
    assert doctor["counts"]["PRIMARY_BUSINESS_API"]==2
    assert doctor["counts"]["UNRESOLVED_PRIMARY_INTERACTION"]==0
    assert doctor["counts"]["DYNAMIC_PRIMARY_INTERACTION"]==0
    assert user["counts"]["PRIMARY_BUSINESS_API"]==6
    candidates=[candidate for row in rows.values() for interaction in row["interactions"] for candidate in interaction["candidate_endpoints"]]
    assert candidates==[]


def test_customer_markdown_hides_internal_api_classification(tmp_path):
    synthesize_feature_narratives(SOURCE,tmp_path/"out",KG,APP)
    root=tmp_path/"out/latest"
    markdown="\n".join(path.read_text(encoding="utf-8") for path in root.glob("feature-*.md") if "index" not in path.name)
    assert "## 5. API Requirements" in markdown
    assert "PRIMARY_BUSINESS_API" not in markdown and "SUPPORTING_SHARED_API" not in markdown
    assert "source_reference" not in markdown and "src/MyHealth" not in markdown
    assert not any(term in markdown.lower() for term in ("angularjs", "razor", "proven", "mapping", "legacy", "modernization"))


def test_human_markdown_quality_and_lineage(tmp_path):
    result=synthesize_feature_narratives(SOURCE,tmp_path/"out",KG,APP)
    root=tmp_path/"out/latest"
    validation=result["validation"]
    assert validation["functional_requirements_generated"]==18
    assert validation["business_rules_generated"]==1
    assert validation["api_requirements_generated"]==17
    assert validation["clarifications_generated"]==17
    assert all(validation[key]==0 for key in (
        "polaris_terms_in_human_markdown", "kg_terms_in_human_markdown",
        "analyzer_terms_in_human_markdown", "resolver_classifications_in_human_markdown",
        "source_file_paths_in_human_markdown", "source_line_references_in_human_markdown",
        "evidence_jargon_in_human_markdown", "legacy_implementation_language_in_human_markdown",
        "semantically_circular_stories", "vague_human_ac", "generic_clarification_questions",
        "backend_task_wrappers_as_primary_response",
    ))
    dashboard=(root/"feature-operational-dashboard-insights.md").read_text(encoding="utf-8")
    for contract in (
        "GET /api/reports/expenses/{year}", "GET /api/reports/patients/{year}",
        "GET /api/reports/clinicsummary", "GET /api/users/current/tenant",
    ):
        assert contract in dashboard
    assert "Enable users to access the operational dashboard" in dashboard
    assert "Expense summary information is retrieved for the selected reporting year." in dashboard
    assert "Which expense fields and metrics must be displayed for the selected reporting year?" in dashboard
    assert "| Response | Expense summary information |" in dashboard
    assert "Task<" not in dashboard and "ValueTask<" not in dashboard
    human_markdown="\n".join(path.read_text(encoding="utf-8") for path in root.glob("feature-*.md") if "index" not in path.name)
    assert not any(phrase in human_markdown.lower() for phrase in (
        "flow has", "flow needs", "information remains available", "feature is ready for delivery",
        "feature is implemented", "which information must be considered mandatory", "resulting behavior",
        "access to the access", "claims is", "the the", "linked feature behavior", "information views",
    ))
    artifact=json.loads((root/"feature-narrative-model.json").read_text())
    presentations=[item["narrative_model"]["human_presentation"] for item in artifact["features"]]
    dashboard_model=next(item for item in presentations if item["feature"]["source_feature_id"]=="feature-operational-dashboard-insights")
    assert [item["title"] for item in dashboard_model["functional_requirements"]]==[
        "Access Operational Dashboard", "View Yearly Expense Information", "View Yearly Patient Information",
        "View Clinic Summary", "Establish Organization Context",
    ]
    assert all(item["source_story_ids"] and item["source_behavior_ids"] for model in presentations for item in model["functional_requirements"])
    assert all(item["source_story_id"] for model in presentations for item in model["stories"])
    assert all(item["source_ac_id"] and item["source_story_id"] for model in presentations for item in model["acceptance_criteria"])
    assert all(item["source_interaction_ids"] for model in presentations for item in model["api_requirements"])
    assert all(item["source_ids"] for model in presentations for item in model["clarifications"])
    user_model=next(item for item in presentations if item["feature"]["source_feature_id"]=="feature-user-access-context")
    assert {item["question"] for item in user_model["clarifications"]} >= {
        "Which application user fields must be displayed in the detail view?",
        "Which application user fields must be displayed in the directory?",
    }
    clinic=(root/"feature-clinic-appointment-experience.md").read_text(encoding="utf-8")
    assert "Enable users to view clinic details and review the clinic directory within the applicable organization context." in clinic
    assert "Appointment creation/update behavior" in clinic
    assert "appointment creation" not in clinic.lower().replace("appointment creation/update behavior", "")
