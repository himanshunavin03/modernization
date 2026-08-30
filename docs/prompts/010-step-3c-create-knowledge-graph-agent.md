Resume the Polaris Modernization POC safely.

Read completely:
- PROJECT_MEMORY.md
- PROGRESS.md
- DECISIONS.md
- AGENTS.md
- .github/copilot-instructions.md
- docs/prompts/009-step-3b-3-local-roslyn-validation.md
- docs/validation/step-3b-local-validation.md

Save this exact request as:
docs/prompts/010-step-3c-create-knowledge-graph-agent.md

Goal:
Implement Step 3C — the executable Create Knowledge Graph agent.

Customer experience:

1. User chooses a source repository/folder.
2. User supplies a unique project ID.
3. User selects `/Create-Knowledge-Graph`.
4. The agent validates input.
5. It runs Tree-sitter analysis and optional Roslyn enrichment.
6. It creates knowledge-graph.json.
7. It loads only that project graph into Neo4j.
8. It returns a customer-friendly run status and the Neo4j Browser URL.

Architecture rule:
This agent orchestrates deterministic tools. It must not use an LLM, LangChain, LangGraph, Graphiti, Figma, business-story generation, or Angular generation.

Strict boundaries:
- Never modify source/.
- Never commit or copy the customer source project into Git.
- Keep project isolation through project_id.
- Never issue a database-wide Neo4j delete.
- Do not automatically open a browser or start Docker. Return instructions and URLs instead.
- Do not claim that a VS Code slash command is automatically available unless the IDE integration is actually configured.

Implement:

1. Executable workflow command
Add a new CLI command, such as:

python -m polaris_modernization.cli create-knowledge-graph \
  --source-root "<path-to-any-project>" \
  --project-id "<unique-project-id>" \
  --profile "default" \
  --output "artifacts" \
  --enable-roslyn \
  --load-neo4j

Expected workflow stages:
- validate_input
- analyze_source
- validate_graph
- load_neo4j
- produce_run_status

2. Input validation
- Require source root exists and is a directory.
- Require a non-empty safe project ID.
- Fail safely if Neo4j environment variables or connection are unavailable when --load-neo4j is selected.
- Allow graph-only execution without Neo4j using:
  --skip-neo4j
- Never delete or overwrite another project’s data.

3. Customer-friendly result
Create these ignored local artifacts under:
artifacts/<project-id>/

- graph-run-status.json
- graph-run-summary.md

They must include:
- project_id
- source root path
- start/end time and overall status
- each workflow stage with succeeded, warning, or failed status
- file count, fact count, node count, edge count, warning count
- whether Roslyn ran or was skipped
- whether Neo4j loaded or was skipped
- artifact paths
- Neo4j Browser URL: http://localhost:7474
- safe next actions for the user

Do not expose passwords or secrets in status artifacts.

4. Agent definition for recovery and demo
Create:
docs/agents/create-knowledge-graph.md

Document:
- purpose
- user inputs
- workflow stages
- output contract
- error handling
- source-read-only rule
- project isolation rule
- the exact command to run
- a sample customer-facing success response

Also create an IDE/Codex-friendly instruction file only if it is accurate for this repository. It must clearly state that the actual executable entry point is the CLI command, while a future UI can map a button or slash command to it.

5. Tests
Add tests for:
- graph-only success using fixtures and --skip-neo4j
- invalid/missing source path
- unsafe or empty project ID
- status artifact shape and required fields
- source fixture hash unchanged
- Neo4j load failure is returned as a controlled failed stage without a database-wide delete
- all existing tests remain green

6. Demo instructions
Update README with these exact demo steps:

- Start Neo4j:
  docker compose up -d

- Run the agent on a project:
  python -m polaris_modernization.cli create-knowledge-graph ...

- Open Neo4j Browser:
  http://localhost:7474

- Run a read-only graph query from docs/neo4j-demo-queries.cypher.

7. Durable project history
- Update PROJECT_MEMORY.md, PROGRESS.md, and DECISIONS.md.
- Set the next stage only after tests pass:
  Step 4 — Graph-backed business feature, epic, user-story, and acceptance-criteria workflow.
- Include a resume instruction referencing prompt 010.
- Do not commit or push unless I explicitly ask.

Validation:
- Run python -m pytest -q.
- Run the new agent in graph-only mode against tests/fixtures/roslyn-semantic.
- If Neo4j is available locally, run one optional end-to-end Neo4j load.
- Show the generated graph-run-summary.md.
