"""LangGraph orchestration for optional design and technical task planning."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from polaris_modernization.design.conflicts import detect_design_conflicts
from polaris_modernization.design.models import DesignMode
from polaris_modernization.design.providers import FigmaDesignProvider, NoDesignProvider
from polaris_modernization.design.renderers import render_design_html, render_design_markdown
from polaris_modernization.modernization_operations.ids import ANGULAR_FEATURE_OPERATION_ID

from .generator import technical_task_chain
from .models import TechnicalTaskPlan
from .renderers import render_technical_tasks_html, render_technical_tasks_markdown
from .validators import selection_hash, validate_tasks


class TechnicalTaskWorkflowError(ValueError):
    """Frozen inputs or generated delivery contracts are inconsistent."""


class TechnicalTaskState(TypedDict, total=False):
    project_id: str
    feature_id: str
    architecture_root: str
    specification_root: str
    design_provider: str
    design_mode: str
    figma_url: str | None
    architecture: dict
    feature: dict
    requirements: list[dict]
    stories: list[dict]
    acceptance_criteria: list[dict]
    api_contracts: list[dict]
    design: dict
    tasks: list[dict]
    validation: dict
    nodes_executed: list[str]
    state_transitions: list[dict]
    current_stage: str
    status: str


NODES = [
    "load_approved_context", "load_optional_design", "resolve_design_conflicts",
    "compose_technical_tasks", "validate_technical_tasks", "finalize_technical_tasks",
]


def _read(path: Path) -> dict:
    if not path.is_file():
        raise TechnicalTaskWorkflowError(f"Required approved artifact is missing: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _advance(state: TechnicalTaskState, node: str, updates: dict) -> TechnicalTaskState:
    previous = state.get("current_stage", "START")
    return {
        **updates,
        "nodes_executed": [*state.get("nodes_executed", []), node],
        "state_transitions": [*state.get("state_transitions", []), {"from": previous, "to": node}],
        "current_stage": node,
    }


def _load_context(state: TechnicalTaskState) -> TechnicalTaskState:
    architecture_root = Path(state["architecture_root"])
    architecture = _read(architecture_root / "architecture.json")
    selection = _read(architecture_root / "architecture-selection.json")
    lock = architecture.get("architecture_lock", {})
    if architecture.get("selection") != selection:
        raise TechnicalTaskWorkflowError("Frozen architecture selection does not match architecture.json.")
    if lock.get("status") != "LOCKED" or lock.get("selection_hash") != selection_hash(selection):
        raise TechnicalTaskWorkflowError("Architecture selection is not validly locked.")
    specification = _read(Path(state["specification_root"]) / "jira-quality.json")
    feature = next((item for item in specification["features"] if item["feature_id"] == state["feature_id"]), None)
    if not feature:
        raise TechnicalTaskWorkflowError(f"Unknown approved Feature: {state['feature_id']}")
    stories = feature["stories"]
    requirements = list({item["id"]: item for story in stories for item in story["functional_requirement_refs"]}.values())
    criteria = [item for story in stories for item in story["acceptance_criteria"]]
    apis = list({item["api_id"]: item for story in stories for item in story["api_dependencies"]}.values())
    return _advance(state, NODES[0], {"architecture": architecture, "feature": feature, "stories": stories, "requirements": requirements, "acceptance_criteria": criteria, "api_contracts": apis})


def _load_design(state: TechnicalTaskState) -> TechnicalTaskState:
    provider_name = state["design_provider"].upper()
    mode = DesignMode(state["design_mode"].upper())
    if provider_name in {"NONE", "NO_DESIGN"}:
        provider = NoDesignProvider()
    elif provider_name == "FIGMA":
        if mode == DesignMode.NONE:
            raise TechnicalTaskWorkflowError("Figma requires FIXTURE or LIVE design mode.")
        provider = FigmaDesignProvider()
    else:
        raise TechnicalTaskWorkflowError(f"Unknown design provider: {provider_name}")
    design = provider.analyze(state.get("figma_url"), mode)
    return _advance(state, NODES[1], {"design": design.model_dump(mode="json")})


def _resolve_conflicts(state: TechnicalTaskState) -> TechnicalTaskState:
    from polaris_modernization.design.models import DesignSpecification
    design = DesignSpecification.model_validate(state["design"])
    resolved = detect_design_conflicts(design, {item["id"] for item in state["requirements"]})
    return _advance(state, NODES[2], {"design": resolved.model_dump(mode="json")})


def _compose_tasks(state: TechnicalTaskState) -> TechnicalTaskState:
    tasks = technical_task_chain().invoke({
        "feature": state["feature"], "requirements": state["requirements"], "stories": state["stories"],
        "acceptance_criteria": state["acceptance_criteria"], "api_contracts": state["api_contracts"],
        "architecture": state["architecture"]["selection"], "design": state["design"],
    })
    return _advance(state, NODES[3], {"tasks": tasks})


def _validate(state: TechnicalTaskState) -> TechnicalTaskState:
    result = validate_tasks({
        "feature": state["feature"], "requirements": state["requirements"], "stories": state["stories"],
        "acceptance_criteria": state["acceptance_criteria"], "api_contracts": state["api_contracts"],
        "architecture": state["architecture"], "design": state["design"],
    }, state["tasks"])
    return _advance(state, NODES[4], {"validation": result})


def _finalize(state: TechnicalTaskState) -> TechnicalTaskState:
    if state["validation"]["status"] != "PASS":
        raise TechnicalTaskWorkflowError(f"Technical task validation failed: {state['validation']['blockers']}")
    return _advance(state, NODES[5], {"status": "TECHNICAL_TASKS_READY"})


def build_technical_task_graph():
    graph = StateGraph(TechnicalTaskState)
    functions = (_load_context, _load_design, _resolve_conflicts, _compose_tasks, _validate, _finalize)
    for name, function in zip(NODES, functions, strict=True):
        graph.add_node(name, function)
    graph.add_edge(START, NODES[0])
    for current, following in zip(NODES, NODES[1:]):
        graph.add_edge(current, following)
    graph.add_edge(NODES[-1], END)
    return graph.compile()


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")


def _modernization_operation(architecture: dict) -> dict:
    selected_ids = set(architecture["selection"]["selected_decision_ids"])
    selected = [item for item in architecture["selection"]["decisions"] if item["id"] in selected_ids]
    if not any("angular" in item.get("technology", "").casefold() for item in selected):
        raise TechnicalTaskWorkflowError("No supported modernization operation matches the selected target architecture.")
    return {
        "operation_id": ANGULAR_FEATURE_OPERATION_ID,
        "target": "ANGULAR",
        "selection_source": "LOCKED_ARCHITECTURE",
    }


def generate_technical_tasks(project_id: str, feature_id: str, architecture_root: Path, specification_root: Path, design_provider: str, design_mode: str, figma_url: str | None, output_root: Path, design_output_root: Path) -> dict:
    state = build_technical_task_graph().invoke({
        "project_id": project_id, "feature_id": feature_id, "architecture_root": str(architecture_root),
        "specification_root": str(specification_root), "design_provider": design_provider,
        "design_mode": design_mode, "figma_url": figma_url, "nodes_executed": [],
        "state_transitions": [], "current_stage": "START", "status": "STARTED",
    })
    run_id = f"{project_id}-{datetime.now(timezone.utc).strftime('%Y-%m-%d-%H%M%S-%f')}"
    workflow = {
        "workflow_id": run_id, "nodes_executed": state["nodes_executed"],
        "state_transitions": state["state_transitions"], "start_status": "STARTED",
        "final_status": state["status"], "langgraph_execution": True,
        "langchain_boundary": "RunnableLambda (offline deterministic technical task composition)",
        "langchain_runnable_execution": True, "external_llm_calls": 0,
        "design_provider": state["design"]["provider"], "design_mode": state["design"]["mode"],
        "design_status": state["design"]["status"],
    }
    traceability = {
        "feature_refs": [feature_id], "functional_requirement_refs": [item["id"] for item in state["requirements"]],
        "story_refs": [item["story_id"] for item in state["stories"]],
        "acceptance_criteria_refs": [item["authoritative_ac_ref"] for item in state["acceptance_criteria"]],
        "api_refs": [item["api_id"] for item in state["api_contracts"]],
        "architecture_decision_refs": list(dict.fromkeys(ref for item in state["tasks"] for ref in item["architecture_decision_refs"])),
        "adr_refs": list(dict.fromkeys(ref for item in state["tasks"] for ref in item["adr_refs"])),
        "design_refs": list(dict.fromkeys(ref for item in state["tasks"] for ref in item["design_refs"])),
    }
    plan = TechnicalTaskPlan(
        project_id=project_id, feature_id=feature_id, feature_name=state["feature"]["feature_name"],
        modernization_operation=_modernization_operation(state["architecture"]),
        architecture_selection_ref=str(architecture_root / "architecture-selection.json"),
        architecture_selection_hash=state["architecture"]["architecture_lock"]["selection_hash"],
        architecture_lock_status="LOCKED", design=state["design"], requirements=state["requirements"],
        stories=[{"story_id": item["story_id"], "summary": item["summary"]} for item in state["stories"]],
        acceptance_criteria=[{"id": item["id"], "authoritative_ac_ref": item["authoritative_ac_ref"], "title": item["title"]} for item in state["acceptance_criteria"]],
        existing_api_contracts=state["api_contracts"], tasks=state["tasks"], validation=state["validation"],
        traceability=traceability, workflow=workflow,
    ).model_dump(mode="json")
    run = output_root / "runs" / run_id
    run.mkdir(parents=True)
    _write_json(run / "technical-tasks.json", plan)
    _write_json(run / "workflow-run.json", workflow)
    (run / "technical-tasks.md").write_text(render_technical_tasks_markdown(plan), encoding="utf-8")
    (run / "technical-tasks.html").write_text(render_technical_tasks_html(plan), encoding="utf-8")
    latest = output_root / "latest"
    if not latest.exists():
        shutil.copytree(run, latest)
    feature_latest = output_root / "features" / feature_id / "latest"
    shutil.rmtree(feature_latest, ignore_errors=True)
    shutil.copytree(run, feature_latest)

    design_run = design_output_root / "runs" / run_id
    design_run.mkdir(parents=True)
    _write_json(design_run / "design.json", state["design"])
    (design_run / "design.md").write_text(render_design_markdown(state["design"]), encoding="utf-8")
    (design_run / "design.html").write_text(render_design_html(state["design"]), encoding="utf-8")
    design_latest = design_output_root / "latest"
    if not design_latest.exists():
        shutil.copytree(design_run, design_latest)
    design_feature_latest = design_output_root / "features" / feature_id / "latest"
    shutil.rmtree(design_feature_latest, ignore_errors=True)
    shutil.copytree(design_run, design_feature_latest)
    return {"run_id": run_id, "path": run, "design_path": design_run, "state": state, "plan": plan, "workflow": workflow}
