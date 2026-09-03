"""Executable existing-UI to Angular 22 hero generation workflow."""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import shutil
from typing import TypedDict

from langchain_core.runnables import RunnableLambda
from langgraph.graph import END, START, StateGraph

from .models import GenerationManifest, PepValidationContract, TaskExecutionStatus
from .reconstruction import ASSET_FILES, ANGULARJS_FILES, RAZOR_FILES, reconstruct_existing_ui
from .renderers import render_modernization_html, render_traceability_markdown, render_ui_html, render_ui_markdown
from .templates import workspace_files
from .validators import validate_generation


class ModernizationGenerationError(ValueError):
    """Frozen generation inputs or generated output failed validation."""


class GenerationState(TypedDict, total=False):
    project_id: str
    feature_id: str
    source_root: str
    architecture_root: str
    technical_task_root: str
    specification_root: str
    workspace: str
    architecture: dict
    technical_plan: dict
    specification: dict
    feature: dict
    ui_specification: dict
    file_templates: dict[str, str]
    manifest: dict
    traceability: dict
    validation: dict
    source_hash_before: str
    source_hash_after: str
    nodes_executed: list[str]
    state_transitions: list[dict]
    current_stage: str
    status: str


NODES = [
    "load_frozen_generation_inputs", "load_existing_ui", "reconstruct_existing_ui",
    "compose_angular_workspace", "generate_angular_hero", "build_generation_traceability",
    "validate_generated_workspace", "finalize_generation",
]


