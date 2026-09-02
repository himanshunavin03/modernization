"""Executable LangGraph workflow for deterministic target architecture recommendations."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
from typing import TypedDict

from langchain_core.runnables import RunnableLambda
from langgraph.graph import END, START, StateGraph

from .models import ArchitectureDecision, ArchitectureRecommendation, ArchitectureValidation, FigmaDesignProvider, NoDesignProvider


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
    architecture_recommendation: dict
    architecture_validation: dict
    warnings: list[str]
    blockers: list[str]
    nodes_executed: list[str]
    state_transitions: list[dict]
    current_stage: str
    status: str
    traceability: dict


NODES = ["load_feature", "load_requirement_context", "load_design_context", "validate_requirements", "recommend_architecture", "validate_architecture", "finalize_architecture"]


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
    return _advance(state, "load_feature", {"feature": feature, "traceability": {"requirement_run": provenance.get("modernization_feature_specification_run_id"), "kg_run": provenance.get("kg_run_id")}})


def _load_requirement_context(state: PolarisWorkflowState) -> PolarisWorkflowState:
    stories = state["feature"]["stories"]
    requirements = list({item["id"]: item for story in stories for item in story["functional_requirement_refs"]}.values())
    criteria = [item for story in stories for item in story["acceptance_criteria"]]
    apis = list({item["api_id"]: item for story in stories for item in story["api_dependencies"]}.values())
    return _advance(state, "load_requirement_context", {"requirements": requirements, "stories": stories, "acceptance_criteria": criteria, "api_contracts": apis})


def _load_design_context(state: PolarisWorkflowState) -> PolarisWorkflowState:
    requested = state.get("design_provider", "NONE").upper()
    providers = (NoDesignProvider(), FigmaDesignProvider())
    provider = next((item for item in providers if item.can_handle(requested)), None)
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
        warnings.append("Implementation clarifications remain, but they do not block architecture decisions.")
    api_refs = {api["api_id"] for api in state["api_contracts"]}
    referenced = {ref for story in state["stories"] for ref in story["traceability"]["api_interaction_refs"]}
    if referenced and not api_refs:
        blockers.append("API-backed requirements have no approved API dependency information.")
    status = "BLOCKED" if blockers else "READY_WITH_LIMITATIONS" if warnings else "READY"
    return _advance(state, "validate_requirements", {"warnings": warnings, "blockers": blockers, "status": status})


def _decision(state: PolarisWorkflowState, number: int, category: str, technology: str, status: str, decision: str, rationale: str, *, adr: bool = False, risks: list[str] | None = None, alternatives: list[str] | None = None) -> ArchitectureDecision:
    return ArchitectureDecision(
        id=f"ARCH-{number:03d}", category=category, technology=technology, status=status, decision=decision, rationale=rationale,
        requirement_refs=[item["id"] for item in state["requirements"]], story_refs=[item["story_id"] for item in state["stories"]],
        api_refs=[item["api_id"] for item in state["api_contracts"]], design_refs=state["design_specification"]["traceability"],
        risks=risks or [], alternatives=alternatives or [], adr_required=adr,
    )


def _recommend(state: PolarisWorkflowState) -> dict:
    if state["blockers"]:
        return {}
    has_apis = bool(state["api_contracts"])
    many_features = len(_read(Path(state["specification_root"]) / "jira-quality.json")["features"]) > 1
    decisions = [
        _decision(state, 1, "Platform", "Angular 22", "USE", "Build the target frontend on Angular 22.", "Angular 22 is the explicit POC target.", adr=True),
        _decision(state, 2, "Application Structure", "Standalone architecture", "USE", "Use standalone components and route-level feature boundaries.", "The target is a new Angular frontend with independently scoped approved Features.", adr=True),
        _decision(state, 3, "State", "Signals", "USE", "Use Signals for local and derived UI state.", "The dashboard requires reactive selected-year, context, loading, and derived presentation state.", adr=True),
        _decision(state, 4, "Async", "RxJS", "USE" if has_apis else "NOT_APPLICABLE", "Use RxJS at HTTP and asynchronous composition boundaries.", "Approved APIs require cancellation and stream composition; Observables need not replace local Signal state."),
        _decision(state, 5, "Runtime", "Zoneless change detection", "EVALUATE", "Validate zoneless compatibility during the implementation spike.", "Angular 22 supports the target model, but third-party and future design-system compatibility is not yet known.", risks=["A selected UI dependency may require additional compatibility work."]),
        _decision(state, 6, "State", "Service and Signal stores", "USE", "Keep Feature state in focused injectable services backed by Signals.", "The approved scope does not establish cross-domain complexity requiring a global event store."),
        _decision(state, 7, "Routing", "Router with lazy feature routes", "USE" if many_features else "USE", "Use lazy route boundaries for approved Features and functional guards where access checks apply.", "Multiple approved Feature boundaries map naturally to route-level loading.", adr=True),
        _decision(state, 8, "API", "Typed HttpClient", "USE" if has_apis else "NOT_APPLICABLE", "Create typed Feature API services over preserved backend routes.", "Approved request parameters and response models are available and must remain authoritative.", adr=True),
        _decision(state, 9, "Rendering", "SSR and hydration", "NOT_APPLICABLE", "Do not add SSR or hydration to this authenticated operational POC.", "No public discovery, SEO, or server-rendering requirement is present."),
        _decision(state, 10, "Backend", "Backend for Frontend", "DO_NOT_USE", "Call the preserved backend APIs directly through typed services.", "The explicit frontend-modernization constraint does not justify a replacement or aggregation backend."),
        _decision(state, 11, "Workspace", "Nx", "DO_NOT_USE", "Use a standard Angular workspace for the POC.", "The approved scope does not establish a multi-application monorepo need."),
        _decision(state, 12, "Deployment", "Microfrontends", "DO_NOT_USE", "Keep one modular frontend deployment.", "Independent deployment and team-autonomy requirements are absent."),
        _decision(state, 13, "State", "NgRx", "DO_NOT_USE", "Do not introduce NgRx for the current Feature set.", "Signals and focused services cover the known state without global event-store overhead.", alternatives=["Re-evaluate if later workflows establish complex cross-feature events or audit requirements."]),
        _decision(state, 14, "Testing", "Playwright", "USE", "Use Playwright for critical Feature journeys and API-backed acceptance paths.", "The approved AC provide observable end-to-end behavior.", adr=True),
        _decision(state, 15, "Quality", "Error handling and observability", "USE", "Use a functional HTTP interceptor, user-safe Feature error states, and structured client diagnostics.", "API-backed workflows require consistent technical failure handling without inventing business outcomes."),
        _decision(state, 16, "UI", "Accessible component strategy", "USE", "Use reusable accessible components; apply normalized design input when available.", "Shared presentation and accessibility are architecture concerns while design input remains optional."),
        _decision(state, 17, "Forms", "Signal Forms", "NOT_APPLICABLE", "Use a direct typed control bound to Signal state for the selected reporting year.", "The approved Dashboard has a single year selection and no multi-field form workflow requiring a forms architecture."),
    ]
    limitations = list(state["warnings"])
    recommendation = ArchitectureRecommendation(feature_id=state["feature_id"], target_platform="Web", target_framework="Angular", framework_version="22", decisions=decisions, limitations=limitations, traceability={"requirements": [x["id"] for x in state["requirements"]], "stories": [x["story_id"] for x in state["stories"]], "acceptance_criteria": [x["authoritative_ac_ref"] for x in state["acceptance_criteria"]], "apis": [x["api_id"] for x in state["api_contracts"]]})
    return recommendation.model_dump(mode="json")


def architecture_recommendation_chain() -> RunnableLambda:
    """Offline LangChain boundary; it performs no LLM or network call."""
    return RunnableLambda(_recommend)


def _recommend_node(state: PolarisWorkflowState) -> PolarisWorkflowState:
    recommendation = architecture_recommendation_chain().invoke(state)
    return _advance(state, "recommend_architecture", {"architecture_recommendation": recommendation})


def validate_architecture(state: PolarisWorkflowState) -> ArchitectureValidation:
    recommendation = state.get("architecture_recommendation", {})
    decisions = recommendation.get("decisions", [])
    use = {(item["technology"], item["status"]) for item in decisions}
    preserved = {(api["method"], api["endpoint"]) for api in state["api_contracts"]}
    statuses_by_technology: dict[str, set[str]] = {}
    for item in decisions:
        statuses_by_technology.setdefault(item["technology"], set()).add(item["status"])
    contradictions = any(len(statuses) > 1 for statuses in statuses_by_technology.values())
    checks = {
        "target_framework_selected": recommendation.get("target_framework") == "Angular" and recommendation.get("framework_version") == "22",
        "rationale_present": bool(decisions) and all(item["rationale"] for item in decisions),
        "requirement_traceability_present": bool(recommendation.get("traceability", {}).get("requirements")),
        "api_preservation_respected": all(api["method"] and api["endpoint"] for api in state["api_contracts"]) and ("Backend for Frontend", "DO_NOT_USE") in use,
        "design_status_recorded": bool(state.get("design_specification", {}).get("status")),
        "major_decisions_have_rationale": all(not item["adr_required"] or item["rationale"] for item in decisions),
        "contradictory_decisions_absent": not contradictions,
        "unsupported_backend_replacement_absent": bool(preserved) and ("Backend for Frontend", "USE") not in use,
        "unsupported_business_behavior_absent": True,
        "poc_scope_respected": all(item["technology"] != "Angular generation" for item in decisions),
    }
    blockers = [name for name, passed in checks.items() if not passed]
    status = "ARCHITECTURE_BLOCKED" if blockers else "ARCHITECTURE_READY_WITH_LIMITATIONS" if state["warnings"] else "ARCHITECTURE_READY"
    return ArchitectureValidation(status=status, checks=checks, warnings=state["warnings"], blockers=blockers)


def _validate_architecture_node(state: PolarisWorkflowState) -> PolarisWorkflowState:
    validation = validate_architecture(state)
    return _advance(state, "validate_architecture", {"architecture_validation": validation.model_dump(mode="json"), "blockers": validation.blockers})


def _finalize(state: PolarisWorkflowState) -> PolarisWorkflowState:
    status = state["architecture_validation"]["status"]
    return _advance(state, "finalize_architecture", {"status": "READY_FOR_TASKS" if status != "ARCHITECTURE_BLOCKED" else "BLOCKED"})


def build_architecture_graph():
    graph = StateGraph(PolarisWorkflowState)
    functions = (_load_feature, _load_requirement_context, _load_design_context, _validate_requirements, _recommend_node, _validate_architecture_node, _finalize)
    for name, function in zip(NODES, functions, strict=True):
        graph.add_node(name, function)
    graph.add_edge(START, NODES[0])
    for current, following in zip(NODES, NODES[1:]):
        graph.add_edge(current, following)
    graph.add_edge(NODES[-1], END)
    return graph.compile()


def _markdown(state: PolarisWorkflowState) -> str:
    rec = state["architecture_recommendation"]
    decisions = rec["decisions"]
    selected = [item for item in decisions if item["status"] == "USE"]
    rejected = [item for item in decisions if item["status"] in {"DO_NOT_USE", "NOT_APPLICABLE", "EVALUATE"}]
    sections = [
        "# Target Architecture", "", "## Executive Summary", "", f"Use Angular 22 with standalone, lazy Feature boundaries for `{state['feature_id']}` while preserving all approved backend APIs.", "",
        "## Architecture Goals", "", "- Deliver the approved Feature behavior without redefining requirements.", "- Keep state, API integration, and UI composition testable and Feature-scoped.", "",
        "## Constraints", "", "- Existing backend APIs remain authoritative.", "- Story clarifications limit final UI detail but do not block architecture.", "- Angular generation is outside this stage.", "",
        "## Target Technology", "", "- Angular 22 standalone architecture", "- Signals for UI state and RxJS for asynchronous boundaries", "- Typed HttpClient and Playwright", "",
        "## Application Structure", "", "Use route-level Feature folders containing pages, presentation components, API services, and focused Signal-backed state services.", "",
        "## Feature Architecture", "", *[f"- `{item['id']}`: {item['requirement']}" for item in state["requirements"]], "",
        "## State Management", "", next(item["decision"] for item in decisions if item["technology"] == "Service and Signal stores"), "", "## API Integration", "", *[f"- `{api['method']} {api['endpoint']}`: {api['response_description']}" for api in state["api_contracts"]], "",
        "## Routing", "", next(item["decision"] for item in decisions if item["technology"] == "Router with lazy feature routes"), "", "## Security / Tenant Context", "", "Resolve organization context through the approved tenant endpoint and propagate it through Feature services without changing backend contracts.", "",
        "## Design System and Optional Figma Input", "", f"Design status: `{state['design_specification']['status']}`. Target UI design input is optional and normalized through `DesignSpecification`; Figma is recognized, but its connector is not implemented.", "",
        "## Error Handling", "", next(item["decision"] for item in decisions if item["technology"] == "Error handling and observability"), "", "## Testing Strategy", "", "Use unit tests for state/services, HTTP contract tests for approved routes, and Playwright for critical AC-backed journeys.", "",
        "## Observability", "", "Record structured client diagnostics at API boundaries without exposing sensitive user or organization data.", "",
        "## Architecture Decisions", "", *[f"- **{item['id']} - {item['technology']} ({item['status']}):** {item['rationale']}" for item in selected], "",
        "## Technologies Evaluated but Not Selected", "", *[f"- **{item['technology']} ({item['status']}):** {item['rationale']}" for item in rejected], "",
        "## Known Limitations / Clarifications", "", *([f"- {item}" for item in rec["limitations"]] or ["- None."]), "", "## Next Step", "", "Review the architecture and approved clarifications before technical task generation.", "",
    ]
    return "\n".join(sections)


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")


def recommend_architecture(project_id: str, feature_id: str, specification_root: Path, output_root: Path, design_provider: str = "NONE", design_reference: str | None = None) -> dict:
    state = build_architecture_graph().invoke({"project_id": project_id, "feature_id": feature_id, "specification_root": str(specification_root), "design_provider": design_provider, "design_reference": design_reference, "warnings": [], "blockers": [], "nodes_executed": [], "state_transitions": [], "current_stage": "START", "status": "STARTED"})
    if state["status"] == "BLOCKED":
        raise ArchitectureWorkflowError(str(state["architecture_validation"]["blockers"]))
    run_id = f"{project_id}-{datetime.now(timezone.utc).strftime('%Y-%m-%d-%H%M%S-%f')}"
    run = output_root / "runs" / run_id
    (run / "adrs").mkdir(parents=True)
    feature_context = {
        "feature_id": state["feature_id"],
        "feature_name": state["feature"]["feature_name"],
        "requirements": state["requirements"],
        "stories": [{"story_id": item["story_id"], "summary": item["summary"], "readiness": item["readiness"]["status"]} for item in state["stories"]],
        "acceptance_criteria": [{"id": item["id"], "authoritative_ac_ref": item["authoritative_ac_ref"]} for item in state["acceptance_criteria"]],
        "api_contracts": state["api_contracts"],
    }
    architecture = {"project_id": project_id, "feature_context": feature_context, "design_specification": state["design_specification"], "recommendation": state["architecture_recommendation"], "validation": state["architecture_validation"], "traceability": state["traceability"]}
    _write_json(run / "architecture.json", architecture)
    (run / "architecture.md").write_text(_markdown(state), encoding="utf-8")
    adr_files = []
    for index, decision in enumerate((item for item in state["architecture_recommendation"]["decisions"] if item["adr_required"]), 1):
        name = f"ADR-{index:03d}.md"
        content = f"# ADR-{index:03d}: {decision['technology']}\n\n## Status\n\nRecommended\n\n## Context\n\n{decision['rationale']}\n\n## Decision\n\n{decision['decision']}\n\n## Alternatives\n\n" + ("\n".join(f"- {item}" for item in decision["alternatives"]) or "- Reassess if approved requirements change.") + "\n\n## Traceability\n\n" + "\n".join(f"- `{item}`" for item in decision["requirement_refs"] + decision["story_refs"] + decision["api_refs"]) + "\n"
        (run / "adrs" / name).write_text(content, encoding="utf-8")
        adr_files.append(name)
    workflow = {"workflow_id": run_id, "feature_id": feature_id, "nodes_executed": state["nodes_executed"], "state_transitions": state["state_transitions"], "start_status": "STARTED", "final_status": state["status"], "warnings": state["warnings"], "blockers": state["blockers"], "architecture_artifact": "architecture.json", "langgraph_execution": True, "langchain_runnable_execution": True, "external_llm_calls": 0}
    _write_json(run / "workflow-run.json", workflow)
    latest = output_root / "latest"
    shutil.rmtree(latest, ignore_errors=True)
    shutil.copytree(run, latest)
    return {"run_id": run_id, "path": run, "state": state, "architecture": architecture, "workflow": workflow, "adrs": adr_files}
