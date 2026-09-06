from pathlib import Path

from polaris_modernization.graph.normalizer import normalize
from polaris_modernization.tree_sitter_extractors import html, javascript


def test_html_extracts_conditions_without_interpreting_control_text(tmp_path: Path) -> None:
    root = tmp_path / "source"
    view = root / "views" / "records.html"
    view.parent.mkdir(parents=True)
    view.write_text('<button ng-click="load()" ng-disabled="!form.$valid">Misleading label</button><div ng-show="isEmpty">No entries</div>', encoding="utf-8")
    facts = html.extract(view, root, "hash", "fixture")
    condition = next(item for item in facts if item.kind == "ui_condition")
    assert condition.properties == {"element": "div", "condition": "isEmpty", "visibility": "SHOW", "text": "No entries"}
    assert not any(item.kind == "empty_state" for item in facts)
    assert any(item.kind == "validation_condition" for item in facts)


def test_javascript_extracts_mutation_navigation_and_confirmation_from_structure(tmp_path: Path) -> None:
    root = tmp_path / "source"
    script = root / "components" / "records" / "recordsController.js"
    script.parent.mkdir(parents=True)
    script.write_text('class RecordsController { run() { this.records.push(item); this.records.splice(0, 1); modal.showConfirmModal({}).then(() => state.transitionTo("records")); this.visible = false; } }', encoding="utf-8")
    facts = javascript.extract(script, root, "hash", "fixture")
    assert {item.kind for item in facts} >= {"collection_mutation", "navigation", "confirmation", "state_mutation"}
    graph = normalize("fixture", [{"source_path": item.evidence.source_path, "source_hash": "hash"} for item in facts[:1]], facts)
    assert {edge["type"] for edge in graph["edges"]} >= {"MUTATES_COLLECTION", "NAVIGATES", "REQUIRES_CONFIRMATION"}


def test_api_and_label_evidence_do_not_create_ui_results(tmp_path: Path) -> None:
    root = tmp_path / "source"
    script = root / "recordsService.js"
    root.mkdir()
    script.write_text('function recordsService() { return $http({ method: "GET", url: "/api/records", params: { pageSize: 4 } }); }', encoding="utf-8")
    facts = javascript.extract(script, root, "hash", "fixture")
    assert not any(item.kind in {"collection_mutation", "navigation", "confirmation", "state_mutation"} for item in facts)


def test_anonymous_callbacks_have_stable_enclosing_identity(tmp_path: Path) -> None:
    root = tmp_path / "source"; root.mkdir()
    script = root / "handlers.js"
    script.write_text('function HandlerA() { ServiceA.run(() => HelperA()); ServiceA.run(() => HelperB()); }', encoding="utf-8")
    first = javascript.extract(script, root, "hash", "fixture")
    second = javascript.extract(script, root, "hash", "fixture")
    callbacks = [item for item in first if item.kind == "frontend_function" and item.properties.get("anonymous")]
    assert [item.name for item in callbacks] == [item.name for item in second if item.kind == "frontend_function" and item.properties.get("anonymous")]
    assert len({item.name for item in callbacks}) == 2
    assert {item.properties["enclosing_function"] for item in callbacks} == {"HandlerA"}


def test_callback_invocations_resolve_with_nearest_scope_and_no_cross_association(tmp_path: Path) -> None:
    root = tmp_path / "source"; root.mkdir()
    script = root / "handlers.js"
    script.write_text(
        'function HelperA() {} function HelperB() {} '
        'function HandlerA() { ServiceA.execute(() => { HelperA(); state.value = 1; }); } '
        'function HandlerB() { ServiceB.execute(() => HelperB()); }', encoding="utf-8",
    )
    facts = javascript.extract(script, root, "hash", "fixture")
    callbacks = [item for item in facts if item.kind == "frontend_function" and item.properties.get("anonymous")]
    invocations = [item for item in facts if item.kind == "frontend_invocation"]
    callback_a = next(item for item in callbacks if item.properties["enclosing_function"] == "HandlerA")
    callback_b = next(item for item in callbacks if item.properties["enclosing_function"] == "HandlerB")
    helper_a = next(item for item in invocations if item.properties["target_function"] == "HelperA")
    helper_b = next(item for item in invocations if item.properties["target_function"] == "HelperB")
    assert helper_a.properties["caller"] == callback_a.properties["function_name"]
    assert helper_b.properties["caller"] == callback_b.properties["function_name"]
    assert next(item for item in facts if item.kind == "state_mutation" and item.properties.get("target") == "state.value").properties["function_name"] == callback_a.properties["function_name"]
    service_a = next(item for item in invocations if item.name == "ServiceA.execute")
    assert service_a.properties["caller"] == "HandlerA"
    assert service_a.properties["callback_ids"] == [callback_a.properties["function_name"]]

    graph = normalize("fixture", [{"source_path": "handlers.js", "source_hash": "hash"}], facts)
    edges = {(item["type"], item["source"], item["target"]) for item in graph["edges"]}
    assert ("CONTAINS", "fixture:FrontendFunction:HandlerA", f"fixture:FrontendFunction:{callback_a.name}") in edges
    assert ("INVOKES", f"fixture:FrontendFunction:{callback_a.name}", "fixture:FrontendFunction:HelperA") in edges
    assert ("INVOKES", f"fixture:FrontendFunction:{callback_b.name}", "fixture:FrontendFunction:HelperB") in edges
    assert not any(source.endswith(callback_a.name) and target.endswith("HelperB") for _, source, target in edges)
    assert any(kind == "PASSES_CALLBACK" and target.endswith(callback_a.name) for kind, _, target in edges)
    assert ("INVOKES", "fixture:FrontendFunction:HandlerA", "fixture:FrontendInvocation:ServiceA.execute") in edges


def test_nested_callbacks_and_uncalled_identifiers_are_deterministic(tmp_path: Path) -> None:
    root = tmp_path / "source"; root.mkdir()
    script = root / "nested.js"
    script.write_text('function HelperA() {} function HandlerA() { const ref = HelperA; ServiceA.execute(() => ServiceB.execute(() => HelperA())); }', encoding="utf-8")
    first = javascript.extract(script, root, "hash", "fixture")
    second = javascript.extract(script, root, "hash", "fixture")
    assert [item.to_dict() for item in first] == [item.to_dict() for item in second]
    callbacks = [item for item in first if item.kind == "frontend_function" and item.properties.get("anonymous")]
    assert len(callbacks) == 2
    outer = next(item for item in callbacks if item.properties["enclosing_function"] == "HandlerA")
    inner = next(item for item in callbacks if item.properties["enclosing_function"] == outer.properties["function_name"])
    helper = next(item for item in first if item.kind == "frontend_invocation" and item.properties["target_function"] == "HelperA")
    assert helper.properties["caller"] == inner.properties["function_name"]
    assert len([item for item in first if item.kind == "frontend_invocation" and item.properties["target_function"] == "HelperA"]) == 1
