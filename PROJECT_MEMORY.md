# Project Memory

- Project name: Polaris Modernization POC
- Objective: Customized AI-driven modernization solution for Polaris-style .NET/C# applications into Angular 22.
- Reference source: `source/HealthClinic.biz`
- Read-only source rule: Never modify, format, delete, rename, or add files inside `source/HealthClinic.biz`.

## Final Architecture Vision

Tree-sitter + Roslyn/LSP -> Neo4j knowledge graph -> Graphiti shared memory -> LangGraph orchestration -> LangChain structured LLM work -> policy-driven Angular 22 generation -> build/test/human review

## Angular Target

Angular 22 in an Nx workspace with standalone domain boundaries, Signals for UI state, RxJS for asynchronous boundaries, zoneless change detection, lazy routes, typed API clients, provider-neutral API Gateway/BFF target integration, accessibility, observability, and Playwright. CSR is selected; SSR/hydration, NgRx, microfrontends, and Module Federation are evaluated but not selected.

## Current Step

Prompt 064 executed the real generated Angular 22/Nx validation pipeline from baseline `a7d00a2`. Five implementation repairs resolved the Vitest peer conflict, missing Nx TypeScript ESLint dependency, TypeScript 6 path configuration, strict boolean template bindings, and missing DOM test environment. Dependency installation and `npx nx build healthclinic-web` pass. Unit tests remain blocked before discovery because the generated build target lacks a `development` configuration; the five-repair limit was reached, so serve, browser, and Playwright validation were not executed. Frozen source, requirements, architecture, technical tasks, APIs, and Figma separation remain unchanged. Next action: authorize a focused continuation that adds and validates the missing development build configuration.

## Optional Design And Technical Tasks

- `DesignProvider` isolates downstream planning from provider JSON. `NoDesignProvider` returns `NOT_PROVIDED`; `FigmaDesignProvider` supports real REST access through `FIGMA_ACCESS_TOKEN` and converts invalid URL, missing auth, denied access, unavailable document, network, and invalid-response outcomes into explicit non-blocking statuses.
- `FIXTURE` is a deterministic generic Operational Dashboard sample and is always labeled as fixture data. It is not represented as customer, legacy-source, or live Figma content.
- Normalized design data controls presentation only. Approved requirements control functionality, locked architecture controls technical structure, and explicit inconsistencies produce `DESIGN_REQUIREMENT_CONFLICT` records requiring clarification.
- The canonical technical plan covers only `feature-operational-dashboard-insights`, forms a valid 16-task dependency DAG, and traces Feature, five FRs, three Stories, five hero AC, 28 selected architecture decisions, eight ADRs, four APIs, and optional design nodes.
- `TARGET_CONTRACT_TO_BE_DESIGNED` distinguishes future BFF facade design from the exact four existing backend API contracts. No new endpoint or backend behavior is asserted.

## Agent Command

`/create-knowledge-graph` is registered as a repository-local agent instruction at `docs/agents/commands/create-knowledge-graph.md`. It is a thin wrapper over `python -m polaris_modernization.cli agent-create-knowledge-graph`; deterministic source analysis, validation, and artifact publishing remain the only graph source of truth.

## Complete Application Baseline

The full-application repair retains native worker isolation and now emits literal deterministic C#/JavaScript/Razor facts for first-party worker crashes, rather than allowing a provenance-only record. The latest full analysis produced 2,384 files, 3,386 nodes, 4,593 edges, 38 review warnings, 44 proven opaque dependencies, zero extraction warnings, and `complete_with_opaque_dependencies`. Neo4j loading is pending local credential configuration, so full viewer export remains blocked. Recovery reading includes prompts 010 through 031 plus `docs/validation/complete-application-failure-disposition.md` and `docs/validation/complete-application-final-validation.md`.

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

Await explicit authorization for `FIGMA_ADAPTER_AND_TECHNICAL_TASK_GENERATION`. The Figma provider type is recognized but no connector is implemented; do not claim design analysis, generate tasks or Angular 22 code, implement target Gateway/BFF/Nx infrastructure, or modify legacy source automatically.

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