def _read(path: Path) -> dict:
    if not path.is_file():
        raise ModernizationGenerationError(f"Required frozen artifact is missing: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _tree_hash(root: Path) -> str:
    digest = sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


def _selection_hash(selection: dict) -> str:
    return sha256(json.dumps(selection, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def _advance(state: GenerationState, node: str, updates: dict) -> GenerationState:
    previous = state.get("current_stage", "START")
    return {**updates, "nodes_executed": [*state.get("nodes_executed", []), node], "state_transitions": [*state.get("state_transitions", []), {"from": previous, "to": node}], "current_stage": node}


def _load_frozen(state: GenerationState) -> GenerationState:
    architecture = _read(Path(state["architecture_root"]) / "architecture.json")
    selection = _read(Path(state["architecture_root"]) / "architecture-selection.json")
    tasks = _read(Path(state["technical_task_root"]) / "technical-tasks.json")
    specification = _read(Path(state["specification_root"]) / "jira-quality.json")
    feature = next((item for item in specification["features"] if item["feature_id"] == state["feature_id"]), None)
    lock = architecture.get("architecture_lock", {})
    if architecture.get("selection") != selection or lock.get("status") != "LOCKED" or lock.get("selection_hash") != _selection_hash(selection):
        raise ModernizationGenerationError("Architecture selection is not the valid locked source of truth.")
    if tasks.get("status") != "TECHNICAL_TASKS_READY" or tasks.get("feature_id") != state["feature_id"] or len(tasks.get("tasks", [])) != 16:
        raise ModernizationGenerationError("The approved 16-task hero plan is unavailable or inconsistent.")
    if not feature:
        raise ModernizationGenerationError(f"Unknown approved Feature: {state['feature_id']}")
    source_hash = _tree_hash(Path(state["source_root"]))
    return _advance(state, NODES[0], {"architecture": architecture, "technical_plan": tasks, "specification": specification, "feature": feature, "source_hash_before": source_hash})


def _load_existing_ui(state: GenerationState) -> GenerationState:
    root = Path(state["source_root"])
    missing = [path for path in [*RAZOR_FILES, *ANGULARJS_FILES] if not (root / path).is_file()]
    if missing:
        raise ModernizationGenerationError(f"Existing Dashboard UI surfaces are missing: {missing}")
    return _advance(state, NODES[1], {})


def _reconstruct(state: GenerationState) -> GenerationState:
    ui = reconstruct_existing_ui(Path(state["source_root"]), state["feature_id"])
    return _advance(state, NODES[2], {"ui_specification": ui.model_dump(mode="json")})


def _compose_workspace(context: dict) -> dict[str, str]:
    if context["source_mode"] != "EXISTING_APPLICATION_UI" or context.get("figma_for_generation") != "DISABLED":
        raise ModernizationGenerationError("Angular generation requires existing UI mode with Figma disabled.")
    return workspace_files()


def angular_generation_chain() -> RunnableLambda:
    """Offline deterministic code composition with no model or network call."""
    return RunnableLambda(_compose_workspace)


def _compose(state: GenerationState) -> GenerationState:
    files = angular_generation_chain().invoke({"source_mode": state["ui_specification"]["source_mode"], "figma_for_generation": "DISABLED"})
    return _advance(state, NODES[3], {"file_templates": files})


def _generate(state: GenerationState) -> GenerationState:
    workspace = Path(state["workspace"])
    if workspace.exists():
        shutil.rmtree(workspace)
    for relative, content in state["file_templates"].items():
        target = workspace / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    source_root = Path(state["source_root"])
    for source_relative in ASSET_FILES:
        asset_relative = source_relative.split("content/images/", 1)[1]
        target = workspace / "apps/healthclinic-web/public/assets" / asset_relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_root / source_relative, target)
    return _advance(state, NODES[4], {"source_hash_after": _tree_hash(source_root)})


def _task_statuses() -> list[TaskExecutionStatus]:
    implemented = {
        "TT-001": "Angular 22/Nx workspace generated with zoneless-compatible package configuration.",
        "TT-002": "Five tagged Nx library boundaries define app, feature, UI, data, state, and platform responsibilities.",
        "TT-003": "Shared Dashboard UI primitives and source-derived visual tokens are implemented.",
        "TT-004": "Typed models and clients preserve all four existing API contracts.",
        "TT-008": "The /dashboard route is lazy-loaded through Angular Router.",
        "TT-009": "Standalone private shell and Dashboard feature components are generated.",
        "TT-010": "Signals own UI state and RxJS owns tenant-aware asynchronous loading and cancellation.",
        "TT-011": "Tenant context is retrieved and propagated through the approved TenantId header behavior without an identity-provider assumption.",
        "TT-012": "Clinic cards and both yearly report regions reconstruct the existing Dashboard presentation.",
        "TT-013": "Semantic controls, labels, focus indicators, status regions, and responsive layouts are generated.",
    }
    partial = {
        "TT-007": "Configurable API base URL and typed client boundary are implemented; the future BFF facade remains TARGET_CONTRACT_TO_BE_DESIGNED.",
        "TT-014": "Frontend correlation and centralized HTTP error foundations are implemented; deployment-layer telemetry remains deferred.",
        "TT-015": "Unit/component test sources are generated but not executed in this generation stage.",
        "TT-016": "Playwright scenarios map all five hero AC but are not executed in this generation stage.",
    }
    deferred = {
        "TT-005": "Provider-neutral Gateway implementation is DEFERRED_TO_DEPLOYMENT.",
        "TT-006": "BFF implementation is deferred; its facade remains TARGET_CONTRACT_TO_BE_DESIGNED.",
    }
    refs = {
        "TT-001": ["package.json", "nx.json", "apps/healthclinic-web/project.json"],
        "TT-002": ["libs/dashboard/feature/project.json", "libs/dashboard/data-access/project.json", "libs/dashboard/state/project.json"],
        "TT-003": ["libs/dashboard/ui/src/index.ts", "apps/healthclinic-web/src/styles.css"],
        "TT-004": ["libs/dashboard/data-access/src/lib/dashboard.models.ts", "libs/dashboard/data-access/src/lib/dashboard-api.client.ts"],
        "TT-007": ["libs/core/platform/src/lib/runtime-config.ts", "libs/dashboard/data-access/src/lib/dashboard-api.client.ts"],
        "TT-008": ["apps/healthclinic-web/src/app/app.routes.ts", "libs/dashboard/feature/src/lib/dashboard.routes.ts"],
        "TT-009": ["apps/healthclinic-web/src/app/private-shell.component.ts", "libs/dashboard/feature/src/lib/dashboard-feature.component.ts"],
        "TT-010": ["libs/dashboard/state/src/lib/dashboard.store.ts"],
        "TT-011": ["libs/core/platform/src/lib/tenant-context.service.ts"],
        "TT-012": ["libs/dashboard/feature/src/lib/dashboard-feature.component.html"],
        "TT-013": ["libs/dashboard/ui/src/lib/year-navigator.component.ts", "apps/healthclinic-web/src/app/private-shell.component.css"],
        "TT-014": ["libs/core/platform/src/lib/correlation.interceptor.ts", "libs/core/platform/src/lib/error.interceptor.ts", "libs/core/platform/src/lib/frontend-logger.service.ts"],
        "TT-015": ["libs/dashboard/feature/src/lib/dashboard-feature.component.spec.ts", "libs/dashboard/state/src/lib/dashboard.store.spec.ts"],
        "TT-016": ["apps/healthclinic-web-e2e/src/dashboard.spec.ts"],
    }
    result = []
    for index in range(1, 17):
        task_id = f"TT-{index:03d}"
        if task_id in implemented:
            result.append(TaskExecutionStatus(task_id=task_id, status="IMPLEMENTED", detail=implemented[task_id], generated_file_refs=refs.get(task_id, [])))
        elif task_id in partial:
            result.append(TaskExecutionStatus(task_id=task_id, status="PARTIALLY_IMPLEMENTED", detail=partial[task_id], generated_file_refs=refs.get(task_id, [])))
        else:
            result.append(TaskExecutionStatus(task_id=task_id, status="DEFERRED", detail=deferred[task_id]))
    return result


def _traceability(task_statuses: list[dict], ui: dict) -> dict:
    ac = {
        "ac-operational-dashboard-insights-access-yearly-operational-reports-001": (["DashboardFeatureComponent", "DashboardStore", "DashboardApiClient", "YearNavigatorComponent"], ["dashboard-api.client.spec.ts", "dashboard.store.spec.ts", "year-navigator.component.spec.ts", "dashboard.spec.ts"]),
        "ac-operational-dashboard-insights-view-tenant-aware-dashboard-summary-001": (["DashboardFeatureComponent", "SummaryCardComponent", "TenantContextService"], ["dashboard-feature.component.spec.ts", "dashboard-api.client.spec.ts", "dashboard.spec.ts"]),
        "ac-operational-dashboard-insights-view-tenant-aware-dashboard-summary-002": (["DashboardApiClient", "DashboardStore", "TenantContextService"], ["dashboard-api.client.spec.ts", "dashboard.store.spec.ts", "dashboard.spec.ts"]),
        "ac-operational-dashboard-insights-open-operational-dashboard-001": (["appRoutes", "DASHBOARD_ROUTES", "DashboardFeatureComponent"], ["app.routes.spec.ts", "dashboard-feature.component.spec.ts", "dashboard.spec.ts"]),
        "ac-operational-dashboard-insights-open-operational-dashboard-002": (["PrivateShellComponent", "DashboardFeatureComponent"], ["app.routes.spec.ts", "dashboard-feature.component.spec.ts", "dashboard.spec.ts"]),
    }
    return {
        "feature": [{"id": "feature-operational-dashboard-insights", "generated_refs": ["DashboardFeatureComponent", "DASHBOARD_ROUTES"]}],
        "functional_requirements": [
            {"id": "FR-01", "generated_refs": ["PrivateShellComponent", "DASHBOARD_ROUTES"]},
            {"id": "FR-02", "generated_refs": ["DashboardApiClient.getExpenses", "DashboardChartComponent"]},
            {"id": "FR-03", "generated_refs": ["DashboardApiClient.getPatients", "DashboardChartComponent"]},
            {"id": "FR-04", "generated_refs": ["DashboardApiClient.getClinicSummary", "SummaryCardComponent"]},
            {"id": "FR-05", "generated_refs": ["TenantContextService", "DashboardStore"]},
        ],
        "stories": [
            {"id": "US-01", "generated_refs": ["DashboardStore", "DashboardChartComponent", "YearNavigatorComponent"]},
            {"id": "US-02", "generated_refs": ["TenantContextService", "SummaryCardComponent"]},
            {"id": "US-03", "generated_refs": ["PrivateShellComponent", "DASHBOARD_ROUTES"]},
        ],
        "acceptance_criteria": [{"id": key, "implementation_refs": value[0], "test_refs": value[1]} for key, value in ac.items()],
        "architecture_decisions": ["ARCH-001", "ARCH-003", "ARCH-006", "ARCH-008", "ARCH-009", "ARCH-010", "ARCH-012", "ARCH-013", "ARCH-015", "ARCH-016", "ARCH-017", "ARCH-021", "ARCH-024", "ARCH-025", "ARCH-028", "ARCH-034", "ARCH-037", "ARCH-038", "ARCH-039", "ARCH-041", "ARCH-044", "ARCH-046", "ARCH-048", "ARCH-049", "ARCH-050", "ARCH-051", "ARCH-052"],
        "adrs": ["ADR-001", "ADR-002", "ADR-003", "ADR-004", "ADR-005", "ADR-007", "ADR-008", "ADR-009"],
        "technical_tasks": task_statuses,
        "source_ui": [{"source_ref": item["id"], "source_path": item["source_path"], "target_refs": [region["target"] for region in ui["regions"] if region["source_ref"] == item["id"]]} for item in ui["surfaces"]],
        "route_mappings": ui["navigation"],
    }


def _build_traceability(state: GenerationState) -> GenerationState:
    workspace = Path(state["workspace"])
    task_statuses = [item.model_dump(mode="json") for item in _task_statuses()]
    traceability = _traceability(task_statuses, state["ui_specification"])
    acceptance_criteria_ids = [item["id"] for item in traceability["acceptance_criteria"]]
    generated_files = sorted([*state["file_templates"], *[f"apps/healthclinic-web/public/assets/{path.split('content/images/', 1)[1]}" for path in ASSET_FILES]])
    components = [
        {"name": "AppComponent", "kind": "ROOT", "file": "apps/healthclinic-web/src/app/app.component.ts"},
        {"name": "PrivateShellComponent", "kind": "SHELL", "file": "apps/healthclinic-web/src/app/private-shell.component.ts"},
        {"name": "DashboardFeatureComponent", "kind": "FEATURE", "file": "libs/dashboard/feature/src/lib/dashboard-feature.component.ts"},
        {"name": "SummaryCardComponent", "kind": "UI", "file": "libs/dashboard/ui/src/lib/summary-card.component.ts"},
        {"name": "YearNavigatorComponent", "kind": "UI", "file": "libs/dashboard/ui/src/lib/year-navigator.component.ts"},
        {"name": "DashboardChartComponent", "kind": "UI", "file": "libs/dashboard/ui/src/lib/dashboard-chart.component.ts"},
    ]
    tests = [
        {"file": "apps/healthclinic-web/src/app/app.routes.spec.ts", "acceptance_criteria_refs": ["ac-operational-dashboard-insights-open-operational-dashboard-001", "ac-operational-dashboard-insights-open-operational-dashboard-002"]},
        {"file": "libs/dashboard/ui/src/lib/year-navigator.component.spec.ts", "acceptance_criteria_refs": ["ac-operational-dashboard-insights-access-yearly-operational-reports-001"]},
        {"file": "libs/dashboard/data-access/src/lib/dashboard-api.client.spec.ts", "acceptance_criteria_refs": ["ac-operational-dashboard-insights-access-yearly-operational-reports-001", "ac-operational-dashboard-insights-view-tenant-aware-dashboard-summary-001", "ac-operational-dashboard-insights-view-tenant-aware-dashboard-summary-002"]},
        {"file": "libs/dashboard/state/src/lib/dashboard.store.spec.ts", "acceptance_criteria_refs": ["ac-operational-dashboard-insights-access-yearly-operational-reports-001", "ac-operational-dashboard-insights-view-tenant-aware-dashboard-summary-002"]},
        {"file": "libs/dashboard/feature/src/lib/dashboard-feature.component.spec.ts", "acceptance_criteria_refs": acceptance_criteria_ids},
        {"file": "apps/healthclinic-web-e2e/src/dashboard.spec.ts", "acceptance_criteria_refs": acceptance_criteria_ids},
    ]
    manifest = GenerationManifest(
        project_id=state["project_id"], feature_id=state["feature_id"], source_ui_mode="EXISTING_APPLICATION_UI",
        architecture_selection_ref=str(Path(state["architecture_root"]) / "architecture-selection.json"),
        technical_task_ref=str(Path(state["technical_task_root"]) / "technical-tasks.json"), generated_workspace=str(workspace),
        generated_files=generated_files, generated_components=components,
        generated_services=[{"name": name, "file": file} for name, file in (("DashboardApiClient", "libs/dashboard/data-access/src/lib/dashboard-api.client.ts"), ("DashboardStore", "libs/dashboard/state/src/lib/dashboard.store.ts"), ("TenantContextService", "libs/core/platform/src/lib/tenant-context.service.ts"), ("FrontendErrorService", "libs/core/platform/src/lib/error.interceptor.ts"), ("FrontendLogger", "libs/core/platform/src/lib/frontend-logger.service.ts"))],
        generated_routes=[{"name": "appRoutes", "path": "/", "file": "apps/healthclinic-web/src/app/app.routes.ts"}, {"name": "DASHBOARD_ROUTES", "path": "/dashboard", "file": "libs/dashboard/feature/src/lib/dashboard.routes.ts"}],
        generated_models=[{"name": name, "file": file} for name, file in (("ClinicSummary", "libs/dashboard/data-access/src/lib/dashboard.models.ts"), ("ExpensesSummary", "libs/dashboard/data-access/src/lib/dashboard.models.ts"), ("PatientsSummary", "libs/dashboard/data-access/src/lib/dashboard.models.ts"), ("TenantId", "libs/dashboard/data-access/src/lib/dashboard.models.ts"), ("RuntimeConfig", "libs/core/platform/src/lib/runtime-config.ts"))],
        generated_tests=tests, preserved_api_contracts=state["architecture"]["selection"]["existing_api_contracts"],
        reused_assets=[{"source_path": path, "generated_path": f"apps/healthclinic-web/public/assets/{path.split('content/images/', 1)[1]}"} for path in ASSET_FILES],
        task_statuses=task_statuses,
        unresolved_items=[*state["ui_specification"]["unresolved_visual_details"], {"status": "DEFERRED_TO_DEPLOYMENT", "item": "API Gateway", "detail": "No Gateway infrastructure is generated."}, {"status": "TARGET_CONTRACT_TO_BE_DESIGNED", "item": "BFF facade", "detail": "The Angular client remains compatible with a configurable future BFF base URL."}],
        generation_timestamp=datetime.now(timezone.utc).isoformat(), generator={"name": "Polaris deterministic Angular hero generator", "version": "1.0", "external_llm_calls": 0},
    ).model_dump(mode="json")
    return _advance(state, NODES[5], {"manifest": manifest, "traceability": traceability})


def _validate(state: GenerationState) -> GenerationState:
    result = validate_generation({"workspace": state["workspace"], "manifest": state["manifest"], "traceability": state["traceability"], "ui_specification": state["ui_specification"], "source_hash_before": state["source_hash_before"], "source_hash_after": state["source_hash_after"]})
    return _advance(state, NODES[6], {"validation": result})


def _finalize(state: GenerationState) -> GenerationState:
    if state["validation"]["status"] != "PASS":
        raise ModernizationGenerationError(f"Generation validation failed: {state['validation']['blockers']}")
    return _advance(state, NODES[7], {"status": "MODERNIZATION_GENERATION_READY"})


def build_generation_graph():
    graph = StateGraph(GenerationState)
    functions = (_load_frozen, _load_existing_ui, _reconstruct, _compose, _generate, _build_traceability, _validate, _finalize)
    for name, function in zip(NODES, functions, strict=True):
        graph.add_node(name, function)
    graph.add_edge(START, NODES[0])
    for current, following in zip(NODES, NODES[1:]):
        graph.add_edge(current, following)
    graph.add_edge(NODES[-1], END)
    return graph.compile()


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")


def generate_angular_hero(project_id: str, feature_id: str, source_root: Path, architecture_root: Path, technical_task_root: Path, specification_root: Path, workspace: Path, output_root: Path) -> dict:
    state = build_generation_graph().invoke({"project_id": project_id, "feature_id": feature_id, "source_root": str(source_root), "architecture_root": str(architecture_root), "technical_task_root": str(technical_task_root), "specification_root": str(specification_root), "workspace": str(workspace), "nodes_executed": [], "state_transitions": [], "current_stage": "START", "status": "STARTED"})
    run_id = f"{project_id}-{datetime.now(timezone.utc).strftime('%Y-%m-%d-%H%M%S-%f')}"
    workflow = {"workflow_id": run_id, "nodes_executed": state["nodes_executed"], "state_transitions": state["state_transitions"], "start_status": "STARTED", "final_status": state["status"], "langgraph_execution": True, "langchain_boundary": "RunnableLambda (offline deterministic Angular workspace composition)", "langchain_runnable_execution": True, "external_llm_calls": 0, "build_executed": False, "generated_tests_executed": False}
    contract = {"manifest": state["manifest"], "ui_specification": state["ui_specification"], "traceability": state["traceability"], "validation": state["validation"], "workflow": workflow}
    run = output_root / "runs" / run_id
    run.mkdir(parents=True)
    _write_json(run / "generation-manifest.json", state["manifest"])
    _write_json(run / "ui-reconstruction.json", state["ui_specification"])
    (run / "ui-reconstruction.md").write_text(render_ui_markdown(state["ui_specification"]), encoding="utf-8")
    (run / "ui-reconstruction.html").write_text(render_ui_html(state["ui_specification"]), encoding="utf-8")
    _write_json(run / "traceability.json", state["traceability"])
    (run / "traceability.md").write_text(render_traceability_markdown(state["traceability"]), encoding="utf-8")
    _write_json(run / "generation-validation.json", state["validation"])
    _write_json(run / "workflow-run.json", workflow)
    _write_json(run / "pep-validation.json", PepValidationContract().model_dump(mode="json"))
    (run / "modernization.html").write_text(render_modernization_html(contract), encoding="utf-8")
    latest = output_root / "latest"
    shutil.rmtree(latest, ignore_errors=True)
    shutil.copytree(run, latest)
    return {"run_id": run_id, "path": run, "workspace": workspace, "state": state, "contract": contract}
