# Prompt 065 - Reusable Polaris Command And Plugin Interface

Checkpoint: `6a04d05`

Create a reusable, IDE-neutral command interface over the existing deterministic Polaris lifecycle so developers do not need long prompts or internal artifact filenames. Commands must remain thin wrappers over existing Understand, Plan, Modernize, Validate, Design, Discovery, and Status operations.

Required canonical commands:

- `/create-knowledge-graph`, `/understand-application`
- `/generate-features`, `/generate-stories`, `/generate-acceptance-criteria`, `/recommend-architecture`, `/generate-technical-tasks`
- `/list-features`, `/show-feature <feature>`, `/show-traceability <feature>`
- `/modernize-feature <feature>`, `/modernize-story <story>`, `/start-modernization`, `/resume-modernization`
- `/validate-modernization`, `/validate-feature <feature>`
- `/configure-design <figma-url>`, `/modernization-status`, `/help-polaris`

Feature resolution must use generated metadata, support ID/slug/name, reject ambiguity, and direct unknown names to `/list-features`. Add a deterministic machine navigation index with Story, AC, API, architecture, task, implementation, test, and modernization-state references. Persist deterministic state for status and resume behavior.

Commands must validate prerequisites, be idempotent, and avoid application-specific branches. Codex and Copilot must delegate to the same operation service, with future CLI/MCP/plugin compatibility. Add focused tests including Doctor Directory as fixture data and at least one synthetic non-POC Feature.

Do not change source applications, frozen Features/Stories/AC/architecture, the working Dashboard, or modernize Doctor Directory. Run focused and full tests plus the Angular build, audit reusable production code, and create one commit titled `Add reusable Polaris command interface`.
