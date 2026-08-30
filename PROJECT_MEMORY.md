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

Step 3B.2 — Roslyn graph-label correction; real SDK validation pending.

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

On a machine with the .NET SDK, build `tools/Polaris.RoslynAnalyzer/Polaris.RoslynAnalyzer.csproj` and run the SDK-gated semantic fixture analysis. Do not begin Step 4 until this real semantic validation passes.

## Step 3B.2 Result

Roslyn enrichment is opt-in through `--enable-roslyn`. The helper uses `SemanticModel`, `GetDeclaredSymbol`, `GetSymbolInfo`, and type-symbol results to emit namespaces, controller/action, type/DTO, property, endpoint, authorization, invocation, and type-reference facts. Fully qualified symbol identities prevent namespace collisions; graph relationships are added only from proven evidence. `RETURNS_TYPE` and `HAS_PROPERTY` now choose `DTO` only when that identity has a proven DTO fact, otherwise `Type`, without duplicate nodes. Python fixture tests pass, but this machine has no `dotnet` executable, so the required real helper build and integration test are pending. LSP remains a documented future interactive boundary, not an implemented analysis provider.

## Step 3A Result

The CLI loads normalized JSON into Neo4j with parameterized, idempotent `MERGE` operations. Graph nodes, generic relationships, warnings, evidence, and project IDs persist as project-scoped data. Clearing requires repeated project-ID confirmation and cannot issue a database-wide delete.

## Step 2.2 Result

Project-to-file graph edges use `CONTAINS`; `CONTAINS_CONTROL` is reserved for file-hosted UI controls/components. MVC `RETURNS` edges are emitted only for explicit static `View("Name")` calls with a matching discovered Razor view. Implicit `View()` calls are review warnings. API calls are owned only by a unique Angular owner declared in the same file; otherwise the File owns the edge with unresolved metadata.

## Project Isolation

The solution is project-agnostic. Every source project is selected by `--source-root` and `--project-id`; artifacts, graph namespace, future Graphiti memory, future Neo4j nodes, architecture decisions, Agile backlog, Figma mappings, and generated outputs must remain isolated by project ID. HealthClinic Dashboard is a sample profile, not hardcoded application logic. Source projects are local runtime inputs and are not committed.

## Recovery Instruction

Before doing any work, read `PROJECT_MEMORY.md`, `PROGRESS.md`, `DECISIONS.md`, and the latest file in `docs/prompts/`. Continue only from the Current Step.
