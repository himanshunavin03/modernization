# Project Memory

- Project name: Polaris Modernization POC
- Objective: Customized AI-driven modernization solution for Polaris-style .NET/C# applications into Angular 22.
- Reference source: `source/HealthClinic.biz`
- Read-only source rule: Never modify, format, delete, rename, or add files inside `source/HealthClinic.biz`.

## Final Architecture Vision

Tree-sitter + Roslyn/LSP -> Neo4j knowledge graph -> Graphiti shared memory -> LangGraph orchestration -> LangChain structured LLM work -> policy-driven Angular 22 generation -> build/test/human review

## Angular Target

Angular 22, Nx modular monolith, standalone components, Signals, OnPush, lazy routes, typed API clients, typed Reactive Forms, guards/interceptors, SSR/BFF configurable by policy.

## Current Step

Step 3C.5 — Scope-complete HealthClinic Dashboard Neo4j visual-demo preparation.

## Step 1 Result

The Dashboard MVC view is a protected Razor shell. It composes Dashboard partials and delegates feature content/navigation to client-side components and an AngularJS `ui-view`. The detailed evidence and unproven areas are recorded in `docs/dashboard-analysis.md`.

## Step 2 Result

The current Git repository root is the solution root. A Python 3.11 deterministic extractor uses Tree-sitter JavaScript, HTML, and C# grammars to inventory the approved Dashboard scope and write evidence-bearing inventory, facts, graph, and summary artifacts under `artifacts/`. It does not call an LLM or modify the reference source.

## Approved Future Capabilities

- Transform the knowledge graph into PRDs, epics, features, user stories, acceptance criteria, and traceability links for business approval before code generation.
- Accept customer Figma designs as optional target-design input for target look and design tokens; retain the knowledge graph as evidence for existing behavior and APIs.
- Discover and reuse approved Angular shared components and design systems before generating duplicate components.
- Create a target architecture assessment, architecture diagram, ADR, Nx boundaries, and migration plan before Angular generation.
- Select standard Angular, Nx modular monolith, or microfrontend architecture through evidence-based, rule-driven assessment of shared libraries, SSR/hydration, BFF, Signals, typed forms, security, and testing.
- Keep Angular 22 Nx modular monolith as the likely POC default while making the architecture assessment configurable.

## Next Step

Install/start Docker Neo4j and load only `healthclinic-dashboard-scope-demo-v3` for the visual demo. Use the scope-complete profile graph validated in `docs/validation/healthclinic-dashboard-scope-complete-v3.md`; do not begin Step 4.

## Step 3B.2 Result

Roslyn enrichment is opt-in through `--enable-roslyn`. The helper uses `SemanticModel`, `GetDeclaredSymbol`, `GetSymbolInfo`, and type-symbol results to emit namespaces, controller/action, type/DTO, property, endpoint, authorization, invocation, and type-reference facts. `RETURNS_TYPE` and `HAS_PROPERTY` choose `DTO` only when that identity has a proven DTO fact, otherwise `Type`, without duplicate nodes. LSP remains a documented future interactive boundary, not an implemented analysis provider.

## Step 3B.3 Result

Local validation on .NET SDK `8.0.424` built `tools/Polaris.RoslynAnalyzer/Polaris.RoslynAnalyzer.csproj`, passed `python -m pytest -q` with `13 passed, 1 skipped`, and ran `python -m polaris_modernization.cli analyze --source-root tests\fixtures\roslyn-semantic --project-id semantic-fixture --profile default --output artifacts --enable-roslyn` successfully. The helper now emits fully qualified CLR symbol identities, including framework types such as `global::System.String`, and the semantic fixture produced `artifacts/semantic-fixture/roslyn-semantic.json` plus `knowledge-graph.json` with proven `DECLARES`, `EXPOSES`, `RETURNS_TYPE`, `HAS_PROPERTY`, `INVOKES`, and `PROTECTED_BY` edges. `Fetch` returns `ShipmentSummary` as `DTO`, `Status` returns `global::System.String` as `Type`, and the semantic fixture source hash remained unchanged.

## Step 3A Result

The CLI loads normalized JSON into Neo4j with parameterized, idempotent `MERGE` operations. Graph nodes, generic relationships, warnings, evidence, and project IDs persist as project-scoped data. Clearing requires repeated project-ID confirmation and cannot issue a database-wide delete.

## Step 3C Result

`python -m polaris_modernization.cli create-knowledge-graph` is the executable deterministic Create Knowledge Graph workflow. It validates a safe project ID and source directory, runs Tree-sitter analysis with optional Roslyn enrichment, validates project-scoped graph records, optionally loads only that graph into Neo4j, and writes ignored customer-facing `graph-run-status.json` plus `graph-run-summary.md` under `artifacts/<project-id>/`. It defaults to graph-only mode and reports Neo4j configuration or connection failures as a controlled failed stage without any delete operation. Local validation against `tests/fixtures/roslyn-semantic` with `--enable-roslyn --skip-neo4j` succeeded with 1 file, 32 facts, 26 nodes, 23 edges, and 0 warnings; source hashes remained unchanged. Docker was unavailable locally, so optional Neo4j end-to-end validation was not run.