Profiles now declare reusable evidence-backed scope fields: `scope_id`, `scope_name`, `scope_description`, `scope_type`, and `include_paths`. The `full_application` profile graphs every audited file. A `selected_modernization_flow` profile retains a complete inventory with `in_scope_succeeded`, `in_scope_failed_isolated`, `in_scope_unsupported`, and `out_of_scope` states, while File nodes and normal Roslyn facts are limited to selected paths. Proven cross-scope semantic dependencies are represented honestly by `OutOfScopeReference` nodes and `DEPENDS_ON_OUT_OF_SCOPE` edges. The regenerated v3 HealthClinic root run succeeded with 2,384 audited files, 24 selected graph files, 88 facts, 119 nodes, 167 edges, 11 total warnings, 11 review warnings, and zero extraction warnings. Its coverage is `scope_complete`; no cross-scope dependency was proven. The 2,395-file per-file aggregate source-tree SHA-256 was unchanged at `c8b0e9f1be7724d5a15bb0a6a4ccda73920c653ff65181cc39ba96adbdc795d5`. The graph is ready for the Neo4j Dashboard modernization-flow visual demo; load only `healthclinic-dashboard-scope-demo-v3` after Docker Neo4j is available.

## Step 3C.6 Result

Docker Desktop `4.88.1` and Docker Compose `v5.4.0` started the local `neo4j:5-community` service successfully. The Roslyn-enabled Create Knowledge Graph workflow loaded only `healthclinic-dashboard-scope-demo-v3` into Neo4j with status `succeeded`; the load stage succeeded, scope coverage remained `scope_complete`, and the persisted counts match `knowledge-graph.json`: 123 nodes, 169 edges, and 27 warning records. The scope retains 2,384 audited files, 24 selected File nodes, 2,360 out-of-scope audited files, zero extraction warnings, and 27 visible review warnings. Neo4j contains project-scoped records only for that project ID. The 2,395-file source fingerprint was unchanged before and after: `0b92e1701cdd2374e259ea4fed9811b7e20e4719ff8ea70e4a8aa5023cacf2b4`. See `docs/validation/healthclinic-dashboard-neo4j-visual-demo.md`; do not begin Step 4 without user direction.

## HealthClinic UI Technology Discovery

Read-only discovery confirms `src/MyHealth.Web` is a Legacy ASP.NET MVC/Razor UI with embedded Legacy AngularJS 1.x client-side code: Razor layouts load `/app/app.js`, Dashboard content hosts `ui-view`, and `bower.json` declares Angular `~1.4.5` with AngularJS UI Router. No `angular.json`, `@angular/core`, React, or Vue dependency proof was found. The repository also contains a separate ASP.NET API/backend, data/model/integration libraries, a Node/Express clinic web application, Cordova, and native/mobile projects. The existing `healthclinic-dashboard` profile is a complete legacy UI-flow demo, not a pure Razor-only demo. See `docs/validation/healthclinic-ui-technology-discovery.md`.

## Step 3C.7 Result

The official Understand Anything Windows installer created Codex skill junctions and a local upstream MIT checkout at commit `ba450c43425f3de6d43daf76526950ad8ca93536`; VS Code/Codex must restart to discover those skills. A deterministic adapter exported only the validated canonical graph to ignored `artifacts/healthclinic-dashboard-scope-demo-v3/visualization/.ua/knowledge-graph.json`. It rejects non-approved, incomplete, or extraction-warning inputs, retains canonical labels, relationship types, evidence, and review warnings, and uses no LLM/API calls. The v2.9.0 viewer requires non-empty layers for structural canvas rendering, so the adapter now assigns every canonical node exactly once to five evidence-derived layers and creates a three-step tour of existing Dashboard records. The corrected export retains 123 nodes, 169 edges, and 27 warnings, and is served locally on port 5175. Source remained unchanged at the 2,395-file fingerprint `0b92e1701cdd2374e259ea4fed9811b7e20e4719ff8ea70e4a8aa5023cacf2b4`. See `docs/validation/understand-anything-readonly-visualization.md`.

## Viewer Runbook

Use `docs/runbooks/understand-anything-viewer.md` and `tools/launch_understand_anything_viewer.ps1` to export and launch any approved project-scoped canonical graph locally. The helper requires an explicit project ID, unused port, and caller-supplied local token, writes only ignored visualization output, and must never be replaced with an Understand Anything analyzer command.
The one-time `tools/install_understand_anything_viewer.ps1` installs the official pinned MIT `understand-anything-viewer` v2.9.0 package under ignored `tools/vendor/`; normal launches use only that local executable and make no runtime package request.

## Customer Branding

Customer-visible graph and viewer branding uses `Legacy Dashboard POC`; internal project IDs, paths, and the `polaris_modernization` package remain technical identifiers. See `docs/validation/customer-facing-branding-audit.md`.

## Step 3C.8 Result

