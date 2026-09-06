import json
from pathlib import Path

from polaris_modernization.capability_completeness import (
    CapabilityDisposition,
    SourceCapability,
    api_operation_identity,
    assess_graph_readiness,
    assign_feature_dispositions,
    derive_source_capabilities,
    validate_capability_coverage,
)
from polaris_modernization.graph.api_mapping import resolve_api_relationships
from polaris_modernization.graph.normalizer import normalize
from polaris_modernization.feature_scope_completeness import build_feature_scope_contract, publish_feature_scope_refresh, render_feature_markdown
from polaris_modernization.models import Evidence, Fact


def ev(path: str, line: int = 1) -> Evidence:
    return Evidence("fixture", path, line, line, "tree-sitter", 1.0, "hash")


def operation_facts(method: str, function: str, handler: str, line: int) -> list[Fact]:
    route = "/api/orders/{id}" if method == "DELETE" else "/api/orders"
    raw_route = "'/api/orders/' + id" if method == "DELETE" else "/api/orders"
    controller = "ordersController"
    service = "OrdersService"
    action = function.title()
    return [
        Fact("ui_action", f"components/orders/views/main.html:{line}:ng-click", ev("components/orders/views/main.html", line), {"handler": handler, "expression": f"{handler}()", "text": function}),
        Fact("frontend_function", f"{controller}.{handler}", ev("components/orders/controllers/ordersController.js", line), {"function_name": handler, "owner": controller}),
        Fact("frontend_invocation", f"ordersService.{function}", ev("components/orders/controllers/ordersController.js", line), {"caller": handler, "caller_owner": controller, "target_owner": "ordersService", "target_function": function}),
        Fact("frontend_function", f"{service}.{function}", ev("components/orders/services/ordersService.js", line), {"function_name": function, "owner": service}),
        Fact("api_call", raw_route, ev("components/orders/services/ordersService.js", line), {"http_method": method, "raw_url_expression": raw_route, "function_name": function, "service": service}),
        Fact("endpoint", f"{method} {route}", ev("Api/OrdersController.cs", line), {"http_method": method, "normalized_route": route, "action": action, "controller": "OrdersController"}),
        Fact("action", action, ev("Api/OrdersController.cs", line), {"controller": "OrdersController"}),
        Fact("backend_handler", f"OrdersController.{action}/0", ev("Api/OrdersController.cs", line), {"owner": "OrdersController", "function_name": action, "arity": 0, "handler_kind": "CONTROLLER"}),
        Fact("backend_invocation", f"OrdersController.{action}:ordersRepository.{action}", ev("Api/OrdersController.cs", line), {"caller": action, "caller_owner": "OrdersController", "caller_arity": 0, "target_owner_hint": "ordersRepository", "target_function": action, "target_arity": 0}),
        Fact("method", action, ev("Data/OrdersRepository.cs", line), {"controller": "OrdersRepository"}),
        Fact("backend_handler", f"OrdersRepository.{action}/0", ev("Data/OrdersRepository.cs", line), {"owner": "OrdersRepository", "function_name": action, "arity": 0, "handler_kind": "DOMAIN"}),
        Fact("persistence_operation", f"OrdersRepository.{action}:SaveChanges", ev("Data/OrdersRepository.cs", line), {"repository": "OrdersRepository", "handler": action, "handler_arity": 0, "operation": "SaveChanges", "expression": "context.SaveChanges()"}),
    ]


def graph_with_crud() -> dict:
    facts = [
        *operation_facts("GET", "getList", "load", 1),
        *operation_facts("POST", "add", "save", 2),
        *operation_facts("PUT", "update", "save", 3),
        *operation_facts("DELETE", "remove", "remove", 4),
    ]
    resolved = resolve_api_relationships(facts)
    mapped = [fact for fact in facts if fact.kind not in {"api_call", "api_mapping"}]
    mapped.extend(resolved["call_facts"])
    mapped.extend(resolved["mapping_facts"])
    inventory = [{"source_path": path, "source_hash": "hash"} for path in sorted({fact.evidence.source_path for fact in mapped})]
    return normalize("fixture", inventory, mapped)


