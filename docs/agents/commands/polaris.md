# Polaris Command Interface

Polaris exposes one IDE-neutral command registry. Codex, Copilot prompt files, a future MCP server, and other adapters call the same `CommandService`; command definitions contain descriptions and argument metadata only.

Install the repository package in editable mode, or run directly with the repository `src` path configured. CLI syntax is:

```powershell
polaris --repository-root <repository> <command> [argument]
```

Canonical slash-style names are the conversational aliases. For example, `/show-feature Doctor Directory Management` maps to:

```powershell
polaris --repository-root . show-feature "Doctor Directory Management"
```

## Understand

- `/create-knowledge-graph [--source-root <path>]` runs the existing deterministic graph workflow.
- `/understand-application` prepares evidence for active-agent reasoning; `--agent-result` submits it for deterministic validation.

## Plan

- `/generate-features` prepares or validates business Feature generation.
- `/generate-stories` prepares or validates Jira-quality Stories.
- `/generate-acceptance-criteria` prepares or validates immutable AC.
- `/recommend-architecture [feature]` invokes the existing architecture workflow. With no argument it uses the artifact-selected Feature.
- `/generate-technical-tasks [feature]` invokes architecture-driven planning after prerequisite validation. `--prerequisite-only` verifies readiness without writing task artifacts.

Architecture resolution checks `artifacts/architecture/features/<feature-id>/latest` for an explicit locked override, then inherits the canonical locked application selection at `artifacts/architecture/latest`. A missing or invalid lock blocks with `/recommend-architecture`; normal Features do not require separate architecture recommendations.

## Discover

- `/list-features` rebuilds the deterministic `artifacts/commands/feature-index.json` and lists ID, name, status, Stories, AC, APIs, tasks, implementation, and tests.
- `/show-feature <feature>` resolves ID, canonical slug, or name and returns the specification.
- `/show-traceability <feature>` returns Feature -> FR -> Story -> AC -> API -> architecture -> task -> implementation -> test links.

Unknown Features return `/list-features`. Ambiguous names return candidates and are never selected silently.

## Modernize

- `/modernize-feature <feature>` validates the specification, AC, locked feature architecture, and feature-specific technical tasks before dispatching an artifact-selected engine operation. Existing implementations return `ALREADY_IMPLEMENTED` rather than being overwritten.
- `/modernize-story <story-id>` resolves the owning Feature and uses the same operation.
- `/start-modernization` selects the next artifact-ready Feature without bypassing task order.
- `/resume-modernization` uses persisted state from `artifacts/commands/modernization-state.json`.

A Feature with no registered deterministic generator is blocked honestly. Adding a new generator means registering an operation in the adapter and selecting it through generated planning metadata, not adding application-name branches.

## Validate

- `/validate-feature <feature>` verifies generated implementation and test inventory, then runs the generated workspace's configured `build`, `test`, and `e2e` package scripts. Use `--static-only` for an inventory-only check.
- `/validate-modernization` validates every implemented Feature through the same boundary.

The core command layer does not fabricate runtime success. Its process runner is injectable so IDE, CI, CLI, or future MCP adapters can preserve the same result contract.

## Design And Status

- `/configure-design <figma-url>` persists optional customer design configuration. Without configured design, downstream planning uses `DESIGN_SOURCE=EXISTING_APPLICATION_UI`.
- `/modernization-status` derives lifecycle and per-Feature state from repository artifacts.
- `/help-polaris` returns this canonical catalog grouped by capability.

## End-To-End Use

```text
/create-knowledge-graph
/understand-application
/generate-features
/generate-stories
/generate-acceptance-criteria
/recommend-architecture
/generate-technical-tasks
/list-features
/modernize-feature <feature>
/validate-feature <feature>
```

Commands are safely rerunnable. Generated artifacts and persisted command state, never chat history, are the source of truth.
