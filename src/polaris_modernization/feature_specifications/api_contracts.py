"""Project deterministic API evidence into Feature-scoped preservation contracts."""
from __future__ import annotations

from collections import Counter
from pathlib import Path, PurePosixPath
import re


STATUSES = {"PROVEN", "DYNAMIC", "UNRESOLVED", "EXTERNAL", "NO_BACKEND_ROUTE"}


def _evidence(value: dict, source: str | None = None) -> list[dict]:
    items = value.get("evidence", [])
    return [item for item in items if source is None or item.get("source_path") == source]


def _trace(contract_id: str, prop: str, value: object, evidence: list[dict]) -> dict:
    if value is None or value == []:
        raise ValueError(f"Cannot trace an empty API property: {contract_id}.{prop}")
    if not evidence:
        raise ValueError(f"API property lacks deterministic evidence: {contract_id}.{prop}")
    item = evidence[0]
    return {
        "api_contract_id": contract_id,
        "property": prop,
        "value": value,
        "evidence_source": item.get("extraction_method"),
        "source_file": item.get("source_path"),
        "source_range": {"line_start": item.get("line_start"), "line_end": item.get("line_end")},
        "analyzer": item.get("extraction_method"),
        "confidence": item.get("confidence"),
    }


def _frontend_node(nodes: list[dict], reference: dict) -> tuple[dict, list[dict]]:
    source = reference["frontend_source"]
    candidates = [
        node for node in nodes
        if node.get("label") == "ApiCall"
        and node.get("name") == reference["api_contract"]
        and _evidence(node, source)
    ]
    if candidates:
        return candidates[0], _evidence(candidates[0], source)
    targets = {value for value in (reference.get("api_contract"), reference.get("backend_endpoint")) if value}
    candidates = [
        node for node in nodes
        if node.get("label") == "ApiCall"
        and _evidence(node, source)
        and targets.intersection(_api_call_signatures(node))
    ]
    if not candidates:
        raise ValueError(f"No frontend API evidence for {source}: {reference['api_contract']}")
    return candidates[0], _evidence(candidates[0], source)


def _api_call_signatures(node: dict) -> set[str]:
    props = node.get("properties", {})
    method = str(props.get("http_method") or "").upper()
    raw_expression = str(props.get("raw_url_expression") or node.get("name") or "")
    normalized_route = str(props.get("normalized_route") or "")
    resolved_endpoint = str(props.get("resolved_backend_endpoint") or "")
    values = {str(node.get("name") or ""), raw_expression, normalized_route, resolved_endpoint}
    if method and raw_expression.startswith("/"):
        values.add(f"{method} {raw_expression}")
    if method and normalized_route:
        values.add(f"{method} {normalized_route}")
    return {value for value in values if value}


def _current_reference(frontend_node: dict, reference: dict, mapping_edges: list[dict], node_by_id: dict[str, dict]) -> dict:
    props = frontend_node.get("properties", {})
    status = str(props.get("match_status") or reference["status"])
    if status not in STATUSES:
        status = reference["status"]
    matching_edges = [edge for edge in mapping_edges if edge.get("source") == frontend_node["id"]]
    backend_endpoint = str(props.get("resolved_backend_endpoint") or reference.get("backend_endpoint") or "")
    if backend_endpoint:
        matching_edges = [
            edge for edge in matching_edges
            if node_by_id.get(edge["target"], {}).get("name") == backend_endpoint
        ] or matching_edges
    mapping_edge = matching_edges[0] if len(matching_edges) == 1 else None
    if status == "PROVEN" and mapping_edge is None:
        raise ValueError(f"PROVEN API contract cannot be reconciled to a single IMPLEMENTED_BY edge: {reference}")
    return {
        "status": status,
        "frontend_expression": str(props.get("raw_url_expression") or frontend_node.get("name") or reference["api_contract"]),
        "frontend_method": str(props.get("http_method")).upper() if props.get("http_method") else None,
        "mapping_edge": mapping_edge,
    }


