Create a clean, Dashboard-scoped graph for the HealthClinic customer demo.

Read:

- PROJECT_MEMORY.md
- PROGRESS.md
- DECISIONS.md
- AGENTS.md
- docs/agents/create-knowledge-graph.md
- docs/prompts/010-step-3c-create-knowledge-graph-agent.md
- docs/prompts/011-step-3c-1-tree-sitter-fault-isolation.md
- docs/prompts/012-step-3c-2-isolated-worker-bootstrap-fix.md
- docs/prompts/013-step-3c-3-dashboard-demo-graph-validation.md
- docs/validation/healthclinic-dashboard-graph-demo.md

Save this exact request as:
docs/prompts/014-step-3c-4-clean-dashboard-profile-graph.md

Goal:
Run the existing healthclinic-dashboard YAML profile from the HealthClinic repository root. This is configuration-based scoping for the POC demo, not application-specific logic in the reusable engine.

Do not modify source/.
Do not add LangChain, LangGraph, Graphiti, Angular generation, Figma work, or Neo4j loading yet.

First inspect config/profiles/healthclinic-dashboard.yaml and confirm its selected paths exclude:
src/MyHealth.Web/Views/Home/Index.cshtml

Then run:

python -m polaris_modernization.cli create-knowledge-graph \
  --source-root "source\HealthClinic.biz" \
  --project-id "healthclinic-dashboard-clean-demo" \
  --profile "healthclinic-dashboard" \
  --output "artifacts" \
  --enable-roslyn \
  --skip-neo4j

Validate:

1. graph-run-summary.md and knowledge-graph.json exist.
2. Dashboard controller/action, authorization, Dashboard UI controls, AngularJS route/service, and API-call relationships are present.
3. `Views/Home/Index.cshtml` was not selected for extraction.
4. No source file changed; provide source hash proof.
5. Report total warnings separately from extraction warnings.

Decision:

- If extraction warnings are zero, mark this graph as ready for Neo4j visual-demo loading.
- If any extraction warning remains, do not load Neo4j. Report the exact warning and stop.

Create and commit:
docs/validation/healthclinic-dashboard-clean-graph.md

The report must contain only scope, counts, warning summary, five graph relationships, and source-integrity evidence. Do not commit generated artifacts or source code.

Update PROJECT_MEMORY.md, PROGRESS.md, and DECISIONS.md accurately.
Commit and push the documentation and memory updates only.
