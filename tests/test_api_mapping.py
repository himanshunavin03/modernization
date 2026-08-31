from polaris_modernization.graph.api_mapping import map_api_calls, normalize_route


EVIDENCE = {"source_path": "fixture", "line_start": 1}


def test_normalizes_literals_query_strings_and_trailing_slashes():
    assert normalize_route("https://example.test/api/customers/123/?page=1") == "/api/customers/{id}"


def test_maps_exact_verb_and_normalized_route_with_both_evidence_records():
    result = map_api_calls([{"verb": "GET", "route": "/api/customers/123", "evidence": {"source_path": "web.js"}}], [{"verb": "GET", "route": "api/customers/{id}", "evidence": {"source_path": "CustomersController.cs"}}])
    assert len(result) == 1
    assert {item["source_path"] for item in result[0]["evidence"]} == {"web.js", "CustomersController.cs"}


def test_does_not_guess_ambiguous_or_verb_mismatched_routes():
    call = {"verb": "GET", "route": "/api/customers/123", "evidence": EVIDENCE}
    endpoints = [{"verb": "POST", "route": "/api/customers/{id}", "evidence": EVIDENCE}, {"verb": "GET", "route": "/api/customers/{id}", "evidence": EVIDENCE}, {"verb": "GET", "route": "/api/customers/{id}", "evidence": EVIDENCE}]
    assert map_api_calls([call], endpoints) == []
