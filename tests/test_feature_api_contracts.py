from polaris_modernization.feature_specifications.api_contracts import build_feature_api_contracts


def _evidence(path, method="framework-analyzer"):
    return [{"source_path": path, "line_start": 3, "line_end": 3, "extraction_method": method, "confidence": 1.0}]


def _inputs(status="PROVEN"):
    frontend="client/app/services/itemService.js"
    endpoint="GET /api/items/{id}"
    reference={"workflow":"Load item", "status":status, "frontend_source":frontend, "api_contract":endpoint, "backend_endpoint":endpoint}
    spec={"feature_id":"feature-example", "stories":[{"story_id":"story-example", "title":"Load Item", "api_contract_refs":[reference]}], "acceptance_criteria":[{"story_id":"story-example", "acceptance_criterion_id":"ac-example"}]}
    api_id="project:ApiCall:"+endpoint; endpoint_id="project:Endpoint:"+endpoint
    graph={"nodes":[
        {"id":api_id,"label":"ApiCall","name":endpoint,"evidence":_evidence(frontend)},
        {"id":endpoint_id,"label":"Endpoint","name":endpoint,"evidence":_evidence("server/ItemsController.cs"),"properties":{"http_method":"GET","route_template":"api/items/{id}","normalized_route":"/api/items/{id}","controller":"ItemsController","action":"Get","parameters":["id"],"query_parameters":[{"name":"expand","type":"bool","required":"Not established"}],"request_type":"ItemRequest","request_fields":[{"name":"filter","type":"string"}],"response_type":"ItemDto","response_fields":[{"name":"name","type":"string"}]}},
    ],"edges":[{"source":api_id,"target":endpoint_id,"type":"IMPLEMENTED_BY","evidence":_evidence(frontend)}]}
    frameworks={"frameworks":[{"framework":"AngularJS","source_path":"client/bower.json","method":"deterministic-file-evidence","confidence":1.0}]}
    forensics={"backend_endpoint_facts":1,"frontend_api_call_facts":1,"proven":1,"ambiguous":0,"dynamic_url_warnings":0,"external_api":0,"no_backend_route":0,"unresolved_structural_calls":0,"controller_template_endpoints":0,"controllers_with_controller_template":0,"http_methods":{"GET":1}}
    return [spec],graph,frameworks,forensics


def test_generic_contract_extracts_only_endpoint_evidence():
    artifact,coverage,trace=build_feature_api_contracts(*_inputs())
    contract=artifact["features"][0]["contracts"][0]
    assert contract["backend"]["http_method"]=="GET"
    assert contract["backend"]["resolved_endpoint"]=="/api/items/{id}"
    assert contract["request"]["path_parameters"][0]["name"]=="id"
    assert contract["request"]["query_parameters"][0]["name"]=="expand"
    assert contract["request"]["body_type"]=="ItemRequest"
    assert contract["request"]["body_fields"][0]["name"]=="filter"
    assert contract["response"]["response_type"]=="ItemDto"
    assert contract["response"]["response_fields"][0]["name"]=="name"
    assert coverage["totals"]["untraceable_api_contract_fields"]==0 and trace


def test_external_contract_never_inherits_backend_signature():
    specifications,graph,frameworks,forensics=_inputs("EXTERNAL")
    graph["edges"]=[]
    artifact,coverage,_=build_feature_api_contracts(specifications,graph,frameworks,forensics)
    contract=artifact["features"][0]["contracts"][0]
    assert coverage["totals"]["external"]==1
    assert not any(contract["backend"].values())
    assert not contract["request"]["path_parameters"]
    assert not contract["response"]["response_type"]
