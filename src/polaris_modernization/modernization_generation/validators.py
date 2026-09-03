"""Static generation validators; these do not claim build or runtime success."""
from __future__ import annotations

import json
from pathlib import Path
import re


EXPECTED_APIS = {
    ("GET", "/api/reports/expenses/{year}"),
    ("GET", "/api/reports/patients/{year}"),
    ("GET", "/api/reports/clinicsummary"),
    ("GET", "/api/users/current/tenant"),
}


def validate_generation(context: dict) -> dict:
    workspace = Path(context["workspace"])
    manifest = context["manifest"]
    traceability = context["traceability"]
    ui = context["ui_specification"]
    texts = {path: (workspace / path).read_text(encoding="utf-8") for path in manifest["generated_files"] if path.endswith((".ts", ".html", ".css", ".json", ".md")) and (workspace / path).is_file()}
    combined = "\n".join(texts.values())
    package = json.loads(texts["package.json"])
    source_api_refs = set()
    for match in re.findall(r"/api/[A-Za-z0-9_/${}.-]+", combined):
        endpoint = match.replace("${year}", "{year}")
        endpoint = re.sub(r"(/api/reports/(?:expenses|patients)/)\d+$", r"\1{year}", endpoint)
        source_api_refs.add(("GET", endpoint))
    component_files = [item["file"] for item in manifest["generated_components"]]
    test_ac = {ref for item in manifest["generated_tests"] for ref in item["acceptance_criteria_refs"]}
    implementation_ac = {ref for item in traceability["acceptance_criteria"] for ref in item["implementation_refs"]}
    checks = {
        "GENERATED_WORKSPACE_EXISTS": workspace.is_dir() and all((workspace / path).is_file() for path in manifest["generated_files"]),
        "NX_ARCHITECTURE_ALIGNED": package["devDependencies"].get("nx", "").startswith("23.") and (workspace / "nx.json").is_file() and len(list(workspace.glob("libs/**/project.json"))) == 5,
        "ANGULAR_22_TARGETED": package["dependencies"].get("@angular/core", "").startswith("22."),
        "STANDALONE_COMPONENTS_USED": all("standalone: true" in texts[path] for path in component_files),
        "SIGNALS_STRATEGY_ALIGNED": "signal(" in combined and "computed(" in combined and "toSignal(" in combined,
        "RXJS_ASYNC_BOUNDARY_ALIGNED": "switchMap" in combined and "Observable" in combined and "HttpClient" in combined,
        "ZONELESS_TARGET_ALIGNED": "zone.js" not in combined.lower() and "provideZoneChangeDetection" not in combined,
        "NO_UNSELECTED_NGRX": "ngrx" not in combined.lower(),
        "NO_UNSELECTED_SSR": "@angular/ssr" not in json.dumps(package).lower(),
        "NO_UNSELECTED_HYDRATION": "provideClientHydration" not in combined,
        "NO_UNSELECTED_MICROFRONTEND": "microfrontend" not in combined.lower(),
        "NO_UNSELECTED_MODULE_FEDERATION": "module federation" not in combined.lower() and "module-federation" not in combined.lower(),
        "HERO_FEATURE_ONLY": manifest["feature_id"] == "feature-operational-dashboard-insights" and not any("doctor" in path or "patient-directory" in path for path in manifest["generated_files"]),
        "EXISTING_API_CONTRACTS_PRESERVED": {(item["method"], item["endpoint"]) for item in manifest["preserved_api_contracts"]} == EXPECTED_APIS and EXPECTED_APIS <= source_api_refs,
        "NO_INVENTED_EXISTING_API": source_api_refs <= EXPECTED_APIS,
        "UI_RECONSTRUCTION_TRACEABLE": ui["source_mode"] == "EXISTING_APPLICATION_UI" and all(item["source_ref"] in {surface["id"] for surface in ui["surfaces"]} for item in ui["regions"]),
        "CURRENT_GENERATION_DESIGN_SOURCE_IS_EXISTING_UI": manifest["source_ui_mode"] == "EXISTING_APPLICATION_UI",
        "NO_FIGMA_FIXTURE_CONTAMINATION": manifest["figma_for_generation"] == "DISABLED" and "FIXTURE_DASHBOARD" not in combined and "figma://" not in combined.lower(),
        "TECHNICAL_TASKS_ACCOUNTED_FOR": {item["task_id"] for item in manifest["task_statuses"]} == {f"TT-{index:03d}" for index in range(1, 17)},
        "HERO_FR_TRACEABILITY_COMPLETE": {item["id"] for item in traceability["functional_requirements"]} == {f"FR-{index:02d}" for index in range(1, 6)},
        "HERO_STORY_TRACEABILITY_COMPLETE": {item["id"] for item in traceability["stories"]} == {"US-01", "US-02", "US-03"},
        "HERO_AC_TRACEABILITY_COMPLETE": len(traceability["acceptance_criteria"]) == 5 and all(item["implementation_refs"] for item in traceability["acceptance_criteria"]),
        "GENERATED_TEST_TRACEABILITY_COMPLETE": test_ac == {item["id"] for item in traceability["acceptance_criteria"]},
        "SOURCE_UNCHANGED": context["source_hash_before"] == context["source_hash_after"],
        "PACKAGE_MANIFEST_CONSISTENT": package["devDependencies"]["@nx/angular"] == package["devDependencies"]["nx"] and package["dependencies"]["@angular/core"] == package["devDependencies"]["@angular/compiler-cli"],
        "GENERATED_COMPONENT_INVENTORY_VALID": set(component_files) <= set(manifest["generated_files"]) and len(component_files) == 6,
    }
    blockers = [name for name, passed in checks.items() if not passed]
    return {"status": "PASS" if not blockers else "FAIL", "checks": checks, "blockers": blockers, "static_validation_only": True, "build_executed": False, "generated_tests_executed": False, "figma_fixture_contamination_count": 0 if checks["NO_FIGMA_FIXTURE_CONTAMINATION"] else 1}