`end_to_end_context_flow` adds explicit `transform_ui`, `preserve_backend`, and `preserve_domain_data` roles to selected records and rejects backend records as Angular-generation candidates. Initial local CLI and Neo4j authentication failures were resolved: Roslyn succeeded and the isolated `healthclinic-dashboard-end-to-end-demo-v1` graph was loaded into Neo4j after the local password was corrected. See `docs/validation/healthclinic-dashboard-end-to-end-context-graph.md`.

The graph now also projects the proven Reports controller-to-repository-to-EF/LINQ-to-model-to-`MyHealthContext` paths as read-only context. No raw SQL was found or inferred; dynamic client routes remain warnings.

## Step 2.2 Result

Project-to-file graph edges use `CONTAINS`; `CONTAINS_CONTROL` is reserved for file-hosted UI controls/components. MVC `RETURNS` edges are emitted only for explicit static `View("Name")` calls with a matching discovered Razor view. Implicit `View()` calls are review warnings. API calls are owned only by a unique Angular owner declared in the same file; otherwise the File owns the edge with unresolved metadata.

## Project Isolation

The solution is project-agnostic. Every source project is selected by `--source-root` and `--project-id`; artifacts, graph namespace, future Graphiti memory, future Neo4j nodes, architecture decisions, Agile backlog, Figma mappings, and generated outputs must remain isolated by project ID. HealthClinic Dashboard is a sample profile, not hardcoded application logic. Source projects are local runtime inputs and are not committed.

## Recovery Instruction

Before further work, read `PROJECT_MEMORY.md`, `PROGRESS.md`, `DECISIONS.md`, prompts through 058 under `docs/prompts/`, immutable KG run `legacy-dashboard-complete-application-demo-v1-2026-09-02-050627`, and final BA/SA-quality feature-specification run `legacy-dashboard-complete-application-demo-v1-2026-09-02-023203-926950` plus `artifacts/feature-specifications/latest/`. The UNDERSTAND pillar is frozen `FROZEN_READY_WITH_LIMITATIONS`. Await explicit authorization to implement the LangGraph/LangChain POC orchestration foundation.

## Final API Relationship Resolution Audit And Freeze Gate

Immutable KG run `legacy-dashboard-complete-application-demo-v1-2026-09-02-050627` completes the final UNDERSTAND-pillar API relationship repair. Fact-level API evidence is 33 frontend API calls and 58 backend endpoint facts. The deterministic resolver now proves 32 first-party relationships: 21 `PROVEN_EXACT_STATIC`, 11 `PROVEN_EXACT_TEMPLATE`, 0 `PROVEN_UNIQUE_PARAMETERIZED`, 0 `PROVEN_FRAMEWORK_SEMANTIC`, 0 remaining dynamic-resolvable calls, 0 ambiguous calls, 0 no-backend-route calls, 0 unresolved calls, and 1 true external API call.

The root cause of the earlier Doctor, Patient, Dashboard, Tenant, and User misses was generic rather than application-specific: identifier-backed AngularJS URL variables and simple template/concatenation expressions were extracted but did not flow into deterministic method-plus-route normalization. The reusable `NormalizedApiRoute` resolver now reconciles literal, identifier-backed, and structurally resolvable template/concatenation forms without promoting name-only candidates or adding application-specific rules.

The Knowledge Graph is the authoritative source for proven frontend-to-backend API relationships. Cross-language API relationships may be established deterministically using HTTP method, normalized route/template, uniqueness, and non-contradictory evidence. Dynamic syntax does not automatically mean unresolved; structurally resolvable dynamic paths may become proven. Candidate backend endpoints must not be promoted based only on controller, endpoint, or domain naming. Downstream Features and Feature Specifications consume KG relationship truth and must not independently promote unresolved API relationships. The goal is maximum truthful deterministic resolution, not maximum proven count.

Compared with approved KG run `legacy-dashboard-complete-application-demo-v1-2026-09-01-034128`, deterministic contract enrichment added query-parameter evidence to 24 endpoints, request types to 9 endpoints, request fields to 4 endpoints, and response fields to 10 endpoints. Final feature-specification run `legacy-dashboard-complete-application-demo-v1-2026-09-01-230757-788124` preserves the approved 5 Feature / 12 Story / 14 Acceptance Criterion semantic lineage while promoting all 11 feature-relevant API contracts to `PROVEN`. Tenant API classification remains Feature-relative: supporting for Dashboard, Doctor, Patient, and Clinic; primary for User Access and Tenant Context.

The UNDERSTAND pillar is frozen `FROZEN_READY_WITH_LIMITATIONS`. Remaining legitimate limitations are one true external API call, `complete_with_opaque_dependencies` coverage with 43 opaque dependencies, 72 Roslyn warnings with 4,344 unresolved semantic symbols, and 57 inherited evidence-range anomalies that are unchanged from approved KG run `legacy-dashboard-complete-application-demo-v1-2026-09-01-034128`.

