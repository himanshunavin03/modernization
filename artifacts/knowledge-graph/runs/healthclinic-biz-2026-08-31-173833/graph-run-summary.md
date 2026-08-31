# Create Knowledge Graph Run

- Overall status: `succeeded`
- Project ID: `healthclinic-biz`
- Source root: `C:\Users\himan\OneDrive\Documents\polaris-modernization-poc\modernization\modernization\source\HealthClinic.biz`
- Started: `2026-08-31T17:37:52.689352Z`
- Ended: `2026-08-31T17:38:31.472873Z`
- Neo4j Browser: http://localhost:7474

## Workflow Stages

- `validate_input`: `succeeded` - Source root and project ID are valid.
- `analyze_source`: `succeeded` - Deterministic analysis completed.
- `validate_graph`: `succeeded` - Knowledge graph is project-scoped and valid.
- `load_neo4j`: `warning` - Neo4j load skipped by --skip-neo4j or default graph-only mode.
- `produce_run_status`: `succeeded` - Customer-facing run status artifacts were created.

## Results

- Files: 2384
- Facts: 5936
- Nodes: 4136
- Edges: 4369
- Warnings: 3639
- Extraction warnings: 0
- Scope: `Full application analysis`
- Coverage: `complete_with_opaque_dependencies`
- Roslyn: `warning`
- Neo4j: `skipped`

## Artifacts

- `knowledge_graph`: `artifacts\healthclinic-biz\knowledge-graph.json`
- `source_inventory`: `artifacts\healthclinic-biz\source-inventory.json`
- `facts`: `artifacts\healthclinic-biz\facts.json`
- `graph_run_status`: `artifacts\healthclinic-biz\graph-run-status.json`
- `graph_run_summary`: `artifacts\healthclinic-biz\graph-run-summary.md`

## Safe Next Actions

- Review knowledge-graph.json locally.
- Start Neo4j with `docker compose up -d` when ready; this command does not start Docker.
- Rerun with --load-neo4j after setting NEO4J_URI, NEO4J_USERNAME, and NEO4J_PASSWORD.
- Open Neo4j Browser manually at http://localhost:7474.
