We are building a customized Polaris AI modernization POC.

The project must preserve its own durable memory. If this Codex session fails, another Codex session must be able to read the project files and continue from the exact same point.

STRICT BOUNDARIES

- source/HealthClinic.biz is read-only reference code.
- Never modify, format, delete, rename, or add files inside source/HealthClinic.biz.
- Create all new files only inside solution/.
- This is a proof of concept, not a production solution.
- Do not generate Angular code, install packages, create Docker files, connect Neo4j, or scaffold the full platform in this step.

FIRST: CREATE DURABLE PROJECT MEMORY

Create this structure inside solution/:

solution/
README.md
PROJECT\_MEMORY.md
PROGRESS.md
DECISIONS.md
AGENTS.md
.github/
copilot-instructions.md
docs/
prompts/
001-initial-discovery.md
dashboard-analysis.md

Initialize solution/ as its own Git repository if it is not already initialized.

Put the complete text of this prompt, unchanged, into:
solution/docs/prompts/001-initial-discovery.md

Create PROJECT\_MEMORY.md with:

- Project name: Polaris Modernization POC
- Objective: customized AI-driven modernization solution for Polaris-style .NET/C# applications into Angular 22
- Reference source: source/HealthClinic.biz
- Read-only source rule
- Final architecture vision:
  Tree-sitter + Roslyn/LSP → Neo4j knowledge graph → Graphiti shared memory →
  LangGraph orchestration → LangChain structured LLM work →
  policy-driven Angular 22 generation → build/test/human review
- Angular target:
  Angular 22, Nx modular monolith, standalone components, Signals, OnPush,
  lazy routes, typed API clients, typed Reactive Forms, guards/interceptors,
  SSR/BFF configurable by policy
- Current step: Step 1 — Dashboard source discovery
- Recovery instruction:
  “Before doing any work, read PROJECT\_MEMORY.md, PROGRESS.md, DECISIONS.md,
  and the latest file in docs/prompts/. Continue only from the Current Step.”

Create AGENTS.md and .github/copilot-instructions.md with these permanent rules:

1. Always read PROJECT\_MEMORY.md, PROGRESS.md, and DECISIONS.md before work.
2. Never modify source/HealthClinic.biz.
3. Create all work only in solution/.
4. Before implementing a new user request, save that request in docs/prompts/
   using the next sequential number.
5. After every completed task, update PROJECT\_MEMORY.md and PROGRESS.md.
6. Record architecture choices in DECISIONS.md with the reason.
7. Never claim something was analyzed, generated, tested, or working unless it is proven.
8. If blocked, document the blocker and the exact next action in PROGRESS.md.

Create PROGRESS.md with:

- Status: In progress
- Current step: Step 1 — Dashboard source discovery
- Completed work: Project memory initialized
- Next action: Analyze selected legacy Dashboard flow and write dashboard-analysis.md
- Resume command:
  “Read PROJECT\_MEMORY.md, PROGRESS.md, DECISIONS.md, and docs/prompts/001-initial-discovery.md, then continue Step 1.”

Create DECISIONS.md and record:

- The solution is customized for Polaris-style enterprise applications, not a generic conversion tool.
- HealthClinic.biz is only a public reference application for the POC.
- The POC will support one selected legacy ASP.NET MVC Dashboard flow first.
- Neo4j is the source-of-truth code/UI knowledge graph.
- Graphiti is shared team/agent working memory, not the source-of-truth code graph.
- LangGraph orchestrates the workflow; LangChain manages LLM schemas, retrieval, and structured outputs.
- The first runnable target will be Angular 22 Nx modular monolith.

SECOND: ANALYZE ONLY THIS SOURCE SCOPE

Analyze only:

source/HealthClinic.biz/src/MyHealth.Web/Views/Dashboard
source/HealthClinic.biz/src/MyHealth.Web/Views/Shared
source/HealthClinic.biz/src/MyHealth.Web/Controllers
source/HealthClinic.biz/src/MyHealth.Web/Models

Create solution/docs/dashboard-analysis.md.

The report must be fact-based and include:

- Dashboard Razor views and shared layouts
- Navigation/menu items
- UI controls: cards, tables, charts, forms, buttons, filters
- Related controllers, actions, models, and view models
- Authentication/authorization indicators
- API, service, repository, or database dependencies
- User actions and navigation flow
- Source file paths and line references for important findings
- Proposed Neo4j nodes and relationships
- “Needs review” section for anything not proven from source
- “Recommended Angular 22 target feature” section:
  proposed route, standalone components, Signals/local state, typed Reactive Form if needed,
  typed API client, Nx library boundaries, and tests to generate later

When finished:

- Update PROJECT\_MEMORY.md, PROGRESS.md, and DECISIONS.md.
- Do not start Step 2.
- Give me a concise summary of files created and findings.
