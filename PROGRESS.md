# Progress

- Status: Step 3C.8 completed. Roslyn succeeded and the end-to-end project loaded into Neo4j after local password correction.
- Agent command: `/create-knowledge-graph` is documented at `docs/agents/commands/create-knowledge-graph.md` and delegates to the deterministic `agent-create-knowledge-graph` CLI adapter. It derives a safe project ID from the selected source root, enables project-aware Roslyn only when .NET project evidence exists, keeps Neo4j opt-in, and does not use an LLM.
- Current step: Review the neutral customer-facing visualization and documentation changes.
- Complete application correction: deterministic first-party native-crash fallback now emits literal C#/JavaScript/Razor facts alongside provenance. Final analysis: 2,384 files, 3,386 nodes, 4,593 edges, 38 review warnings, zero extraction warnings, 44 opaque dependencies, and `complete_with_opaque_dependencies`. The attempted Neo4j load is blocked solely by unavailable local Neo4j environment configuration; full viewer export remains gated on that load.
- Failure inventory: 42 JavaScript, 3 C#, and 2 HTML Tree-sitter workers exit with `3221225477`; all are supported-language parser defects requiring a generic repair. See `docs/validation/complete-application-extraction-failure-inventory.md`.
- Viewer runbook: `docs/runbooks/understand-anything-viewer.md` documents the validated UI-only command and `tools/launch_understand_anything_viewer.ps1` safely exports and launches any approved project-scoped graph with a caller-supplied local token.
- Viewer runtime: `tools/install_understand_anything_viewer.ps1` performs the one-time pinned v2.9.0 installation under ignored `tools/vendor/`; normal viewer launch has no package-network access.
- Customer-facing viewer branding is neutralized as `Legacy Dashboard POC`; audit: `docs/validation/customer-facing-branding-audit.md`.
- End-to-end data context: the isolated graph now shows the proven Reports controller to repository, EF/LINQ query, selected model, and `MyHealthContext` flow; raw SQL is not represented because no literal SQL evidence exists.
- Completed work: Project memory initialized; Dashboard source discovery completed; deterministic scoped inventory, facts, normalized graph JSON, summary, CLI, and tests created; Roslyn graph-label correction validated on a real .NET 8 SDK; Create Knowledge Graph now validates input, analyzes source, validates the project-scoped graph, optionally loads only that project into Neo4j, and writes customer-facing run status artifacts. Native Tree-sitter extraction is isolated per file; child workers bootstrap the repository-local `src` directory through a copied `PYTHONPATH`, and abnormal exits, timeouts, invalid worker output, startup/import errors, and Python extraction errors produce safe structured warnings while remaining files continue. Profiles now carry explicit scope metadata, audit every discovered file, limit selected-flow graph File nodes and normal Roslyn facts to the approved scope, and expose proven cross-scope semantic references without silently widening the graph. Step 3C.6 loaded only `healthclinic-dashboard-scope-demo-v3` with 123 Neo4j nodes, 169 relationships, 27 warnings, and `scope_complete` coverage. Step 3C.7 now assigns all 123 exported viewer nodes exactly once across five deterministic evidence-derived layers, preserving 169 edges and 27 warnings; the port-5175 viewer returned HTTP 200 for both the page and graph endpoint.
- Next action: Review the read-only end-to-end viewer; initial CLI and Neo4j authentication failures are historical and final Roslyn/Neo4j validation succeeded.
- Blockers: None for Step 3C.6. Known review warnings remain visible: unresolved API-call ownership, implicit MVC `View()` matching, and Roslyn symbols that could not be resolved against the legacy source context.
- Exact next action when resumed: Read `PROJECT_MEMORY.md`, `PROGRESS.md`, `DECISIONS.md`, prompts 010 through 021 under `docs/prompts/`, `docs/validation/healthclinic-ui-technology-discovery.md`, and `docs/validation/understand-anything-readonly-visualization.md`. Neo4j loading is complete and the read-only visualization is complete. Manually confirm the corrected port-5175 canvas; do not begin Step 4 automatically.

## Resume Command

Read `PROJECT_MEMORY.md`, `PROGRESS.md`, `DECISIONS.md`, prompts 010 through 021 under `docs/prompts/`, `docs/agents/create-knowledge-graph.md`, `docs/validation/healthclinic-ui-technology-discovery.md`, and `docs/validation/understand-anything-readonly-visualization.md`. Neo4j loading and read-only visualization are complete. Manually confirm the corrected port-5175 canvas; do not begin Step 4 automatically.

## Project-Aware Roslyn Engine Proof

- Completed: generic multi-project and safe-fallback fixtures, helper repair, and tests. The focused suite passed `11` tests, proving compiler-backed `Web -> Business -> Data` semantics with no fallback and a narrowly scoped fallback only for a C# file not owned by any project.
- Completed: solution-first workspace loading avoids duplicate project opens; declared extension-method identities are retained; partial compilation facts are visibly lower-confidence and classify unresolved items as `COMPILATION_ERROR` rather than `UNKNOWN`.
- Not performed: no complete-application graph regeneration, Neo4j load, viewer export, or source modification.
- Next action: run the full regression suite. If it passes, the generic engine gates permit a separately approved complete-application regeneration. Recovery reading includes prompts 010 through 034 and `docs/analysis/roslyn-semantic-diagnostic.md`.

