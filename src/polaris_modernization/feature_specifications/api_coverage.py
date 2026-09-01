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


def build_feature_api_coverage(specifications: list[dict], api_artifact: dict, graph: dict, facts: dict, source_root: Path) -> tuple[dict, dict]:
    endpoints = [node for node in graph["nodes"] if node.get("label") == "Endpoint"]
    raw_facts = facts.get("facts", facts)
    tree_calls = [fact for fact in raw_facts if fact.get("kind") == "api_call" and fact.get("evidence", {}).get("extraction_method") == "tree-sitter"]
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
            if is_context and not context_is_primary:
                classification = {"PROVEN":"SUPPORTING_SHARED_API", "DYNAMIC":"DYNAMIC_SUPPORTING_INTERACTION", "UNRESOLVED":"UNRESOLVED_SUPPORTING_INTERACTION", "EXTERNAL":"EXTERNAL_API"}[status]
            else:
                classification = {"PROVEN":"PRIMARY_BUSINESS_API", "DYNAMIC":"DYNAMIC_PRIMARY_INTERACTION", "UNRESOLVED":"UNRESOLVED_PRIMARY_INTERACTION", "EXTERNAL":"EXTERNAL_API"}[status]
            contract["classification"] = classification
            matching_fact = next((fact for fact in tree_calls if fact["evidence"]["source_path"] == contract["frontend"]["source_reference"] and fact["name"] == contract["frontend"]["api_expression"]), None)
            method = contract["backend"].get("http_method") or (_read_method(source_root, matching_fact) if matching_fact else None)
            candidates = [] if status == "PROVEN" or not method else _candidate_endpoints(contract["frontend"]["api_expression"], method, endpoints)
            interactions.append({"interaction_id":contract["contract_id"], "classification":classification, "status":status, "frontend":contract["frontend"], "backend":contract["backend"], "candidate_endpoints":candidates, "story_ids":contract["related_story_ids"], "ac_ids":contract["related_ac_ids"]})

        caller_files = sorted({contract["frontend"]["source_reference"] for contract in contracts})
        existing = {(contract["frontend"]["source_reference"], contract["frontend"]["api_expression"]) for contract in contracts}
        extra_number = 1
        primary_stories = [story for story in spec["stories"] if any(word in story["business_goal"].lower() for word in ("access", "view", "review", "open"))]
        for fact in tree_calls:
            source = fact["evidence"]["source_path"]
            if source not in caller_files or (source, fact["name"]) in existing:
                continue
            method = _read_method(source_root, fact)
            if method != "GET" or "/current/" in fact["name"].lower():
                continue
            candidates = _candidate_endpoints(fact["name"], method, endpoints)
            dynamic = any(token in fact["name"] for token in ("${", " + "))
            classification = "DYNAMIC_PRIMARY_INTERACTION" if dynamic else "UNRESOLVED_PRIMARY_INTERACTION"
            interaction_id = f"API-{feature_id.removeprefix('feature-').upper().replace('-', '_')}-DISCOVERED-{extra_number:03d}"
            extra_number += 1
            interactions.append({
                "interaction_id": interaction_id, "classification": classification,
                "status": "DYNAMIC" if dynamic else "UNRESOLVED",
                "frontend": {"technology":"Legacy AngularJS 1.x", "controller_or_component":None, "service":None,
                             "method":method, "api_expression":fact["name"], "source_reference":source,
                             "evidence":fact["evidence"]},
                "backend": {"http_method":None,"route_template":None,"resolved_endpoint":None,"controller":None,"action":None,"source_reference":None},
                "candidate_endpoints": candidates,
                "story_ids": [story["story_id"] for story in primary_stories],
                "ac_ids": [ac["acceptance_criterion_id"] for ac in spec["acceptance_criteria"] if ac["story_id"] in {story["story_id"] for story in primary_stories}],
                "relationship_reason": "The associated frontend caller proves the interaction; no deterministic frontend-to-endpoint mapping exists.",
            })
        counts = {name:sum(item["classification"] == name for item in interactions) for name in (
            "PRIMARY_BUSINESS_API", "SUPPORTING_SHARED_API", "EXTERNAL_API", "UNRESOLVED_PRIMARY_INTERACTION",
            "DYNAMIC_PRIMARY_INTERACTION", "UNRESOLVED_SUPPORTING_INTERACTION", "DYNAMIC_SUPPORTING_INTERACTION")}
        unresolved = counts["UNRESOLVED_PRIMARY_INTERACTION"]
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