## Step 3C.1 Result

Each native Tree-sitter extraction now runs in an isolated child Python process through structured JSON input and argument-array invocation. The worker derives the local `src` directory from its module location, prepends it to a copied `PYTHONPATH`, and uses the repository root as its explicit working directory when available, so it works from uninstalled source checkouts, editable installs, and normal package installs. The parent detects startup/import failures separately from abnormal parser exits, timeouts, invalid worker output, and Python extraction errors without recording source content or worker tracebacks. Failed files receive `failed_isolated` inventory status and a structured `skipped` extraction warning; no facts are invented. Partial runs write all artifacts and return `succeeded_with_warnings`, while all-files-failed runs return `failed`; Neo4j loading is blocked when isolated extraction warnings exist. The verified `source/HealthClinic.biz` graph-only retry completed as `succeeded_with_warnings` with 2,384 files, 8,262 facts, 5,309 nodes, 5,975 edges, and 47 extraction warnings. `MobileServices.Web.js` was safely isolated exactly once after exit code `3221225477`, and the 2,395-file source-tree SHA-256 fingerprint was unchanged before and after the run.

## Step 3C.3 Result

The scoped `source/HealthClinic.biz/src/MyHealth.Web` Dashboard demo graph run completed as `succeeded_with_warnings`: 326 files, 321 facts, 518 nodes, 604 edges, 120 total warnings, and 1 extraction warning. Framework detection identified ASP.NET MVC/Razor. Dashboard controller/action, authorization, route, UI-control, and dashboard API-call relationships were proven. `Views/Home/Index.cshtml` caused one isolated HTML worker abnormal exit (`3221225477`) and was skipped without source modification; the 326-file source hash remained unchanged. Neo4j was not loaded and the graph is not ready for visual demo until warning review.

## Step 3C.4 Result

The reusable `healthclinic-dashboard` YAML profile was run from the HealthClinic repository root. Its selected paths exclude `src/MyHealth.Web/Views/Home/Index.cshtml`, so the known failing HTML file was not selected for extraction. The clean project graph completed successfully with 2,384 inventoried files, 6,967 facts, 4,597 nodes, 4,095 edges, 2,055 total warnings, and 0 extraction warnings. Dashboard controller/action, authorization, UI-control, AngularJS route, and dashboard API-call relationships were proven. The full 2,395-file source-tree SHA-256 fingerprint was unchanged. The graph is ready for Neo4j visual-demo loading only after Docker Neo4j is installed and started; do not begin Step 4.

## Step 3C.5 Result

Profiles now declare reusable evidence-backed scope fields: `scope_id`, `scope_name`, `scope_description`, `scope_type`, and `include_paths`. The `full_application` profile graphs every audited file. A `selected_modernization_flow` profile retains a complete inventory with `in_scope_succeeded`, `in_scope_failed_isolated`, `in_scope_unsupported`, and `out_of_scope` states, while File nodes and normal Roslyn facts are limited to selected paths. Proven cross-scope semantic dependencies are represented honestly by `OutOfScopeReference` nodes and `DEPENDS_ON_OUT_OF_SCOPE` edges. The final v3 HealthClinic root run succeeded with 2,384 audited files, 24 selected graph files, 88 facts, 119 nodes, 167 edges, 11 review warnings, and zero extraction warnings. Its coverage is `scope_complete`; no cross-scope dependency was proven. The 2,395-file per-file aggregate source-tree SHA-256 was unchanged at `c8b0e9f1be7724d5a15bb0a6a4ccda73920c653ff65181cc39ba96adbdc795d5`. The graph is ready for the Neo4j Dashboard modernization-flow visual demo; load only `healthclinic-dashboard-scope-demo-v3` after Docker Neo4j is available.

## Step 2.2 Result

Project-to-file graph edges use `CONTAINS`; `CONTAINS_CONTROL` is reserved for file-hosted UI controls/components. MVC `RETURNS` edges are emitted only for explicit static `View("Name")` calls with a matching discovered Razor view. Implicit `View()` calls are review warnings. API calls are owned only by a unique Angular owner declared in the same file; otherwise the File owns the edge with unresolved metadata.

## Project Isolation

The solution is project-agnostic. Every source project is selected by `--source-root` and `--project-id`; artifacts, graph namespace, future Graphiti memory, future Neo4j nodes, architecture decisions, Agile backlog, Figma mappings, and generated outputs must remain isolated by project ID. HealthClinic Dashboard is a sample profile, not hardcoded application logic. Source projects are local runtime inputs and are not committed.

## Recovery Instruction

Before doing any work, read `PROJECT_MEMORY.md`, `PROGRESS.md`, `DECISIONS.md`, prompts 010 through 015 under `docs/prompts/`, `docs/agents/create-knowledge-graph.md`, and `docs/validation/healthclinic-dashboard-scope-complete-v3.md`. Continue only from the Current Step.
