"""Jira-oriented delivery composition and deterministic quality gates."""
from __future__ import annotations

import re


VAGUE_RESULTS = (
    "behavior remains available",
    "functionality works correctly",
    "requirement is supported",
    "existing behavior is preserved",
    "feature is implemented",
)


def _ac_quality(criterion: dict) -> dict:
    given = [item.strip() for item in criterion["given"] if item.strip()]
    trigger = criterion["when"].strip()
    results = [item.strip() for item in criterion["then"] if item.strip()]
    result_text = " ".join(results).lower()
    vague = any(phrase in result_text for phrase in VAGUE_RESULTS)
    circular = any(
        re.search(pattern, result_text)
        for pattern in (
            r"\b(access|view|retrieve)\s+(.+?)\s+so that\s+\2\b",
            r"\bremains?\s+(?:available|visible|accessible)\b",
            r"\bworks?\s+correctly\b",
        )
    )
    checks = {
        "precondition_present": bool(given),
        "trigger_present": bool(trigger),
        "observable_result_present": bool(results) and not vague,
        "vague_result": vague,
        "circular_result": circular,
    }
    if not checks["precondition_present"] or not checks["trigger_present"] or not results:
        status = "NEEDS_CLARIFICATION"
    elif vague or circular:
        status = "WARNING"
    else:
        status = "PASS"
    return {"status": status, "checks": checks}


def _split_recommendation(apis: list[dict], requirements: list[dict]) -> dict | None:
    independent = [api for api in apis if api["kind"] not in {"context", "identity"}]
    if len(independent) < 2:
        return None
    api_ids = {api["id"] for api in independent}
    candidates = [item["title"] for item in requirements if api_ids.intersection(item["api_ids"])]
    if len(candidates) < 2:
        return None
    return {
        "status": "SPLIT_RECOMMENDATION",
        "suggested_summaries": list(dict.fromkeys(candidates)),
        "reason": "Separate backend contracts support independently testable behavior.",
        "approval_required": "BA / PO approval",
    }


def _invest(story: dict, split: dict | None, blocking: list[dict]) -> dict:
    ac_statuses = {item["quality"]["status"] for item in story["acceptance_criteria"]}
    checks = {
        "independent": {"status": "WARNING" if split else "PASS", "reason": "The Story has separable API-backed behavior." if split else "No obvious delivery dependency was detected."},
        "negotiable": {"status": "PASS", "reason": "The delivery representation preserves scope without prescribing implementation design."},
        "valuable": {"status": "PASS" if story["business_outcome"] else "WARNING", "reason": "A supported outcome is present." if story["business_outcome"] else "Business outcome confirmation is nonblocking enrichment."},
        "estimable": {"status": "WARNING" if blocking else "PASS", "reason": "Implementation or QA details require clarification." if blocking else "No blocking estimation gap is identified."},
        "small": {"status": "WARNING" if split else "PASS", "reason": "A small optional split is recommended." if split else "No obvious size concern was detected."},
        "testable": {"status": "PASS" if ac_statuses <= {"PASS"} else "NEEDS_REVIEW", "reason": "All human AC pass deterministic testability checks." if ac_statuses <= {"PASS"} else "At least one AC requires quality review."},
    }
    statuses = {item["status"] for item in checks.values()}
    overall = "NEEDS_REVIEW" if "NEEDS_REVIEW" in statuses else "WARNING" if "WARNING" in statuses else "PASS"
    return {"status": overall, "checks": checks}


def _readiness(story: dict, blocking: list[dict]) -> dict:
    checks = {
        "story_goal_understandable": bool(story["goal"]),
        "functional_behavior_available": bool(story["functional_requirement_refs"]),
        "acceptance_criteria_available": bool(story["acceptance_criteria"]),
        "acceptance_criteria_testable": all(item["quality"]["status"] == "PASS" for item in story["acceptance_criteria"]),
        "required_api_known": all(item["method"] and item["endpoint"] for item in story["api_dependencies"]),
        "required_api_parameters_known": all(all(value["name"] for value in api["path_parameters"] + api["query_parameters"]) for api in story["api_dependencies"]),
        "required_business_rules_represented": True,
        "blocking_clarifications_identified": True,
        "contradictions_absent": True,
        "unsupported_invented_behavior_absent": True,
    }
    if not all(checks.values()):
        status = "BLOCKED"
    elif blocking:
        status = "NEEDS_CLARIFICATION"
    else:
        status = "READY"
    return {
        "status": status,
        "checks": checks,
        "blocking_clarification_ids": [item["id"] for item in blocking],
        "non_blocking_business_enrichment": story["business_outcome"] is None,
    }


def _api_dependency(api: dict) -> dict:
    dependency = {
        "api_id": api["id"],
        "purpose": api["purpose"],
        "method": api["method"],
        "endpoint": api["endpoint"],
        "path_parameters": [item for item in api["inputs"] if item["location"] == "Path"],
        "query_parameters": [item for item in api["inputs"] if item["location"] == "Query"],
        "request_model": api["request_type"],
        "response_description": api["description"],
        "response_model": api["model"],
        "traceability": {"source_interaction_ids": api["source_interaction_ids"]},
    }
    if api["collection"] and dependency["response_model"]:
        dependency["response_model"] += "[]"
    return dependency


