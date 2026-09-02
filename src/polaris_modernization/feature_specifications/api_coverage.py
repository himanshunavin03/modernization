"""Feature-relative API completeness over approved deterministic evidence."""
from __future__ import annotations

from pathlib import Path
import re


def _read_method(source_root: Path, fact: dict) -> str | None:
    evidence = fact["evidence"]
    path = source_root / evidence["source_path"]
    if not path.is_file():
        return None
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    start = max(0, evidence["line_start"] - 4)
    end = min(len(lines), evidence["line_end"] + 3)
    match = re.search(r"method\s*:\s*['\"]([A-Z]+)['\"]", "\n".join(lines[start:end]))
    return match.group(1) if match else None


def _route_shape(expression: str) -> str:
    value = expression.strip("'\"`").replace("' + ", "{").replace('" + ', "{")
    value = re.sub(r"\$\{[^}]+\}", "{value}", value)
    value = re.sub(r"\{[^}]*$", "{value}", value)
    return value.rstrip("/") or "/"


def _candidate_endpoints(expression: str, method: str, endpoints: list[dict]) -> list[dict]:
    shape = _route_shape(expression)
    static_prefix = shape.split("{", 1)[0].rstrip("/")
    result = []
    for endpoint in endpoints:
        props = endpoint["properties"]
        route = props.get("normalized_route", "")
        if props.get("http_method") != method:
            continue
        exact = "{" not in shape and route.rstrip("/") == shape
        templated = "{" in shape and route.startswith(static_prefix + "/{")
        if exact or templated:
            result.append({
                "classification": "CANDIDATE_RELEVANT_BACKEND_ENDPOINT",
                "endpoint_id": endpoint["id"], "http_method": props.get("http_method"),
                "route": route, "controller": props.get("controller"), "action": props.get("action"),
                "parameters": props.get("parameters", []), "response_type": props.get("response_type"),
                "evidence": endpoint.get("evidence", []),
                "promotion_status": "NOT_PROVEN_NO_FRONTEND_MAPPING",
            })
    return result


def _api_expression(fact: dict) -> str:
    return str(fact.get("properties", {}).get("raw_url_expression") or fact["name"])


def _api_status(fact: dict) -> str:
    status = fact.get("properties", {}).get("match_status")
    if status in {"PROVEN", "DYNAMIC", "UNRESOLVED", "EXTERNAL", "NO_BACKEND_ROUTE"}:
        return str(status)
    return "DYNAMIC" if any(token in _api_expression(fact) for token in ("${", " + ")) else "UNRESOLVED"


def _api_signatures(fact: dict) -> set[tuple[str, str]]:
    props = fact.get("properties", {})
    source = fact["evidence"]["source_path"]
    method = str(props.get("http_method") or "").upper()
    expression = _api_expression(fact)
    normalized = str(props.get("normalized_route") or "")
    resolved = str(props.get("resolved_backend_endpoint") or "")
    values = {fact["name"], expression, normalized, resolved}
    if method and expression.startswith("/"):
        values.add(f"{method} {expression}")
    if method and normalized:
        values.add(f"{method} {normalized}")
    return {(source, value) for value in values if value}


def _contract_signatures(contract: dict) -> set[tuple[str, str]]:
    source = contract["frontend"]["source_reference"]
    method = str(contract["frontend"].get("method") or "").upper()
    expression = contract["frontend"]["api_expression"]
    resolved = contract["backend"].get("resolved_endpoint") or ""
    values = {expression, resolved}
    if method and expression.startswith("/"):
        values.add(f"{method} {expression}")
    if method and resolved:
        values.add(f"{method} {resolved}")
    return {(source, value) for value in values if value}


