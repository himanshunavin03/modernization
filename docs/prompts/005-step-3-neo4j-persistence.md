Resume the Polaris Modernization POC safely.

First read completely:
\- PROJECT\_MEMORY.md
\- PROGRESS.md
\- DECISIONS.md
\- AGENTS.md
\- .github/copilot-instructions.md
\- docs/prompts/004-step-2-2-generic-graph-correctness.md

Before changing code, save this exact request as:
docs/prompts/005-step-3-neo4j-persistence.md

Goal:
Implement Step 3A: load the existing deterministic knowledge-graph JSON into Neo4j safely and make it queryable by project\_id.

This step proves:
source code -> Tree-sitter facts -> evidence-backed JSON graph -> Neo4j graph.

Strict boundaries:
\- Do not modify anything under source/.
\- Do not add an LLM, LangChain, LangGraph, Graphiti, Roslyn, LSP, Figma, Angular generation, or business-story generation yet.
\- Do not change the deterministic extraction logic unless a Neo4j mapping bug requires a minimal correction.
\- Neo4j is the source of truth for code/UI relationships. It is not AI memory.
\- Never store secrets in Git.

Implement:

1\. Local Neo4j development setup
\- Add a docker-compose.yml for Neo4j Community Edition.
\- Use named Docker volumes for database persistence.
\- Expose Neo4j Browser on [http://localhost:7474](http://localhost:7474) and Bolt on 7687.
\- Add .env.example only, with safe placeholder values:
&#x20; NEO4J\_URI=bolt://localhost:7687
&#x20; NEO4J\_USERNAME=neo4j
&#x20; NEO4J\_PASSWORD=change-me
\- Ensure .env is ignored by Git.
\- Document exact Windows PowerShell commands to start, stop, and open Neo4j.

2\. Python Neo4j graph loader
\- Add the official neo4j Python driver dependency.
\- Create a reusable loader module, for example:
&#x20; src/polaris\_modernization/graph/neo4j\_loader.py
\- It must read a generated knowledge-graph.json and load nodes, edges, evidence, properties, and warnings.
\- Every persisted node and relationship must retain project\_id.
\- Use parameterized Cypher only.
\- Use idempotent MERGE behavior so loading the same graph twice does not create duplicates.
\- Create appropriate indexes/constraints for project\_id and node id.

3\. Safe project isolation
\- Provide a command to delete/reload only one project\_id.
\- Never use a database-wide delete.
\- Require an explicit --project-id for any delete/reload operation.
\- If the project\_id in the JSON does not match the CLI argument, fail safely.

4\. CLI commands
Add clear commands similar to:

python -m polaris\_modernization.cli analyze \\
&#x20; \--source-root "\<path-to-any-project>" \\
&#x20; \--project-id "\<project-id>" \\
&#x20; \--profile "\<profile>" \\
&#x20; \--output "artifacts"

python -m polaris\_modernization.cli load-neo4j \\
&#x20; \--graph "artifacts/\<project-id>/knowledge-graph.json" \\
&#x20; \--project-id "\<project-id>"

python -m polaris\_modernization.cli clear-neo4j-project \\
&#x20; \--project-id "\<project-id>" \\
&#x20; \--confirm-project-id "\<project-id>"

The clear command must require the repeated confirmation value.

5\. Query examples for the customer demo
Add docs/neo4j-demo-queries.cypher containing useful queries:
\- All files and UI controls for one project.
\- Controllers/actions/views and their relationships.
\- AngularJS services and API calls.
\- API calls with unresolved ownership.
\- Nodes/edges with source path and line evidence.
\- Count graph nodes and relationships by type.
\- Delete nothing in this query file.

6\. Tests
Add automated tests without requiring a running Docker/Neo4j server:
\- Test mapping from JSON graph to parameterized Cypher payloads.
\- Test project-id mismatch fails.
\- Test clear operation requires matching confirmation.
\- Test loader never emits a database-wide delete query.
\- Preserve all current tests.

If Docker/Neo4j is available locally, also perform one optional smoke test:
\- Start Neo4j.
\- Analyze the generic fixture.
\- Load project\_id \`orders-demo\`.
\- Run one read-only Cypher query and show its result.
If Docker is unavailable, do not block the work; document the commands and mark the smoke test as pending.

7\. Documentation and durable recovery
\- Update README with installation, environment setup, run commands, and Neo4j Browser URL.
\- Update PROJECT\_MEMORY.md, PROGRESS.md, and DECISIONS.md.
\- Set the next planned step to: Step 3B — Roslyn/LSP semantic enrichment for C# symbol and endpoint resolution.
\- Do not commit or push unless I explicitly ask.

Validation:
\- Run python -m pytest -q.
\- Run a graph analysis against test fixtures.
\- Show the exact commands I should run in VS Code terminal.
\- Summarize files created/changed and any pending Docker smoke test.
