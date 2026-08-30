# HealthClinic Dashboard Neo4j Visual Demo

## Result

- Workflow status: `succeeded`
- Neo4j load stage: `succeeded`
- Project ID: `healthclinic-dashboard-scope-demo-v3`
- Neo4j Browser: [http://localhost:7474](http://localhost:7474)
- Docker Compose service: `modernization-neo4j-1` is running with ports 7474 and 7687 published.

## Commands Run

```powershell
docker version
docker compose version
docker compose up -d
docker compose ps
python -m polaris_modernization.cli create-knowledge-graph --source-root "source\HealthClinic.biz" --project-id "healthclinic-dashboard-scope-demo-v3" --profile "healthclinic-dashboard" --output "artifacts" --enable-roslyn --load-neo4j
python -m pytest -q
```

The Neo4j environment variables were set in the session from the ignored local `.env`; no password is included in this report.

## Verified Counts

- Audited files: 2,384
- Selected File nodes: 24
- Out-of-scope audited files: 2,360
- Generated and persisted GraphNode records: 123
- Generated and persisted GRAPH_REL relationships: 169
- Generated and persisted GraphWarning records: 27
- Facts: 115
- Extraction warnings: 0
- Review warnings: 27
- Scope coverage: `scope_complete`
- Roslyn: `succeeded`

Neo4j project-scoped records contain only `healthclinic-dashboard-scope-demo-v3`: 123 `GraphNode` records and 27 `GraphWarning` records. Generated `knowledge-graph.json` node and edge counts match Neo4j exactly.

## Source Integrity

- Files checked before and after: 2,395
- Per-file aggregate source-tree SHA-256 before and after: `0b92e1701cdd2374e259ea4fed9811b7e20e4719ff8ea70e4a8aa5023cacf2b4`
- Result: unchanged

## Customer Demo Queries

Set `$project_id` to `healthclinic-dashboard-scope-demo-v3` in Neo4j Browser parameters before running these read-only queries.

```cypher
MATCH (n:GraphNode {project_id: $project_id})
WITH count(n) AS node_count
MATCH ()-[r:GRAPH_REL {project_id: $project_id}]->()
RETURN $project_id AS project_id, node_count, count(r) AS edge_count;
```

```cypher
MATCH (module:GraphNode {project_id: $project_id, label: 'AngularModule'})-[:GRAPH_REL {project_id: $project_id, type: 'CONFIGURES_ROUTE'}]->(route:GraphNode)
OPTIONAL MATCH (route)-[:GRAPH_REL {project_id: $project_id, type: 'USES_TEMPLATE'}]->(template:GraphNode)
RETURN module.name, route.name, template.name
ORDER BY route.name;
```

```cypher
MATCH (file:GraphNode {project_id: $project_id, label: 'File'})-[r:GRAPH_REL {project_id: $project_id, type: 'CALLS_API'}]->(api:GraphNode)
RETURN file.name, api.name, r.properties_json
ORDER BY file.name, api.name;
```

## Review Warnings

- 9 unresolved Roslyn invocation targets
- 3 unresolved Roslyn method declarations or return types
- 2 unresolved Roslyn property declarations or property types
- 3 unresolved Roslyn return types
- 6 API calls with owner not uniquely proven, attached to their File node
- 4 implicit MVC `View()` calls that cannot be matched deterministically

These are review warnings, not extraction failures; all selected files were successfully analyzed.

## Validation

`python -m pytest -q` completed with `34 passed, 2 skipped`.