## Repository Hygiene And Frontend API Count Terminology

Cleanup after commit `9970fba` removes five accidentally committed root-level `.tmp-*` execution-output directories and protects equivalent Polaris temporary runs with the narrow `.tmp-*/` ignore rule. Canonical `artifacts/` outputs and immutable approved runs remain unchanged. API resolver production behavior is unchanged.

The historical `FRONTEND_API_CALLS_VISIBLE_PREVIOUS=44` value is the old KG's mixed-producer `api_call` fact count, not 44 distinct source occurrences: 32 facts came from Tree-sitter, 11 from the former AngularJS framework analyzer, and 1 from deterministic crash fallback. Ten framework-analyzer facts duplicate Tree-sitter call sites; one framework-only fact represents `this.$http.get('/clinics')`. The final resolver inventory intentionally contains 33 normalized resolver-input facts from the retained primary extraction paths: 32 Tree-sitter facts plus 1 crash-fallback fact. Of those final facts, 32 are first-party and 1 is external. The difference is therefore reconciled as a fact-producer/model change, not source loss, deduplication performed by the resolver, or a reason to alter analyzer behavior during freeze cleanup.

## Jira-Ready Feature Specification Presentation

Feature Specification run `legacy-dashboard-complete-application-demo-v1-2026-09-02-004448-723610` presents the approved requirements as delivery artifacts for PO, BA, architecture, development, and QA review. The five Markdown documents contain 12 functional requirements, 12 Jira-style Stories, 14 authoritative Given/When/Then Acceptance Criteria, 17 API requirements, 1 supported business rule, and 14 genuine stakeholder clarifications. Dashboard retains its 3 functional requirements, 3 Stories, 5 Acceptance Criteria, and all four required reporting/tenant APIs.

Human-facing Feature Specifications are delivery artifacts, not analysis reports. Machine-readable evidence/provenance remains in JSON/KG while Markdown presents business, functional, API, development, and QA requirements in normal project terminology. The source Feature JSON files remain byte-identical, all human-document leakage and invention counters are zero, and no Knowledge Graph, analyzer, resolver semantics, or application source changed.

## Final BA/SA Feature Specification Semantics

Run `legacy-dashboard-complete-application-demo-v1-2026-09-02-023203-926950` strengthens the approved human-presentation architecture without changing frozen machine meaning. The final semantic layer derives 18 implementable Functional Requirements, 17 concise API requirements, 1 supported business rule, and 17 specific linked clarifications from the approved 5 Features, 12 Stories, and 14 authoritative Acceptance Criteria. Dashboard decomposes naturally into access, yearly expense, yearly patient, clinic summary, and organization-context requirements.

Functional Requirements may decompose approved Story behavior for human readability without changing authoritative Story lineage. Machine evidence remains authoritative; human presentation expresses the supported meaning as BA/SA/developer/QA-readable requirements. Circular Stories, vague human AC, generic clarification questions, backend Task wrappers as primary responses, analysis jargon, and implementation-history language are all zero.

## Project-Aware Roslyn Engine Proof

Generic offline fixtures now prove solution-first, cross-project Roslyn semantic extraction and narrow fallback behavior. `Fixture.Web -> Fixture.Business -> Fixture.Data` is compiler-proven with no fallback; it resolves interface, inheritance, constructor, overload, generic extension, parameter, return, and invocation relationships. A deliberately broken project remains project-owned with explicit `PARTIAL_PROJECT_COMPILATION` and `COMPILATION_ERROR`; only a source file outside all projects uses lower-confidence `SYNTHETIC_FALLBACK` with `PROJECT_LOAD_FAILURE`. No targets are guessed. The focused engine/API/readiness suite passed `11`; no application graph, Neo4j data, or viewer output was regenerated. Recovery reading now includes prompts 010 through 034 and `docs/analysis/roslyn-semantic-diagnostic.md`.

## Phase 2 Application Understanding

Phase 2 remains a separate provider-free LangGraph workflow over an approved immutable KG. Fresh run `legacy-dashboard-complete-application-demo-v1-2026-09-01-054440-719694` is bound to KG `legacy-dashboard-complete-application-demo-v1-2026-09-01-034128` and a deterministic manifest of all 139 evidence-package hashes. Validation passed for KG identity, manifest hash, package references, source provenance, claim evidence, and every `PROVEN` workflow's existing `IMPLEMENTED_BY` edge; external LLM API calls and unsupported accepted claims are zero.