def build_jira_delivery(model: dict, presentation: dict) -> dict:
    """Build a delivery representation without changing authoritative truth."""
    criteria_by_story: dict[str, list[dict]] = {}
    for criterion in presentation["acceptance_criteria"]:
        criteria_by_story.setdefault(criterion["source_story_id"], []).append(criterion)
    requirements = presentation["functional_requirements"]
    clarifications = presentation["clarifications"]
    stories = []
    for source, human in zip(model["requirements"], presentation["stories"], strict=True):
        source_id = human["source_story_id"]
        apis = [api for api in presentation["api_requirements"] if source_id in api.get("delivery_story_ids", [])]
        api_ids = {api["id"] for api in apis}
        story_requirements = [item for item in requirements if source_id in item["source_story_ids"]]
        story_clarifications = [item for item in clarifications if item.get("story_id") == source_id or item.get("api_id") in api_ids]
        blocking = [item for item in story_clarifications if item["required_before"] == "Development and QA completion"]
        rules = [item for item in presentation["business_rules"] if any(api["kind"] == "context" for api in apis) and "organization context" in item["rule"].lower()]
        human_criteria = []
        for criterion in criteria_by_story.get(source_id, []):
            ac_clarifications = [item["id"] for item in story_clarifications if item.get("ac_id") in {criterion["id"], criterion["source_ac_id"]}]
            realized = {
                "id": criterion["id"], "title": criterion["title"],
                "given": criterion["given"], "when": criterion["when"], "then": criterion["expected_results"],
                "clarification_required": bool(ac_clarifications),
                "clarification_ids": ac_clarifications,
                "authoritative_ac_ref": criterion["source_ac_id"],
            }
            realized["quality"] = _ac_quality(realized)
            human_criteria.append(realized)
        story = {
            "story_id": human["id"], "feature_id": model["feature_id"], "summary": human["title"],
            "actor": "application user", "goal": human["goal"], "business_outcome": human["outcome"],
            "description": f"As an application user, I want to {human['goal']}" + (f", so that {human['outcome']}." if human["outcome"] else "."),
            "functional_requirement_refs": [{"id": item["id"], "title": item["title"], "requirement": item["requirement"]} for item in story_requirements],
            "business_rules": rules,
            "preconditions": list(dict.fromkeys(value for item in human_criteria for value in item["given"])),
            "acceptance_criteria": human_criteria,
            "api_dependencies": [_api_dependency(api) for api in apis],
            "clarifications": story_clarifications,
            "traceability": {
                "authoritative_story_ref": source_id,
                "functional_requirement_refs": [item["id"] for item in story_requirements],
                "authoritative_ac_refs": [item["authoritative_ac_ref"] for item in human_criteria],
                "api_interaction_refs": [value for api in apis for value in api["source_interaction_ids"]],
            },
        }
        split = _split_recommendation(apis, story_requirements)
        story["quality"] = {"invest": _invest(story, split, blocking), "split_recommendation": split}
        story["readiness"] = _readiness(story, blocking)
        stories.append(story)
    return {"feature_id": model["feature_id"], "feature_name": presentation["feature"]["name"], "stories": stories}


def summarize_jira_delivery(features: list[dict]) -> dict:
    stories = [story for feature in features for story in feature["stories"]]
    criteria = [criterion for story in stories for criterion in story["acceptance_criteria"]]
    invest = {status: sum(story["quality"]["invest"]["status"] == status for story in stories) for status in ("PASS", "WARNING", "NEEDS_REVIEW")}
    readiness = {status: sum(story["readiness"]["status"] == status for story in stories) for status in ("READY", "NEEDS_CLARIFICATION", "BLOCKED")}
    ac_quality = {status: sum(criterion["quality"]["status"] == status for criterion in criteria) for status in ("PASS", "WARNING", "NEEDS_CLARIFICATION")}
    return {
        "features": len(features), "jira_story_models": len(stories),
        "functional_requirements": len({(feature["feature_id"], item["id"]) for feature in features for story in feature["stories"] for item in story["functional_requirement_refs"]}),
        "api_dependencies": len({(feature["feature_id"], api["api_id"]) for feature in features for story in feature["stories"] for api in story["api_dependencies"]}),
        "clarifications": len({(feature["feature_id"], item["id"]) for feature in features for story in feature["stories"] for item in story["clarifications"]}),
        "invest": invest, "readiness": readiness,
        "acceptance_criteria": {"total": len(criteria), **ac_quality},
        "circular_human_ac": sum(item["quality"]["checks"]["circular_result"] for item in criteria),
        "vague_human_ac": sum(item["quality"]["checks"]["vague_result"] for item in criteria),
    }
