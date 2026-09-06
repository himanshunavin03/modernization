# Polaris Modernization POC Instructions

1. Always read `PROJECT_MEMORY.md`, `PROGRESS.md`, and `DECISIONS.md` before work.
2. Never modify any project under `source/`; source projects are read-only runtime inputs.
3. Treat the current Git repository root as the solution root; do not create a nested `solution/` folder.
4. Before implementing a new user request, save that request in `docs/prompts/` using the next sequential number.
5. After every completed task, update `PROJECT_MEMORY.md` and `PROGRESS.md`.
6. Record architecture choices in `DECISIONS.md` with the reason.
7. Never claim something was analyzed, generated, tested, or working unless it is proven.
8. If blocked, document the blocker and the exact next action in `PROGRESS.md`.
9. Keep scanner behavior project-agnostic; select projects through `--source-root`, `--project-id`, and profiles.

## Developer capabilities

Use `.github/prompts/polaris.prompt.md` for the complete canonical command catalog. Existing focused prompt files remain supported. Every prompt is a thin adapter over the shared `polaris` command registry and CLI. In interactive `understand-application`, Copilot reasons only over Polaris-prepared evidence packages and submits a schema-valid result to deterministic validation; it does not require an external API key. Unresolved backend mappings remain unresolved.
