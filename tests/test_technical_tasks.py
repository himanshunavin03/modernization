from __future__ import annotations

import io
import json
from pathlib import Path
from urllib.error import HTTPError

import pytest

from polaris_modernization.design.conflicts import detect_design_conflicts
from polaris_modernization.design.fixture import FIGMA_DASHBOARD_FIXTURE
from polaris_modernization.design.models import DesignMode, DesignRequirementLink, DesignSpecification, DesignStatus, FigmaReference
from polaris_modernization.design.normalizer import normalize_figma_response
from polaris_modernization.design.providers import FigmaDesignProvider, NoDesignProvider, parse_figma_url
from polaris_modernization.technical_tasks.models import TechnicalTaskCategory, TechnicalTaskModel
from polaris_modernization.technical_tasks.renderers import render_technical_tasks_html
from polaris_modernization.technical_tasks.workflow import NODES, build_technical_task_graph, generate_technical_tasks


ROOT = Path(__file__).parents[1]
ARCHITECTURE = ROOT / "artifacts" / "architecture" / "latest"
SPECIFICATIONS = ROOT / "artifacts" / "feature-specifications" / "latest"
FEATURE_ID = "feature-operational-dashboard-insights"
DOCTOR_FEATURE_ID = "feature-doctor-directory-management"
PROJECT_ID = "legacy-dashboard-complete-application-demo-v1"
EXPECTED_APIS = {
    ("GET", "/api/reports/expenses/{year}"),
    ("GET", "/api/reports/patients/{year}"),
    ("GET", "/api/reports/clinicsummary"),
    ("GET", "/api/users/current/tenant"),
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def run_plan(tmp_path: Path, provider: str = "NONE", mode: str = "NONE") -> dict:
    return generate_technical_tasks(PROJECT_ID, FEATURE_ID, ARCHITECTURE, SPECIFICATIONS, provider, mode, None, tmp_path / "tasks", tmp_path / "design")


def test_design_provider_interface_and_no_design_path() -> None:
    provider = NoDesignProvider()
    result = provider.analyze(None, DesignMode.NONE)
    assert provider.provider_type == "NO_DESIGN"
    assert result.status == DesignStatus.NOT_PROVIDED
    assert result.mode == DesignMode.NONE
    assert result.screens == []


@pytest.mark.parametrize("url,key,node", [
    ("https://www.figma.com/design/AbC_123/Dashboard?node-id=1-2", "AbC_123", "1-2"),
    ("https://figma.com/file/FileKey/Dashboard", "FileKey", None),
    ("https://www.figma.com/proto/Proto-Key/Dashboard?node-id=5%3A9", "Proto-Key", "5:9"),
])
def test_figma_url_parser_common_urls(url: str, key: str, node: str | None) -> None:
    result = parse_figma_url(url)
    assert result.file_key == key
    assert result.node_id == node
    assert result.provider == "FIGMA"
    assert result.normalized_reference.startswith(f"figma://file/{key}")


@pytest.mark.parametrize("url", [None, "", "https://example.com/design/key/name", "https://figma.com/community/key", "not a url"])
def test_figma_url_parser_rejects_malformed_urls(url: str | None) -> None:
    with pytest.raises(ValueError, match="FIGMA_INVALID_URL"):
        parse_figma_url(url)


def test_missing_figma_auth_is_safe_and_token_is_not_serialized(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FIGMA_ACCESS_TOKEN", raising=False)
    result = FigmaDesignProvider().analyze("https://www.figma.com/design/abc/Test", DesignMode.LIVE)
    assert result.status == DesignStatus.UNAVAILABLE
    assert result.error_code == "FIGMA_AUTH_NOT_CONFIGURED"
    serialized = result.model_dump_json()
    assert "FIGMA_ACCESS_TOKEN" not in serialized
    assert "X-Figma-Token" not in serialized


def test_denied_figma_access_is_explicit_and_secret_safe() -> None:
    secret = "test-secret-that-must-not-leak"

    def denied(request, timeout):
        raise HTTPError(request.full_url, 403, "Forbidden", {}, io.BytesIO())

    result = FigmaDesignProvider(opener=denied, token=secret).analyze("https://www.figma.com/design/abc/Test", DesignMode.LIVE)
    assert result.status == DesignStatus.UNAUTHORIZED
    assert result.error_code == "FIGMA_ACCESS_DENIED"
    assert secret not in result.model_dump_json()


def test_invalid_and_unavailable_figma_failures_are_distinct() -> None:
    invalid = FigmaDesignProvider(token="unused").analyze("invalid", DesignMode.LIVE)

    def unavailable(request, timeout):
        raise HTTPError(request.full_url, 404, "Missing", {}, io.BytesIO())

    missing = FigmaDesignProvider(opener=unavailable, token="unused").analyze("https://figma.com/file/abc/Test", DesignMode.LIVE)
    assert (invalid.status, invalid.error_code) == (DesignStatus.INVALID, "FIGMA_INVALID_URL")
    assert (missing.status, missing.error_code) == (DesignStatus.UNAVAILABLE, "FIGMA_DOCUMENT_UNAVAILABLE")


def test_fixture_mode_is_labeled_and_normalized() -> None:
    result = FigmaDesignProvider().analyze(None, DesignMode.FIXTURE)
    assert result.mode == DesignMode.FIXTURE
    assert result.status == DesignStatus.AVAILABLE
    assert result.document_name == "Operational Dashboard Fixture"
    assert {item["name"] for item in result.screens} == {"Operational Dashboard", "Summary cards"}
    assert result.components and result.component_instances and result.layouts
    assert result.controls and result.typography and result.colors and result.spacing


def test_partial_response_is_honestly_labeled() -> None:
    result = normalize_figma_response({"name": "Partial", "document": {"id": "0:0", "type": "DOCUMENT", "name": "Document"}}, FigmaReference(file_key="abc", normalized_reference="figma://file/abc"), DesignMode.LIVE)
    assert result.status == DesignStatus.PARTIAL
    assert result.unresolved_items


def test_design_does_not_infer_requirements_or_api_behavior() -> None:
    result = normalize_figma_response(FIGMA_DASHBOARD_FIXTURE, FigmaReference(file_key="FIXTURE_DASHBOARD", normalized_reference="figma://file/FIXTURE_DASHBOARD"), DesignMode.FIXTURE)
    serialized = result.model_dump_json()
    assert "/api/" not in serialized
    assert {link.requirement_ref for link in result.requirement_links} == {"FR-01", "FR-02"}


def test_explicit_design_conflict_preserves_requirement_priority() -> None:
    design = DesignSpecification(provider="FIGMA", mode="FIXTURE", status="AVAILABLE", requirement_links=[DesignRequirementLink(design_ref="figma://file/test?node-id=1", requirement_ref="FR-01", relationship="CONFLICTS", description="The explicit design link omits the required Dashboard access surface.")])
    result = detect_design_conflicts(design, {"FR-01"})
    assert result.conflicts[0].status == "DESIGN_REQUIREMENT_CONFLICT"
    assert result.conflicts[0].requirement_reference == "FR-01"
    assert "without changing" in result.conflicts[0].required_clarification


def test_no_design_and_fixture_workflows_reach_ready(tmp_path: Path) -> None:
    none = run_plan(tmp_path / "none")
    fixture = run_plan(tmp_path / "fixture", "FIGMA", "FIXTURE")
    assert none["plan"]["status"] == fixture["plan"]["status"] == "TECHNICAL_TASKS_READY"
    assert none["plan"]["design"]["status"] == "NOT_PROVIDED"
    assert fixture["plan"]["design"]["mode"] == "FIXTURE"
    assert fixture["workflow"]["nodes_executed"] == NODES
    assert fixture["workflow"]["langgraph_execution"] is True
    assert fixture["workflow"]["langchain_runnable_execution"] is True
    assert fixture["workflow"]["external_llm_calls"] == 0


def test_task_model_and_controlled_categories(tmp_path: Path) -> None:
    plan = run_plan(tmp_path)["plan"]
    assert all(TechnicalTaskModel.model_validate(item) for item in plan["tasks"])
    assert {item["category"] for item in plan["tasks"]} <= {item.value for item in TechnicalTaskCategory}
    assert len(plan["tasks"]) == 16


def test_non_hero_feature_plan_is_derived_from_its_own_contracts(tmp_path: Path) -> None:
    result = generate_technical_tasks(
        PROJECT_ID, DOCTOR_FEATURE_ID, ARCHITECTURE, SPECIFICATIONS,
        "NONE", "NONE", None, tmp_path / "tasks", tmp_path / "design",
    )
    plan = result["plan"]
    serialized_tasks = json.dumps(plan["tasks"])

    assert plan["feature_name"] == "Doctor Directory Management"
    assert plan["modernization_operation"] == {
        "operation_id": "angular-feature-modernization",
        "target": "ANGULAR",
        "selection_source": "LOCKED_ARCHITECTURE",
    }
    assert len(plan["tasks"]) == 16
    assert {item["story_id"] for item in plan["stories"]} == {"US-01", "US-02"}
    assert {item["endpoint"] for item in plan["existing_api_contracts"]} == {
        "/api/users/current/tenant", "/api/doctors/{id}", "/api/doctors",
    }
    assert plan["validation"]["status"] == "PASS"
    assert "Operational Dashboard" not in serialized_tasks
    assert "/api/reports" not in serialized_tasks


def test_tasks_load_locked_selection_and_use_selected_decisions_only(tmp_path: Path) -> None:
    plan = run_plan(tmp_path)["plan"]
    architecture = load_json(ARCHITECTURE / "architecture.json")
    selected = set(architecture["selection"]["selected_decision_ids"])
    assert plan["architecture_lock_status"] == "LOCKED"
    assert plan["architecture_selection_hash"] == architecture["architecture_lock"]["selection_hash"]
    assert all(set(task["architecture_decision_refs"]) <= selected for task in plan["tasks"])


def test_hero_only_ids_dependencies_cycles_and_order(tmp_path: Path) -> None:
    plan = run_plan(tmp_path)["plan"]
    validation = plan["validation"]
    assert {task["feature_id"] for task in plan["tasks"]} == {FEATURE_ID}
    assert validation["checks"]["task_ids_unique"]
    assert validation["checks"]["dependencies_exist"]
    assert validation["checks"]["implementation_order_valid"]
    assert validation["cycle_count"] == 0


def test_all_four_dashboard_apis_are_preserved_without_invention(tmp_path: Path) -> None:
    plan = run_plan(tmp_path)["plan"]
    assert {(api["method"], api["endpoint"]) for api in plan["existing_api_contracts"]} == EXPECTED_APIS
    assert plan["validation"]["checks"]["no_invented_existing_api"]
    assert set(plan["traceability"]["api_refs"]) == {"API-01", "API-02", "API-03", "API-04"}


def test_gateway_bff_and_target_contract_strategy(tmp_path: Path) -> None:
    tasks = run_plan(tmp_path)["plan"]["tasks"]
    gateway = next(item for item in tasks if item["category"] == "GATEWAY")
    bff = next(item for item in tasks if item["category"] == "BFF")
    assert set(gateway["api_refs"]) == set(bff["api_refs"]) == {"API-01", "API-02", "API-03", "API-04"}
    assert "TARGET_CONTRACT_TO_BE_DESIGNED" in " ".join(bff["implementation_requirements"])
    assert not any("/api/" in value for value in bff["implementation_requirements"])


@pytest.mark.parametrize("decision", ["ARCH-001", "ARCH-003", "ARCH-006", "ARCH-012", "ARCH-015", "ARCH-017", "ARCH-039", "ARCH-041", "ARCH-050"])
def test_selected_delivery_alignment_is_represented(tmp_path: Path, decision: str) -> None:
    tasks = run_plan(tmp_path)["plan"]["tasks"]
    assert any(decision in task["architecture_decision_refs"] for task in tasks)


@pytest.mark.parametrize("technology", ["NgRx", "Server-Side Rendering", "Hydration", "Microfrontends", "Module Federation"])
def test_unselected_technology_has_no_implementation_task(tmp_path: Path, technology: str) -> None:
    serialized = json.dumps(run_plan(tmp_path)["plan"]["tasks"])
    assert technology.lower() not in serialized.lower()


def test_acceptance_criteria_and_all_traceability_dimensions(tmp_path: Path) -> None:
    plan = run_plan(tmp_path, "FIGMA", "FIXTURE")["plan"]
    traceability = plan["traceability"]
    assert traceability["feature_refs"] == [FEATURE_ID]
    assert set(traceability["functional_requirement_refs"]) == {"FR-01", "FR-02", "FR-03", "FR-04", "FR-05"}
    assert set(traceability["story_refs"]) == {"US-01", "US-02", "US-03"}
    assert len(traceability["acceptance_criteria_refs"]) == 5
    assert traceability["api_refs"] and traceability["architecture_decision_refs"] and traceability["adr_refs"] and traceability["design_refs"]


def test_all_artifacts_are_generated_and_json_is_valid(tmp_path: Path) -> None:
    result = run_plan(tmp_path, "FIGMA", "FIXTURE")
    latest = tmp_path / "tasks" / "latest"
    design = tmp_path / "design" / "latest"
    assert load_json(latest / "technical-tasks.json")["status"] == "TECHNICAL_TASKS_READY"
    assert (latest / "technical-tasks.md").is_file()
    assert (latest / "technical-tasks.html").is_file()
    assert (design / "design.json").is_file() and (design / "design.md").is_file() and (design / "design.html").is_file()
    assert result["plan"]["design"]["mode"] == "FIXTURE"


def test_html_is_data_driven_and_customer_facing(tmp_path: Path) -> None:
    plan = run_plan(tmp_path, "FIGMA", "FIXTURE")["plan"]
    html = render_technical_tasks_html(plan)
    changed = json.loads(json.dumps(plan))
    changed["tasks"][0]["title"] = "Changed from machine contract"
    assert "Changed from machine contract" in render_technical_tasks_html(changed)
    for phrase in ("Selected architecture consumed", "Implementation Roadmap", "Gateway / BFF Delivery Areas", "/api/reports/expenses/{year}", "Design Input Status"):
        assert phrase in html
    for internal in ("Tree-sitter", "Roslyn", "KG internals", "source hash"):
        assert internal not in html


def test_frozen_business_and_architecture_baselines_remain_exact() -> None:
    specification = load_json(SPECIFICATIONS / "jira-quality.json")
    architecture = load_json(ARCHITECTURE / "architecture.json")
    assert len(specification["features"]) == 5
    assert sum(len(feature["stories"]) for feature in specification["features"]) == 12
    assert sum(len(story["acceptance_criteria"]) for feature in specification["features"] for story in feature["stories"]) == 14
    assert architecture["counts"]["decisions"] == 52
    assert architecture["architecture_lock"]["selection_hash"] == "0aa1b6f662bd9b41bd1a646a4c640ca8825bf8a5c0dd38383674e2a5cf46c3ed"


def test_source_tree_is_not_a_generation_target(tmp_path: Path) -> None:
    source = ROOT / "source" / "HealthClinic.biz"
    before = {path.relative_to(source): (path.stat().st_size, path.stat().st_mtime_ns) for path in source.rglob("*") if path.is_file()}
    run_plan(tmp_path)
    after = {path.relative_to(source): (path.stat().st_size, path.stat().st_mtime_ns) for path in source.rglob("*") if path.is_file()}
    assert after == before
