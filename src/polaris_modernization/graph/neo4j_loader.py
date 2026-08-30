"""Project-isolated, parameterized Neo4j persistence for normalized graph JSON."""
from __future__ import annotations
import json
from pathlib import Path

NODE_CONSTRAINT = "CREATE CONSTRAINT graph_node_identity IF NOT EXISTS FOR (n:GraphNode) REQUIRE (n.project_id, n.graph_id) IS UNIQUE"
PROJECT_INDEX = "CREATE INDEX graph_node_project IF NOT EXISTS FOR (n:GraphNode) ON (n.project_id)"
WARNING_CONSTRAINT = "CREATE CONSTRAINT graph_warning_identity IF NOT EXISTS FOR (n:GraphWarning) REQUIRE (n.project_id, n.warning_key) IS UNIQUE"
MERGE_NODES = """UNWIND $rows AS row MERGE (n:GraphNode {project_id: row.project_id, graph_id: row.graph_id}) SET n.label=row.label, n.name=row.name, n.properties_json=row.properties_json, n.evidence_json=row.evidence_json"""
MERGE_EDGES = """UNWIND $rows AS row MATCH (a:GraphNode {project_id: row.project_id, graph_id: row.source}) MATCH (b:GraphNode {project_id: row.project_id, graph_id: row.target}) MERGE (a)-[r:GRAPH_REL {project_id: row.project_id, edge_key: row.edge_key}]->(b) SET r.type=row.type, r.properties_json=row.properties_json, r.evidence_json=row.evidence_json"""
MERGE_WARNINGS = """UNWIND $rows AS row MERGE (w:GraphWarning {project_id: row.project_id, warning_key: row.warning_key}) SET w.source_path=row.source_path, w.message=row.message"""
CLEAR_NODES = "MATCH (n:GraphNode {project_id: $project_id}) DETACH DELETE n"
CLEAR_WARNINGS = "MATCH (n:GraphWarning {project_id: $project_id}) DETACH DELETE n"

def read_graph(graph_path: Path, project_id: str) -> dict:
    graph = json.loads(graph_path.read_text(encoding="utf-8"))
    values = [item.get("project_id") for item in [*graph.get("nodes", []), *graph.get("edges", [])]]
    if any(value != project_id for value in values):
        raise ValueError("Graph project_id does not match --project-id")
    return graph

def payloads(graph: dict, project_id: str) -> dict[str, list[dict]]:
    nodes = [{"project_id": project_id, "graph_id": item["id"], "label": item["label"], "name": item["name"], "properties_json": json.dumps(item.get("properties", {}), sort_keys=True), "evidence_json": json.dumps(item.get("evidence", []), sort_keys=True)} for item in graph["nodes"]]
    edges = [{"project_id": project_id, "edge_key": f"{item['type']}:{item['source']}:{item['target']}", "source": item["source"], "target": item["target"], "type": item["type"], "properties_json": json.dumps(item.get("properties", {}), sort_keys=True), "evidence_json": json.dumps(item.get("evidence", []), sort_keys=True)} for item in graph["edges"]]
    warnings = [{"project_id": project_id, "warning_key": f"{index}:{item.get('source_path', '')}", "source_path": item.get("source_path", ""), "message": item.get("message", "")} for index, item in enumerate(graph.get("warnings", []))]
    return {"nodes": nodes, "edges": edges, "warnings": warnings}

class Neo4jLoader:
    def __init__(self, driver): self.driver = driver
    def load(self, graph: dict, project_id: str) -> dict:
        data = payloads(graph, project_id)
        with self.driver.session() as session:
            for query in (NODE_CONSTRAINT, PROJECT_INDEX, WARNING_CONSTRAINT): session.run(query)
            for query, rows in ((MERGE_NODES, data["nodes"]), (MERGE_EDGES, data["edges"]), (MERGE_WARNINGS, data["warnings"])):
                if rows: session.run(query, rows=rows)
        return {key: len(value) for key, value in data.items()}
    def clear_project(self, project_id: str, confirmation: str) -> None:
        if not project_id or confirmation != project_id: raise ValueError("--confirm-project-id must exactly match --project-id")
        with self.driver.session() as session:
            session.run(CLEAR_NODES, project_id=project_id)
            session.run(CLEAR_WARNINGS, project_id=project_id)

def connect(uri: str, username: str, password: str):
    from neo4j import GraphDatabase
    return GraphDatabase.driver(uri, auth=(username, password))