def _classification(status: str, *, supporting: bool) -> str:
    supporting_map = {
        "PROVEN": "SUPPORTING_SHARED_API",
        "DYNAMIC": "DYNAMIC_SUPPORTING_INTERACTION",
        "UNRESOLVED": "UNRESOLVED_SUPPORTING_INTERACTION",
        "EXTERNAL": "EXTERNAL_API",
        "NO_BACKEND_ROUTE": "UNRESOLVED_SUPPORTING_INTERACTION",
    }
    primary_map = {
        "PROVEN": "PRIMARY_BUSINESS_API",
        "DYNAMIC": "DYNAMIC_PRIMARY_INTERACTION",
        "UNRESOLVED": "UNRESOLVED_PRIMARY_INTERACTION",
        "EXTERNAL": "EXTERNAL_API",
        "NO_BACKEND_ROUTE": "UNRESOLVED_PRIMARY_INTERACTION",
    }
    return (supporting_map if supporting else primary_map)[status]


def _resolved_backend(fact: dict, endpoints_by_name: dict[str, dict]) -> dict:
    endpoint = endpoints_by_name.get(str(fact.get("properties", {}).get("resolved_backend_endpoint") or ""))
    if not endpoint:
        return {"http_method": None, "route_template": None, "resolved_endpoint": None, "controller": None, "action": None, "source_reference": None}
    props = endpoint["properties"]
    evidence = endpoint.get("evidence", [])
    return {
        "http_method": props.get("http_method"),
        "route_template": props.get("route_template"),
        "resolved_endpoint": props.get("normalized_route"),
        "controller": props.get("controller"),
        "action": props.get("action"),
        "source_reference": evidence[0]["source_path"] if evidence else None,
    }


