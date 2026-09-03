from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

from polaris_modernization.modernization_generation.models import PepRun


ROOT = Path(__file__).parents[1]
LATEST = ROOT / "artifacts" / "modernization" / "latest"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_pep_run_preserves_real_failure_and_repair_sequence() -> None:
    pep = PepRun.model_validate(read_json(LATEST / "pep-run.json"))
    assert pep.status == "BLOCKED"
    assert len(pep.attempts) == 11
    assert len(pep.failures) == 7
    assert len(pep.repairs) == 5
    assert len(pep.revalidations) == 7
    assert pep.failures[0].category == "GENERATED_DEPENDENCY_VERSION_CONFLICT"
    assert pep.failures[-1].category == "NX_ANGULAR_TEST_CONFIGURATION"
    assert pep.diagnoses[-1].selected_repair == "NONE_AUTOMATIC_REPAIR_LIMIT_REACHED"


def test_repaired_dependency_metadata_is_compatible_and_locked() -> None:
    package = read_json(ROOT / "modernized" / "package.json")
    lock = read_json(ROOT / "modernized" / "package-lock.json")
    assert package["devDependencies"]["vitest"] == "4.1.11"
    assert package["devDependencies"]["typescript-eslint"] == "8.69.0"
    assert package["devDependencies"]["jsdom"] == "30.0.1"
    assert lock["packages"][""]["devDependencies"] == package["devDependencies"]


def test_runtime_validation_reports_only_executed_evidence() -> None:
    runtime = read_json(LATEST / "runtime-validation.json")
    assert runtime["dependency_status"] == "PASS"
    assert runtime["build_status"] == "PASS"
    assert runtime["unit_test_status"] == "BLOCKED_BEFORE_TEST_DISCOVERY"
    assert runtime["unit_test_count"] == 0
    assert runtime["serve_status"] == "NOT_EXECUTED_PREREQUISITE_FAILED"
    assert runtime["browser_render_status"] == "NOT_EXECUTED_PREREQUISITE_FAILED"
    assert runtime["playwright_status"] == "NOT_EXECUTED_PREREQUISITE_FAILED"
    assert runtime["readiness"] == "BLOCKED_BY_UNIT_TEST_CONFIGURATION"
    assert all(item["status"] == "IMPLEMENTED_NOT_RUNTIME_VERIFIED" for item in runtime["acceptance_criteria"])


def test_runtime_validation_preserves_api_and_design_contracts() -> None:
    runtime = read_json(LATEST / "runtime-validation.json")
    assert runtime["api_preservation"] == {
        "status": "PASS_STATIC_AND_BUILD_VALIDATED",
        "contract_count": 4,
        "invented_existing_api_count": 0,
    }
    assert runtime["design_source"] == {
        "current": "EXISTING_APPLICATION_UI",
        "figma_capability": "SUPPORTED_OPTIONAL",
        "figma_fixture_influence": "NONE",
    }


def test_runtime_evidence_is_reflected_in_traceability_and_demo() -> None:
    traceability = read_json(LATEST / "traceability.json")
    html = (LATEST / "modernization.html").read_text(encoding="utf-8")
    assert traceability["runtime_validation"]["angular_build"] == "PASS"
    assert traceability["runtime_validation"]["unit_tests"] == "BLOCKED_BEFORE_TEST_DISCOVERY"
    assert "modernization validation" in html.lower()
    assert "Test Configuration Blocker" in html
    assert "Figma fixture influence" in html


def test_prompt_064_does_not_change_frozen_inputs() -> None:
    architecture = ROOT / "artifacts" / "architecture" / "latest" / "architecture-selection.json"
    tasks = ROOT / "artifacts" / "technical-tasks" / "latest" / "technical-tasks.json"
    assert sha256(architecture.read_bytes()).hexdigest() == "661bdacf00f061718afef9862bd9875a44d976451407cf0dc6c76006bcf9e8fb"
    assert sha256(tasks.read_bytes()).hexdigest() == "fa773edaf3ea82ff1fdc009b9b4cadbcf94c717283d6c9b02ecf454ae7687182"
