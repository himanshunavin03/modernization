import json
from hashlib import sha256
from pathlib import Path

import pytest

from polaris_modernization.architecture.catalog import load_architecture_catalog
from polaris_modernization.architecture.models import DecisionStatus, FigmaDesignProvider
from polaris_modernization.architecture.renderers import render_architecture_html
from polaris_modernization.architecture.workflow import (
    ArchitectureWorkflowError, NODES, _validate_requirements,
    build_architecture_graph, recommend_architecture, validate_architecture,
)


SPECIFICATIONS = Path("artifacts/feature-specifications/latest")
FEATURE = "feature-operational-dashboard-insights"
APIS = {
    ("GET", "/api/reports/expenses/{year}"),
    ("GET", "/api/reports/patients/{year}"),
    ("GET", "/api/reports/clinicsummary"),
    ("GET", "/api/users/current/tenant"),
}


def _run(tmp_path: Path) -> dict:
    return recommend_architecture("poc", FEATURE, SPECIFICATIONS, tmp_path / "architecture")


def _decisions(result: dict) -> dict[str, dict]:
    return {item["technology"]: item for item in result["state"]["architecture_selection"]["decisions"]}


def test_catalog_loads_with_controlled_statuses_and_enterprise_coverage():
    catalog = load_architecture_catalog()
    assert len(catalog) >= 45
    assert all(item.status in DecisionStatus for item in catalog)
    categories = {item.category for item in catalog}
    assert {"Frontend Platform", "Workspace", "Reactivity", "Forms", "State Management", "Rendering", "API Gateway", "Backend for Frontend", "Security", "Testing"} <= categories


def test_real_langgraph_executes_catalog_recommendation_selection_and_lock(tmp_path):
    graph = build_architecture_graph()
    assert set(NODES) <= set(graph.get_graph().nodes)
    result = _run(tmp_path)
    state = result["state"]
    assert state["nodes_executed"] == NODES
    assert len(state["state_transitions"]) == len(NODES) == 9
    assert state["architecture_lock"]["status"] == "LOCKED"
    assert state["architecture_lock"]["locked_after_validation"] is True
    encoded = json.dumps(state["architecture_selection"], sort_keys=True, separators=(",", ":")).encode("utf-8")
    assert state["architecture_lock"]["selection_hash"] == sha256(encoded).hexdigest()
    assert result["workflow"]["langgraph_execution"] is True
    assert result["workflow"]["langchain_runnable_execution"] is True
    assert result["workflow"]["external_llm_calls"] == 0


def test_recommendation_and_selected_downstream_contract_are_distinct(tmp_path):
    result = _run(tmp_path)
    state = result["state"]
    assert state["architecture_recommendation"] is not state["architecture_selection"]
    assert state["architecture_selection"]["selection_source"] == "POLARIS_POC_DEFAULT"
    assert state["architecture_selection"]["downstream_source_of_truth"] is True
    assert state["architecture_selection"]["recommendation_ref"] == "architecture-recommendation.json"
    assert state["architecture_selection"]["selected_decision_ids"]
    assert state["architecture_selection"]["recommended_decision_ids"]
    assert not set(state["architecture_selection"]["selected_decision_ids"]) & set(state["architecture_selection"]["recommended_decision_ids"])
    assert state["architecture_selection"]["alternative_decision_ids"]


def test_selected_angular_target_and_alternatives_are_deliberate(tmp_path):
    decisions = _decisions(_run(tmp_path))
    for technology in ("Angular 22", "TypeScript", "Nx Monorepo", "Standalone Components", "Angular Signals", "Computed Signals", "RxJS", "Signals and RxJS Interoperability", "Zoneless Angular", "Angular Router", "Lazy Feature Routes", "Client-Side Rendering", "Typed Angular HttpClient", "Provider-Neutral API Gateway", "Backend for Frontend", "Playwright"):
        assert decisions[technology]["status"] == "SELECTED"
    assert decisions["Signal Forms"]["status"] == "RECOMMENDED"
    assert decisions["Reactive Forms"]["status"] == "EVALUATED_ALTERNATIVE"
    assert decisions["Server-Side Rendering"]["status"] == "EVALUATED_ALTERNATIVE"
    assert decisions["Hydration"]["status"] == "EVALUATED_ALTERNATIVE"
    assert decisions["NgRx"]["status"] == "NOT_SELECTED"
    assert decisions["Microfrontends"]["status"] == "NOT_SELECTED"
    assert decisions["Module Federation"]["status"] == "NOT_SELECTED"
    assert decisions["Authentication Provider"]["status"] == "REQUIRES_CLARIFICATION"


def test_gateway_and_bff_preserve_existing_business_contracts_without_invention(tmp_path):
    result = _run(tmp_path)
    selection = result["state"]["architecture_selection"]
    assert {(api["method"], api["endpoint"]) for api in selection["existing_api_contracts"]} == APIS
    assert selection["target_integration_topology"] == ["Browser", "Angular 22", "Provider-Neutral API Gateway", "Backend for Frontend", "Existing Business APIs"]
    bff = _decisions(result)["Backend for Frontend"]
    assert "endpoints are designed" not in bff["decision"]
    assert bff["api_refs"] == ["API-01", "API-02", "API-03", "API-04"]
    assert result["state"]["architecture_validation"]["checks"]["existing_api_contracts_preserved"] is True
    assert result["state"]["architecture_validation"]["checks"]["bff_does_not_invent_business_behavior"] is True


