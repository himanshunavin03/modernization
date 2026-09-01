# Progress

- Status: Phase 2 Application Understanding validated against approved immutable KG run `legacy-dashboard-complete-application-demo-v1-2026-09-01-034128`.
- Agent command: `/create-knowledge-graph` is documented at `docs/agents/commands/create-knowledge-graph.md` and delegates to the deterministic `agent-create-knowledge-graph` CLI adapter. It derives a safe project ID from the selected source root, enables project-aware Roslyn only when .NET project evidence exists, keeps Neo4j opt-in, and does not use an LLM.
- Current step: Application Understanding is `APPLICATION_UNDERSTANDING_READY_WITH_LIMITATIONS`; await explicit authorization for `GENERATE_FEATURES`.
- Complete application correction: deterministic first-party native-crash fallback now emits literal C#/JavaScript/Razor facts alongside provenance. Final analysis: 2,384 files, 3,386 nodes, 4,593 edges, 38 review warnings, zero extraction warnings, 44 opaque dependencies, and `complete_with_opaque_dependencies`. The attempted Neo4j load is blocked solely by unavailable local Neo4j environment configuration; full viewer export remains gated on that load.
- Failure inventory: 42 JavaScript, 3 C#, and 2 HTML Tree-sitter workers exit with `3221225477`; all are supported-language parser defects requiring a generic repair. See `docs/validation/complete-application-extraction-failure-inventory.md`.
- Viewer runbook: `docs/runbooks/understand-anything-viewer.md` documents the validated UI-only command and `tools/launch_understand_anything_viewer.ps1` safely exports and launches any approved project-scoped graph with a caller-supplied local token.
- Viewer runtime: `tools/install_understand_anything_viewer.ps1` performs the one-time pinned v2.9.0 installation under ignored `tools/vendor/`; normal viewer launch has no package-network access.
- Customer-facing viewer branding is neutralized as `Legacy Dashboard POC`; audit: `docs/validation/customer-facing-branding-audit.md`.
- End-to-end data context: the isolated graph now shows the proven Reports controller to repository, EF/LINQ query, selected model, and `MyHealthContext` flow; raw SQL is not represented because no literal SQL evidence exists.
- Completed work: Project memory initialized; Dashboard source discovery completed; deterministic scoped inventory, facts, normalized graph JSON, summary, CLI, and tests created; Roslyn graph-label correction validated on a real .NET 8 SDK; Create Knowledge Graph now validates input, analyzes source, validates the project-scoped graph, optionally loads only that project into Neo4j, and writes customer-facing run status artifacts. Native Tree-sitter extraction is isolated per file; child workers bootstrap the repository-local `src` directory through a copied `PYTHONPATH`, and abnormal exits, timeouts, invalid worker output, startup/import errors, and Python extraction errors produce safe structured warnings while remaining files continue. Profiles now carry explicit scope metadata, audit every discovered file, limit selected-flow graph File nodes and normal Roslyn facts to the approved scope, and expose proven cross-scope semantic references without silently widening the graph. Step 3C.6 loaded only `healthclinic-dashboard-scope-demo-v3` with 123 Neo4j nodes, 169 relationships, 27 warnings, and `scope_complete` coverage. Step 3C.7 now assigns all 123 exported viewer nodes exactly once across five deterministic evidence-derived layers, preserving 169 edges and 27 warnings; the port-5175 viewer returned HTTP 200 for both the page and graph endpoint.
- Next action: `GENERATE_FEATURES` only when explicitly requested. Do not begin stories, architecture, Angular generation, or source modification.
- Blockers: None for Step 3C.6. Known review warnings remain visible: unresolved API-call ownership, implicit MVC `View()` matching, and Roslyn symbols that could not be resolved against the legacy source context.
- Exact next action when resumed: Read prompts through 044, approved KG run `legacy-dashboard-complete-application-demo-v1-2026-09-01-034128`, and `artifacts/application-understanding/latest/`. Await explicit authorization for `GENERATE_FEATURES`.

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

## Approved-KG Application Understanding Rerun