def _framework_evidence(frameworks: dict, source: str) -> list[dict]:
    project = source.split("/content/", 1)[0] + "/"
    matches = [
        item for item in frameworks.get("frameworks", [])
        if item.get("framework") == "AngularJS" and item.get("source_path", "").startswith(project)
    ]
    return [{
        "confidence": item["confidence"], "extraction_method": item["method"],
        "line_start": None, "line_end": None, "source_path": item["source_path"],
    } for item in matches]


def _contract_key(reference: dict) -> tuple[str, str, str, str]:
    return (reference["frontend_source"], reference["api_contract"], reference["backend_endpoint"], reference["status"])


def build_feature_api_contracts(
    specifications: list[dict], graph: dict, frameworks: dict, forensics: dict
) -> tuple[dict, dict, list[dict]]:
    """Build caller-specific contracts without promoting unresolved relationships."""
    nodes = graph["nodes"]
    node_by_id = {node["id"]: node for node in nodes}
    mapping_edges = [edge for edge in graph["edges"] if edge.get("type") == "IMPLEMENTED_BY"]
    features: list[dict] = []
    traceability: list[dict] = []

    for spec in specifications:
        grouped: dict[tuple[str, str, str, str], dict] = {}
        criteria_by_story: dict[str, list[str]] = {}
        for criterion in spec["acceptance_criteria"]:
            criteria_by_story.setdefault(criterion["story_id"], []).append(criterion["acceptance_criterion_id"])
        for story in spec["stories"]:
            for reference in story.get("api_contract_refs", []):
                if not reference:
                    continue
                status = reference["status"]
                if status not in STATUSES:
                    raise ValueError(f"Unsupported API relationship status: {status}")
                item = grouped.setdefault(_contract_key(reference), {
                    "reference": reference,
                    "story_ids": [], "ac_ids": [], "behavior_ids": [], "workflows": [],
                })
                item["story_ids"].append(story["story_id"])
                item["ac_ids"].extend(criteria_by_story.get(story["story_id"], []))
                item["behavior_ids"].append(re.sub(r"[^A-Z0-9]+", "_", story["title"].upper()).strip("_"))
                item["workflows"].append(reference["workflow"])

        contracts: list[dict] = []
        for number, item in enumerate(grouped.values(), 1):
            reference = item["reference"]
            contract_id = f"API-{spec['feature_id'].removeprefix('feature-').upper().replace('-', '_')}-{number:03d}"
            frontend_node, frontend_evidence = _frontend_node(nodes, reference)
            current = _current_reference(frontend_node, reference, mapping_edges, node_by_id)
            technology_evidence = _framework_evidence(frameworks, reference["frontend_source"])
            source = PurePosixPath(reference["frontend_source"])
            declared = [
                (node, _evidence(node, reference["frontend_source"])) for node in nodes
                if node.get("label") in {"AngularService", "AngularController"}
                and _evidence(node, reference["frontend_source"])
            ]
            services = [(node, evidence) for node, evidence in declared if node["label"] == "AngularService"]
            controllers = [(node, evidence) for node, evidence in declared if node["label"] == "AngularController" and node["name"].lower() == source.stem.lower()]
            service = services[0][0]["name"] if len(services) == 1 else None
            controller = controllers[0][0]["name"] if len(controllers) == 1 else None
            frontend = {
                "technology": "Legacy AngularJS 1.x" if technology_evidence else None,
                "surface": "/".join(source.parts[:-2]) if len(source.parts) > 2 else None,
                "controller_or_component": controller,
                "service": service,
                "method": current["frontend_method"],
                "api_expression": current["frontend_expression"],
                "source_reference": reference["frontend_source"],
            }
            evidence_by_property: dict[str, list[dict]] = {
                "frontend.api_expression": frontend_evidence,
                "frontend.source_reference": frontend_evidence,
            }
            if frontend["technology"]:
                evidence_by_property["frontend.technology"] = technology_evidence
            if service:
                evidence_by_property["frontend.service"] = services[0][1]
            if controller:
                evidence_by_property["frontend.controller_or_component"] = controllers[0][1]
            if frontend["method"]:
                evidence_by_property["frontend.method"] = frontend_evidence

            backend = {"http_method": None, "route_template": None, "resolved_endpoint": None,
                       "controller": None, "action": None, "source_reference": None}
            request = {"path_parameters": [], "query_parameters": [], "headers": [],
                       "body_type": None, "body_fields": []}
            response = {"response_type": None, "response_fields": [],
                        "collection_or_single": None, "known_status_behavior": []}
            relationship_evidence: list[dict] = []
            if current["status"] == "PROVEN":
                edge = current["mapping_edge"]
                endpoint = node_by_id[edge["target"]]
                endpoint_evidence = _evidence(endpoint)
                relationship_evidence = _evidence(edge, reference["frontend_source"])
                props = endpoint["properties"]
                backend.update({
                    "http_method": props.get("http_method"), "route_template": props.get("route_template"),
                    "resolved_endpoint": props.get("normalized_route"), "controller": props.get("controller"),
                    "action": props.get("action"), "source_reference": endpoint_evidence[0]["source_path"],
                })
                request["path_parameters"] = [
                    {"name": name, "location": "Path", "type": None, "required": "Not established"}
                    for name in props.get("path_parameters", []) or props.get("parameters", [])
                ]
                request["query_parameters"] = props.get("query_parameters", [])
                request["body_type"] = props.get("request_type") or props.get("request_body_type")
                request["body_fields"] = props.get("request_fields", [])
                response["response_type"] = props.get("response_type")
                response["response_fields"] = props.get("response_fields", [])
                response["collection_or_single"] = "collection" if response["response_type"] and "IEnumerable<" in response["response_type"] else ("single" if response["response_type"] else None)
                for key, value in backend.items():
                    if value is not None:
                        evidence_by_property[f"backend.{key}"] = endpoint_evidence
                if request["path_parameters"]:
                    evidence_by_property["request.path_parameters"] = endpoint_evidence
                if request["query_parameters"]:
                    evidence_by_property["request.query_parameters"] = endpoint_evidence
                if request["body_type"]:
                    evidence_by_property["request.body_type"] = endpoint_evidence
                if request["body_fields"]:
                    evidence_by_property["request.body_fields"] = endpoint_evidence
                if response["response_type"]:
                    evidence_by_property["response.response_type"] = endpoint_evidence
                    evidence_by_property["response.collection_or_single"] = endpoint_evidence
                if response["response_fields"]:
                    evidence_by_property["response.response_fields"] = endpoint_evidence

            relationship = {
                "status": current["status"],
                "evidence": relationship_evidence or frontend_evidence,
                "confidence_classification": "CONFIRMED" if current["status"] == "PROVEN" else "REQUIRES_CONFIRMATION",
            }
            evidence_by_property["relationship.status"] = relationship["evidence"]
            contract = {
                "contract_id": contract_id, "feature_id": spec["feature_id"],
                "business_purpose": " / ".join(sorted(set(item["workflows"]))),
                "related_behavior_ids": sorted(set(item["behavior_ids"])),
                "related_story_ids": sorted(set(item["story_ids"])),
                "related_ac_ids": sorted(set(item["ac_ids"])),
                "frontend": frontend, "backend": backend, "request": request, "response": response,
                "relationship": relationship,
                "modernization": {"preservation_required": current["status"] == "PROVEN", "clarification_required": current["status"] != "PROVEN"},
            }
            for prop, evidence in evidence_by_property.items():
                target: object = contract
                for part in prop.split("."):
                    target = target[part]  # type: ignore[index]
                traceability.append(_trace(contract_id, prop, target, evidence))
            contracts.append(contract)
        features.append({"feature_id": spec["feature_id"], "contracts": contracts})

    all_contracts = [contract for feature in features for contract in feature["contracts"]]
    statuses = Counter(contract["relationship"]["status"] for contract in all_contracts)
    coverage_features = []
    for feature in features:
        contracts = feature["contracts"]
        counts = Counter(contract["relationship"]["status"] for contract in contracts)
        coverage_features.append({
            "feature_id": feature["feature_id"], "frontend_api_calls": len(contracts),
            "proven_backend_contracts": counts["PROVEN"], "dynamic_relationships": counts["DYNAMIC"],
            "unresolved_relationships": counts["UNRESOLVED"], "external_relationships": counts["EXTERNAL"],
            "no_backend_route_relationships": counts["NO_BACKEND_ROUTE"],
            "contracts_with_method": sum(bool(x["backend"]["http_method"]) for x in contracts),
            "contracts_with_route": sum(bool(x["backend"]["resolved_endpoint"]) for x in contracts),
            "contracts_with_parameters": sum(bool(x["request"]["path_parameters"] or x["request"]["query_parameters"]) for x in contracts),
            "contracts_with_request_type": sum(bool(x["request"]["body_type"]) for x in contracts),
            "contracts_with_request_fields": sum(bool(x["request"]["body_fields"]) for x in contracts),
            "contracts_with_response_type": sum(bool(x["response"]["response_type"]) for x in contracts),
            "contracts_with_response_fields": sum(bool(x["response"]["response_fields"]) for x in contracts),
        })
    totals = {
        "feature_relevant_api_contracts": len(all_contracts), "proven": statuses["PROVEN"],
        "dynamic": statuses["DYNAMIC"], "unresolved": statuses["UNRESOLVED"], "external": statuses["EXTERNAL"],
        "no_backend_route": statuses["NO_BACKEND_ROUTE"],
        "contracts_with_http_method": sum(bool(x["backend"]["http_method"]) for x in all_contracts),
        "contracts_with_route": sum(bool(x["backend"]["resolved_endpoint"]) for x in all_contracts),
        "contracts_with_path_parameters": sum(bool(x["request"]["path_parameters"]) for x in all_contracts),
        "contracts_with_query_parameters": sum(bool(x["request"]["query_parameters"]) for x in all_contracts),
        "contracts_with_request_type": sum(bool(x["request"]["body_type"]) for x in all_contracts),
        "contracts_with_request_fields": sum(bool(x["request"]["body_fields"]) for x in all_contracts),
        "contracts_with_response_type": sum(bool(x["response"]["response_type"]) for x in all_contracts),
        "contracts_with_response_fields": sum(bool(x["response"]["response_fields"]) for x in all_contracts),
    }
    baseline = {key: forensics[key] for key in (
        "backend_endpoint_facts", "frontend_api_call_facts", "proven", "ambiguous",
        "dynamic_url_warnings", "external_api", "no_backend_route", "unresolved_structural_calls",
        "controller_template_endpoints", "controllers_with_controller_template", "http_methods",
    )}
    populated_fields = 0
    for contract in all_contracts:
        populated_fields += sum(value is not None for value in contract["frontend"].values())
        populated_fields += sum(value is not None for value in contract["backend"].values())
        populated_fields += sum(bool(value) for value in contract["request"].values())
        populated_fields += sum(bool(value) for value in contract["response"].values())
        populated_fields += 1  # relationship.status
    # Surface and API association identifiers are narrative associations, not API signature fields.
    non_signature_frontend_fields = sum(bool(contract["frontend"]["surface"]) for contract in all_contracts)
    traceable_fields = len(traceability)
    totals["traceable_api_contract_fields"] = traceable_fields
    totals["untraceable_api_contract_fields"] = max(0, populated_fields - non_signature_frontend_fields - traceable_fields)
    api_artifact = {"features": features, "baseline": baseline, "property_traceability": traceability}
    return (api_artifact, {"features": coverage_features, "totals": totals}, traceability)
