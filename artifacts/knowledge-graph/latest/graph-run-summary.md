# Create Knowledge Graph Run

- Overall status: `succeeded`
- Project ID: `legacy-dashboard-complete-application-demo-v1`
- Source root: `C:\Users\himan\OneDrive\Documents\polaris-modernization-poc\modernization\modernization\source\HealthClinic.biz`
- Started: `2026-09-06T09:20:23.752654Z`
- Ended: `2026-09-06T09:21:04.829583Z`
- Neo4j Browser: http://localhost:7474

## Workflow Stages

- `validate_input`: `succeeded` - Source root and project ID are valid.
- `analyze_source`: `succeeded` - Deterministic analysis completed.
- `validate_graph`: `succeeded` - Knowledge graph is project-scoped and valid.
- `load_neo4j`: `warning` - Neo4j load skipped by --skip-neo4j or default graph-only mode.
- `produce_run_status`: `succeeded` - Customer-facing run status artifacts were created.

## Results

- Files: 2384
- Facts: 14383
- Nodes: 6773
- Edges: 10204
- Warnings: 4453
- Extraction warnings: 0
- Scope: `Full application analysis`
- Coverage: `complete_with_opaque_dependencies`
- Roslyn: `warning`
- Neo4j: `skipped`

## Artifacts

- `knowledge_graph`: `C:\Users\himan\AppData\Local\Temp\polaris-capability-release-1a461c0ce23341c5b2793847a5399717\legacy-dashboard-complete-application-demo-v1\knowledge-graph.json`
- `source_inventory`: `C:\Users\himan\AppData\Local\Temp\polaris-capability-release-1a461c0ce23341c5b2793847a5399717\legacy-dashboard-complete-application-demo-v1\source-inventory.json`
- `facts`: `C:\Users\himan\AppData\Local\Temp\polaris-capability-release-1a461c0ce23341c5b2793847a5399717\legacy-dashboard-complete-application-demo-v1\facts.json`
- `graph_run_status`: `C:\Users\himan\AppData\Local\Temp\polaris-capability-release-1a461c0ce23341c5b2793847a5399717\legacy-dashboard-complete-application-demo-v1\graph-run-status.json`
- `graph_run_summary`: `C:\Users\himan\AppData\Local\Temp\polaris-capability-release-1a461c0ce23341c5b2793847a5399717\legacy-dashboard-complete-application-demo-v1\graph-run-summary.md`

## Safe Next Actions

- Review knowledge-graph.json locally.
- Start Neo4j with `docker compose up -d` when ready; this command does not start Docker.
- Rerun with --load-neo4j after setting NEO4J_URI, NEO4J_USERNAME, and NEO4J_PASSWORD.
- Open Neo4j Browser manually at http://localhost:7474.
