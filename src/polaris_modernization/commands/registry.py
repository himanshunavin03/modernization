"""Canonical Polaris command catalog with no workflow implementation logic."""

from __future__ import annotations

from collections.abc import Iterable

from .models import CommandDefinition, CommandError


COMMANDS = (
    CommandDefinition("create-knowledge-graph", "UNDERSTAND", "Create or update deterministic source facts and the Knowledge Graph.", "create_knowledge_graph"),
    CommandDefinition("understand-application", "UNDERSTAND", "Prepare evidence-backed application and domain understanding.", "understand_application"),
    CommandDefinition("generate-features", "PLAN", "Generate business Features from approved understanding.", "generate_features"),
    CommandDefinition("generate-stories", "PLAN", "Generate Jira-quality Stories for approved Features.", "generate_stories", "feature", False),
    CommandDefinition("generate-acceptance-criteria", "PLAN", "Generate immutable acceptance criteria for approved Stories.", "generate_acceptance_criteria", "feature", False),
    CommandDefinition("recommend-architecture", "PLAN", "Recommend and select architecture from approved requirements.", "recommend_architecture", "feature", False),
    CommandDefinition("generate-technical-tasks", "PLAN", "Generate architecture-driven technical tasks.", "generate_technical_tasks", "feature", False),
    CommandDefinition("list-features", "DISCOVER", "List artifact-derived Feature metadata and modernization status.", "list_features"),
    CommandDefinition("show-feature", "DISCOVER", "Show one canonical Feature without requiring an artifact filename.", "show_feature", "feature"),
    CommandDefinition("show-traceability", "DISCOVER", "Show Feature-to-implementation traceability.", "show_traceability", "feature"),
    CommandDefinition("modernize-feature", "MODERNIZE", "Modernize one ready Feature through the registered engine operation.", "modernize_feature", "feature"),
    CommandDefinition("modernize-story", "MODERNIZE", "Modernize one Story through its owning Feature operation.", "modernize_story", "story"),
    CommandDefinition("start-modernization", "MODERNIZE", "Start work in artifact-defined technical-task order.", "start_modernization"),
    CommandDefinition("resume-modernization", "MODERNIZE", "Resume from persisted deterministic modernization state.", "resume_modernization"),
    CommandDefinition("validate-modernization", "VALIDATE", "Validate all implemented modernization outputs.", "validate_modernization"),
    CommandDefinition("validate-feature", "VALIDATE", "Validate one modernized Feature.", "validate_feature", "feature"),
    CommandDefinition("configure-design", "DESIGN", "Configure optional design input; existing UI remains the default.", "configure_design", "figma_url"),
    CommandDefinition("modernization-status", "STATUS", "Report lifecycle readiness and per-Feature state.", "modernization_status"),
    CommandDefinition("help-polaris", "STATUS", "Display the canonical command catalog.", "help"),
)


class CommandRegistry:
    def __init__(self, commands: Iterable[CommandDefinition]) -> None:
        materialized = tuple(commands)
        self._commands = {command.name: command for command in materialized}
        if len(self._commands) != len(materialized):
            raise CommandError("Command names must be unique.")

    def get(self, name: str) -> CommandDefinition:
        key = name.removeprefix("/")
        try:
            return self._commands[key]
        except KeyError as exc:
            raise CommandError(f"Unknown Polaris command '/{key}'. Run /help-polaris.") from exc

    def all(self) -> list[CommandDefinition]:
        return list(self._commands.values())

    def grouped(self) -> dict[str, list[CommandDefinition]]:
        groups: dict[str, list[CommandDefinition]] = {}
        for command in self._commands.values():
            groups.setdefault(command.category, []).append(command)
        return groups


def default_registry() -> CommandRegistry:
    return CommandRegistry(COMMANDS)
