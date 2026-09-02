import json
from pathlib import Path

import pytest

from polaris_modernization.cli import analyze
from polaris_modernization.framework_analyzers import AspNetRouteAnalyzer
from polaris_modernization.models import Evidence, Fact


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "framework-contract"


def test_framework_registry_emits_endpoint_contracts_and_proven_mapping(tmp_path):
    result = analyze(FIXTURE, "contracts", "default", tmp_path)
    facts = [fact.to_dict() for fact in result["facts"]]
    endpoints = [fact for fact in facts if fact["kind"] == "endpoint"]
    assert any(item["name"] == "GET /api/orders/{id}" and item["properties"]["response_type"] == "OrderDto" for item in endpoints)
    assert any(item["name"] == "POST /api/orders" for item in endpoints)
    assert any(item["kind"] == "api_mapping" and item["properties"]["status"] == "PROVEN" for item in facts)
    graph = json.loads((result["output"] / "knowledge-graph.json").read_text())
    assert any(edge["type"] == "IMPLEMENTED_BY" for edge in graph["edges"])


def test_razor_model_and_action_relationships_are_evidence_backed(tmp_path):
    result = analyze(FIXTURE, "contracts", "default", tmp_path)
    graph = result["graph"]
    assert any(edge["type"] == "USES_VIEW_MODEL" for edge in graph["edges"])
    assert any(edge["type"] == "CALLS_ACTION" for edge in graph["edges"])
    assert all(edge["evidence"] for edge in graph["edges"])


def test_structurally_resolvable_angular_url_becomes_proven_template_match(tmp_path):
    result = analyze(FIXTURE, "contracts", "default", tmp_path)
    mappings = [fact for fact in result["facts"] if fact.kind == "api_mapping"]
    assert not result["warnings"]
    assert any(
        fact.name == "'/api/orders/' + id"
        and fact.properties["detail_status"] == "PROVEN_EXACT_TEMPLATE"
        and fact.properties["resolution"] == "EXACT_TEMPLATE_METHOD_ROUTE"
        for fact in mappings
    )


def _entry(path: str) -> dict:
    return {"selected_for_extraction": True, "source_path": path, "source_hash": "fixture-hash"}


def _route_facts(tmp_path, path: str, source: str):
    target = tmp_path / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(source, encoding="utf-8")
    return AspNetRouteAnalyzer().analyze(tmp_path, [_entry(path)], "fixture").facts


def test_bracketed_class_route_templates_are_balanced_and_tokenized(tmp_path):
    facts = _route_facts(tmp_path, "SomeProduct.API/Controllers/AppointmentsController.cs", '''
[Route("api/[controller]")]
public class AppointmentsController {
    [HttpGet("{id}")]
    public async Task<AppointmentDto> GetAsync(int id) { return null; }
    [HttpGet]
    [Route("[action]")]
    public Task<AppointmentDto> Recent() { return null; }
}
''')
    endpoints = {fact.name: fact.properties for fact in facts}
    assert "GET /api/appointments/{id}" in endpoints
    assert endpoints["GET /api/appointments/{id}"]["route_template"] == "api/[controller]/{id}"
    assert endpoints["GET /api/appointments/{id}"]["route_token_resolution"] == {"controller": "appointments"}
    assert "GET /api/appointments/Recent" in endpoints
    assert endpoints["GET /api/appointments/Recent"]["route_token_resolution"] == {"controller": "appointments", "action": "Recent"}


def test_action_name_is_used_for_action_route_token(tmp_path):
    facts = _route_facts(tmp_path, "Product.API/Controllers/ReportsController.cs", '''
[Route("api/[controller]/[action]")]
public class ReportsController {
    [HttpGet]
    [ActionName("overview")]
    public Result Current() { return null; }
}
''')
    assert [fact.name for fact in facts] == ["GET /api/reports/overview"]


