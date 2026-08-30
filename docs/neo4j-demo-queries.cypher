// Set $project_id before running. These queries are read-only.
MATCH (p:GraphNode {project_id: $project_id, label: 'Project'})-[:GRAPH_REL {type: 'CONTAINS'}]->(f:GraphNode)
OPTIONAL MATCH (f)-[:GRAPH_REL {type: 'CONTAINS_CONTROL'}]->(control:GraphNode)
RETURN f.name, collect(control.name) AS controls;

MATCH (controller:GraphNode {project_id: $project_id, label: 'Controller'})-[:GRAPH_REL {type: 'DECLARES'}]->(action:GraphNode)
OPTIONAL MATCH (action)-[:GRAPH_REL {type: 'RETURNS'}]->(view:GraphNode)
RETURN controller.name, action.name, view.name;

MATCH (service:GraphNode {project_id: $project_id, label: 'AngularService'})-[r:GRAPH_REL {type: 'CALLS_API'}]->(api:GraphNode)
RETURN service.name, api.name, r.properties_json;

MATCH (file:GraphNode {project_id: $project_id, label: 'File'})-[r:GRAPH_REL {type: 'CALLS_API'}]->(api:GraphNode)
WHERE r.properties_json CONTAINS 'unresolved'
RETURN file.name, api.name, r.properties_json;

MATCH (n:GraphNode {project_id: $project_id}) RETURN n.name, n.evidence_json LIMIT 25;
MATCH ()-[r:GRAPH_REL {project_id: $project_id}]->() RETURN r.type, r.evidence_json LIMIT 25;
MATCH (n:GraphNode {project_id: $project_id}) RETURN n.label, count(*) ORDER BY count(*) DESC;
MATCH ()-[r:GRAPH_REL {project_id: $project_id}]->() RETURN r.type, count(*) ORDER BY count(*) DESC;
