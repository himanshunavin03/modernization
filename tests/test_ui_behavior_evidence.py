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
    assert condition.properties == {"element": "div", "condition": "isEmpty", "visibility": "SHOW", "text": "No entries", "element_identity": "views/records.html:1:78"}
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
    node_ids = {node["name"]: node["id"] for node in graph["nodes"] if node["label"] == "FrontendFunction"}
    invocation_a = next(node["id"] for node in graph["nodes"] if node["label"] == "FrontendInvocation" and node["name"] == "ServiceA.execute")
    assert ("CONTAINS", node_ids["HandlerA"], node_ids[callback_a.name]) in edges
    assert ("INVOKES", node_ids[callback_a.name], node_ids["HelperA"]) in edges
    assert ("INVOKES", node_ids[callback_b.name], node_ids["HelperB"]) in edges
    assert not any(source == node_ids[callback_a.name] and target == node_ids["HelperB"] for _, source, target in edges)
    assert any(kind == "PASSES_CALLBACK" and target == node_ids[callback_a.name] for kind, _, target in edges)
    assert ("INVOKES", node_ids["HandlerA"], invocation_a) in edges


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


def test_explicit_route_target_links_navigation_controller_and_lifecycle(tmp_path: Path) -> None:
    root = tmp_path / "source"; root.mkdir()
    config = root / "routes.js"
    controller = root / "recordsController.js"
    controller.write_text(
        "function ControllerAController() { state.transitionTo('state-a'); ServiceA.load(() => { model.value = 1; }); } "
        "function StateAController() { state.transitionTo(dynamicTarget); }",
        encoding="utf-8",
    )
    config.write_text(
        "router.state('state-a', { templateUrl: '/views/a.html', controller: 'ControllerAController' }); "
        "router.state('state-b', { templateUrl: '/views/b.html', controller: 'ControllerBController' });",
        encoding="utf-8",
    )
    facts = javascript.extract(config, root, "h1", "fixture") + javascript.extract(controller, root, "h2", "fixture")
    inventory = [{"source_path": path.name, "source_hash": digest} for path, digest in ((config, "h1"), (controller, "h2"))]
    graph = normalize("fixture", inventory, facts)
    edges = {(edge["type"], edge["source"], edge["target"]) for edge in graph["edges"]}
    route_a = next(node["id"] for node in graph["nodes"] if node["label"] == "Route" and node["name"] == "state-a")
    controller_a = "fixture:AngularController:ControllerAController"
    lifecycle = next(node["id"] for node in graph["nodes"] if node["label"] == "FrontendFunction" and node["properties"].get("function_name") == "ControllerAController")
    callback = next(node["id"] for node in graph["nodes"] if node["label"] == "FrontendFunction" and node["properties"].get("anonymous"))
    mutation = next(node["id"] for node in graph["nodes"] if node["label"] == "StateMutation" and node["properties"].get("target") == "model.value")
    load = next(node["id"] for node in graph["nodes"] if node["label"] == "FrontendInvocation" and node["name"] == "ServiceA.load")
    assert any(kind == "NAVIGATES_TO" and target == route_a for kind, _, target in edges)
    assert ("DEPENDS_ON", route_a, controller_a) in edges
    assert ("INITIALIZES_WITH", controller_a, lifecycle) in edges
    assert ("INVOKES", lifecycle, load) in edges
    assert ("PASSES_CALLBACK", load, callback) in edges
    assert ("MUTATES", callback, mutation) in edges
    assert not any(kind == "NAVIGATES_TO" and target.endswith("Route:state-b") for kind, _, target in edges)
    assert not any(kind == "INITIALIZES_WITH" and target.endswith("FrontendFunction:StateAController") for kind, _, target in edges)


def test_directive_binding_and_conditional_render_use_exact_structure(tmp_path: Path) -> None:
    root = tmp_path / "source"; root.mkdir()
    module = root / "module.js"; directive = root / "valueDirective.js"; view = root / "view.html"
    module.write_text("angular.module('app').directive('valueReader', ValueReader).directive('otherReader', OtherReader);", encoding="utf-8")
    directive.write_text(
        "class ValueReader { constructor() { this.scope = { value: '=' }; } link(scope, element) { element.on('change', () => { scope.value = element.value; }); } } "
        "class OtherReader { constructor() { this.scope = { other: '=' }; } link(scope) { scope.other = 2; } }",
        encoding="utf-8",
    )
    view.write_text(
        '<input value-reader data-value="record.value" data-value-extra="record.valueExtra">'
        '<input other-reader data-other="record.other">'
        '<div ng-if="record.value">Ready</div><div ng-if="record.valueExtra">Other</div>',
        encoding="utf-8",
    )
    facts = javascript.extract(module, root, "h1", "fixture") + javascript.extract(directive, root, "h2", "fixture") + html.extract(view, root, "h3", "fixture")
    inventory = [{"source_path": path.name, "source_hash": digest} for path, digest in ((module, "h1"), (directive, "h2"), (view, "h3"))]
    graph = normalize("fixture", inventory, facts)
    types = {edge["type"] for edge in graph["edges"]}
    assert {"USES_DIRECTIVE", "BINDS_TO", "BINDS_STATE", "MUTATES_BINDING", "CONTROLS_RENDER"} <= types
    mutation = next(item for item in facts if item.kind == "state_mutation" and item.properties.get("target") == "scope.value")
    assert mutation.properties["function_name"].startswith("callback@")
    value_binding = next(node["id"] for node in graph["nodes"] if node["label"] == "DirectiveBinding" and node["properties"].get("directive_type") == "ValueReader")
    other_binding = next(node["id"] for node in graph["nodes"] if node["label"] == "DirectiveBinding" and node["properties"].get("directive_type") == "OtherReader")
    value_mutation = next(node["id"] for node in graph["nodes"] if node["label"] == "StateMutation" and node["properties"].get("target") == "scope.value")
    value_state = next(node["id"] for node in graph["nodes"] if node["label"] == "BoundState" and node["name"] == "record.value")
    extra_condition = next(node["id"] for node in graph["nodes"] if node["label"] == "UICondition" and node["properties"].get("condition") == "record.valueExtra")
    edges = {(edge["type"], edge["source"], edge["target"]) for edge in graph["edges"]}
    assert ("MUTATES_BINDING", value_mutation, value_binding) in edges
    assert ("MUTATES_BINDING", value_mutation, other_binding) not in edges
    assert ("CONTROLS_RENDER", value_state, extra_condition) not in edges
    assert not any(edge["type"] == "BINDS_TO" and edge["source"].endswith(":data-value-extra") for edge in graph["edges"])
    assert not any(edge["type"] == "USES_DIRECTIVE" and edge["target"].endswith("AngularDirective:value") for edge in graph["edges"])


