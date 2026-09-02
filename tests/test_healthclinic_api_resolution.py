import hashlib
from pathlib import Path

import pytest

from polaris_modernization.framework_analyzers import AspNetRouteAnalyzer
from polaris_modernization.graph.api_mapping import resolve_api_relationships
from polaris_modernization.tree_sitter_extractors.registry import extractor_for


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "source" / "HealthClinic.biz"
FRONTEND_FILES = [
    "src/MyHealth.Web/content/app/components/clinics/services/clinicsService.js",
    "src/MyHealth.Web/content/app/components/dashboard/services/dashboardService.js",
    "src/MyHealth.Web/content/app/components/doctors/services/doctorsService.js",
    "src/MyHealth.Web/content/app/components/patients/services/patientsService.js",
    "src/MyHealth.Web/content/app/components/shared/controllers/headerController.js",
    "src/MyHealth.Web/content/app/components/shared/services/initialPageService.js",
    "src/MyHealth.Web/content/app/components/users/services/usersService.js",
]
BACKEND_FILES = [
    "src/MyHealth.API/Controllers/DoctorsController.cs",
    "src/MyHealth.API/Controllers/PatientsController.cs",
    "src/MyHealth.API/Controllers/ReportsController.cs",
    "src/MyHealth.API/Controllers/TenantsController.cs",
    "src/MyHealth.API/Controllers/UsersController.cs",
]


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _entry(relative_path: str) -> dict:
    path = SOURCE_ROOT / relative_path
    return {"selected_for_extraction": True, "source_path": relative_path, "source_hash": _hash(path)}


def _frontend_facts(relative_path: str):
    path = SOURCE_ROOT / relative_path
    extractor = extractor_for(path)
    if extractor is None:
        raise AssertionError(f"No extractor is available for {relative_path}")
    return extractor.extract(path, SOURCE_ROOT, _hash(path), "fixture")


@pytest.fixture(scope="module")
def healthclinic_api_resolution() -> dict[str, object]:
    facts = []
    for relative_path in FRONTEND_FILES:
        facts.extend(_frontend_facts(relative_path))
    facts.extend(AspNetRouteAnalyzer().analyze(SOURCE_ROOT, [_entry(path) for path in BACKEND_FILES], "fixture").facts)
    return resolve_api_relationships(facts)


def _row(resolution: dict[str, object], source_file: str, raw_url_expression: str, method: str) -> dict:
    return next(
        row for row in resolution["audit_rows"]
        if row["source_file"] == source_file
        and row["raw_url_expression"] == raw_url_expression
        and row["http_method"] == method
    )


def test_healthclinic_actual_repository_patterns_are_proven(healthclinic_api_resolution):
    expectations = {
        ("src/MyHealth.Web/content/app/components/doctors/services/doctorsService.js", "/api/doctors", "GET"): ("UNRESOLVED", "PROVEN_EXACT_STATIC"),
        ("src/MyHealth.Web/content/app/components/doctors/services/doctorsService.js", "`/api/doctors/${doctorId}`", "GET"): ("DYNAMIC", "PROVEN_EXACT_TEMPLATE"),
        ("src/MyHealth.Web/content/app/components/patients/services/patientsService.js", "/api/patients", "GET"): ("UNRESOLVED", "PROVEN_EXACT_STATIC"),
        ("src/MyHealth.Web/content/app/components/dashboard/services/dashboardService.js", "'/api/reports/expenses/' + year", "GET"): ("DYNAMIC", "PROVEN_EXACT_TEMPLATE"),
        ("src/MyHealth.Web/content/app/components/dashboard/services/dashboardService.js", "'/api/reports/patients/' + year", "GET"): ("DYNAMIC", "PROVEN_EXACT_TEMPLATE"),
        ("src/MyHealth.Web/content/app/components/dashboard/services/dashboardService.js", "/api/reports/clinicsummary", "GET"): ("UNRESOLVED", "PROVEN_EXACT_STATIC"),
        ("src/MyHealth.Web/content/app/components/clinics/services/clinicsService.js", "`/api/tenants/${tenantId}`", "GET"): ("DYNAMIC", "PROVEN_EXACT_TEMPLATE"),
        ("src/MyHealth.Web/content/app/components/clinics/services/clinicsService.js", "/api/tenants/list", "GET"): ("UNRESOLVED", "PROVEN_EXACT_STATIC"),
        ("src/MyHealth.Web/content/app/components/shared/controllers/headerController.js", "/api/users/current/user", "GET"): ("PROVEN", "PROVEN_EXACT_STATIC"),
        ("src/MyHealth.Web/content/app/components/shared/controllers/headerController.js", "/api/users/current/claims", "GET"): ("PROVEN", "PROVEN_EXACT_STATIC"),
        ("src/MyHealth.Web/content/app/components/users/services/usersService.js", "/api/users/current/tenant", "GET"): ("PROVEN", "PROVEN_EXACT_STATIC"),
    }
    for key, (previous, final) in expectations.items():
        row = _row(healthclinic_api_resolution, *key)
        assert row["previous_status"] == previous
        assert row["final_status"] == final
        assert row["public_status"] == "PROVEN"
        assert row["candidate_backend_endpoints"]


def test_healthclinic_subset_has_no_remaining_internal_uncertainty(healthclinic_api_resolution):
    summary = healthclinic_api_resolution["summary"]
    assert summary["total_frontend_calls"] == len(healthclinic_api_resolution["audit_rows"])
    assert summary["final_proven"] == summary["total_frontend_calls"]
    assert summary["remaining_dynamic"] == 0
    assert summary["remaining_ambiguous"] == 0
    assert summary["external"] == 0
    assert summary["no_backend_match"] == 0
    assert summary["unresolved"] == 0
