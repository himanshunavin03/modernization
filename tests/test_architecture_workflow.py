import json
from pathlib import Path

import pytest

from polaris_modernization.architecture.models import FigmaDesignProvider
from polaris_modernization.architecture.workflow import (
    ArchitectureWorkflowError,
    NODES,
    _validate_requirements,
    build_architecture_graph,
    recommend_architecture,
    validate_architecture,
)


SPECIFICATIONS = Path("artifacts/feature-specifications/latest")
FEATURE = "feature-operational-dashboard-insights"


def test_real_langgraph_contains_expected_nodes_and_transitions():
    graph = build_architecture_graph()
    assert set(NODES) <= set(graph.get_graph().nodes)
    assert len(NODES) == 7


def test_dashboard_workflow_consumes_jira_models_and_preserves_apis(tmp_path):
    result = recommend_architecture("poc", FEATURE, SPECIFICATIONS, tmp_path / "architecture")
    state = result["state"]
    assert state["nodes_executed"] == NODES
    assert len(state["state_transitions"]) == 7
    assert state["status"] == "READY_FOR_TASKS"
    assert (len(state["requirements"]), len(state["stories"]), len(state["acceptance_criteria"])) == (5, 3, 5)
    assert {(api["method"], api["endpoint"]) for api in state["api_contracts"]} == {
        ("GET", "/api/reports/expenses/{year}"),
        ("GET", "/api/reports/patients/{year}"),
        ("GET", "/api/reports/clinicsummary"),
        ("GET", "/api/users/current/tenant"),
    }
    assert state["architecture_validation"]["status"] == "ARCHITECTURE_READY_WITH_LIMITATIONS"


def test_no_design_and_unimplemented_figma_paths_both_continue(tmp_path):
    no_design = recommend_architecture("poc", FEATURE, SPECIFICATIONS, tmp_path / "none")
    figma = recommend_architecture("poc", FEATURE, SPECIFICATIONS, tmp_path / "figma", "FIGMA", "https://figma.example/design/123")
    assert no_design["state"]["design_specification"]["status"] == "NOT_PROVIDED"
    assert figma["state"]["design_specification"]["status"] == "FIGMA_CONNECTOR_NOT_IMPLEMENTED"
    assert no_design["state"]["status"] == figma["state"]["status"] == "READY_FOR_TASKS"
    assert FigmaDesignProvider().can_handle("figma")


def test_architecture_uses_offline_structured_decisions_and_traceability(tmp_path):
    result = recommend_architecture("poc", FEATURE, SPECIFICATIONS, tmp_path / "architecture")
    recommendation = result["state"]["architecture_recommendation"]
    decisions = {item["technology"]: item for item in recommendation["decisions"]}
    assert (recommendation["target_framework"], recommendation["framework_version"]) == ("Angular", "22")
    assert decisions["Signals"]["status"] == decisions["RxJS"]["status"] == "USE"
    assert decisions["Backend for Frontend"]["status"] == "DO_NOT_USE"
    assert decisions["NgRx"]["status"] == "DO_NOT_USE"
    assert all(item["rationale"] and item["requirement_refs"] and item["story_refs"] for item in decisions.values())
    assert result["workflow"]["langgraph_execution"] is True
    assert result["workflow"]["langchain_runnable_execution"] is True
    assert result["workflow"]["external_llm_calls"] == 0


def test_unknown_feature_and_missing_specification_fail_explicitly(tmp_path):
    with pytest.raises(ArchitectureWorkflowError, match="Unknown Feature"):
        recommend_architecture("poc", "feature-does-not-exist", SPECIFICATIONS, tmp_path / "unknown")
    with pytest.raises(ArchitectureWorkflowError, match="missing"):
        recommend_architecture("poc", FEATURE, tmp_path / "missing", tmp_path / "output")


def test_missing_api_information_is_a_requirement_blocker():
    story = {"readiness": {"status": "READY"}, "traceability": {"api_interaction_refs": ["source-api"]}}
    state = _validate_requirements({"requirements": [{"id": "FR-01"}], "stories": [story], "acceptance_criteria": [{"id": "AC-01"}], "api_contracts": [], "warnings": [], "blockers": [], "current_stage": "load_design_context"})
    assert state["status"] == "BLOCKED"
    assert "API-backed requirements" in state["blockers"][0]


def test_architecture_validator_rejects_contradictory_decisions(tmp_path):
    result = recommend_architecture("poc", FEATURE, SPECIFICATIONS, tmp_path / "architecture")
    state = result["state"]
    duplicate = dict(state["architecture_recommendation"]["decisions"][0])
    duplicate["status"] = "DO_NOT_USE"
    state["architecture_recommendation"]["decisions"].append(duplicate)
    validation = validate_architecture(state)
    assert validation.status == "ARCHITECTURE_BLOCKED"
    assert validation.checks["contradictory_decisions_absent"] is False


def test_architecture_artifacts_and_adrs_are_concise_and_complete(tmp_path):
    result = recommend_architecture("poc", FEATURE, SPECIFICATIONS, tmp_path / "architecture")
    latest = tmp_path / "architecture/latest"
    assert (latest / "architecture.md").is_file()
    assert (latest / "architecture.json").is_file()
    assert (latest / "workflow-run.json").is_file()
    assert len(list((latest / "adrs").glob("ADR-*.md"))) == 6
    workflow = json.loads((latest / "workflow-run.json").read_text(encoding="utf-8"))
    assert workflow["final_status"] == "READY_FOR_TASKS"