def test_http_method_is_part_of_api_operation_identity():
    assert api_operation_identity("GET", "/api/orders") != api_operation_identity("POST", "/api/orders")
    graph = graph_with_crud()
    names = {node["name"] for node in graph["nodes"] if node["label"] == "ApiCall"}
    assert {"GET /api/orders", "POST /api/orders", "PUT /api/orders"} <= names
    assert any(node["properties"].get("http_method") == "DELETE" for node in graph["nodes"] if node["label"] == "ApiCall")


def test_ui_action_handler_api_and_backend_chain_preserves_crud_capabilities():
    graph = graph_with_crud()
    edge_types = {edge["type"] for edge in graph["edges"]}
    assert {"TRIGGERS", "INVOKES", "CALLS_API", "IMPLEMENTED_BY"} <= edge_types
    capabilities = derive_source_capabilities(graph)
    assert {item.operation_kind for item in capabilities} >= {"LIST", "CREATE", "UPDATE", "DELETE"}
    assert all(any(evidence.stage == "UI" for evidence in item.source_evidence) for item in capabilities if item.operation_kind in {"CREATE", "UPDATE", "DELETE"})
    assert all(any(evidence.stage == "PERSISTENCE" for evidence in item.source_evidence) for item in capabilities if item.operation_kind in {"CREATE", "UPDATE", "DELETE"})


def test_concrete_ui_interaction_survives_broad_capability_classification():
    graph = graph_with_crud()
    for node in graph["nodes"]:
        if node["label"] == "UIAction" and node["properties"].get("handler") == "load":
            node["properties"]["text"] = "Fetch next records"
    capabilities = derive_source_capabilities(graph)
    list_capability = next(item for item in capabilities if item.operation_kind == "LIST")
    assert list_capability.interaction_semantics[0].label == "Fetch next records"


def test_selection_is_preserved_as_interaction_not_inferred_from_delete_api():
    graph = graph_with_crud()
    graph["nodes"].append({
        "id": "fixture:UISelection:1", "label": "UISelection", "name": "components/orders/views/main.html:9",
        "properties": {"model": "record.selected", "change": "refreshSelection()"},
        "evidence": [{"source_path": "components/orders/views/main.html", "line_start": 9, "line_end": 9}],
    })
    capabilities = derive_source_capabilities(graph)
    selection = next(item for item in capabilities if any(
        interaction.interaction_type == "SELECTION" for interaction in item.interaction_semantics
    ))
    assert selection.interaction_semantics[0].interaction_type == "SELECTION"
    assert selection.interaction_semantics[0].state_change == "selection model record.selected"


def test_silent_loss_fails_even_when_aggregate_prose_mentions_operations():
    capabilities = derive_source_capabilities(graph_with_crud())
    aggregate_understanding = "List, create, update, and delete orders"
    assert aggregate_understanding
    result = validate_capability_coverage(capabilities, [])
    assert result["status"] == "FAIL"
    assert result["silently_dropped_capabilities"]


def test_included_excluded_deferred_and_unresolved_dispositions_remain_traceable():
    capabilities = [SourceCapability(
        capability_id=f"capability-{kind.lower()}", domain_context="orders", operation_kind=kind,
        operation_identity=f"{kind} evidence", source_evidence=[], confidence="PROVEN",
    ) for kind in ("READ", "CREATE", "UPDATE", "DELETE")]
    dispositions = [
        CapabilityDisposition(capability_id="capability-read", scope_status="INCLUDED", feature_id="feature-orders", downstream_refs=["FR-01"]),
        CapabilityDisposition(capability_id="capability-create", scope_status="EXCLUDED", reason="Not selected for this release.", evidence_refs=["decision:1"]),
        CapabilityDisposition(capability_id="capability-update", scope_status="DEFERRED", reason="Requires contract confirmation.", evidence_refs=["question:1"]),
        CapabilityDisposition(capability_id="capability-delete", scope_status="UNRESOLVED", reason="Workflow ownership is not proven.", evidence_refs=["evidence:1"]),
    ]
    result = validate_capability_coverage(capabilities, dispositions)
    assert result["status"] == "PASS_WITH_EXCLUSION"
    dispositions[1].reason = None
    assert validate_capability_coverage(capabilities, dispositions)["status"] == "FAIL"


