from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

import pytest

from polaris_modernization.modernization_generation.models import ExistingUiSpecification, GenerationManifest, PepValidationContract
from polaris_modernization.modernization_generation.reconstruction import reconstruct_existing_ui
from polaris_modernization.modernization_generation.renderers import render_modernization_html
from polaris_modernization.modernization_generation.workflow import NODES, generate_angular_hero


ROOT = Path(__file__).parents[1]
SOURCE = ROOT / "source" / "HealthClinic.biz"
ARCHITECTURE = ROOT / "artifacts" / "architecture" / "latest"
TASKS = ROOT / "artifacts" / "technical-tasks" / "latest"
SPECIFICATIONS = ROOT / "artifacts" / "feature-specifications" / "latest"
FEATURE_ID = "feature-operational-dashboard-insights"
PROJECT_ID = "legacy-dashboard-complete-application-demo-v1"
EXPECTED_APIS = {
    ("GET", "/api/reports/expenses/{year}"),
    ("GET", "/api/reports/patients/{year}"),
    ("GET", "/api/reports/clinicsummary"),
    ("GET", "/api/users/current/tenant"),
}
AC_IDS = {
    "ac-operational-dashboard-insights-access-yearly-operational-reports-001",
    "ac-operational-dashboard-insights-view-tenant-aware-dashboard-summary-001",
    "ac-operational-dashboard-insights-view-tenant-aware-dashboard-summary-002",
    "ac-operational-dashboard-insights-open-operational-dashboard-001",
    "ac-operational-dashboard-insights-open-operational-dashboard-002",
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def generated(tmp_path_factory: pytest.TempPathFactory) -> dict:
    root = tmp_path_factory.mktemp("angular-generation")
    return generate_angular_hero(PROJECT_ID, FEATURE_ID, SOURCE, ARCHITECTURE, TASKS, SPECIFICATIONS, root / "modernized", root / "artifacts")


def test_existing_application_ui_is_the_only_design_source(generated: dict) -> None:
    manifest = generated["state"]["manifest"]
    assert manifest["source_ui_mode"] == "EXISTING_APPLICATION_UI"
    assert manifest["figma_for_generation"] == "DISABLED"
    assert generated["state"]["validation"]["checks"]["NO_FIGMA_FIXTURE_CONTAMINATION"]


def test_dashboard_razor_and_angularjs_surfaces_are_discovered(generated: dict) -> None:
    surfaces = generated["state"]["ui_specification"]["surfaces"]
    assert len([item for item in surfaces if item["kind"] == "RAZOR"]) == 5
    assert len([item for item in surfaces if item["kind"] == "ANGULARJS"]) == 6
    assert any(item["source_path"].endswith("Views/Dashboard/Index.cshtml") for item in surfaces)
    assert any(item["source_path"].endswith("dashboardController.js") for item in surfaces)


def test_ui_reconstruction_model_normalizes_regions_controls_and_sources(generated: dict) -> None:
    ui = ExistingUiSpecification.model_validate(generated["state"]["ui_specification"])
    assert len(ui.regions) == 10
    assert len(ui.controls) == 6
    assert len(ui.source_traceability) == 30
    assert len([item for item in ui.surfaces if item["kind"] == "SHARED_UI"]) == 2
    assert {item["name"] for item in ui.regions} >= {"Clinic summary card row", "Income and expenses yearly chart", "Patient visits yearly chart"}
    assert {item["name"] for item in ui.controls} >= {"Previous income and expense year", "Next patient year"}


def test_source_ui_visible_text_layout_and_style_are_preserved(generated: dict) -> None:
    ui = generated["state"]["ui_specification"]
    labels = {item["text"] for item in ui["visible_text"]}
    tokens = {item["token"]: item["value"] for item in ui["styles"]}
    assert {"NEW PATIENTS", "MONTH BENEFITS", "ANNUAL BENEFITS", "INCOMES AND EXPENSES", "PATIENT VISITS"} <= labels
    assert tokens["summary-patients"] == "#00d8cc"
    assert tokens["private-shell"] == "#1d1e2a"
    assert any("Three equal columns" in item["relationship"] for item in ui["layouts"])


def test_reconstruction_records_honest_visual_clarifications(generated: dict) -> None:
    unresolved = generated["state"]["ui_specification"]["unresolved_visual_details"]
    assert len(unresolved) == 3
    assert all(item["status"] == "UI_RECONSTRUCTION_CLARIFICATION" for item in unresolved)


def test_nx_angular_22_workspace_is_generated(generated: dict) -> None:
    workspace = Path(generated["state"]["workspace"])
    package = read_json(workspace / "package.json")
    assert package["dependencies"]["@angular/core"] == "22.1.4"
    assert package["devDependencies"]["nx"] == package["devDependencies"]["@nx/angular"] == "23.2.0"
    assert (workspace / "nx.json").is_file()
    assert len(list(workspace.glob("libs/**/project.json"))) == 5
    assert "@nx/enforce-module-boundaries" in (workspace / "eslint.config.mjs").read_text(encoding="utf-8")


def test_standalone_components_are_generated(generated: dict) -> None:
    workspace = Path(generated["state"]["workspace"])
    components = generated["state"]["manifest"]["generated_components"]
    assert len(components) == 6
    assert all("standalone: true" in (workspace / item["file"]).read_text(encoding="utf-8") for item in components)


def test_signals_and_computed_are_used_for_feature_state(generated: dict) -> None:
    workspace = Path(generated["state"]["workspace"])
    store = (workspace / "libs/dashboard/state/src/lib/dashboard.store.ts").read_text(encoding="utf-8")
    feature = (workspace / "libs/dashboard/feature/src/lib/dashboard-feature.component.ts").read_text(encoding="utf-8")
    assert "signal(" in store and "computed(" in store and "toSignal(" in store
    assert "computed<ChartSeries[]>" in feature


def test_rxjs_owns_http_and_async_boundaries(generated: dict) -> None:
    workspace = Path(generated["state"]["workspace"])
    store = (workspace / "libs/dashboard/state/src/lib/dashboard.store.ts").read_text(encoding="utf-8")
    client = (workspace / "libs/dashboard/data-access/src/lib/dashboard-api.client.ts").read_text(encoding="utf-8")
    assert "switchMap" in store and "Observable" in store
    assert "HttpClient" in client and "Observable" in client


@pytest.mark.parametrize("needle", ["ngrx", "@angular/ssr", "provideClientHydration", "microfrontend", "module federation", "module-federation"])
def test_unselected_technologies_are_absent(generated: dict, needle: str) -> None:
    workspace = Path(generated["state"]["workspace"])
    combined = "\n".join(path.read_text(encoding="utf-8", errors="ignore") for path in workspace.rglob("*") if path.is_file() and path.suffix not in {".png"})
    assert needle.lower() not in combined.lower()


def test_zoneless_target_has_no_zone_dependency(generated: dict) -> None:
    workspace = Path(generated["state"]["workspace"])
    assert "zone.js" not in (workspace / "package.json").read_text(encoding="utf-8").lower()
    assert generated["state"]["validation"]["checks"]["ZONELESS_TARGET_ALIGNED"]


def test_lazy_dashboard_route_and_functional_guard_are_generated(generated: dict) -> None:
    workspace = Path(generated["state"]["workspace"])
    routes = (workspace / "apps/healthclinic-web/src/app/app.routes.ts").read_text(encoding="utf-8")
    guard = (workspace / "libs/core/platform/src/lib/dashboard-route.guard.ts").read_text(encoding="utf-8")
    assert "path: 'dashboard'" in routes and "loadChildren" in routes
    assert "canActivate: [dashboardRouteGuard]" in routes
    assert "CanActivateFn" in guard and "authorization rules remain unselected" in guard


def test_typed_api_client_preserves_exact_existing_contracts(generated: dict) -> None:
    manifest = GenerationManifest.model_validate(generated["state"]["manifest"])
    assert {(item["method"], item["endpoint"]) for item in manifest.preserved_api_contracts} == EXPECTED_APIS
    assert generated["state"]["validation"]["checks"]["NO_INVENTED_EXISTING_API"]
    assert len(manifest.generated_models) == 5


def test_tenant_context_and_header_propagation_are_generated(generated: dict) -> None:
    workspace = Path(generated["state"]["workspace"])
    tenant = (workspace / "libs/core/platform/src/lib/tenant-context.service.ts").read_text(encoding="utf-8")
    client = (workspace / "libs/dashboard/data-access/src/lib/dashboard-api.client.ts").read_text(encoding="utf-8")
    assert "/api/users/current/tenant" in tenant
    assert "TenantId" in client


def test_vendor_neutral_error_and_logging_boundaries_are_generated(generated: dict) -> None:
    workspace = Path(generated["state"]["workspace"])
    errors = (workspace / "libs/core/platform/src/lib/error.interceptor.ts").read_text(encoding="utf-8")
    logger = (workspace / "libs/core/platform/src/lib/frontend-logger.service.ts").read_text(encoding="utf-8")
    assert "FrontendLogger" in errors and "dashboard_http_request_failed" in errors
    assert "class FrontendLogger" in logger
    assert len(generated["state"]["manifest"]["generated_services"]) == 5


def test_year_expense_patient_and_clinic_behaviors_are_generated(generated: dict) -> None:
    workspace = Path(generated["state"]["workspace"])
    template = (workspace / "libs/dashboard/feature/src/lib/dashboard-feature.component.html").read_text(encoding="utf-8")
    store = (workspace / "libs/dashboard/state/src/lib/dashboard.store.ts").read_text(encoding="utf-8")
    assert "INCOMES AND EXPENSES" in template and "PATIENT VISITS" in template and "Clinic summary" in template
    assert "incomeExpenseYear" in store and "patientYear" in store
    assert "Math.min(this.currentYear" in store


def test_existing_ui_assets_are_selectively_reused(generated: dict) -> None:
    workspace = Path(generated["state"]["workspace"])
    assets = generated["state"]["manifest"]["reused_assets"]
    assert len(assets) == 9
    assert all((workspace / item["generated_path"]).is_file() for item in assets)
    assert all("dashboard" in item["source_path"] or "private" in item["source_path"] for item in assets)
    generated_text = "\n".join(path.read_text(encoding="utf-8") for path in workspace.rglob("*") if path.is_file() and path.suffix in {".ts", ".html", ".css"})
    assert all(Path(item["generated_path"]).name in generated_text for item in assets)


def test_api_base_url_is_loaded_from_runtime_configuration(generated: dict) -> None:
    workspace = Path(generated["state"]["workspace"])
    index = (workspace / "apps/healthclinic-web/src/index.html").read_text(encoding="utf-8")
    config = (workspace / "apps/healthclinic-web/src/app/app.config.ts").read_text(encoding="utf-8")
    assert 'src="runtime-config.js"' in index
    assert "__HEALTHCLINIC_CONFIG__" in config


def test_all_sixteen_technical_tasks_are_honestly_accounted_for(generated: dict) -> None:
    statuses = generated["state"]["manifest"]["task_statuses"]
    assert {item["task_id"] for item in statuses} == {f"TT-{index:03d}" for index in range(1, 17)}
    assert sum(item["status"] == "IMPLEMENTED" for item in statuses) == 10
    assert sum(item["status"] == "PARTIALLY_IMPLEMENTED" for item in statuses) == 4
    assert sum(item["status"] == "DEFERRED" for item in statuses) == 2
    assert sum(item["status"] == "NOT_APPLICABLE" for item in statuses) == 0


def test_hero_requirement_story_and_ac_traceability_is_complete(generated: dict) -> None:
    trace = generated["state"]["traceability"]
    assert {item["id"] for item in trace["functional_requirements"]} == {f"FR-{index:02d}" for index in range(1, 6)}
    assert {item["id"] for item in trace["stories"]} == {"US-01", "US-02", "US-03"}
    assert {item["id"] for item in trace["acceptance_criteria"]} == AC_IDS
    assert all(item["implementation_refs"] and item["test_refs"] for item in trace["acceptance_criteria"])


def test_generated_tests_map_to_every_ac_without_execution(generated: dict) -> None:
    manifest = generated["state"]["manifest"]
    assert len(manifest["generated_tests"]) == 6
    assert {ref for item in manifest["generated_tests"] for ref in item["acceptance_criteria_refs"]} == AC_IDS
    assert manifest["generated_test_status"] == "NOT_YET_EXECUTED"
    assert generated["state"]["validation"]["generated_tests_executed"] is False


def test_generation_manifest_and_pep_contract_are_valid(generated: dict) -> None:
    latest = Path(generated["path"]).parent.parent / "latest"
    manifest = GenerationManifest.model_validate(read_json(latest / "generation-manifest.json"))
    pep = PepValidationContract.model_validate(read_json(latest / "pep-validation.json"))
    assert manifest.generated_workspace
    assert manifest.build_status == "NOT_YET_EXECUTED"
    assert pep.status == "NOT_STARTED"


def test_modernization_artifacts_are_generated(generated: dict) -> None:
    latest = Path(generated["path"]).parent.parent / "latest"
    expected = {"generation-manifest.json", "generation-validation.json", "modernization.html", "pep-validation.json", "traceability.json", "traceability.md", "ui-reconstruction.html", "ui-reconstruction.json", "ui-reconstruction.md", "workflow-run.json"}
    assert {path.name for path in latest.iterdir() if path.is_file()} == expected
    assert read_json(latest / "generation-validation.json")["status"] == "PASS"


def test_modernization_html_is_data_driven_and_customer_safe(generated: dict) -> None:
    contract = generated["contract"]
    html = render_modernization_html(contract)
    changed = json.loads(json.dumps(contract))
    changed["manifest"]["generated_components"][0]["name"] = "ChangedComponent"
    assert "ChangedComponent" in render_modernization_html(changed)
    for phrase in ("Existing UI", "Angular 22", "API Contract Preservation", "Technical Task Progress", "NOT YET EXECUTED"):
        assert phrase in html
    for internal in ("Tree-sitter", "Roslyn", "analyzer warning", "KG internals"):
        assert internal not in html


def test_real_langgraph_and_langchain_generation_boundaries_execute(generated: dict) -> None:
    workflow = generated["contract"]["workflow"]
    assert workflow["nodes_executed"] == NODES
    assert workflow["langgraph_execution"] is True
    assert workflow["langchain_runnable_execution"] is True
    assert workflow["external_llm_calls"] == 0


def test_static_generation_validator_passes_without_build_claim(generated: dict) -> None:
    validation = generated["state"]["validation"]
    assert validation["status"] == "PASS"
    assert all(validation["checks"].values())
    assert validation["static_validation_only"] is True
    assert validation["build_executed"] is False


def test_frozen_business_architecture_and_task_contracts_are_unchanged() -> None:
    specification = read_json(SPECIFICATIONS / "jira-quality.json")
    assert len(specification["features"]) == 5
    assert sum(len(feature["stories"]) for feature in specification["features"]) == 12
    assert sum(len(story["acceptance_criteria"]) for feature in specification["features"] for story in feature["stories"]) == 14
    assert sha256((ARCHITECTURE / "architecture-selection.json").read_bytes()).hexdigest() == "661bdacf00f061718afef9862bd9875a44d976451407cf0dc6c76006bcf9e8fb"
    assert sha256((TASKS / "technical-tasks.json").read_bytes()).hexdigest() == "fa773edaf3ea82ff1fdc009b9b4cadbcf94c717283d6c9b02ecf454ae7687182"


def test_source_tree_is_unchanged_by_generation(tmp_path: Path) -> None:
    before = {path.relative_to(SOURCE): (path.stat().st_size, path.stat().st_mtime_ns) for path in SOURCE.rglob("*") if path.is_file()}
    generate_angular_hero(PROJECT_ID, FEATURE_ID, SOURCE, ARCHITECTURE, TASKS, SPECIFICATIONS, tmp_path / "modernized", tmp_path / "artifacts")
    after = {path.relative_to(SOURCE): (path.stat().st_size, path.stat().st_mtime_ns) for path in SOURCE.rglob("*") if path.is_file()}
    assert after == before


def test_reconstruction_can_run_independently_from_figma() -> None:
    ui = reconstruct_existing_ui(SOURCE, FEATURE_ID)
    assert ui.source_mode == "EXISTING_APPLICATION_UI"
    assert not any("figma" in json.dumps(item).lower() for item in ui.model_dump(mode="json").values())
