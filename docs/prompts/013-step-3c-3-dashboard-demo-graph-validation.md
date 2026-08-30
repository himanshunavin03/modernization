Prepare and validate the HealthClinic Dashboard graph for the customer demo.

Read:

- PROJECT_MEMORY.md
- PROGRESS.md
- DECISIONS.md
- AGENTS.md
- docs/agents/create-knowledge-graph.md
- docs/prompts/010-step-3c-create-knowledge-graph-agent.md
- docs/prompts/011-step-3c-1-tree-sitter-fault-isolation.md
- docs/prompts/012-step-3c-2-isolated-worker-bootstrap-fix.md

Save this exact request as:
docs/prompts/013-step-3c-3-dashboard-demo-graph-validation.md

This is a demo validation step, not Step 4.
Do not modify any file under source/.
Do not load Neo4j yet.
Do not generate Angular code, stories, LangChain, LangGraph, or Graphiti code.

Run the Create Knowledge Graph agent only against the legacy ASP.NET web application scope:

python -m polaris_modernization.cli create-knowledge-graph \
  --source-root "source\HealthClinic.biz\src\MyHealth.Web" \
  --project-id "healthclinic-dashboard-demo" \
  --profile "default" \
  --output "artifacts" \
  --enable-roslyn \
  --skip-neo4j

Then inspect and show:

1. graph-run-summary.md
2. framework-detection.json
3. total files, facts, nodes, edges, warnings, and extraction warnings
4. five strongest Dashboard-relevant relationships, preferably:
   - Controller -> Action
   - Action -> Razor View
   - Razor/UI file -> UI control
   - Angular service/controller -> API call
   - Action -> Endpoint or returned type
5. whether any parser files were skipped
6. proof that all source files under MyHealth.Web are unchanged

Create and commit a concise durable report:
docs/validation/healthclinic-dashboard-graph-demo.md

The report must contain only counts, paths, relationship examples, warning summaries, and source-integrity result. Do not include customer source code or generated artifact files.

If extraction warnings are zero:

- Mark the Dashboard graph as ready for the Neo4j visual demo.
- Set the next action to: install/start Docker Neo4j and load only healthclinic-dashboard-demo.

If warnings remain:

- Do not load Neo4j.
- Explain the warnings and stop for review.

Update PROJECT_MEMORY.md, PROGRESS.md, and DECISIONS.md accurately.
Commit and push only the validation report and durable-memory updates.
