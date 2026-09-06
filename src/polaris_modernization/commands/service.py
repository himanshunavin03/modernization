"""Shared command service that delegates to existing Polaris workflows."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any, Callable

from .artifacts import (
    ArchitectureResolution,
    ArchitectureSelectionResolver,
    ArtifactPaths,
    FeatureIndex,
    ModernizationState,
    _read,
)
from .models import CommandResult, PrerequisiteError
from .registry import CommandRegistry, default_registry


Operation = Callable[..., CommandResult]


class CommandService:
    def __init__(
        self,
        repository_root: Path,
        *,
        registry: CommandRegistry | None = None,
        modernizers: dict[str, Callable[..., dict[str, Any]]] | None = None,
        process_runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
    ) -> None:
        self.paths = ArtifactPaths(repository_root.resolve())
        self.registry = registry or default_registry()
        self.index = FeatureIndex(self.paths)
        self.architecture = ArchitectureSelectionResolver(self.paths)
        self.state = ModernizationState(self.paths)
        self.modernizers = modernizers or {}
        self.process_runner = process_runner

    def execute(self, command_name: str, argument: str | None = None, **options: Any) -> CommandResult:
        definition = self.registry.get(command_name)
        operation: Operation = getattr(self, definition.operation)
        if definition.argument and definition.argument_required and not argument:
            raise PrerequisiteError(f"/{definition.name} requires <{definition.argument}>.", ["/help-polaris"])
        return operation(argument=argument, **options)

    def help(self, **_: Any) -> CommandResult:
        groups = {
            category: [command.to_dict() for command in commands]
            for category, commands in self.registry.grouped().items()
        }
        return CommandResult("help-polaris", "READY", {"groups": groups})

    def list_features(self, **_: Any) -> CommandResult:
        index = self.index.build()
        return CommandResult("list-features", "READY", {"features": index["features"], "index_path": str(self.paths.feature_index)})

    def show_feature(self, *, argument: str, **_: Any) -> CommandResult:
        feature = self.index.resolve(argument)
        specification = _read(self.paths.repository_root / feature["spec_path"], {})
        return CommandResult("show-feature", "READY", {"feature": feature, "specification": specification})

    def show_traceability(self, *, argument: str, **_: Any) -> CommandResult:
        feature = self.index.resolve(argument)
        architecture = self.architecture.resolve(feature["feature_id"])
        decisions = architecture.selection.get("decisions", []) if architecture.selection else []
        specification = _read(self.paths.repository_root / feature["spec_path"], {})
        functional_requirements = [
            {"acceptance_criterion_id": item.get("acceptance_criterion_id"), "requirement": item.get("requirement")}
            for item in specification.get("functional_requirements", [])
        ]
        traceability = {
            "feature": feature["feature_id"],
            "functional_requirements": functional_requirements,
            "stories": feature["story_ids"],
            "acceptance_criteria": feature["acceptance_criteria_ids"],
            "api_contracts": feature["api_contract_ids"],
            "architecture_decisions": [item["id"] for item in decisions if item.get("id")],
            "adrs": list(dict.fromkeys(item["adr_ref"] for item in decisions if item.get("adr_ref"))),
            "architecture_source": architecture.source,
            "architecture_selection_ref": architecture.selection_ref,
            "technical_tasks": feature["technical_task_ids"],
            "generated_implementation": feature["implementation_paths"],
            "tests": feature["test_paths"],
        }
        return CommandResult("show-traceability", "READY", {"traceability": traceability})

    def modernization_status(self, **_: Any) -> CommandResult:
        index = self.index.build()
        features = index["features"]
        status = {
            "application": self._project_id(),
            "knowledge_graph": self._artifact_status("knowledge-graph", "graph-run-status.json"),
            "understanding": self._artifact_status("application-understanding", "application-understanding.json"),
            "feature_count": len(features),
            "story_count": sum(len(item["story_ids"]) for item in features),
            "acceptance_criteria_count": sum(len(item["acceptance_criteria_ids"]) for item in features),
            "architecture": self._artifact_status("architecture", "architecture.json"),
            "technical_tasks": self._artifact_status("technical-tasks", "technical-tasks.json"),
            "features": [{"feature_id": item["feature_id"], "name": item["name"], "status": item["modernization_status"]} for item in features],
        }
        return CommandResult("modernization-status", "READY", status)

    def create_knowledge_graph(self, *, source_root: Path | None = None, **options: Any) -> CommandResult:
        from polaris_modernization.agent_commands import create_knowledge_graph_command

        root = source_root or options.get("source") or self.paths.repository_root
        result = create_knowledge_graph_command(
            Path(root), project_id=options.get("project_id"), profile=options.get("profile", "default"),
            output=Path(options.get("output", self.paths.artifacts)), load_neo4j=bool(options.get("load_neo4j", False)),
        )
        return CommandResult("create-knowledge-graph", str(result.get("overall_status", "UNKNOWN")).upper(), {"result": result})

    def understand_application(self, **options: Any) -> CommandResult:
        from polaris_modernization.application_understanding.workflow import prepare_application_understanding, validate_and_persist_application_understanding

        kg_root = Path(options.get("kg_root", self._latest_run("knowledge-graph")))
        output = Path(options.get("output", self.paths.artifacts / "application-understanding"))
        agent_result = options.get("agent_result")
        result = validate_and_persist_application_understanding(kg_root, output, Path(agent_result)) if agent_result else prepare_application_understanding(kg_root, output)
        return CommandResult("understand-application", "PREPARED" if not agent_result else "COMPLETE", {"path": str(result["path"])})

    def generate_features(self, **options: Any) -> CommandResult:
        from polaris_modernization.feature_generation.workflow import prepare_feature_generation, validate_and_persist_features

        source = Path(options.get("application_understanding_root", self.paths.artifacts / "application-understanding" / "latest"))
        output = Path(options.get("output", self.paths.artifacts / "features"))
        agent_result = options.get("agent_result")
        result = validate_and_persist_features(source, output, Path(agent_result)) if agent_result else prepare_feature_generation(source, output)
        return CommandResult("generate-features", "PREPARED" if not agent_result else "COMPLETE", {"path": str(result["path"])})

    def generate_stories(self, **options: Any) -> CommandResult:
        from polaris_modernization.stories.workflow import prepare_story_generation, validate_and_persist_stories

        source = Path(options.get("business_feature_root", self.paths.artifacts / "business-features" / "latest"))
        output = Path(options.get("output", self.paths.artifacts / "stories"))
        agent_result = options.get("agent_result")
        result = validate_and_persist_stories(source, output, Path(agent_result)) if agent_result else prepare_story_generation(source, output)
        return CommandResult("generate-stories", "PREPARED" if not agent_result else "COMPLETE", {"path": str(result["path"])})

    def generate_acceptance_criteria(self, **options: Any) -> CommandResult:
        from polaris_modernization.acceptance_criteria.workflow import prepare_acceptance_criteria, validate_and_persist_acceptance_criteria

        source = Path(options.get("story_root", self.paths.artifacts / "stories" / "latest"))
        output = Path(options.get("output", self.paths.artifacts / "acceptance-criteria"))
        agent_result = options.get("agent_result")
        result = validate_and_persist_acceptance_criteria(source, output, Path(agent_result)) if agent_result else prepare_acceptance_criteria(source, output)
        return CommandResult("generate-acceptance-criteria", "PREPARED" if not agent_result else "COMPLETE", {"path": str(result["path"])})

    def recommend_architecture(self, *, argument: str | None, **options: Any) -> CommandResult:
        from polaris_modernization.architecture.workflow import recommend_architecture

        feature = self._resolve_optional_feature(argument)
        result = recommend_architecture(
            self._project_id(), feature["feature_id"], self.paths.specifications,
            Path(options.get("output", self.paths.artifacts / "architecture")),
            options.get("design_provider", "NONE"), options.get("design_reference"),
        )
        return CommandResult("recommend-architecture", "COMPLETE", {"path": str(result["path"]), "feature_id": feature["feature_id"]})

    def generate_technical_tasks(self, *, argument: str | None, **options: Any) -> CommandResult:
        from polaris_modernization.technical_tasks.workflow import generate_technical_tasks

        feature = self._resolve_optional_feature(argument)
        if not feature["acceptance_criteria_ids"]:
            raise PrerequisiteError("Acceptance Criteria are missing.", ["/generate-acceptance-criteria"])
        architecture = self._require_architecture(feature)
        if options.get("prerequisite_only"):
            return CommandResult("generate-technical-tasks", "READY", {
                "feature_id": feature["feature_id"],
                "architecture_source": architecture.source,
                "architecture_selection_ref": architecture.selection_ref,
                "architecture_override": architecture.override,
            })
        design = _read(self.paths.command_root / "design-config.json", {"provider": "NONE", "mode": "NONE"})
        result = generate_technical_tasks(
            self._project_id(), feature["feature_id"], architecture.root,
            self.paths.specifications, design["provider"], design["mode"], design.get("reference"),
            Path(options.get("output", self.paths.artifacts / "technical-tasks")), self.paths.artifacts / "design",
        )
        self.index.build()
        return CommandResult("generate-technical-tasks", "COMPLETE", {"path": str(result["path"]), "feature_id": feature["feature_id"]})

    def modernize_feature(self, *, argument: str, **options: Any) -> CommandResult:
        feature = self.index.resolve(argument)
        if feature["modernization_status"] in {"IMPLEMENTED", "RUNTIME_VALIDATED"}:
            return CommandResult(
                "modernize-feature", "ALREADY_IMPLEMENTED", {"feature": feature},
                "Existing implementation detected; regeneration was skipped.", [f"/validate-feature {feature['slug']}", "/resume-modernization"],
            )
        self._validate_modernization_prerequisites(feature)
        operation_name = feature.get("modernization_operation") or options.get("operation_name")
        if not operation_name or operation_name not in self.modernizers:
            raise PrerequisiteError(
                "No artifact-selected modernization operation is registered for this Feature.",
                [f"/generate-technical-tasks {feature['slug']}"],
            )
        self.state.set(feature["feature_id"], "IN_PROGRESS", operation_name)
        result = self.modernizers[operation_name](feature=feature, service=self, **options)
        self.state.set(feature["feature_id"], "IMPLEMENTED", operation_name, result)
        self.index.build()
        return CommandResult("modernize-feature", "IMPLEMENTED", {"feature_id": feature["feature_id"], "result": result})

    def modernize_story(self, *, argument: str, **options: Any) -> CommandResult:
        feature, story_id = self.index.resolve_story(argument)
        result = self.modernize_feature(argument=feature["feature_id"], **options)
        result.command = "modernize-story"
        result.data["story_id"] = story_id
        return result

    def start_modernization(self, **_: Any) -> CommandResult:
        features = self.index.build()["features"]
        ready = [item for item in features if item["modernization_status"] == "READY"]
        if not ready:
            pending = next((item for item in features if item["modernization_status"] == "NOT_STARTED"), None)
            next_commands = [f"/generate-technical-tasks {pending['slug']}"] if pending else ["/validate-modernization"]
            return CommandResult("start-modernization", "BLOCKED", {"features": features}, "No Feature is currently ready for modernization.", next_commands)
        feature = ready[0]
        return CommandResult("start-modernization", "READY", {"next_feature": feature}, next_commands=[f"/modernize-feature {feature['slug']}"])

    def resume_modernization(self, **_: Any) -> CommandResult:
        index = self.index.build()
        active = [item for item in index["features"] if item["modernization_status"] in {"IN_PROGRESS", "PARTIAL", "BLOCKED"}]
        if active:
            feature = active[0]
            return CommandResult("resume-modernization", "READY", {"feature": feature}, next_commands=[f"/modernize-feature {feature['slug']}"])
        return self.start_modernization()

    def validate_feature(self, *, argument: str, static_only: bool = False, **_: Any) -> CommandResult:
        feature = self.index.resolve(argument)
        generation = _read(self.paths.artifacts / "modernization" / "latest" / "generation-manifest.json", {})
        workspace = self.paths.repository_root / generation.get("generated_workspace", "modernized")
        missing = [path for path in [*feature["implementation_paths"], *feature["test_paths"]] if not (workspace / path).exists()]
        if not feature["implementation_paths"]:
            raise PrerequisiteError("No generated implementation exists for this Feature.", [f"/modernize-feature {feature['slug']}"])
        if missing:
            self.state.set(feature["feature_id"], "BLOCKED", "validate-feature", {"missing_paths": missing})
            return CommandResult("validate-feature", "BLOCKED", {"missing_paths": missing}, "Generated implementation files are missing.", [f"/modernize-feature {feature['slug']}"])
        if static_only:
            return CommandResult("validate-feature", "STATIC_VALIDATION_PASS", {"feature": feature})
        package = _read(workspace / "package.json", {})
        scripts = package.get("scripts", {})
        validations = []
        for name in ("build", "test", "e2e"):
            if name not in scripts:
                validations.append({"name": name, "status": "NOT_CONFIGURED"})
                continue
            command = ["npm", "run", name]
            if name == "test":
                command.extend(["--", "--watch=false"])
            completed = self.process_runner(command, cwd=workspace, capture_output=True, text=True, check=False)
            validations.append({"name": name, "status": "PASS" if completed.returncode == 0 else "FAIL", "returncode": completed.returncode})
            if completed.returncode != 0:
                break
        passed = all(item["status"] in {"PASS", "NOT_CONFIGURED"} for item in validations)
        if passed:
            self.state.set(feature["feature_id"], "RUNTIME_VALIDATED", "validate-feature", {"validations": validations})
            self.index.build()
        return CommandResult(
            "validate-feature", "PASS" if passed else "BLOCKED", {"feature": feature, "validations": validations},
            "Configured build, unit, and browser validation completed." if passed else "A configured validation command failed.",
            [] if passed else [f"/validate-feature {feature['slug']}"]
        )

    def validate_modernization(self, *, static_only: bool = False, **_: Any) -> CommandResult:
        implemented = [item for item in self.index.build()["features"] if item["modernization_status"] in {"IMPLEMENTED", "RUNTIME_VALIDATED"}]
        results = [self.validate_feature(argument=item["feature_id"], static_only=static_only).to_dict() for item in implemented]
        expected = "STATIC_VALIDATION_PASS" if static_only else "PASS"
        return CommandResult("validate-modernization", "PASS" if results and all(item["status"] == expected for item in results) else "BLOCKED", {"features": results})

    def configure_design(self, *, argument: str, **_: Any) -> CommandResult:
        value = argument.strip()
        if not value:
            config = {"provider": "NONE", "mode": "NONE", "status": "NOT_PROVIDED", "source": "EXISTING_APPLICATION_UI"}
        elif "figma.com/" not in value.casefold():
            raise PrerequisiteError("The design reference must be a Figma URL.", ["/configure-design <figma-url>"])
        else:
            config = {"provider": "FIGMA", "mode": "LIVE", "status": "CONFIGURED", "reference": value, "source": "CUSTOMER_DESIGN"}
        self.paths.command_root.mkdir(parents=True, exist_ok=True)
        (self.paths.command_root / "design-config.json").write_text(json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return CommandResult("configure-design", config["status"], config)

    def _validate_modernization_prerequisites(self, feature: dict[str, Any]) -> None:
        if not (self.paths.repository_root / feature["spec_path"]).is_file():
            raise PrerequisiteError("Feature Specification is missing.", ["/generate-features"])
        if not feature["acceptance_criteria_ids"]:
            raise PrerequisiteError("Acceptance Criteria are missing.", ["/generate-acceptance-criteria"])
        self._require_architecture(feature)
        if not feature["technical_task_ids"]:
            raise PrerequisiteError("Feature-specific technical planning is missing.", [f"/generate-technical-tasks {feature['slug']}"])

    def _require_architecture(self, feature: dict[str, Any]) -> ArchitectureResolution:
        architecture = self.architecture.resolve(feature["feature_id"])
        if not architecture.available:
            raise PrerequisiteError("Locked architecture selection is missing.", ["/recommend-architecture"])
        return architecture

    def _resolve_optional_feature(self, argument: str | None) -> dict[str, Any]:
        if argument:
            return self.index.resolve(argument)
        selection = _read(self.paths.artifacts / "architecture" / "latest" / "architecture-selection.json", {})
        selected_feature = selection.get("feature_id")
        if selected_feature:
            return self.index.resolve(selected_feature)
        features = self.index.build()["features"]
        if len(features) == 1:
            return features[0]
        raise PrerequisiteError("A Feature must be selected because multiple Features exist.", ["/list-features", "/recommend-architecture <feature>"])

    def _project_id(self) -> str:
        for path in (
            self.paths.artifacts / "modernization" / "latest" / "generation-manifest.json",
            self.paths.artifacts / "business-features" / "latest" / "business-feature-catalog.json",
        ):
            value = _read(path, {}).get("project_id")
            if value:
                return str(value)
        return self.paths.repository_root.name

    def _artifact_status(self, artifact: str, filename: str) -> str:
        root = self.paths.artifacts / artifact
        candidates = sorted(root.rglob(filename), key=lambda path: path.stat().st_mtime_ns) if root.is_dir() else []
        if not candidates:
            return "MISSING"
        project_id = self._project_id()
        values = [_read(path, {}) for path in reversed(candidates)]
        value = next((item for item in values if not item.get("project_id") or item.get("project_id") == project_id), values[0])
        for key in ("overall_status", "readiness", "status"):
            if value.get(key):
                return str(value[key])
        for container in ("selection", "architecture_lock", "validation"):
            nested = value.get(container, {})
            if nested.get("status"):
                return str(nested["status"])
        return "AVAILABLE"

    def _latest_run(self, artifact: str) -> Path:
        root = self.paths.artifacts / artifact
        latest = root / "latest"
        if latest.is_dir():
            return latest
        runs = sorted((root / "runs").glob("*")) if (root / "runs").is_dir() else []
        if not runs:
            raise PrerequisiteError(f"{artifact} artifacts are missing.", ["/create-knowledge-graph"])
        return runs[-1]
