from __future__ import annotations

import json
from pathlib import Path
import shutil

import pytest

from polaris_modernization.command_cli import build_parser, run
from polaris_modernization.agent_commands import execute_polaris_command
from polaris_modernization.commands.artifacts import ArtifactPaths, FeatureIndex, ModernizationState
from polaris_modernization.commands.models import AmbiguousFeatureError, FeatureNotFoundError, PrerequisiteError
from polaris_modernization.commands.registry import COMMANDS, default_registry
from polaris_modernization.commands.service import CommandService


FIXTURE = Path(__file__).parent / "fixtures" / "commands"


@pytest.fixture()
def repository(tmp_path: Path) -> Path:
    root = tmp_path / "repository"
    shutil.copytree(FIXTURE, root)
    return root


def test_registry_discovers_the_complete_canonical_catalog() -> None:
    registry = default_registry()
    assert len(registry.all()) == 19
    assert {item.category for item in registry.all()} == {"UNDERSTAND", "PLAN", "DISCOVER", "MODERNIZE", "VALIDATE", "DESIGN", "STATUS"}
    assert registry.get("/modernize-feature").operation == "modernize_feature"
    assert len({item.name for item in COMMANDS}) == len(COMMANDS)


def test_cli_discovers_every_registry_command() -> None:
    parser = build_parser()
    subparsers = next(action for action in parser._actions if action.dest == "command")
    assert set(subparsers.choices) == {item.name for item in COMMANDS}


def test_agent_adapter_delegates_to_the_shared_command_service(repository: Path) -> None:
    result = execute_polaris_command("/list-features", repository_root=repository)

    assert result["command"] == "list-features"
    assert {item["feature_id"] for item in result["data"]["features"]} == {
        "feature-doctor-directory-management",
        "feature-inventory-review",
    }


def test_feature_index_and_resolver_use_metadata(repository: Path) -> None:
    navigator = FeatureIndex(ArtifactPaths(repository))
    index = navigator.build()
    doctor = navigator.resolve("Doctor Directory Management", index)
    synthetic = navigator.resolve("feature-inventory-review", index)

    assert navigator.resolve("doctor-directory-management", index) == doctor
    assert doctor["api_contract_ids"] == ["API-DIRECTORY-001"]
    assert synthetic["modernization_status"] == "READY"
    assert synthetic["technical_task_ids"] == ["TT-001"]
    assert synthetic["modernization_operation"] == "synthetic-generator"
    assert synthetic["architecture_decision_ids"] == ["ARCH-001"]
    assert synthetic["adr_ids"] == ["ADR-001"]
    assert json.loads((repository / "artifacts/commands/feature-index.json").read_text(encoding="utf-8")) == index


def test_unknown_and_ambiguous_features_are_never_silently_selected(repository: Path) -> None:
    navigator = FeatureIndex(ArtifactPaths(repository))
    with pytest.raises(FeatureNotFoundError, match="/list-features"):
        navigator.resolve("missing")
    ambiguous = {
        "features": [
            {"feature_id": "feature-one", "slug": "one", "name": "Shared Name"},
            {"feature_id": "feature-two", "slug": "two", "name": "Shared Name"},
        ]
    }
    with pytest.raises(AmbiguousFeatureError, match="feature-one, feature-two"):
        navigator.resolve("Shared Name", ambiguous)


def test_prerequisite_validation_blocks_unplanned_feature(repository: Path) -> None:
    service = CommandService(repository)
    with pytest.raises(PrerequisiteError) as error:
        service.execute("modernize-feature", "doctor-directory-management")
    assert error.value.next_commands == ["/recommend-architecture doctor-directory-management"]


def test_modernization_state_is_persisted_and_rerun_is_idempotent(repository: Path) -> None:
    calls: list[str] = []

    def modernizer(**kwargs):
        calls.append(kwargs["feature"]["feature_id"])
        return {"output": "generated"}

    service = CommandService(repository, modernizers={"synthetic-generator": modernizer})
    first = service.execute("modernize-feature", "inventory-review")
    second = service.execute("modernize-feature", "Inventory Review")

    assert first.status == "IMPLEMENTED"
    assert second.status == "ALREADY_IMPLEMENTED"
    assert calls == ["feature-inventory-review"]
    assert ModernizationState(service.paths).load()["features"]["feature-inventory-review"]["status"] == "IMPLEMENTED"


def test_story_resolution_delegates_to_owning_feature(repository: Path) -> None:
    service = CommandService(repository, modernizers={"synthetic-generator": lambda **_: {"ok": True}})
    result = service.execute("modernize-story", "story-inventory-review-list")
    assert result.command == "modernize-story"
    assert result.data["story_id"] == "story-inventory-review-list"


def test_status_and_help_are_read_only_discovery_operations(repository: Path) -> None:
    service = CommandService(repository)
    assert service.execute("help-polaris").status == "READY"
    status = service.execute("modernization-status")
    assert status.data["feature_count"] == 2
    assert status.data["story_count"] == 2


def test_validation_executes_configured_workspace_scripts(repository: Path) -> None:
    workspace = repository / "output-workspace"
    workspace.mkdir()
    (workspace / "package.json").write_text(json.dumps({"scripts": {"build": "build", "test": "test"}}), encoding="utf-8")
    implementation = workspace / "feature.ts"
    implementation.write_text("export {};", encoding="utf-8")
    modernization = repository / "artifacts/modernization/latest"
    modernization.mkdir(parents=True)
    (modernization / "generation-manifest.json").write_text(json.dumps({
        "feature_id": "feature-inventory-review", "generated_workspace": "output-workspace",
        "generated_files": ["feature.ts"], "generated_tests": [],
    }), encoding="utf-8")
    (modernization / "generation-validation.json").write_text(json.dumps({"status": "PASS"}), encoding="utf-8")
    calls = []

    def runner(command, **kwargs):
        calls.append(command)
        return type("Completed", (), {"returncode": 0})()

    result = CommandService(repository, process_runner=runner).execute("validate-feature", "inventory-review")
    assert result.status == "PASS"
    assert calls == [["npm", "run", "build"], ["npm", "run", "test", "--", "--watch=false"]]


def test_cli_returns_actionable_unknown_feature_error(repository: Path) -> None:
    code, payload = run(["--repository-root", str(repository), "show-feature", "missing"])
    assert code == 2
    assert payload["status"] == "ERROR"
    assert "/list-features" in payload["message"]


def test_generic_command_production_code_has_no_demo_specific_branches() -> None:
    source = Path("src/polaris_modernization/commands")
    contents = "\n".join(path.read_text(encoding="utf-8") for path in source.rglob("*.py"))
    prohibited = ("HealthClinic", "MyHealth", "Operational Dashboard", "Doctor Directory", "/api/reports")
    assert not any(value in contents for value in prohibited)