## Complete Regression Authorization Gate

- Commands: `& 'C:\Program Files\dotnet\dotnet.exe' build tools\Polaris.RoslynAnalyzer\Polaris.RoslynAnalyzer.csproj` and `python -m pytest -q` from the repository root. The Python suite collects all 68 repository tests through `pyproject.toml` (`testpaths = ["tests"]`); no separate .NET test project or JavaScript test runner exists.
- Results: analyzer build succeeded with `0` warnings and `0` errors. Pytest completed `66 passed, 2 skipped, 0 failed, 0 errors` in `17.06s`. No test failure occurred, so no production code or assertion changed during this validation.
- Gates: `MULTI_PROJECT_ROSLYN`, `SAFE_FALLBACK`, `API_MAPPING`, `READINESS_GATE`, and `COMPLETE_REGRESSION_SUITE` are PASS. There are `0` known generic analyzer defects and `0` unknown blockers in the verified fixture/test scope.
- Confirmation: no application `/create-knowledge-graph` command ran, `artifacts/knowledge-graph/latest/` is unchanged, no immutable complete-application run was created, and no Neo4j application load occurred.
- Authorization: SAFE TO REGENERATE in a separately approved follow-up task only.

## Forensic KG Readiness Analysis

- Completed read-only analysis of immutable run `legacy-dashboard-complete-application-demo-v1-2026-08-31-184436` at `922529974b5eb084945933befbf80faca3681e61`; report: `artifacts/knowledge-graph/latest/kg-readiness-analysis.md`.
- Result: `READY_WITH_EXPLAINED_LIMITATIONS`. The graph has valid JSON, complete 2,384-file inventory, zero Tree-sitter warnings, zero evidence gaps, no duplicate/broken records, no C#-as-Angular conflicts, and zero analyzer defects. Of 4,344 unresolved semantics, 4,342 are explicitly partial-compilation, fallback, or overload limitations; two source-backed inaccessible-member candidates remain `UNKNOWN`.
- The 314 invocation increase is fully reconciled against an unchanged prior inventory: 306 newly represented partial-compilation attempts and 8 fallback attempts, not source loss or an analyzer regression. API endpoint mapping remains absent (33 frontend API calls, zero endpoint facts/mappings), so Phase 2 must retain this as a visible limitation.
- Not performed: graph regeneration, graph/fact JSON edits, Neo4j load, analyzer changes, or Phase 2 work.

## Phase 2 Application Understanding

- Completed: separate LangGraph orchestration, provider-neutral LangChain structured boundary, deterministic KG evidence retrieval, provenance confidence model, claim validator, stable package-hash cache, CLI boundary, and project-memory protocol. Phase 1 analyzers and approved KG artifacts were not modified.
- Validation: `python -m pytest -q` returned `72 passed, 2 skipped`. A generic timestamp collision in Phase-2 immutable run IDs was fixed with microsecond precision and the complete suite rerun successfully.
- Actual output: `artifacts/application-understanding/latest/` is `FRAMEWORK_ONLY` with `NONE` provider, 64 evidence packages, 0 LLM calls, 0 input/output tokens, 4,868 KG nodes, 5,124 KG relationships, 8 Razor views, 15 partials, 4 layouts, 26 AngularJS controllers, 10 services, and 14 directives. The Dashboard Razor view and `DashboardController` are the best evidence-backed demo candidates.
- Limitation preserved: 33 frontend API-call facts have zero backend endpoint facts, so all Phase-2 user workflows retain `BACKEND_MAPPING=UNRESOLVED`. No AI-derived business capability or rule was fabricated.
- Next action: `VALIDATE_APPLICATION_UNDERSTANDING`; do not proceed to features, stories, architecture recommendation, or Angular generation.

## Provider And Developer Experience

- Real provider discovery found no Azure OpenAI or AWS Bedrock configuration. `understand-application --provider auto` now produces `WAITING_FOR_PROVIDER_CONFIGURATION` with zero LLM calls/tokens; Azure requires `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, and `AZURE_OPENAI_DEPLOYMENT`, while Bedrock requires `AWS_REGION` and `POLARIS_BEDROCK_MODEL_ID` plus standard AWS credentials.
- Codex uses `AGENTS.md` plus `docs/agents/commands/` and does not claim repository-defined slash-menu discovery. GitHub Copilot uses supported `.github/copilot-instructions.md` and `.github/prompts/*.prompt.md` prompt files. Both delegate to the same CLI; see `docs/developer-experience.md`.
- Validation: `python -m pytest -q` returned `74 passed, 2 skipped`. No KG regeneration, Phase-1 change, Neo4j load, feature/story generation, architecture recommendation, or Angular generation occurred.
- Next action: `CONFIGURE_LLM_PROVIDER`.
