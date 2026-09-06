"""Artifact-driven modernization Feature context assembly."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from polaris_modernization.commands.artifacts import (
    ArchitectureSelectionResolver,
    ArtifactPaths,
    ModernizationState,
    TechnicalTaskResolver,
    _read,
)
from polaris_modernization.commands.models import PrerequisiteError

from .models import ModernizationFeatureContext


class ModernizationContextBuilder:
    def __init__(self, paths: ArtifactPaths) -> None:
        self.paths = paths
        self.architecture = ArchitectureSelectionResolver(paths)
        self.tasks = TechnicalTaskResolver(paths)
        self.state = ModernizationState(paths)

    def build(self, project_id: str, feature: dict[str, Any]) -> ModernizationFeatureContext:
        feature_id = feature["feature_id"]
        specification = _read(self.paths.repository_root / feature["spec_path"], {})
        tasks = self.tasks.resolve(feature_id)
        architecture = self.architecture.resolve(feature_id)
        if not tasks.available or not tasks.plan:
            raise PrerequisiteError("Feature-specific technical planning is missing.", [f"/generate-technical-tasks {feature['slug']}"])
        if not architecture.available or not architecture.selection:
            raise PrerequisiteError("Locked architecture selection is missing.", ["/recommend-architecture"])

        ui_evidence = self._ui_evidence(specification)
        if not ui_evidence["source_paths"] and not ui_evidence["kg_refs"]:
            raise PrerequisiteError("Existing UI evidence is missing for this Feature.", ["/understand-application"])
        design_source, design_input = self._design()
        return ModernizationFeatureContext(
            repository_root=str(self.paths.repository_root),
            project_id=project_id,
            feature=feature,
            feature_specification=specification,
            technical_task_plan=tasks.plan,
            architecture_selection=architecture.selection,
            architecture_source=str(architecture.source),
            api_contracts=list(tasks.plan.get("existing_api_contracts", [])),
            ui_evidence=ui_evidence,
            design_source=design_source,
            design_input=design_input,
            modernization_state=self.state.load().get("features", {}).get(feature_id, {}),
        )

    def _ui_evidence(self, specification: dict[str, Any]) -> dict[str, Any]:
        traceability = specification.get("traceability", {})
        paths = list(traceability.get("source_refs", []))
        for item in specification.get("legacy_mapping", {}).get("integration_contracts", []):
            if item.get("frontend_source"):
                paths.append(item["frontend_source"])
        source_root = self._source_root()
        unique_paths = list(dict.fromkeys(paths))
        existing_paths = [path for path in unique_paths if source_root and (source_root / path).is_file()]
        return {
            "source_root": str(source_root) if source_root else None,
            "source_paths": existing_paths,
            "kg_refs": list(traceability.get("kg_refs", [])),
            "surface_refs": list(specification.get("legacy_mapping", {}).get("ui_surfaces", [])),
        }

    def _source_root(self) -> Path | None:
        status = _read(self.paths.artifacts / "knowledge-graph" / "latest" / "graph-run-status.json", {})
        value = status.get("source_root")
        if not value:
            return None
        path = Path(value)
        return path if path.is_absolute() else self.paths.repository_root / path

    def _design(self) -> tuple[str, dict[str, Any]]:
        config = _read(self.paths.command_root / "design-config.json", {})
        if config.get("status") == "CONFIGURED" and config.get("reference"):
            return "CUSTOMER_TARGET_DESIGN", config
        return "EXISTING_APPLICATION_UI", {"status": "NOT_PROVIDED", "source": "EXISTING_APPLICATION_UI"}
