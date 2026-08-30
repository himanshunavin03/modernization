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

Step 2.1 complete — reusable deterministic scanner and repository hygiene validated.

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

Step 3 — load project-scoped knowledge graph JSON into Neo4j and add a Roslyn/LSP semantic enrichment adapter.

## Project Isolation

The solution is project-agnostic. Every source project is selected by `--source-root` and `--project-id`; artifacts, graph namespace, future Graphiti memory, future Neo4j nodes, architecture decisions, Agile backlog, Figma mappings, and generated outputs must remain isolated by project ID. HealthClinic Dashboard is a sample profile, not hardcoded application logic. Source projects are local runtime inputs and are not committed.

## Recovery Instruction

Before doing any work, read `PROJECT_MEMORY.md`, `PROGRESS.md`, `DECISIONS.md`, and the latest file in `docs/prompts/`. Continue only from the Current Step.
