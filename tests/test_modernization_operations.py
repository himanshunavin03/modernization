from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import shutil

import pytest

from polaris_modernization.commands.artifacts import ArtifactPaths
from polaris_modernization.commands.models import PrerequisiteError
from polaris_modernization.commands.service import CommandService
from polaris_modernization.modernization_operations import (
    ANGULAR_FEATURE_OPERATION_ID,
    ModernizationContextBuilder,
    default_operation_registry,
)


ROOT = Path(__file__).parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "commands"
FEATURES = {
    "feature-doctor-directory-management": "Doctor Directory Management",
    "feature-patient-directory-management": "Patient Directory Management",
    "feature-inventory-review": "Inventory Review",
}


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")


@pytest.fixture()
def operation_repository(tmp_path: Path) -> Path:
    root = tmp_path / "repository"
    shutil.copytree(FIXTURE, root)
    specifications = root / "artifacts/feature-specifications/latest"
    index_path = specifications / "feature-specification-index.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    index["features"] = [
        {"feature_id": feature_id, "feature_name": name}
        for feature_id, name in FEATURES.items()
    ]
    write_json(index_path, index)

    for feature_id, name in FEATURES.items():
        source_ref = f"ui/{feature_id}.html"
        write_json(specifications / f"{feature_id}.json", {
            "feature_id": feature_id,
            "feature_name": name,
            "stories": [{"story_id": f"story-{feature_id}"}],
            "acceptance_criteria": [{"acceptance_criterion_id": f"ac-{feature_id}"}],
            "functional_requirements": [{"requirement": f"Show {name}."}],
            "legacy_mapping": {"ui_surfaces": [name], "integration_contracts": []},
            "traceability": {"source_refs": [source_ref], "kg_refs": [f"kg:{feature_id}"]},
        })
        source = root / "source" / source_ref
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text(f"<{feature_id}></{feature_id}>", encoding="utf-8")
        write_json(root / f"artifacts/technical-tasks/features/{feature_id}/latest/technical-tasks.json", {
            "project_id": "synthetic-application",
            "feature_id": feature_id,
            "status": "TECHNICAL_TASKS_READY",
            "modernization_operation": {
                "operation_id": ANGULAR_FEATURE_OPERATION_ID,
                "target": "ANGULAR",
                "selection_source": "LOCKED_ARCHITECTURE",
            },
            "existing_api_contracts": [],
            "tasks": [{"task_id": "TT-001", "feature_id": feature_id}],
        })

    selection = {
        "feature_id": "feature-inventory-review",
        "selected_decision_ids": ["ARCH-001"],
        "decisions": [{"id": "ARCH-001", "technology": "Angular 22", "status": "SELECTED"}],
    }
    digest = sha256(json.dumps(selection, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    architecture = root / "artifacts/architecture/latest"
    write_json(architecture / "architecture-selection.json", selection)
    write_json(architecture / "architecture.json", {
        "selection": selection,
        "architecture_lock": {"status": "LOCKED", "locked_after_validation": True, "selection_hash": digest},
    })
    write_json(root / "artifacts/knowledge-graph/latest/graph-run-status.json", {
        "project_id": "synthetic-application", "source_root": "source", "overall_status": "succeeded",
    })
    return root


def test_generic_angular_operation_is_registered() -> None:
    assert default_operation_registry().contains(ANGULAR_FEATURE_OPERATION_ID)


@pytest.mark.parametrize("feature", FEATURES)
def test_features_select_the_same_generic_operation(operation_repository: Path, feature: str) -> None:
    result = CommandService(operation_repository).execute("modernize-feature", feature, prerequisite_only=True)

    assert result.status == "READY"
    assert result.data["operation_id"] == ANGULAR_FEATURE_OPERATION_ID
    assert result.data["design_source"] == "EXISTING_APPLICATION_UI"
    assert result.data["modernized"] is False


def test_unknown_operation_is_blocked(operation_repository: Path) -> None:
    path = operation_repository / "artifacts/technical-tasks/features/feature-doctor-directory-management/latest/technical-tasks.json"
    plan = json.loads(path.read_text(encoding="utf-8"))
    plan["modernization_operation"]["operation_id"] = "unknown-operation"
    write_json(path, plan)

    with pytest.raises(PrerequisiteError, match="not registered"):
        CommandService(operation_repository).execute("modernize-feature", "doctor-directory-management", prerequisite_only=True)


def test_missing_operation_selection_is_blocked(operation_repository: Path) -> None:
    path = operation_repository / "artifacts/technical-tasks/features/feature-doctor-directory-management/latest/technical-tasks.json"
    plan = json.loads(path.read_text(encoding="utf-8"))
    plan.pop("modernization_operation")
    write_json(path, plan)

    with pytest.raises(PrerequisiteError, match="No modernization operation is selected"):
        CommandService(operation_repository).execute("modernize-feature", "doctor-directory-management", prerequisite_only=True)


def test_missing_tasks_and_architecture_are_blocked(operation_repository: Path) -> None:
    tasks = operation_repository / "artifacts/technical-tasks/features/feature-doctor-directory-management"
    shutil.rmtree(tasks)
    with pytest.raises(PrerequisiteError, match="technical planning"):
        CommandService(operation_repository).execute("modernize-feature", "doctor-directory-management", prerequisite_only=True)

    shutil.copytree(
        operation_repository / "artifacts/technical-tasks/features/feature-patient-directory-management",
        tasks,
    )
    plan_path = tasks / "latest/technical-tasks.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    plan["feature_id"] = "feature-doctor-directory-management"
    plan["tasks"][0]["feature_id"] = "feature-doctor-directory-management"
    write_json(plan_path, plan)
    shutil.rmtree(operation_repository / "artifacts/architecture")
    with pytest.raises(PrerequisiteError, match="architecture"):
        CommandService(operation_repository).execute("modernize-feature", "doctor-directory-management", prerequisite_only=True)


def test_explicit_target_design_changes_only_design_source(operation_repository: Path) -> None:
    service = CommandService(operation_repository)
    feature = service.index.resolve("inventory-review")
    before = ModernizationContextBuilder(ArtifactPaths(operation_repository)).build("synthetic-application", feature)
    write_json(operation_repository / "artifacts/commands/design-config.json", {
        "provider": "FIGMA", "status": "CONFIGURED", "reference": "https://figma.com/design/test/file",
    })
    after = ModernizationContextBuilder(ArtifactPaths(operation_repository)).build("synthetic-application", feature)

    assert before.design_source == "EXISTING_APPLICATION_UI"
    assert after.design_source == "CUSTOMER_TARGET_DESIGN"
    assert after.feature_specification == before.feature_specification


def test_dashboard_is_not_regenerated_by_prerequisite_check() -> None:
    workspace = ROOT / "modernized"
    before = {path.relative_to(workspace): (path.stat().st_size, path.stat().st_mtime_ns) for path in workspace.rglob("*") if path.is_file()}

    result = CommandService(ROOT).execute("modernize-feature", "operational-dashboard-insights", prerequisite_only=True)

    after = {path.relative_to(workspace): (path.stat().st_size, path.stat().st_mtime_ns) for path in workspace.rglob("*") if path.is_file()}
    assert result.status == "ALREADY_IMPLEMENTED"
    assert after == before


def test_generic_operation_code_has_no_application_specific_logic() -> None:
    source = ROOT / "src/polaris_modernization/modernization_operations"
    contents = "\n".join(path.read_text(encoding="utf-8") for path in source.rglob("*.py"))
    prohibited = (
        "HealthClinic", "MyHealth", "Operational Dashboard", "Doctor Directory",
        "doctor-directory-management", "Patient Directory", "/api/reports", "/api/doctors",
    )
    assert not any(value in contents for value in prohibited)