def build_feature_api_coverage(specifications: list[dict], api_artifact: dict, graph: dict, facts: dict, source_root: Path) -> tuple[dict, dict]:
    endpoints = [node for node in graph["nodes"] if node.get("label") == "Endpoint"]
    endpoints_by_name = {node["name"]: node for node in endpoints}
    raw_facts = facts.get("facts", facts)
    tree_calls = [fact for fact in raw_facts if fact.get("kind") == "api_call"]
    contracts_by_feature = {item["feature_id"]: item["contracts"] for item in api_artifact["features"]}
    matrices, classifications = [], []
    for spec in specifications:
        feature_id = spec["feature_id"]
        contracts = contracts_by_feature[feature_id]
        context_is_primary = "context" in spec["feature_name"].lower()
        interactions = []
        for contract in contracts:
            route = (contract["backend"].get("resolved_endpoint") or contract["frontend"]["api_expression"]).lower()
            is_context = "/current/" in route
            status = contract["relationship"]["status"]
            classification = _classification(status, supporting=is_context and not context_is_primary)
            contract["classification"] = classification
            matching_fact = next((
                fact for fact in tree_calls
                if fact["evidence"]["source_path"] == contract["frontend"]["source_reference"]
                and (contract["frontend"]["source_reference"], contract["frontend"]["api_expression"]) in _api_signatures(fact)
            ), None)
            method = contract["backend"].get("http_method") or contract["frontend"].get("method") or (_read_method(source_root, matching_fact) if matching_fact else None)
            candidates = [] if status == "PROVEN" or not method else _candidate_endpoints(contract["frontend"]["api_expression"], method, endpoints)
            interactions.append({"interaction_id":contract["contract_id"], "classification":classification, "status":status, "frontend":contract["frontend"], "backend":contract["backend"], "candidate_endpoints":candidates, "story_ids":contract["related_story_ids"], "ac_ids":contract["related_ac_ids"]})

        caller_files = sorted({contract["frontend"]["source_reference"] for contract in contracts})
        existing = {signature for contract in contracts for signature in _contract_signatures(contract)}
        extra_number = 1
        primary_stories = [story for story in spec["stories"] if any(word in story["business_goal"].lower() for word in ("access", "view", "review", "open"))]
        for fact in tree_calls:
            source = fact["evidence"]["source_path"]
            if source not in caller_files or _api_signatures(fact).intersection(existing):
                continue
            method = fact.get("properties", {}).get("http_method") or _read_method(source_root, fact)
            if method != "GET" or "/current/" in fact["name"].lower():
                continue
            status = _api_status(fact)
            candidates = [] if status == "PROVEN" else _candidate_endpoints(_api_expression(fact), method, endpoints)
            classification = _classification(status, supporting=False)
            interaction_id = f"API-{feature_id.removeprefix('feature-').upper().replace('-', '_')}-DISCOVERED-{extra_number:03d}"
            extra_number += 1
            interactions.append({
                "interaction_id": interaction_id, "classification": classification,
                "status": status,
                "frontend": {"technology":"Legacy AngularJS 1.x", "controller_or_component":fact.get("properties", {}).get("controller_or_component"), "service":fact.get("properties", {}).get("service"),
                             "method":method, "api_expression":_api_expression(fact), "source_reference":source,
                             "evidence":fact["evidence"]},
                "backend": _resolved_backend(fact, endpoints_by_name) if status == "PROVEN" else {"http_method":None,"route_template":None,"resolved_endpoint":None,"controller":None,"action":None,"source_reference":None},
                "candidate_endpoints": candidates,
                "story_ids": [story["story_id"] for story in primary_stories],
                "ac_ids": [ac["acceptance_criterion_id"] for ac in spec["acceptance_criteria"] if ac["story_id"] in {story["story_id"] for story in primary_stories}],
                "relationship_reason": fact.get("properties", {}).get("relationship_reason") or "The associated frontend caller proves the interaction; no deterministic frontend-to-endpoint mapping exists.",
            })
        counts = {name:sum(item["classification"] == name for item in interactions) for name in (
            "PRIMARY_BUSINESS_API", "SUPPORTING_SHARED_API", "EXTERNAL_API", "UNRESOLVED_PRIMARY_INTERACTION",
            "DYNAMIC_PRIMARY_INTERACTION", "UNRESOLVED_SUPPORTING_INTERACTION", "DYNAMIC_SUPPORTING_INTERACTION")}
        unresolved = counts["UNRESOLVED_PRIMARY_INTERACTION"] + counts["UNRESOLVED_SUPPORTING_INTERACTION"]
        dynamic = counts["DYNAMIC_PRIMARY_INTERACTION"]
        coverage_status = "COMPLETE_WITH_UNRESOLVED_RELATIONSHIP" if unresolved else ("COMPLETE_WITH_DYNAMIC_RELATIONSHIP" if dynamic else "COMPLETE_PROVEN")
        behavior_rows = []
        for story in spec["stories"]:
            related = [item for item in interactions if story["story_id"] in item["story_ids"]]
            behavior_rows.append({"behavior_id":story["story_id"], "description":story["business_goal"],
                "current_ui_surfaces":story["ui_surface_refs"], "frontend_services":sorted({Path(x["frontend"]["source_reference"]).stem for x in related}),
                "frontend_api_calls":sorted({x["frontend"]["api_expression"] for x in related}),
                "primary_business_api":{"status":"PROVEN" if any(x["classification"]=="PRIMARY_BUSINESS_API" for x in related) else ("DYNAMIC" if any(x["classification"]=="DYNAMIC_PRIMARY_INTERACTION" for x in related) else ("UNRESOLVED" if any(x["classification"]=="UNRESOLVED_PRIMARY_INTERACTION" for x in related) else "NOT_ESTABLISHED")), "contracts":[x["interaction_id"] for x in related if "PRIMARY" in x["classification"]]},
                "supporting_apis":[x["interaction_id"] for x in related if "SUPPORTING" in x["classification"]],
                "unresolved_interactions":[x["interaction_id"] for x in related if x["status"]=="UNRESOLVED"],
                "dynamic_interactions":[x["interaction_id"] for x in related if x["status"]=="DYNAMIC"]})
        matrices.append({"feature_id":feature_id,"primary_behaviors":behavior_rows,"interactions":interactions,"coverage_status":coverage_status,"counts":counts})
        classifications.extend({"feature_id":feature_id, **item} for item in interactions)
    return {"features":matrices}, {"interactions":classifications}
