# Progress

- Status: Step 2 complete — deterministic Tree-sitter extraction and evidence graph JSON created.
- Current step: Step 2 - Deterministic Tree-sitter source extraction
- Completed work: Project memory initialized; Dashboard source discovery completed; deterministic scoped inventory, facts, normalized graph JSON, summary, CLI, and tests created.
- Next action: Step 3 - load normalized graph JSON into Neo4j and add the Roslyn/LSP semantic enrichment adapter.
- Blockers: Razor directives are not semantically modeled because Step 2 uses only the HTML grammar; dynamic JavaScript URL expressions are retained as source expressions rather than resolved endpoints.
- Exact next action when resumed: Read the durable memory files and `docs/prompts/002-deterministic-tree-sitter-extractor.md`, then begin only the authorized Step 3 work.

## Resume Command

Read `PROJECT_MEMORY.md`, `PROGRESS.md`, `DECISIONS.md`, and `docs/prompts/002-deterministic-tree-sitter-extractor.md`, then continue only from the Current Step.