def test_bound_state_identity_is_stable_within_a_view_and_isolated_between_views(tmp_path: Path) -> None:
    root = tmp_path / "source"; root.mkdir()
    view_a = root / "view-a.html"; view_b = root / "view-b.html"
    view_a.write_text('<input ng-model="model.value"><div ng-if="model.value">A</div>', encoding="utf-8")
    view_b.write_text('<input ng-model="model.value"><div ng-if="model.value">B</div>', encoding="utf-8")
    facts = html.extract(view_a, root, "h1", "fixture") + html.extract(view_b, root, "h2", "fixture")
    inventory = [{"source_path": path.name, "source_hash": digest} for path, digest in ((view_a, "h1"), (view_b, "h2"))]
    graph = normalize("fixture", inventory, facts)
    states = [node for node in graph["nodes"] if node["label"] == "BoundState" and node["name"] == "model.value"]
    assert len(states) == 2
    assert {node["properties"]["binding_context"] for node in states} == {"view-a.html", "view-b.html"}
    assert len({node["id"] for node in states}) == 2
    render_edges = [edge for edge in graph["edges"] if edge["type"] == "CONTROLS_RENDER" and edge["source"] in {node["id"] for node in states}]
    assert len(render_edges) == 2


def test_same_call_shape_in_different_files_does_not_cross_associate_callbacks(tmp_path: Path) -> None:
    root = tmp_path / "source"; root.mkdir()
    files = [root / "a.js", root / "b.js"]
    for path in files:
        path.write_text("function HandlerA() { ServiceA.execute(() => { state.value = 1; }); }", encoding="utf-8")
    facts = sum((javascript.extract(path, root, f"h{index}", "fixture") for index, path in enumerate(files)), [])
    inventory = [{"source_path": path.name, "source_hash": f"h{index}"} for index, path in enumerate(files)]
    graph = normalize("fixture", inventory, facts)
    invocations = [node for node in graph["nodes"] if node["label"] == "FrontendInvocation" and node["name"] == "ServiceA.execute"]
    callbacks = [node for node in graph["nodes"] if node["label"] == "FrontendFunction" and node["properties"].get("anonymous")]
    assert len(invocations) == len(callbacks) == 2
    for invocation in invocations:
        path = invocation["evidence"][0]["source_path"]
        targets = [edge["target"] for edge in graph["edges"] if edge["type"] == "PASSES_CALLBACK" and edge["source"] == invocation["id"]]
        assert len(targets) == 1
        assert next(node for node in callbacks if node["id"] == targets[0])["evidence"][0]["source_path"] == path


def test_duplicate_route_name_remains_unresolved_across_independent_configs(tmp_path: Path) -> None:
    root = tmp_path / "source"; root.mkdir()
    config_a = root / "routes-a.js"; config_b = root / "routes-b.js"; handler = root / "handler.js"
    config_a.write_text("router.state('state-a', { controller: 'ControllerA' });", encoding="utf-8")
    config_b.write_text("router.state('state-a', { controller: 'ControllerB' });", encoding="utf-8")
    handler.write_text("function HandlerA() { state.transitionTo('state-a'); }", encoding="utf-8")
    paths = [config_a, config_b, handler]
    facts = sum((javascript.extract(path, root, f"h{index}", "fixture") for index, path in enumerate(paths)), [])
    inventory = [{"source_path": path.name, "source_hash": f"h{index}"} for index, path in enumerate(paths)]
    graph = normalize("fixture", inventory, facts)
    assert len([node for node in graph["nodes"] if node["label"] == "Route" and node["name"] == "state-a"]) == 2
    assert not any(edge["type"] == "NAVIGATES_TO" for edge in graph["edges"])


def test_callback_scope_invocation_resolves_to_same_controller_function(tmp_path: Path) -> None:
    root = tmp_path / "source"; root.mkdir()
    script = root / "recordsController.js"
    script.write_text(
        "class RecordsController { constructor() { this.finish = () => {}; ServiceA.run(() => this.finish()); } }",
        encoding="utf-8",
    )
    facts = javascript.extract(script, root, "hash", "fixture")
    graph = normalize("fixture", [{"source_path": script.name, "source_hash": "hash"}], facts)
    callback = next(node for node in graph["nodes"] if node["label"] == "FrontendFunction" and node["properties"].get("anonymous"))
    finish = next(node for node in graph["nodes"] if node["label"] == "FrontendFunction" and node["properties"].get("function_name") == "finish")
    assert any(edge["type"] == "INVOKES" and edge["source"] == callback["id"] and edge["target"] == finish["id"] for edge in graph["edges"])