- Approved input: immutable KG run `legacy-dashboard-complete-application-demo-v1-2026-09-01-034128`, readiness `READY_WITH_EXPLAINED_LIMITATIONS`; no KG regeneration, Neo4j load, source scan for reasoning, or external LLM API call occurred.
- Fresh evidence: 139 deterministic packages (27 Razor, 34 AngularJS, 3 route, 24 API, 39 backend, 12 domain), bound to KG identity and manifest hash `6cb7ee92a2711a098fd5927f45be5147ba2dc5b2d89cef009c096b422f243f3b`.
- Validated run: `legacy-dashboard-complete-application-demo-v1-2026-09-01-054440-719694`; package hash, provenance, and claim validation are PASS with zero unsupported claims in the accepted submission and zero external LLM API calls. Every interpreted claim and deterministic UI/route record carries exact evidence-package references.
- Result: 6 meaningful modules, 6 capabilities, 28 workflows, 92 UI surfaces, 6 domain concepts, 2 observed behavioral rules, and 5 dependencies. API evidence includes 58 endpoints, 44 calls, 10 proven mappings, 32 unresolved structural calls, 22 dynamic relationships, 1 external relationship, and 1 call without a backend route.
- Demo candidates: `src/MyHealth.Web/Views/Dashboard/Index.cshtml` for Razor and `DashboardController` for legacy AngularJS. Dashboard tenant context is proven; clinic-summary remains unresolved and year-dependent report URLs remain dynamic.
- Previous-run comparison: the historical `010758-025370` result mechanically produced 88 folder-oriented modules, 1 capability, 16 workflows, 94 UI surfaces, and no domains/rules/dependencies against a KG with no endpoints. The fresh result uses functional grouping and the approved API/domain evidence rather than optimizing counts.
- Tests: focused application-understanding/API/framework suite `25 passed`; final complete repository suite `90 passed, 2 skipped, 0 failed, 0 errors` in `20.57s`.
- Readiness: `APPLICATION_UNDERSTANDING_READY_WITH_LIMITATIONS`. Remaining API and approved Roslyn/opaque-dependency limitations stay explicit. Next action is `GENERATE_FEATURES` only after user authorization.

## Provider And Developer Experience

- Superseded historical result: provider discovery previously produced `WAITING_FOR_PROVIDER_CONFIGURATION`. The normal interactive path no longer accepts `--provider auto` or requires external credentials; Azure and Bedrock are optional headless enterprise boundaries only.
- Codex uses `AGENTS.md` plus `docs/agents/commands/` and does not claim repository-defined slash-menu discovery. GitHub Copilot uses supported `.github/copilot-instructions.md` and `.github/prompts/*.prompt.md` prompt files. Both delegate to the same CLI; see `docs/developer-experience.md`.
- Validation: `python -m pytest -q` returned `74 passed, 2 skipped`. No KG regeneration, Phase-1 change, Neo4j load, feature/story generation, architecture recommendation, or Angular generation occurred.
- Next action: `CONFIGURE_LLM_PROVIDER`.

## Removed Local OpenAI Runtime

- Superseded: the local OpenAI API demo provider and `WAITING_FOR_PROVIDER_CONFIGURATION` normal workflow were removed. They incorrectly required a separate billed API connection while the developer was already using Codex/Copilot Chat. Prompt 038 is historical; prompt 039 records the correction.

## Interactive Agent Architecture Correction

- Completed: the normal interactive `understand-application` path is provider-free. It prepares compact evidence packages and a structured schema, relies on the active Codex/Copilot agent for non-deterministic reasoning, then validates exact KG evidence references before publishing immutable artifacts. It does not read or require external LLM credentials.
- Azure OpenAI and AWS Bedrock remain optional headless enterprise provider boundaries and are not called by interactive mode. API safety remains unchanged: 33 frontend API calls, zero backend endpoint facts, and `BACKEND_MAPPING=UNRESOLVED`.
- Actual validation: Codex prepared and reasoned only over 64 evidence packages, then Polaris accepted and persisted `legacy-dashboard-complete-application-demo-v1-2026-09-01-010758-025370` as `COMPLETE`. The result has 88 modules, one agent capability, 16 workflows, 94 UI surfaces, no business rules/domain concepts/dependencies, and zero rejected claims. It uses zero external API calls.
- Demo traceability: `src/MyHealth.Web/Views/Dashboard/Index.cshtml` has the `Dashboard Razor shell modernization candidate`; `DashboardController` has the `Legacy AngularJS Dashboard controller modernization candidate`; both retain the `Dashboard route workflow` with `BACKEND_MAPPING=UNRESOLVED`.
- Next action: `VALIDATE_APPLICATION_UNDERSTANDING`. Do not proceed to features, stories, architecture recommendation, or Angular generation.

## Application Understanding Validation