The validated result is `APPLICATION_UNDERSTANDING_READY_WITH_LIMITATIONS`: healthcare operations application; 6 meaningful modules, 6 business capabilities, 28 workflows (15 deterministic routes plus 13 interpreted workflows), 92 UI surfaces, 6 domain concepts, 2 observed behavioral rules, and 5 dependencies. It incorporates 58 backend endpoints, 44 frontend API calls, and 10 proven mappings while retaining 32 unresolved structural calls, 22 dynamic URL relationships, 1 external API relationship, and 1 call without a backend route. The Dashboard Razor view and legacy AngularJS `DashboardController` remain the evidence-backed POC candidates. The earlier 64-package, zero-endpoint run is historical and superseded.

## Evidence-Backed Features

Feature run `legacy-dashboard-complete-application-demo-v1-2026-09-01-141302-518966` is bound to the approved AU and KG through six deterministic module evidence packages and manifest hash `0e7c8f01696e783f574ed3f4ea4ca35618f8d4d62d765ae7c6b9b84caf42ffb2`. It contains five business Features covering all six approved capabilities and 21 of 28 workflows: Operational Dashboard Insights, Doctor Directory Management, Patient Directory Management, Clinic Appointment Experience, and User Access and Tenant Context. Seven generic/error/calendar/report route records remain explicitly uncovered rather than being forced into unsupported business Features.

The POC selects only `feature-operational-dashboard-insights`; its Razor surface is `src/MyHealth.Web/Views/Dashboard/Index.cshtml` and its AngularJS surface is `DashboardController`. All five Features retain at least one proven API relationship; the Dashboard Feature also retains one unresolved and two dynamic report relationships. The appointment Feature is low confidence because the AU lacks a complete appointment-operation workflow. Readiness is `FEATURES_READY_WITH_LIMITATIONS`; next action is `GENERATE_STORIES` only after approval.

## PO/BA Business Feature Enrichment

Business Feature run `legacy-dashboard-complete-application-demo-v1-2026-09-01-145336-704667` enriches the same five Feature IDs and names without changing the approved catalog. Five compact packages bind the exact Feature/AU/KG lineage through manifest hash `d93c012b5729deda3eb481fbf7de75c209c9a4c6df08723550dc997429a5634f`. Machine-readable catalog, stakeholder summary, five individual specifications, POC specification, open questions, validation, provenance, and token metadata are published under `artifacts/business-features/`.

The specifications cover all six capabilities and 21 approved Feature workflows, use six domain concepts, one approved business rule, and five dependencies. No actor/persona is claimed because none is approved upstream; assumptions remain zero. Five value statements are labeled `INFERRED_BUSINESS_VALUE`, and eight open questions retain stakeholder decisions as questions rather than requirements. Deterministic API paths preserve 10 proven, 1 unresolved, and 2 dynamic relationships. Readiness is `BUSINESS_FEATURES_READY_WITH_LIMITATIONS`; next action is `GENERATE_JIRA_STYLE_STORIES` only after approval.

## Evidence-Backed Jira-Style Stories

Story run `legacy-dashboard-complete-application-demo-v1-2026-09-01-105453-078418` is bound to the approved KG/AU/Feature/Business Feature lineage through 12 deterministic workflow-boundary packages and manifest `cfcb2ed6775cca46374feab41abab20442610ccc2be7f29d995e4bdc525ba194`. The catalog contains 12 stable Stories across all five Business Features, all six capabilities, and all 21 approved Business Feature workflows. Priorities are 6 high, 4 medium, and 2 low.

All Stories use the evidence-safe actor `user of the existing application` at low actor confidence because no persona is approved. All 12 preserve `INFERRED_BUSINESS_VALUE`, assumptions remain zero, all eight stakeholder questions are mapped, and API truth remains 7 Stories with proven mappings, 1 with unresolved mapping, 1 with dynamic mappings, and none with external mappings. The two-Story Dashboard POC includes `Open Operational Dashboard`, which spans the approved Razor and AngularJS surfaces, and `View Tenant-Aware Dashboard Summary`, which retains the unresolved clinic-summary limitation. No Acceptance Criteria or Story Points were generated. Readiness is `STORIES_READY_WITH_LIMITATIONS`; next action is `GENERATE_ACCEPTANCE_CRITERIA` only after approval.

## Evidence-Backed Acceptance Criteria

