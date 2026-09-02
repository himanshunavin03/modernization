"""Executable enterprise architecture recommendation and selection workflow."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import shutil
from typing import TypedDict

from langchain_core.runnables import RunnableLambda
from langgraph.graph import END, START, StateGraph

from .catalog import evaluate_architecture_catalog, load_architecture_catalog
from .models import (
    ArchitectureLock, ArchitectureRecommendation, ArchitectureSelection,
    ArchitectureValidation, DecisionStatus, FigmaDesignProvider, NoDesignProvider,
    SelectionSource,
)
from .renderers import render_adrs, render_architecture_html, render_architecture_markdown


class ArchitectureWorkflowError(ValueError):
    """Approved workflow input is missing or inconsistent."""


class PolarisWorkflowState(TypedDict, total=False):
    project_id: str
    feature_id: str
    specification_root: str
    design_provider: str
    design_reference: str | None
    feature: dict
    requirements: list[dict]
    stories: list[dict]
    acceptance_criteria: list[dict]
    api_contracts: list[dict]
    design_specification: dict
    catalog_decisions: list[dict]
    architecture_recommendation: dict
    architecture_selection: dict
    architecture_validation: dict
    architecture_lock: dict
    warnings: list[str]
    blockers: list[str]
    nodes_executed: list[str]
    state_transitions: list[dict]
    current_stage: str
    status: str
    traceability: dict


NODES = [
    "load_feature", "load_requirement_context", "load_design_context", "validate_requirements",
    "evaluate_architecture_catalog", "recommend_architecture", "select_architecture",
    "validate_architecture", "finalize_architecture",
]


def _read(path: Path) -> dict:
    if not path.is_file():
        raise ArchitectureWorkflowError(f"Required approved artifact is missing: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _advance(state: PolarisWorkflowState, node: str, updates: dict) -> PolarisWorkflowState:
    previous = state.get("current_stage", "START")
    return {
        **updates,
        "nodes_executed": [*state.get("nodes_executed", []), node],
        "state_transitions": [*state.get("state_transitions", []), {"from": previous, "to": node}],
        "current_stage": node,
    }


def _load_feature(state: PolarisWorkflowState) -> PolarisWorkflowState:
    root = Path(state["specification_root"])
    artifact = _read(root / "jira-quality.json")
    feature = next((item for item in artifact["features"] if item["feature_id"] == state["feature_id"]), None)
    if not feature:
        raise ArchitectureWorkflowError(f"Unknown Feature: {state['feature_id']}")
    provenance = _read(root / "provenance.json")
    return _advance(state, "load_feature", {
        "feature": feature,
        "traceability": {
            "requirement_run": provenance.get("modernization_feature_specification_run_id"),
            "kg_run": provenance.get("kg_run_id"),
        },
    })


def _load_requirement_context(state: PolarisWorkflowState) -> PolarisWorkflowState:
    stories = state["feature"]["stories"]
    requirements = list({item["id"]: item for story in stories for item in story["functional_requirement_refs"]}.values())
    criteria = [item for story in stories for item in story["acceptance_criteria"]]
    apis = list({item["api_id"]: item for story in stories for item in story["api_dependencies"]}.values())
    return _advance(state, "load_requirement_context", {
        "requirements": requirements, "stories": stories,
        "acceptance_criteria": criteria, "api_contracts": apis,
    })


def _load_design_context(state: PolarisWorkflowState) -> PolarisWorkflowState:
    requested = state.get("design_provider", "NONE").upper()
    provider = next((item for item in (NoDesignProvider(), FigmaDesignProvider()) if item.can_handle(requested)), None)
    if not provider:
        raise ArchitectureWorkflowError(f"Unknown design provider: {requested}")
    design = provider.analyze(state.get("design_reference"))
    warnings = list(state.get("warnings", []))
    if design.status == "FIGMA_CONNECTOR_NOT_IMPLEMENTED":
        warnings.append("Figma was recognized, but its connector is not implemented; architecture continues without analyzed design content.")
    return _advance(state, "load_design_context", {"design_specification": design.model_dump(mode="json"), "warnings": warnings})


def _validate_requirements(state: PolarisWorkflowState) -> PolarisWorkflowState:
    blockers = list(state.get("blockers", []))
    warnings = list(state.get("warnings", []))
    if not state["requirements"] or not state["stories"] or not state["acceptance_criteria"]:
        blockers.append("Feature delivery requirements are incomplete.")
    if any(story["readiness"]["status"] == "BLOCKED" for story in state["stories"]):
        blockers.append("At least one approved Story is blocked.")
    if any(story["readiness"]["status"] == "NEEDS_CLARIFICATION" for story in state["stories"]):
        warnings.append("Implementation clarifications remain, but they do not block architecture selection.")
    api_refs = {api["api_id"] for api in state["api_contracts"]}
    referenced = {ref for story in state["stories"] for ref in story["traceability"]["api_interaction_refs"]}
    if referenced and not api_refs:
        blockers.append("API-backed requirements have no approved API dependency information.")
    status = "BLOCKED" if blockers else "READY_WITH_LIMITATIONS" if warnings else "READY"
    return _advance(state, "validate_requirements", {"warnings": warnings, "blockers": blockers, "status": status})


def _evaluate_catalog_node(state: PolarisWorkflowState) -> PolarisWorkflowState:
    decisions = [item.model_dump(mode="json") for item in evaluate_architecture_catalog(state)]
    return _advance(state, "evaluate_architecture_catalog", {"catalog_decisions": decisions})


def _recommend(state: PolarisWorkflowState) -> dict:
    if state["blockers"]:
        return {}
    recommendation = ArchitectureRecommendation(
        feature_id=state["feature_id"], target_platform="Web", target_framework="Angular", framework_version="22",
        decisions=state["catalog_decisions"], limitations=list(state["warnings"]),
        traceability={
            "requirements": [item["id"] for item in state["requirements"]],
            "stories": [item["story_id"] for item in state["stories"]],
            "acceptance_criteria": [item["authoritative_ac_ref"] for item in state["acceptance_criteria"]],
            "apis": [item["api_id"] for item in state["api_contracts"]],
        },
    )
    return recommendation.model_dump(mode="json")


def architecture_recommendation_chain() -> RunnableLambda:
    """Offline LangChain boundary; it performs no LLM or network call."""
    return RunnableLambda(_recommend)


def _recommend_node(state: PolarisWorkflowState) -> PolarisWorkflowState:
    return _advance(state, "recommend_architecture", {"architecture_recommendation": architecture_recommendation_chain().invoke(state)})


def _select_architecture(state: PolarisWorkflowState) -> PolarisWorkflowState:
    decisions = state["architecture_recommendation"]["decisions"]
    alternative_statuses = {DecisionStatus.EVALUATED_ALTERNATIVE.value, DecisionStatus.NOT_SELECTED.value, DecisionStatus.NOT_APPLICABLE.value}
    selection = ArchitectureSelection(
        feature_id=state["feature_id"], selection_source=SelectionSource.POLARIS_POC_DEFAULT,
        recommendation_ref="architecture-recommendation.json", decisions=decisions,
        selected_decision_ids=[item["id"] for item in decisions if item["status"] == DecisionStatus.SELECTED.value],
        recommended_decision_ids=[item["id"] for item in decisions if item["status"] == DecisionStatus.RECOMMENDED.value],
        alternative_decision_ids=[item["id"] for item in decisions if item["status"] in alternative_statuses],
        clarification_decision_ids=[item["id"] for item in decisions if item["status"] == DecisionStatus.REQUIRES_CLARIFICATION.value],
        existing_api_contracts=state["api_contracts"],
        target_integration_topology=["Browser", "Angular 22", "Provider-Neutral API Gateway", "Backend for Frontend", "Existing Business APIs"],
    )
    return _advance(state, "select_architecture", {"architecture_selection": selection.model_dump(mode="json")})


def validate_architecture(state: PolarisWorkflowState) -> ArchitectureValidation:
    recommendation = state.get("architecture_recommendation", {})
    selection = state.get("architecture_selection", {})
    decisions = selection.get("decisions", [])
    by_technology = {item["technology"]: item for item in decisions}
    statuses_by_technology: dict[str, set[str]] = {}
    for item in decisions:
        statuses_by_technology.setdefault(item["technology"], set()).add(item["status"])
    original_contracts = [{key: api.get(key) for key in ("api_id", "method", "endpoint", "path_parameters", "query_parameters", "request_model", "response_description", "response_model")} for api in state["api_contracts"]]
    selected_contracts = [{key: api.get(key) for key in ("api_id", "method", "endpoint", "path_parameters", "query_parameters", "request_model", "response_description", "response_model")} for api in selection.get("existing_api_contracts", [])]
    selected = lambda technology: by_technology.get(technology, {}).get("status") == DecisionStatus.SELECTED.value
    not_selected = lambda technology: by_technology.get(technology, {}).get("status") != DecisionStatus.SELECTED.value
    checks = {
        "architecture_has_target_platform": recommendation.get("target_framework") == "Angular" and recommendation.get("framework_version") == "22",
        "architecture_has_selection": selection.get("status") == "ARCHITECTURE_SELECTED",
        "architecture_decisions_have_status": bool(decisions) and all(item["status"] in {value.value for value in DecisionStatus} for item in decisions),
        "selected_decisions_have_rationale": all(item["rationale"] for item in decisions if item["status"] == DecisionStatus.SELECTED.value),
        "selected_decisions_have_traceability": all(item["requirement_refs"] and item["feature_refs"] and item["story_refs"] for item in decisions if item["status"] == DecisionStatus.SELECTED.value),
        "no_contradictory_selections": not any(len(values) > 1 for values in statuses_by_technology.values()),
        "no_unsupported_technology_selection": selected("Angular 22") and selected("Nx Monorepo") and selected("Standalone Components"),
        "no_unjustified_complexity": not_selected("NgRx") and not_selected("Microfrontends") and not_selected("Module Federation"),
        "existing_api_contracts_preserved": original_contracts == selected_contracts and bool(original_contracts),
        "gateway_does_not_rewrite_business_api_contracts": selected("Provider-Neutral API Gateway") and original_contracts == selected_contracts,
        "bff_does_not_invent_business_behavior": selected("Backend for Frontend") and all("endpoint" not in item["decision"].lower() for item in decisions if item["technology"] == "Backend for Frontend"),
        "ssr_not_selected_without_rendering_justification": not_selected("Server-Side Rendering"),
        "mfe_not_selected_without_deployment_justification": not_selected("Microfrontends"),
        "ngrx_not_selected_without_state_complexity": not_selected("NgRx"),
        "rxjs_async_boundary_preserved": selected("RxJS"),
        "signals_ui_state_supported": selected("Angular Signals") and selected("Computed Signals"),
        "architecture_selection_is_downstream_source_of_truth": selection.get("downstream_source_of_truth") is True,
        "design_status_recorded": bool(state.get("design_specification", {}).get("status")),
        "poc_scope_respected": all(item["technology"] not in {"Angular Generation", "Technical Task Generation"} for item in decisions),
    }
    blockers = [name for name, passed in checks.items() if not passed]
    warnings = list(state["warnings"])
    if selection.get("clarification_decision_ids"):
        warnings.append("Identity provider and browser authentication/session architecture require customer clarification.")
    status = "ARCHITECTURE_BLOCKED" if blockers else "ARCHITECTURE_READY_WITH_LIMITATIONS" if warnings else "ARCHITECTURE_READY"
    return ArchitectureValidation(status=status, checks=checks, warnings=warnings, blockers=blockers)


def _validate_architecture_node(state: PolarisWorkflowState) -> PolarisWorkflowState:
    validation = validate_architecture(state)
    return _advance(state, "validate_architecture", {"architecture_validation": validation.model_dump(mode="json"), "warnings": validation.warnings, "blockers": validation.blockers})


def _finalize(state: PolarisWorkflowState) -> PolarisWorkflowState:
    validation_passed = state["architecture_validation"]["status"] != "ARCHITECTURE_BLOCKED"
    encoded = json.dumps(state["architecture_selection"], sort_keys=True, separators=(",", ":")).encode("utf-8")
    lock = ArchitectureLock(
        status="LOCKED" if validation_passed else "NOT_LOCKED",
        selection_source=state["architecture_selection"]["selection_source"],
        selection_hash=sha256(encoded).hexdigest() if validation_passed else None,
        locked_after_validation=validation_passed,
    )
    return _advance(state, "finalize_architecture", {
        "architecture_lock": lock.model_dump(mode="json"),
        "status": "READY_FOR_TASKS" if validation_passed else "BLOCKED",
    })


def build_architecture_graph():
    graph = StateGraph(PolarisWorkflowState)
    functions = (
        _load_feature, _load_requirement_context, _load_design_context, _validate_requirements,
        _evaluate_catalog_node, _recommend_node, _select_architecture,
        _validate_architecture_node, _finalize,
    )
    for name, function in zip(NODES, functions, strict=True):
        graph.add_node(name, function)
    graph.add_edge(START, NODES[0])
    for current, following in zip(NODES, NODES[1:]):
        graph.add_edge(current, following)
    graph.add_edge(NODES[-1], END)
    return graph.compile()


def _feature_context(state: PolarisWorkflowState) -> dict:
    return {
        "feature_id": state["feature_id"], "feature_name": state["feature"]["feature_name"],
        "requirements": state["requirements"],
        "stories": [{"story_id": item["story_id"], "summary": item["summary"], "readiness": item["readiness"]["status"]} for item in state["stories"]],
        "acceptance_criteria": [{"id": item["id"], "authoritative_ac_ref": item["authoritative_ac_ref"]} for item in state["acceptance_criteria"]],
        "api_contracts": state["api_contracts"],
    }


def _counts(state: PolarisWorkflowState, adr_count: int) -> dict:
    statuses = Counter(item["status"] for item in state["architecture_selection"]["decisions"])
    return {
        "decisions": sum(statuses.values()), "selected": statuses[DecisionStatus.SELECTED.value],
        "recommended": statuses[DecisionStatus.RECOMMENDED.value],
        "alternatives": statuses[DecisionStatus.EVALUATED_ALTERNATIVE.value] + statuses[DecisionStatus.NOT_SELECTED.value] + statuses[DecisionStatus.NOT_APPLICABLE.value],
        "evaluated_alternatives": statuses[DecisionStatus.EVALUATED_ALTERNATIVE.value],
        "not_selected": statuses[DecisionStatus.NOT_SELECTED.value],
        "not_applicable": statuses[DecisionStatus.NOT_APPLICABLE.value],
        "clarifications": statuses[DecisionStatus.REQUIRES_CLARIFICATION.value],
        "requirements": len(state["requirements"]), "stories": len(state["stories"]),
        "acceptance_criteria": len(state["acceptance_criteria"]), "apis": len(state["api_contracts"]),
        "adrs": adr_count,
    }


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")


def recommend_architecture(project_id: str, feature_id: str, specification_root: Path, output_root: Path, design_provider: str = "NONE", design_reference: str | None = None) -> dict:
    state = build_architecture_graph().invoke({
        "project_id": project_id, "feature_id": feature_id, "specification_root": str(specification_root),
        "design_provider": design_provider, "design_reference": design_reference,
        "warnings": [], "blockers": [], "nodes_executed": [], "state_transitions": [],
        "current_stage": "START", "status": "STARTED",
    })
    if state["status"] == "BLOCKED":
        raise ArchitectureWorkflowError(str(state["architecture_validation"]["blockers"]))
    run_id = f"{project_id}-{datetime.now(timezone.utc).strftime('%Y-%m-%d-%H%M%S-%f')}"
    run = output_root / "runs" / run_id
    (run / "adrs").mkdir(parents=True)
    shell = {
        "project_id": project_id, "feature_context": _feature_context(state),
        "design_specification": state["design_specification"],
        "recommendation": state["architecture_recommendation"], "selection": state["architecture_selection"],
        "validation": state["architecture_validation"], "architecture_lock": state["architecture_lock"],
        "traceability": state["traceability"],
    }
    adr_documents = render_adrs({**shell, "counts": {}})
    contract = {**shell, "counts": _counts(state, len(adr_documents))}
    _write_json(run / "architecture.json", contract)
    _write_json(run / "architecture-selection.json", state["architecture_selection"])
    _write_json(run / "architecture-recommendation.json", state["architecture_recommendation"])
    _write_json(run / "architecture-catalog.json", {"decisions": state["catalog_decisions"]})
    (run / "architecture.md").write_text(render_architecture_markdown(contract), encoding="utf-8")
    (run / "architecture.html").write_text(render_architecture_html(contract), encoding="utf-8")
    for name, content in adr_documents.items():
        (run / "adrs" / name).write_text(content, encoding="utf-8")
    workflow = {
        "workflow_id": run_id, "feature_id": feature_id,
        "nodes_executed": state["nodes_executed"], "state_transitions": state["state_transitions"],
        "start_status": "STARTED", "final_status": state["status"],
        "decision_counts": contract["counts"],
        "validation_result": state["architecture_validation"]["status"],
        "architecture_lock": state["architecture_lock"]["status"],
        "warnings": state["warnings"], "blockers": state["blockers"],
        "architecture_artifact": "architecture.json", "selection_artifact": "architecture-selection.json",
        "langgraph_execution": True, "langchain_boundary": "RunnableLambda (offline deterministic catalog recommendation)",
        "langchain_runnable_execution": True, "external_llm_calls": 0,
    }
    _write_json(run / "workflow-run.json", workflow)
    latest = output_root / "latest"
    shutil.rmtree(latest, ignore_errors=True)
    shutil.copytree(run, latest)
    return {"run_id": run_id, "path": run, "state": state, "architecture": contract, "workflow": workflow, "adrs": sorted(adr_documents)}
