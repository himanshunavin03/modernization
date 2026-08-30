import json
from pathlib import Path
import pytest
from polaris_modernization.graph.neo4j_loader import CLEAR_NODES, Neo4jLoader, payloads, read_graph

class Session:
    def __init__(self, calls): self.calls = calls
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def run(self, query, **params): self.calls.append((query, params))
class Driver:
    def __init__(self): self.calls = []
    def session(self): return Session(self.calls)

def graph():
    evidence = [{"project_id":"demo","source_path":"a.js","line_start":1,"line_end":1,"extraction_method":"tree-sitter","confidence":1.0,"source_hash":"hash"}]
    return {"nodes":[{"id":"demo:File:a.js","project_id":"demo","label":"File","name":"a.js","properties":{},"evidence":evidence}],"edges":[],"warnings":[]}

def test_payloads_and_merge_are_parameterized():
    driver = Driver(); result = Neo4jLoader(driver).load(graph(), "demo")
    assert result["nodes"] == 1
    assert any("$rows" in query for query, _ in driver.calls)
    assert all("DETACH DELETE" not in query for query, _ in driver.calls)

def test_project_mismatch_fails(tmp_path):
    path = tmp_path / "graph.json"; path.write_text(json.dumps(graph()))
    with pytest.raises(ValueError): read_graph(path, "other")

def test_clear_requires_confirmation_and_is_scoped():
    driver = Driver(); loader = Neo4jLoader(driver)
    with pytest.raises(ValueError): loader.clear_project("demo", "different")
    loader.clear_project("demo", "demo")
    deletes = [query for query, _ in driver.calls if "DELETE" in query]
    assert deletes and all("project_id: $project_id" in query for query in deletes)
    assert "MATCH (n) DETACH DELETE n" not in CLEAR_NODES
