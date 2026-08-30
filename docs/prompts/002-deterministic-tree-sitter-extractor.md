We are starting Step 2 of the customized Polaris Modernization POC.

IMPORTANT:
Codex is now building the customized solution. Codex must not manually act as the runtime analyzer.

The runtime analyzer must use deterministic parsing. Do not call an LLM, LangChain, LangGraph, Graphiti, OpenAI, Copilot, or any AI API in this step.

Before doing anything:
1. Read PROJECT_MEMORY.md, PROGRESS.md, DECISIONS.md, AGENTS.md, and docs/prompts/001-initial-discovery.md.
2. Create docs/prompts/002-deterministic-tree-sitter-extractor.md.
3. Copy this complete prompt unchanged into that file.
4. Treat the current Git repository root as the solution root. Do not create a nested solution/ folder.
5. Never modify the HealthClinic reference source.

FIRST: UPDATE PROJECT MEMORY

Update PROJECT_MEMORY.md and DECISIONS.md to add these approved future capabilities:

1. The knowledge graph will be transformed into PRDs, epics, features, user stories, acceptance criteria, and traceability links for business approval before code generation.
2. Customer Figma designs are an optional target-design input. They define the target look and design tokens; the knowledge graph defines existing behavior and APIs.
3. Existing approved Angular shared components/design systems must be discovered and reused before generating duplicate components.
4. Before Angular generation, the solution must create a target architecture assessment, architecture diagram, ADR, Nx boundaries, and migration plan.
5. Architecture choice must be evidence-based and rule-driven, not LLM-only:
   standard Angular application vs Nx modular monolith vs microfrontend,
   shared libraries, SSR/hydration, BFF, Signals, typed forms, security, and testing.
6. The likely default target for the POC is Angular 22 Nx modular monolith, but the architecture assessment must remain configurable.

SECOND: IMPLEMENT STEP 2 — DETERMINISTIC SOURCE EXTRACTOR

Create a Python project for a deterministic source extractor.

Create this structure:

src/
  polaris_modernization/
    __init__.py
    cli.py
    config.py
    models.py
    source_inventory.py
    tree_sitter_extractors/
      __init__.py
      javascript.py
      html.py
      csharp.py
    graph/
      __init__.py
      normalizer.py
      writer.py

config/
  poc-scope.yaml

tests/
  test_source_inventory.py
  test_dashboard_extraction.py

artifacts/
  .gitkeep

pyproject.toml
README.md

Use Python and real Tree-sitter packages for:
- JavaScript
- HTML
- C#

Do not use regular expressions as a fallback parser.
If a grammar or parser is unavailable, fail clearly and document the blocker.

The solution must accept the reference source root as a command-line argument, for example:

python -m polaris_modernization.cli analyze ^
  --source-root "..\source\HealthClinic.biz" ^
  --scope dashboard ^
  --output "artifacts"

The code must not assume a fixed absolute path.

THIRD: POC SCOPE TO EXTRACT

For scope=dashboard, inspect only these source areas:

src/MyHealth.Web/Views/Dashboard/
src/MyHealth.Web/Views/Shared/
src/MyHealth.Web/Controllers/DashboardController.cs
src/MyHealth.Web/Controllers/AccountController.cs
src/MyHealth.Web/content/app/app.module.js
src/MyHealth.Web/content/app/components/dashboard/
src/MyHealth.Web/content/app/components/shared/directives/headerBar/
src/MyHealth.Web/content/app/components/shared/directives/leftMenu/
src/MyHealth.Web/content/app/components/shared/shared.module.js

FOURTH: REQUIRED OUTPUT

Generate these files after analysis:

artifacts/source-inventory.json
artifacts/dashboard-facts.json
artifacts/dashboard-graph.json
artifacts/dashboard-analysis-summary.md

Every discovered fact must include:
- source path
- line start and line end
- extraction method: tree-sitter
- confidence: 1.0 for deterministic facts
- source hash

The normalized graph JSON must include nodes and edges for any proven item among:

Nodes:
Application
File
RazorView
Layout
PartialView
ScriptAsset
StyleAsset
Controller
Action
AuthorizationPolicy
AngularModule
Route
AngularController
AngularService
AngularDirective
Template
ClientComponent
Chart
UIControl
NavigationItem
ApiCall
DataModel
ExternalReference

Edges:
DECLARES
IMPORTS
USES_LAYOUT
RENDERS
LOADS
HOSTS
PROTECTS
RETURNS
CONFIGURES_ROUTE
USES_TEMPLATE
DEPENDS_ON
CALLS_API
NAVIGATES_TO
CONTAINS_CONTROL

Do not invent API endpoints, DTOs, routes, menu items, or business behavior. Emit only proven relationships. Anything uncertain must be written to dashboard-analysis-summary.md under “Needs Review”.

FIFTH: TESTS AND DOCUMENTATION

Create tests that verify:
- the source inventory finds the approved Dashboard files
- JavaScript module/controller/service/directive extraction works
- HTML/Razor host elements such as header-bar, left-menu, ui-view, toaster-container, and loading overlay are extracted when present
- C# controller/action/Authorize extraction works
- graph JSON contains source evidence for every node and edge
- no source files under the reference application are changed

Update README.md with:
- prerequisite versions
- environment setup
- how to run the analyzer
- expected output files
- what is deterministic versus what will use LLM later

SIXTH: COMPLETE STEP 2

Run the tests and the analyzer against the local HealthClinic reference source.

Update:
PROJECT_MEMORY.md
PROGRESS.md
DECISIONS.md

Set the status to:
“Step 2 complete — deterministic Tree-sitter extraction and evidence graph JSON created.”

Set the next step to:
“Step 3 — load normalized graph JSON into Neo4j and add the Roslyn/LSP semantic enrichment adapter.”

Do not implement Neo4j, Roslyn/LSP, LangGraph, LangChain, Graphiti, Figma, Agile-story generation, architecture assessment, or Angular generation in this step.

At the end, give me:
1. the exact command that successfully ran
2. test results
3. the output artifact paths
4. node and edge counts
5. any proven limitations
