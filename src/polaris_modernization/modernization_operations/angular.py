"""Generic Angular Feature modernization operation boundary."""
from __future__ import annotations

from polaris_modernization.commands.models import CommandError

from .ids import ANGULAR_FEATURE_OPERATION_ID
from .models import ModernizationFeatureContext, OperationExecutor, OperationReadiness


class AngularFeatureModernizationOperation:
    operation_id = ANGULAR_FEATURE_OPERATION_ID
    target = "ANGULAR"

    def __init__(self, executor: OperationExecutor | None = None) -> None:
        self.executor = executor

    def validate(self, context: ModernizationFeatureContext) -> OperationReadiness:
        plan = context.technical_task_plan
        selected = {
            item.get("technology", "").casefold()
            for item in context.architecture_selection.get("decisions", [])
            if item.get("id") in context.architecture_selection.get("selected_decision_ids", [])
        }
        blockers = []
        if plan.get("status") != "TECHNICAL_TASKS_READY":
            blockers.append("TECHNICAL_TASKS_NOT_READY")
        if any(item.get("feature_id") != context.feature["feature_id"] for item in plan.get("tasks", [])):
            blockers.append("TECHNICAL_TASK_FEATURE_MISMATCH")
        if not any("angular" in technology for technology in selected):
            blockers.append("ANGULAR_TARGET_NOT_SELECTED")
        if not context.ui_evidence.get("source_paths") and not context.ui_evidence.get("kg_refs"):
            blockers.append("EXISTING_UI_EVIDENCE_MISSING")
        return OperationReadiness(
            status="READY" if not blockers else "BLOCKED",
            operation_id=self.operation_id,
            target=self.target,
            blockers=tuple(blockers),
        )

    def execute(self, context: ModernizationFeatureContext) -> dict[str, object]:
        if self.executor is None:
            raise CommandError("The Angular Feature operation is registered but no execution adapter is configured.")
        return self.executor(context)