AC run `legacy-dashboard-complete-application-demo-v1-2026-09-01-112024-635713` binds 12 Story-scoped evidence packages to the immutable Story run. Fourteen criteria cover all 12 Stories: 8 proven and 6 supported with limitations. The two extra criteria define POC modernization preservation contracts without architecture or implementation detail. API truth remains 8 AC with proven, 2 with unresolved, 1 with dynamic, and none with external relationships. Eight open questions remain unanswered; nine AC require stakeholder validation. No persona, assumption, NFR, validation rule, error behavior, contradiction, duplicate, or untraceable criterion was introduced.

Polaris supports an optional target-design input such as Figma after Acceptance Criteria and before or fused into Target Architecture. Figma describes target UX/design and must not silently redefine evidence-backed existing behavior. No design analysis occurred in this phase. Readiness is `ACCEPTANCE_CRITERIA_READY_WITH_LIMITATIONS`; next action requires explicit selection between optional design analysis and Target Architecture.

## Consolidated Feature Specifications

Feature Specification run `legacy-dashboard-complete-application-demo-v1-2026-09-01-114638-016471` provides exactly five paired Markdown/JSON contracts, one per approved Feature. All 12 Stories and 14 Acceptance Criteria appear exactly once under their approved parents. Markdown is the primary human validation contract; JSON retains the exact lineage and machine traceability contract for downstream automation. Internal analyzer diagnostics are excluded from primary Markdown while useful legacy surface, integration, data, constraint, decision, and preservation context remains available for architecture review.

The Dashboard specification contains all three Feature Stories and all five Feature AC, including the approved two-Story/four-AC POC subset. Target design is `NOT_YET_ANALYZED`, Target Architecture is pending, and modernization is not started. No Feature, Story, AC, persona, rule, NFR, security requirement, target UX, Figma reference, or architecture decision was invented. Readiness is `FEATURE_SPECIFICATIONS_READY_WITH_LIMITATIONS`; next action remains explicit selection of optional target-design analysis or Target Architecture.

## Professional Feature Presentation

Refined run `legacy-dashboard-complete-application-demo-v1-2026-09-01-121011-515356` keeps all five JSON machine contracts byte-identical to source Feature Specification run `legacy-dashboard-complete-application-demo-v1-2026-09-01-114638-016471` while replacing concatenated Markdown with a semantic-preserving presentation layer. Forty-seven mapped transformations cover 21 workflow labels, 12 Story statements, and 14 Acceptance Criteria. Semantic equivalence passes for every transformed contract.

All 22 document/role quality dimensions score at least 9.0 across every Feature. Internal diagnostic noise and rendering defects are zero; MD/JSON parity and provenance pass. The POC Dashboard document has a stakeholder summary, natural Stories, business-triggered criteria, professional integration clarification, pending Figma/architecture status, and separated technical traceability. Readiness is `FEATURE_PRESENTATION_READY_WITH_LIMITATIONS`; inherited uncertainty remains unchanged.

## Feature Narrative Synthesis

Narrative run `legacy-dashboard-complete-application-demo-v1-2026-09-01-121948-351008` replaces template concatenation with explicit Feature Evidence and Feature Narrative models. It groups multiple workflow/UI/API/source records into 12 traceable business concepts, assigns section ownership/audience/importance, renders eight useful stakeholder sections, and retains all five immutable JSON contracts, 12 Stories, and 14 authoritative AC. Semantic duplication is zero and every narrative statement is traceable.

Customer comprehension and manual reviews pass for Dashboard and all five Features. Every required coherence/usability score is 10.0, with zero raw workflow mechanics, diagnostic noise, invention, or untraceable narrative statements. Readiness is `FEATURE_NARRATIVE_READY_WITH_LIMITATIONS`; inherited application uncertainty remains visible as decisions or constraints.

## Modernization Feature Specifications

The finalized immutable run is `legacy-dashboard-complete-application-demo-v1-2026-09-01-132759-483752`, derived from narrative run `legacy-dashboard-complete-application-demo-v1-2026-09-01-121948-351008` and approved KG run `legacy-dashboard-complete-application-demo-v1-2026-09-01-034128`. It preserves five machine Feature contracts, 12 Stories, and 14 authoritative Acceptance Criteria byte-for-byte while adding an evidence-backed current API view to the human narrative model.

The approved KG baseline is 58 backend endpoint facts, 44 frontend API-call facts, 10 proven mappings, 22 dynamic URL warnings, one external call, one no-backend-route call, and 32 unresolved structural calls. The five Features contain 11 caller-specific relevant contracts: eight proven, two dynamic, one unresolved, and zero external. Eight contracts expose a proven method, route, controller, action, and response type; no relevant proven contract establishes path/query parameters, request DTOs/fields, or response fields. All 110 populated technical fields are traceable and no absent detail is inferred.