- Read-only validation passed for the published `COMPLETE` application-understanding artifact against immutable KG run `legacy-dashboard-complete-application-demo-v1-2026-08-31-184436`: application schema, agent-submission schema, exact package-scoped KG evidence, and all 64 package hashes match. The validation metadata records zero rejected claims, `BACKEND_MAPPING=UNRESOLVED`, and zero external LLM API calls. Source remained unchanged.
- Recovery observation: the mutable `artifacts/knowledge-graph/latest/` directory currently lacks `kg-readiness-analysis.md`, so it cannot independently satisfy the approved-KG gate. Do not retarget or regenerate Phase 2 from that mutable pointer until its review artifact is restored or an approved immutable run is explicitly selected.

## Framework API Contract Analyzer

- Completed: the reusable framework-analyzer registry is wired into normal deterministic KG generation. Current supported analyzers are ASP.NET attribute/conventional route discovery, Razor `@model` and action-link extraction, and AngularJS literal `$http` call extraction with deterministic route matching. Dynamic URLs and ambiguous matches remain unproven.
- New run: `legacy-dashboard-complete-application-demo-v1-2026-09-01-013227` succeeded with 2,384 files, 8,865 facts, 4,878 nodes, 5,148 relationships, zero extraction warnings, and valid graph/evidence integrity. It has 4 endpoint facts, 44 frontend API facts, 0 proven mappings, 3 Razor view-model mappings, 0 Razor action mappings, and 22 visible dynamic-URL review warnings. The source tree is unchanged.
- Readiness: `NOT_READY` for Phase 2 because the new immutable archive has no newly calculated readiness report; do not reuse the earlier readiness result. The new package hashes differ in 8 entries, so the existing Application Understanding is `STALE`. Next action: `COMPLETE_KG_READINESS_ANALYSIS`.
- Forensic readiness analysis for `legacy-dashboard-complete-application-demo-v1-2026-09-01-013227`: graph and evidence integrity pass (4,878 nodes, 5,148 relationships, zero broken endpoints, duplicates, or evidence gaps), and the complete suite passed with 79 passed and 2 skipped. The gate is nevertheless `NOT_READY`: the generic ASP.NET route analyzer mishandles `[Route("api/[controller]")]` and case-sensitive `MyHealth.API` paths, producing only 4 endpoint facts and 0 mappings despite 10 matching literal AngularJS calls. Roslyn has 4,344 unresolved occurrences, including 2 `UNKNOWN`; 4,342 are classified explained limitations. Application Understanding remains `STALE`. Next action: `TARGETED_ANALYZER_FIX`; do not begin Phase 2 or rerun Application Understanding. See `artifacts/knowledge-graph/latest/kg-readiness-analysis.md`.
- Targeted ASP.NET analyzer repair: quote-aware balanced attribute parsing now preserves bracketed `Route`/`RoutePrefix` templates and token evidence; path-segment API fallback is case-insensitive. Generic tests cover bracketed controller/action tokens, `RoutePrefix`, `AcceptVerbs`, `ActionName`, upper/lower/mixed `.api` paths, literal mapping, HTTP mismatch, dynamic/external URLs, and ambiguity. Focused tests passed 11; the full suite passed 87 with 2 skipped. New immutable run `legacy-dashboard-complete-application-demo-v1-2026-09-01-032625` has 58 endpoint facts and 10 proven API mappings, up from 4 and 0, with unchanged source inventory and clean graph/evidence integrity. It is still `NOT_READY` because two Roslyn invocations remain `UNKNOWN`; Application Understanding remains `STALE`. Next action: `ADDITIONAL_DIAGNOSIS`.
- Final KG readiness for immutable run `legacy-dashboard-complete-application-demo-v1-2026-09-01-034128`: `READY_WITH_EXPLAINED_LIMITATIONS`. Graph/evidence integrity pass at 4,931 nodes and 5,205 relationships. Roslyn has 4,344 unresolved occurrences, all classified: 3,701 `COMPILATION_ERROR`, 534 `PROJECT_LOAD_FAILURE`, 107 `OVERLOAD_RESOLUTION`, 2 `INACCESSIBLE`, and 0 `UNKNOWN`; no guessed converter `INVOKES` relationships exist. API metrics remain 58 endpoints, 44 calls, and 10 proven mappings. Focused validation passed 16 with 1 skipped; the complete suite collected 90 and passed 88 with 2 skipped. Application Understanding remains `STALE`; next action is `RERUN_UNDERSTAND_APPLICATION`. See `artifacts/knowledge-graph/latest/kg-readiness-analysis.md`.
