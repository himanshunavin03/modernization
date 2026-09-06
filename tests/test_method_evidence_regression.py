from hashlib import sha256
from pathlib import Path

from polaris_modernization.cli import merge_roslyn
from polaris_modernization.graph.normalizer import normalize
from polaris_modernization.tree_sitter_extractors.csharp import extract


FIXTURE = Path(__file__).parent / "fixtures" / "method-identity" / "MethodContainers.cs"


def syntax_graph():
    facts = extract(FIXTURE, FIXTURE.parent, sha256(FIXTURE.read_bytes()).hexdigest(), "method-fixture")
    inventory = [{"source_path": FIXTURE.name, "source_hash": sha256(FIXTURE.read_bytes()).hexdigest()}]
    return facts, normalize("method-fixture", inventory, facts)


def semantic_method(name: str, identity: str, line: int, status: str = "proven") -> dict:
    return {
        "kind": "method",
        "name": name,
        "project_id": "method-fixture",
        "evidence": {
            "project_id": "method-fixture",
            "source_path": FIXTURE.name,
            "line_start": line,
            "line_end": line + 2,
            "source_hash": "fixture",
            "extractor": "roslyn",
            "confidence": 1.0 if status == "proven" else 0.0,
            "resolution_status": status,
            "diagnostic": None,
        },
        "properties": {"identity": identity, "owner_identity": identity.split("(", 1)[0].rsplit(".", 1)[0]},
    }


def test_all_syntax_methods_survive_with_container_declarations_and_stable_identity():
    first_facts, first = syntax_graph()
    second_facts, second = syntax_graph()
    method_facts = [fact for fact in first_facts if fact.kind == "method"]
    methods = [node for node in first["nodes"] if node["label"] == "Method"]
    types = {node["id"] for node in first["nodes"] if node["label"] == "Type"}
    declared_methods = {
        edge["target"] for edge in first["edges"]
        if edge["type"] == "DECLARES" and edge["source"] in types
    }

    assert {fact.name for fact in method_facts} == {"LoadByCategoryAsync", "Reconcile", "PreserveTailMethod"}
    assert len([node for node in methods if node["name"] == "Reconcile"]) == 4
    assert len({node["id"] for node in methods if node["name"] == "Reconcile"}) == 4
    assert {node["id"] for node in methods} <= declared_methods
    assert {node["id"] for node in methods} == {node["id"] for node in second["nodes"] if node["label"] == "Method"}
    assert [fact.properties["structural_identity"] for fact in method_facts] == [
        fact.properties["structural_identity"] for fact in second_facts if fact.kind == "method"
    ]


def test_proven_semantic_method_reconciles_only_with_same_source_declaration():
    _, graph = syntax_graph()
    merge_roslyn(graph, [semantic_method(
        "LoadByCategoryAsync",
        "global::Alpha.CatalogWorker.LoadByCategoryAsync(global::Alpha.Category)",
        7,
    )], "method-fixture")
    matches = [node for node in graph["nodes"] if node["label"] == "Method" and node["name"] == "LoadByCategoryAsync"]

    assert len(matches) == 1
    assert matches[0]["properties"]["semantic_resolution"] == "PROVEN_EQUIVALENT"
    assert len(matches[0]["evidence"]) == 2

    _, different_line_graph = syntax_graph()
    merge_roslyn(different_line_graph, [semantic_method(
        "LoadByCategoryAsync",
        "global::Alpha.CatalogWorker.LoadByCategoryAsync(global::Alpha.Category)",
        99,
    )], "method-fixture")
    assert len([node for node in different_line_graph["nodes"] if node["label"] == "Method" and node["name"] == "LoadByCategoryAsync"]) == 2


def test_unresolved_semantic_method_never_removes_structural_method():
    _, graph = syntax_graph()
    structural = next(node for node in graph["nodes"] if node["label"] == "Method" and node["name"] == "PreserveTailMethod")
    merge_roslyn(graph, [semantic_method(
        "PreserveTailMethod",
        "global::Beta.CatalogWorker.PreserveTailMethod()",
        34,
        "unresolved",
    )], "method-fixture")

    retained = next(node for node in graph["nodes"] if node["id"] == structural["id"])
    assert len([node for node in graph["nodes"] if node["label"] == "Method" and node["name"] == "PreserveTailMethod"]) == 1
    assert retained["properties"]["semantic_resolution"] == "UNRESOLVED_STRUCTURAL_FALLBACK"
    assert len(retained["evidence"]) == 2


def test_unresolved_declaration_promotes_existing_identity_placeholder():
    identity = "global::Gamma.CatalogWorker.PreserveTailMethod()"
    placeholder_id = f"method-fixture:Method:{identity}"
    graph = {
        "nodes": [{
            "id": placeholder_id,
            "project_id": "method-fixture",
            "label": "Method",
            "name": "PreserveTailMethod()",
            "properties": {"identity": identity},
            "evidence": [],
        }],
        "edges": [],
        "warnings": [],
    }
    merge_roslyn(graph, [semantic_method("PreserveTailMethod", identity, 34, "unresolved")], "method-fixture")
    method = next(node for node in graph["nodes"] if node["id"] == placeholder_id)

    assert method["name"] == "PreserveTailMethod"
    assert method["properties"]["semantic_resolution"] == "UNRESOLVED_STRUCTURAL_FALLBACK"
    assert any(edge["type"] == "DECLARES" and edge["target"] == placeholder_id for edge in graph["edges"])