Natural-language realization now produces coherent behavior, Story, and AC clauses and rejects broken verb constructions and concatenated outcome fragments. Manual review passes all five Feature documents, including the Dashboard's proven/dynamic/unresolved distinctions; the minimum criterion score is 9.2 rather than an automatic perfect score. Focused tests pass 8; the full suite passes 131 with 2 skipped. Source applications, approved KG artifacts, and upstream machine contracts are unchanged. Target design remains `NOT_YET_ANALYZED`, target architecture remains `PENDING`, and modernization has not started.

## Final Feature Specification Correction

Final run `legacy-dashboard-complete-application-demo-v1-2026-09-01-135345-568122` re-evaluates Feature API completeness from every approved caller file rather than treating the previous 11 Story-selected contracts as complete. Tenant context is now supporting/shared for Dashboard, Doctor, Patient, and Clinic, and primary for User Access/Tenant Context. Doctor, Clinic/Tenant, Patient, User-management, and Dashboard reporting calls without `IMPLEMENTED_BY` proof remain explicit unresolved/dynamic primary interactions with candidate endpoints that are never promoted.

## Final PO/BA Semantic Refinement

Run `legacy-dashboard-complete-application-demo-v1-2026-09-01-142601-917816` adds explicit Story and Acceptance Criterion semantic models, Feature-name/behavior alignment, stakeholder-enrichment records, semantic circularity checks, limitation-aware readiness, and evidence-sensitive quality scores. Evidence-proven behavior is distinct from supported business interpretation and stakeholder intent. Missing business rationale is not invented to satisfy a User Story template; five Stories request stakeholder enrichment instead.

All 14 authoritative AC remain present: 4 are fully testable from current evidence, 8 are testable with explicit evidence limitations, and 2 modernization-preservation criteria are rendered separately. Clinic Appointment Experience is `PARTIALLY_ALIGNED` because appointment creation, update, and scheduling behavior is not established; the Feature is not renamed and an explicit PO/BA decision is recorded. Technical/API completeness and PO/BA semantic quality remain independent readiness dimensions.

All five Features have explicit primary-behavior coverage with inherited uncertainty. User Access has four proven primary context contracts; the other Features expose primary business calls as unresolved or dynamic plus a proven shared tenant contract. The documents use non-circular Stories, workflow-derived AC preconditions, labeled modernization-preservation criteria, and separate Primary, Supporting, and Unresolved/Dynamic integration sections. Target design, architecture, and modernization status remain unchanged.

## Provider And Developer Experience

Historical note, superseded by prompt 039: the former provider-driven Phase-2 workflow waited for credentials. Azure OpenAI and Bedrock now remain only optional headless enterprise boundaries; Codex capability guides and GitHub Copilot prompt files invoke the provider-free interactive flow. Repository-defined slash-command discovery is not claimed for Codex. See `docs/developer-experience.md`.

## Headless Provider Boundary

The previous local OpenAI demo runtime was removed from normal developer use. Azure OpenAI and Bedrock remain optional future headless enterprise adapters, isolated from the interactive Codex/Copilot workflow and its artifacts.

## Interactive Agent Architecture Correction

Interactive Phase 2 no longer uses the OpenAI local-demo runtime or requires `OPENAI_API_KEY`. Codex Chat is the primary active reasoning agent and GitHub Copilot Chat is a compatible client interface. Polaris deterministically prepares approved KG evidence packages and schema, the active agent reasons only over those packages, and Polaris deterministically validates and persists the submission. Azure OpenAI and Bedrock are retained only as optional future headless enterprise adapters. Recovery reading includes prompt 039 and `docs/developer-experience.md`.

The validated interactive run `legacy-dashboard-complete-application-demo-v1-2026-09-01-010758-025370` is `COMPLETE`: 64 evidence packages, zero external API calls, 88 modules (87 deterministic plus one agent interpretation), one evidence-backed capability, 16 workflows, 94 UI surfaces, and zero rejected claims. It identifies the Dashboard Razor view and legacy AngularJS `DashboardController` as the approved demo candidates. All backend mappings remain unresolved because the approved KG has 33 frontend API calls and zero backend endpoint facts.

## Framework API Contract Analyzer

The framework-analyzer registry now runs inside normal deterministic KG generation and adds evidence-backed ASP.NET endpoint, Razor contract, and AngularJS API-call facts. The regenerated run `legacy-dashboard-complete-application-demo-v1-2026-09-01-013227` is structurally valid but not readiness-approved until a new readiness analysis is calculated. Its 64 evidence packages differ from the prior application-understanding packages in 8 hashes, so Application Understanding is stale and must not be treated as current. Recovery reading includes prompt 040.