def test_supporting_api_without_ui_evidence_is_not_assigned_by_entity_name():
    capability = SourceCapability(
        capability_id="capability-orders-read-supporting", domain_context="orders", operation_kind="READ",
        operation_identity="GET /api/orders/availability", source_evidence=[], confidence="PARTIAL",
    )
    dispositions = assign_feature_dispositions([capability], [{"feature_id": "feature-orders", "title": "Order Directory", "module": "Orders"}])
    assert dispositions[0].scope_status == "UNRESOLVED"
    assert dispositions[0].feature_id is None


def test_feature_scope_contract_derives_crud_requirements_without_downstream_stories():
    capabilities = derive_source_capabilities(graph_with_crud())
    dispositions = assign_feature_dispositions(capabilities, [{"feature_id": "feature-orders", "title": "Order Directory", "module": "Orders"}])
    coverage = validate_capability_coverage(capabilities, dispositions)
    contract, refreshed = build_feature_scope_contract("feature-orders", "Order Directory Management", coverage)
    titles = {item["title"] for item in contract["functional_requirements"]}
    assert {"Create Order", "Update Order", "Delete Order"} <= titles
    assert {f"{item['method']} {item['route']}" for item in contract["api_contracts"]} >= {"POST /api/orders", "PUT /api/orders"}
    assert contract["stories_regenerated"] is False
    assert validate_capability_coverage(refreshed["capabilities"], refreshed["dispositions"])["status"] == "PASS"
    markdown = render_feature_markdown(contract)
    assert "Create Order" in markdown
    assert "## Dependencies and Clarifications" in markdown
    assert "## Definition of Done" in markdown
    assert all(term not in markdown for term in ("Tree-sitter", "Roslyn", "source_path", "confidence"))


def test_scope_refresh_preserves_stale_story_and_acceptance_criteria_artifacts(tmp_path):
    source = tmp_path / "source"
    output = tmp_path / "output"
    source.mkdir()
    (output / "latest").mkdir(parents=True)
    feature_id = "feature-orders"
    existing = {
        "feature_id": feature_id,
        "feature_name": "Order Directory Management",
        "functional_requirements": [{"id": "old"}],
        "stories": [{"story_id": "story-existing"}],
        "acceptance_criteria": [{"acceptance_criterion_id": "ac-existing"}],
    }
    (source / f"{feature_id}.json").write_text(json.dumps(existing), encoding="utf-8")
    (source / f"{feature_id}.md").write_text("existing", encoding="utf-8")
    (source / "feature-api-contracts.json").write_text(
        json.dumps({"features": [{"feature_id": feature_id, "contracts": []}]}), encoding="utf-8"
    )
    capability = SourceCapability(
        capability_id="cap-create", domain_context="orders", operation_kind="CREATE",
        operation_identity="POST /api/orders", confidence="PROVEN",
        source_evidence=[{"node_id": "api:create", "source_path": "orders.js", "stage": "API"}],
    )
    disposition = CapabilityDisposition(
        capability_id="cap-create", scope_status="INCLUDED", feature_id=feature_id,
        evidence_refs=["api:create"], downstream_refs=[f"feature:{feature_id}"],
    )
    result = publish_feature_scope_refresh(
        source, output, feature_id,
        validate_capability_coverage([capability], [disposition]),
    )
    refreshed = json.loads((result["path"] / f"{feature_id}.json").read_text(encoding="utf-8"))
    assert refreshed["stories"] == existing["stories"]
    assert refreshed["acceptance_criteria"] == existing["acceptance_criteria"]
    assert refreshed["functional_requirements"][0]["title"] == "Create Order"
    assert refreshed["downstream_status"] == "STALE_REGENERATION_REQUIRED"


def test_generic_production_module_has_no_fixture_specific_branch():
    source = Path("src/polaris_modernization/capability_completeness.py").read_text(encoding="utf-8").lower()
    for term in ("healthclinic", "myhealth", "doctor", "patient", "appointment", "/api/doctors"):
        assert term not in source


def test_graph_readiness_requires_valid_warning_free_deterministic_extraction():
    ready = assess_graph_readiness({"valid": True}, {"scope": {"extraction_warning_count": 0, "opaque_dependency_count": 2}}, "run-1")
    assert ready["readiness"] == "READY_WITH_EXPLAINED_LIMITATIONS"
    blocked = assess_graph_readiness({"valid": False}, {"scope": {"extraction_warning_count": 1}}, "run-2")
    assert blocked["readiness"] == "NOT_READY"
