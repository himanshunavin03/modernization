# Create Knowledge Graph Run

- Overall status: `succeeded`
- Project ID: `legacy-dashboard-complete-application-demo-v1`
- Source root: `C:\Users\himan\OneDrive\Documents\polaris-modernization-poc\modernization\modernization\source\HealthClinic.biz`
- Started: `2026-08-31T17:14:58.005208Z`
- Ended: `2026-08-31T17:16:49.495829Z`
- Neo4j Browser: http://localhost:7474

## Workflow Stages

- `validate_input`: `succeeded` - Source root and project ID are valid.
- `analyze_source`: `succeeded` - Deterministic analysis completed.
- `validate_graph`: `succeeded` - Knowledge graph is project-scoped and valid.
- `load_neo4j`: `succeeded` - Loaded only this project graph into Neo4j.
- `produce_run_status`: `succeeded` - Customer-facing run status artifacts were created.

## Results

- Files: 2384
- Facts: 8353
- Nodes: 5430
- Edges: 5524
- Warnings: 2082
- Extraction warnings: 0
- Scope: `Full application analysis`
- Coverage: `complete_with_opaque_dependencies`
- Roslyn: `succeeded`
- Neo4j: `succeeded`

## Artifacts

- `knowledge_graph`: `artifacts\legacy-dashboard-complete-application-demo-v1\knowledge-graph.json`
- `source_inventory`: `artifacts\legacy-dashboard-complete-application-demo-v1\source-inventory.json`
- `facts`: `artifacts\legacy-dashboard-complete-application-demo-v1\facts.json`
- `graph_run_status`: `artifacts\legacy-dashboard-complete-application-demo-v1\graph-run-status.json`
- `graph_run_summary`: `artifacts\legacy-dashboard-complete-application-demo-v1\graph-run-summary.md`

## Safe Next Actions

- Open Neo4j Browser manually at http://localhost:7474 and run a read-only demo query.