## Forensic Readiness Gate

The immutable `legacy-dashboard-complete-application-demo-v1-2026-09-01-013227` run passes structural and evidence integrity: 4,878 nodes, 5,148 relationships, and zero broken references, duplicate IDs/relationships, or evidence gaps. The complete regression suite passed with 79 tests passed and 2 skipped.

This run is `NOT_READY` for Phase 2. The generic ASP.NET attribute-route analyzer terminates class-attribute matching at the `]` in the literal `[controller]` and has a case-sensitive `/Api/` fallback. It emits 4 endpoints and 0 proven mappings even though source evidence shows 12 attribute-routed controllers, 55 HTTP method attributes, and 10 matching literal AngularJS calls to `UsersController` routes. Roslyn contributes 4,344 unresolved occurrences: 4,342 explained limitations and 2 `UNKNOWN` items.

Application Understanding remains `STALE`; do not run it or begin Phase 2. The required next action is `TARGETED_ANALYZER_FIX`, followed by a new immutable graph run and a new forensic gate. Read `artifacts/knowledge-graph/latest/kg-readiness-analysis.md` on recovery.

## Targeted ASP.NET Route Repair

The generic route repair is complete. A deterministic balanced attribute scanner now preserves quoted route attributes containing bracket tokens, records source route templates and token resolution, supports `Route`, `RoutePrefix`, HTTP verb attributes, `AcceptVerbs`, and `ActionName`, and handles API path segments case-insensitively. It contains no application-specific conditions.

The new immutable run `legacy-dashboard-complete-application-demo-v1-2026-09-01-032625` has 58 backend endpoint facts and 10 proven frontend mappings, compared with 4 and 0 in `013227`. The real source retains 55 endpoint facts across 12 controllers with `api/[controller]` class templates. Focused framework tests passed 11 and the complete suite passed 87 with 2 skipped. Source inventory/hash data is unchanged, and graph/evidence integrity pass.

The new forensic gate remains `NOT_READY`, not because either targeted defect remains, but because Roslyn still has two `UNKNOWN` unresolved invocations in the iOS client. Application Understanding remains `STALE`; do not begin Phase 2. Next action: `ADDITIONAL_DIAGNOSIS`. Recovery reading includes prompt 041 and `artifacts/knowledge-graph/latest/kg-readiness-analysis.md`.

## Reusable Polaris Command Interface

Polaris now exposes 19 canonical lifecycle commands through one metadata registry and `CommandService`. The `polaris` CLI, Codex adapter, and Copilot prompt delegate to that shared service; future MCP adapters can do the same. Feature resolution and lifecycle status come from persisted artifacts and `artifacts/commands/feature-index.json`, with explicit unknown and ambiguity failures. Generic production command code contains no HealthClinic-specific branch.

## Architecture Inheritance

Feature planning resolves an explicit valid lock under `artifacts/architecture/features/<feature-id>/latest` first, then inherits the canonical application lock under `artifacts/architecture/latest`. Feature-index metadata distinguishes direct selection from effective availability and references the authoritative selection rather than copying application decisions into every Feature. Missing or invalid locks recommend `/recommend-architecture` without a Feature argument.

## Final Knowledge Graph Readiness

Immutable run `legacy-dashboard-complete-application-demo-v1-2026-09-01-034128` is approved as `READY_WITH_EXPLAINED_LIMITATIONS`. Graph and evidence integrity pass at 2,384 files, 8,929 pipeline facts, 4,931 nodes, and 5,205 relationships. There are no duplicate IDs/relationships, broken endpoints, evidence gaps, invalid evidence paths/hashes/lines, or framework classification conflicts.

Roslyn has 4,344 unresolved occurrences, all deterministically classified: 3,701 compilation errors, 534 project-load failures, 107 overload-resolution limitations, two inaccessible calls, and zero unknowns. The two converter calls in `HomeView.cs` remain unresolved at confidence zero with candidate evidence and no guessed `INVOKES` edges. Framework/API evidence remains stable at 58 endpoints, 44 frontend calls, and 10 proven mappings. The complete suite collected 90 tests: 88 passed and 2 skipped.

Application Understanding remains `STALE` because its prior complete output predates the approved KG. The next action is `RERUN_UNDERSTAND_APPLICATION`; do not generate features, stories, architecture, or Angular work before that rerun is explicitly requested. Recovery reading includes prompts through 043 and `artifacts/knowledge-graph/latest/kg-readiness-analysis.md`.