def test_route_prefix_and_accept_verbs_preserve_method_route(tmp_path):
    facts = _route_facts(tmp_path, "Product.Api/Controllers/OrdersController.cs", '''
[RoutePrefix("api/orders")]
public class OrdersController {
    [AcceptVerbs("GET", "POST")]
    [Route("{id}")]
    public Result Get(int id) { return null; }
}
''')
    assert {fact.name for fact in facts} == {"GET /api/orders/{id}", "POST /api/orders/{id}"}


@pytest.mark.parametrize("path", [
    "Product.API/Controllers/CatalogController.cs",
    "Product.Api/Controllers/CatalogController.cs",
    "Product.api/Controllers/CatalogController.cs",
])
def test_api_path_fallback_is_case_insensitive_by_segment(tmp_path, path):
    facts = _route_facts(tmp_path, path, '''
public class CatalogController {
    [HttpGet]
    public Item Get() { return null; }
}
''')
    assert [fact.name for fact in facts] == ["GET /api/catalog"]


def test_http_mismatch_external_and_dynamic_calls_do_not_become_proven(tmp_path):
    (tmp_path / "bower.json").write_text('{"dependencies":{"angular":"1.8.0"}}', encoding="utf-8")
    api_project = tmp_path / "Product.API" / "Product.API.csproj"
    api_project.parent.mkdir()
    api_project.write_text("<Project />", encoding="utf-8")
    controller = tmp_path / "Product.API" / "Controllers" / "OrdersController.cs"
    controller.parent.mkdir()
    controller.write_text('''
[Route("api/[controller]")]
public class OrdersController {
    [HttpPost("{id}")]
    public Result Save(int id) { return null; }
}
''', encoding="utf-8")
    client = tmp_path / "web" / "ordersService.js"
    client.parent.mkdir()
    client.write_text('''
angular.module('demo').service('ordersService', function ($http) {
  this.get = function () { return $http.get('/api/orders/42'); };
  this.external = function () { return $http.get('https://example.invalid/api/orders/42'); };
  this.dynamic = function (id) { return $http.get('/api/orders/' + id); };
});
    ''', encoding="utf-8")
    result = analyze(tmp_path, "contracts", "default", tmp_path / "output")
    calls = [fact for fact in result["facts"] if fact.kind == "api_call"]
    assert not [fact for fact in result["facts"] if fact.kind == "api_mapping"]
    assert {fact.properties["match_status"] for fact in calls} == {"NO_BACKEND_ROUTE", "EXTERNAL"}
    assert {fact.properties["match_detail_status"] for fact in calls} == {"NO_BACKEND_MATCH", "EXTERNAL"}
    assert any("API relationship remains no_backend_route" in warning["message"] for warning in result["warnings"])


def test_ambiguous_backend_routes_do_not_become_proven(tmp_path):
    (tmp_path / "bower.json").write_text('{"dependencies":{"angular":"1.8.0"}}', encoding="utf-8")
    api_project = tmp_path / "Product.API" / "Product.API.csproj"
    api_project.parent.mkdir()
    api_project.write_text("<Project />", encoding="utf-8")
    for name in ("OneController", "TwoController"):
        controller = tmp_path / "Product.API" / "Controllers" / f"{name}.cs"
        controller.parent.mkdir(exist_ok=True)
        controller.write_text(f'''\
[Route("api/orders")]
public class {name} {{
    [HttpGet]
    public Result Get() {{ return null; }}
}}
''', encoding="utf-8")
    client = tmp_path / "web" / "ordersService.js"
    client.parent.mkdir()
    client.write_text("angular.module('demo').service('ordersService', function ($http) { $http.get('/api/orders'); });", encoding="utf-8")
    result = analyze(tmp_path, "contracts", "default", tmp_path / "output")
    calls = [fact for fact in result["facts"] if fact.kind == "api_call"]
    assert calls[0].properties["match_status"] == "UNRESOLVED"
    assert calls[0].properties["match_detail_status"] == "AMBIGUOUS"
    assert not [fact for fact in result["facts"] if fact.kind == "api_mapping"]
    assert any("compatible after HTTP method and normalized route comparison" in warning["message"] for warning in result["warnings"])
