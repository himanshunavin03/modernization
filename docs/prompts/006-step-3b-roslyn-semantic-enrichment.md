Resume the Polaris Modernization POC safely.

Read completely before making changes:
- PROJECT_MEMORY.md
- PROGRESS.md
- DECISIONS.md
- AGENTS.md
- .github/copilot-instructions.md
- docs/prompts/005-step-3-neo4j-persistence.md

Save this exact request as:
docs/prompts/006-step-3b-roslyn-semantic-enrichment.md

Goal:
Implement Step 3B: optional Roslyn-based semantic enrichment for C#/.NET code.

Architecture principle:
- Tree-sitter remains responsible for fast, deterministic syntax extraction across files.
- Roslyn is responsible for C# semantic enrichment.
- Neo4j remains the durable source-of-truth graph.
- LSP is an optional interactive protocol boundary; do not depend on a running IDE or language server for batch analysis.
- No LLM is allowed in this step.

Strict boundaries:
- Do not modify anything inside source/.
- Do not add LangChain, LangGraph, Graphiti, Figma, Agile-story generation, architecture recommendation, or Angular generation.
- Do not hardcode HealthClinic, DashboardController, controller names, solution names, routes, or DTO names.
- The solution must work for any future project supplied with --source-root and --project-id.
- Do not commit or push unless I explicitly ask.

Implement:

1. Roslyn helper project
Create a small .NET console project, for example:
tools/Polaris.RoslynAnalyzer/

Requirements:
- Target a currently supported .NET version that can run independently of the legacy input application.
- Use Roslyn packages to parse and semantically inspect C# source.
- The helper must not build, run, or alter the legacy application.
- It must emit deterministic JSON to a supplied output path.
- It must accept:
  --source-root "<path>"
  --project-id "<id>"
  --output "<json-path>"

2. Semantic facts to extract
For C# source files, produce evidence-backed semantic facts where they can be proven:

- Namespace
- Class/interface/record/enum
- Base type and implemented interfaces
- ASP.NET MVC/API controller identification
- Controller action methods
- Authorization attributes/policies/roles
- Route attributes at controller and action level
- HTTP verb attributes: GET, POST, PUT, DELETE, PATCH
- Explicit endpoint templates, including combined controller + action route where deterministically possible
- Method return type
- Method parameters and parameter types
- DTO/model properties and property types
- Method invocation references when Roslyn can resolve the target symbol
- Type references when Roslyn can resolve them

Every fact or relationship must include:
- project_id
- source_path relative to source root
- line_start and line_end
- source_hash
- extraction_method = "roslyn"
- confidence
- resolution_status = proven or unresolved
- a reason/diagnostic when unresolved

Never invent endpoint routes or symbol relationships.

3. Graceful fallback
- The existing Tree-sitter-only analysis must continue working when .NET SDK/Roslyn is unavailable.
- Roslyn enrichment must be opt-in, for example:
  python -m polaris_modernization.cli analyze ... --enable-roslyn
- If dotnet is unavailable, output a clear warning and complete Tree-sitter analysis successfully.
- If a source repository has no C# files, complete successfully with an empty Roslyn result.
- Do not require the customer source project to compile successfully.

4. Python integration
- Add a Python Roslyn bridge/adapter that invokes the helper safely with argument arrays, not shell string concatenation.
- Add Roslyn facts to artifacts/<project-id>/roslyn-semantic.json.
- Merge supported proven Roslyn facts into the normalized knowledge graph without duplicating Tree-sitter nodes.
- Add graph labels/relationships only where evidence is available, such as:
  Controller -> DECLARES -> Action
  Action -> EXPOSES -> Endpoint
  Action -> RETURNS_TYPE -> DTO
  DTO -> HAS_PROPERTY -> Property
  Method -> INVOKES -> Method
  Controller/Action -> PROTECTED_BY -> AuthorizationPolicy

Preserve Tree-sitter facts as separate evidence where both extractors find the same concept.

5. LSP boundary, without fake implementation
- Add a small documented abstraction/interface for future LSP enrichment, for example:
  semantic_provider = tree_sitter | roslyn | lsp
- Document that LSP will later be used for interactive definition/reference lookup or IDE integration.
- Do not add a fake LSP server, do not require VS Code, and do not claim LSP analysis is implemented if it is not.

6. Tests
Add deterministic fixture-based tests for arbitrary names, covering:
- A controller with a route and HTTP verb endpoint.
- A DTO with typed properties.
- An authorization attribute.
- A method reference that can be resolved, if feasible.
- Project-id isolation and evidence fields.
- Roslyn unavailable fallback behavior.

Tests must not require a running Neo4j instance.
Python tests must still pass even if dotnet is unavailable.
If dotnet is available, add a separate optional Roslyn integration test.

7. Neo4j compatibility
- Ensure the enriched JSON graph can be loaded with the existing Neo4j loader without unsafe dynamic Cypher.
- Add one read-only Cypher demo query showing:
  Controller -> Action -> Endpoint and Action -> DTO relationships.

8. Documentation and recovery
- Update README with prerequisites, exact Windows PowerShell commands, and the difference between Tree-sitter, Roslyn, and future LSP.
- Update PROJECT_MEMORY.md, PROGRESS.md, and DECISIONS.md.
- Set the next planned stage to:
  Step 4 — Business feature, epic, user-story, and acceptance-criteria generation from approved graph evidence.
- Document any limitation honestly.

Validation:
- Run python -m pytest -q.
- If dotnet exists, build the Roslyn helper and run one fixture analysis with --enable-roslyn.
- If Docker exists, optionally load the enriched graph into Neo4j; do not block if Docker is unavailable.
- Show all commands I need to run from the VS Code terminal.
- Summarize changed files, test results, and remaining limitations.
