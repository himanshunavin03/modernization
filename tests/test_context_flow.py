from polaris_modernization.graph.context_flow import add_context_flow


PROJECT = "context-test"
EVIDENCE = {"project_id": PROJECT, "source_path": "api/ReportsController.cs", "line_start": 1, "line_end": 1, "extraction_method": "roslyn", "confidence": 1.0, "source_hash": "hash"}


def graph():
    return {"nodes": [
        {"id": f"{PROJECT}:ApiCall:/api/reports/clinicsummary", "project_id": PROJECT, "label": "ApiCall", "name": "/api/reports/clinicsummary", "properties": {}, "evidence": [{**EVIDENCE, "source_path": "ui/dashboard.js"}]},
        {"id": f"{PROJECT}:ApiCall:/api/reports/expenses/ + year", "project_id": PROJECT, "label": "ApiCall", "name": "/api/reports/expenses/ + year", "properties": {}, "evidence": [{**EVIDENCE, "source_path": "ui/dashboard.js"}]},
        {"id": f"{PROJECT}:Action:report", "project_id": PROJECT, "label": "Action", "name": "GetClinicSummaryAsync", "properties": {"identity": "Reports.GetClinicSummaryAsync()"}, "evidence": [EVIDENCE]},
        {"id": f"{PROJECT}:Type:Other", "project_id": PROJECT, "label": "Type", "name": "Other", "properties": {}, "evidence": [{**EVIDENCE, "source_path": "other/Other.cs"}]},
    ], "edges": [], "warnings": []}


def profile():
    return {"selection_roles": {"ui": "transform_ui", "api": "preserve_backend", "other": "preserve_domain_data"}, "endpoint_routes": [{"path": "/api/reports/clinicsummary", "source_path": "api/ReportsController.cs", "action_name": "GetClinicSummaryAsync", "action_identity": "Reports.GetClinicSummaryAsync()"}]}


def test_unique_static_route_creates_only_proven_endpoint_and_contract():
    result = graph()
    add_context_flow(result, profile(), PROJECT)
    types = {edge["type"] for edge in result["edges"]}
    assert {"RESOLVES_TO_ENDPOINT", "EXPOSES", "PRESERVES_CONTRACT"} <= types
    assert not any("expenses" in edge["target"] for edge in result["edges"] if edge["type"] == "RESOLVES_TO_ENDPOINT")
    assert any("unresolved or dynamic" in warning["message"] for warning in result["warnings"])


def test_backend_nodes_are_never_transform_ui_and_projects_remain_isolated():
    result = graph()
    add_context_flow(result, profile(), PROJECT)
    assert all(node["project_id"] == PROJECT for node in result["nodes"])
    backend = next(node for node in result["nodes"] if node["id"].endswith(":Action:report"))
    assert backend["properties"]["modernization_role"] == "preserve_backend"
    assert backend["properties"]["eligible_for_angular_generation"] is False
