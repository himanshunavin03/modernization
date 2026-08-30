# HealthClinic Dashboard Neo4j Visual Demo Preflight

## Commands Run

```powershell
docker version
docker compose version
```

Both commands failed because PowerShell could not resolve the `docker` command.

## Verification Result

- Neo4j load: not attempted.
- Docker Compose start: not attempted.
- `.env`: not created or modified.
- Neo4j Browser: [http://localhost:7474](http://localhost:7474) is not reachable for this demo until Docker Desktop is available.
- Required action: install and start Docker Desktop so `docker` is available in this PowerShell session, then resume from prompt 016.

## Validated Graph Baseline

- Project ID: `healthclinic-dashboard-scope-demo-v3`
- Audit files: 2,384
- Selected File nodes: 24
- Graph nodes: 119
- Graph edges: 167
- Total warnings: 11
- Extraction warnings: 0
- Review warnings: 11
- Coverage: `scope_complete`

## Customer Demo Queries

Set `$project_id` to `healthclinic-dashboard-scope-demo-v3` before running these read-only queries.

```cypher
MATCH (n:GraphNode {project_id: $project_id})
WITH count(n) AS node_count
MATCH ()-[r:GRAPH_REL {project_id: $project_id}]->()
RETURN $project_id AS project_id, node_count, count(r) AS edge_count;
```

```cypher
MATCH (p:GraphNode {project_id: $project_id, label: 'Project'})-[:GRAPH_REL {type: 'CONTAINS'}]->(f:GraphNode)
OPTIONAL MATCH (f)-[:GRAPH_REL {type: 'CONTAINS_CONTROL'}]->(control:GraphNode)
RETURN f.name, collect(control.name) AS controls;
```

```cypher
MATCH (file:GraphNode {project_id: $project_id, label: 'File'})-[r:GRAPH_REL {type: 'CALLS_API'}]->(api:GraphNode)
RETURN file.name, api.name, r.properties_json;
```

## Source Integrity

- No command in this preflight writes to `source/`.
- No source analysis or Neo4j load was run after the Docker preflight failed.
- The prior scope-complete validation source-tree fingerprint remains `c8b0e9f1be7724d5a15bb0a6a4ccda73920c653ff65181cc39ba96adbdc795d5`.