def test_dashboard_context_and_machine_traceability_remain_compact(tmp_path):
    result = _run(tmp_path)
    state = result["state"]
    assert (len(state["requirements"]), len(state["stories"]), len(state["acceptance_criteria"]), len(state["api_contracts"])) == (5, 3, 5, 4)
    assert {(api["method"], api["endpoint"]) for api in state["api_contracts"]} == APIS
    assert all(item["requirement_refs"] and item["feature_refs"] and item["story_refs"] and item["api_refs"] for item in state["architecture_selection"]["decisions"] if item["status"] == "SELECTED")


def test_no_design_and_unimplemented_figma_paths_continue(tmp_path):
    no_design = _run(tmp_path)
    figma = recommend_architecture("poc", FEATURE, SPECIFICATIONS, tmp_path / "figma", "FIGMA", "https://figma.example/design/123")
    assert no_design["state"]["design_specification"]["status"] == "NOT_PROVIDED"
    assert figma["state"]["design_specification"]["status"] == "FIGMA_CONNECTOR_NOT_IMPLEMENTED"
    assert no_design["state"]["status"] == figma["state"]["status"] == "READY_FOR_TASKS"
    assert FigmaDesignProvider().can_handle("figma")


def test_validator_rejects_contradictory_selected_architecture(tmp_path):
    state = _run(tmp_path)["state"]
    duplicate = dict(state["architecture_selection"]["decisions"][0])
    duplicate["status"] = "NOT_SELECTED"
    state["architecture_selection"]["decisions"].append(duplicate)
    validation = validate_architecture(state)
    assert validation.status == "ARCHITECTURE_BLOCKED"
    assert validation.checks["no_contradictory_selections"] is False


def test_unknown_feature_missing_specification_and_api_gap_fail_explicitly(tmp_path):
    with pytest.raises(ArchitectureWorkflowError, match="Unknown Feature"):
        recommend_architecture("poc", "feature-does-not-exist", SPECIFICATIONS, tmp_path / "unknown")
    with pytest.raises(ArchitectureWorkflowError, match="missing"):
        recommend_architecture("poc", FEATURE, tmp_path / "missing", tmp_path / "output")
    story = {"readiness": {"status": "READY"}, "traceability": {"api_interaction_refs": ["source-api"]}}
    state = _validate_requirements({"requirements": [{"id": "FR-01"}], "stories": [story], "acceptance_criteria": [{"id": "AC-01"}], "api_contracts": [], "warnings": [], "blockers": [], "current_stage": "load_design_context"})
    assert state["status"] == "BLOCKED"
    assert "API-backed requirements" in state["blockers"][0]


def test_machine_markdown_html_and_coherent_adrs_are_generated(tmp_path):
    result = _run(tmp_path)
    latest = tmp_path / "architecture/latest"
    for name in ("architecture.json", "architecture-selection.json", "architecture-recommendation.json", "architecture-catalog.json", "workflow-run.json", "architecture.md", "architecture.html"):
        assert (latest / name).is_file() and (latest / name).stat().st_size > 0
    assert len(list((latest / "adrs").glob("ADR-*.md"))) == 9
    selection = json.loads((latest / "architecture-selection.json").read_text(encoding="utf-8"))
    consolidated = json.loads((latest / "architecture.json").read_text(encoding="utf-8"))
    assert selection == consolidated["selection"]
    assert consolidated["validation"]["status"] == "ARCHITECTURE_READY_WITH_LIMITATIONS"
    counts = consolidated["counts"]
    assert counts["selected"] + counts["recommended"] + counts["alternatives"] + counts["clarifications"] == counts["decisions"]
    for adr in (latest / "adrs").glob("ADR-*.md"):
        text = adr.read_text(encoding="utf-8")
        for heading in ("## Status", "## Context", "## Decision", "## Alternatives Considered", "## Why Selected", "## Consequences", "## Tradeoffs", "## Traceability"):
            assert heading in text
    integration_adr = (latest / "adrs/ADR-007.md").read_text(encoding="utf-8")
    assert "Place a provider-neutral BFF behind the gateway" in integration_adr
    assert "Gateway-Only Integration" in integration_adr
    assert "Direct Browser-to-API Integration" in integration_adr


def test_customer_html_is_data_driven_complete_and_free_of_internal_noise(tmp_path):
    result = _run(tmp_path)
    contract = result["architecture"]
    html = (tmp_path / "architecture/latest/architecture.html").read_text(encoding="utf-8")
    for phrase in ("Angular 22 Capability Landscape", "Gateway / BFF Deep Dive", "Why Not Everything?", "Architecture Traceability", "GET", "/api/reports/expenses/{year}", "/api/reports/patients/{year}", "/api/reports/clinicsummary", "/api/users/current/tenant", "Nx Monorepo", "Server-Side Rendering", "NgRx", "Microfrontends"):
        assert phrase in html
    assert "<style>" in html and "<script src=" not in html
    assert not any(term in html.lower() for term in ("tree-sitter", "roslyn", "source hash", "parser warning", "knowledge graph", "kg internals"))
    changed = json.loads(json.dumps(contract))
    decision = next(item for item in changed["selection"]["decisions"] if item["technology"] == "Nx Monorepo")
    decision["rationale"] = "DATA_DRIVEN_RENDER_PROOF"
    assert "DATA_DRIVEN_RENDER_PROOF" in render_architecture_html(changed)
    assert "DATA_DRIVEN_RENDER_PROOF" not in html
