"""Deterministic safeguards for frozen architecture-driven task plans."""
from __future__ import annotations

import json
import re
from hashlib import sha256


UNSELECTED_TECHNOLOGIES = ("NgRx", "Server-Side Rendering", "Hydration", "Microfrontends", "Module Federation")


def selection_hash(selection: dict) -> str:
    return sha256(json.dumps(selection, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def validate_tasks(context: dict, tasks: list[dict]) -> dict:
    architecture = context["architecture"]
    selection = architecture["selection"]
    task_ids = [item["task_id"] for item in tasks]
    known_tasks = set(task_ids)
    positions = {item["task_id"]: item["implementation_order"] for item in tasks}
    selected = set(selection["selected_decision_ids"])
    valid_frs = {item["id"] for item in context["requirements"]}
    valid_stories = {item["story_id"] for item in context["stories"]}
    valid_ac = {item["authoritative_ac_ref"] for item in context["acceptance_criteria"]}
    valid_apis = {item["api_id"] for item in context["api_contracts"]}
    api_endpoints = {item["endpoint"] for item in context["api_contracts"]}
    represented_apis = {ref for item in tasks for ref in item["api_refs"]}
    serialized_tasks = json.dumps(tasks)
    selected_decisions = [item for item in selection["decisions"] if item["id"] in selected]
    selected_categories = {item["category"] for item in selected_decisions}
    selected_technologies = {item["technology"] for item in selected_decisions}

    cycle_count = 0
    visiting: set[str] = set()
    visited: set[str] = set()
    by_id = {item["task_id"]: item for item in tasks}

    def visit(task_id: str) -> None:
        nonlocal cycle_count
        if task_id in visiting:
            cycle_count += 1
            return
        if task_id in visited or task_id not in by_id:
            return
        visiting.add(task_id)
        for dependency in by_id[task_id]["dependencies"]:
            visit(dependency)
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in task_ids:
        visit(task_id)

    endpoint_literals = set(re.findall(r"/api/[A-Za-z0-9_/{}/.-]+", serialized_tasks))
    checks = {
        "architecture_selection_locked": architecture["architecture_lock"]["status"] == "LOCKED" and architecture["architecture_lock"]["locked_after_validation"] is True,
        "architecture_selection_hash_valid": selection_hash(selection) == architecture["architecture_lock"]["selection_hash"],
        "feature_scope_only": {item["feature_id"] for item in tasks} == {context["feature"]["feature_id"]},
        "task_ids_unique": len(task_ids) == len(known_tasks),
        "dependencies_exist": all(set(item["dependencies"]) <= known_tasks for item in tasks),
        "dependency_graph_acyclic": cycle_count == 0,
        "implementation_order_valid": all(positions[dependency] < item["implementation_order"] for item in tasks for dependency in item["dependencies"]),
        "selected_architecture_only": all(set(item["architecture_decision_refs"]) <= selected for item in tasks),
        "requirement_refs_valid": all(set(item["functional_requirement_refs"]) <= valid_frs for item in tasks),
        "story_refs_valid": all(set(item["story_refs"]) <= valid_stories for item in tasks),
        "acceptance_criteria_refs_valid": all(set(item["acceptance_criteria_refs"]) <= valid_ac for item in tasks),
        "api_refs_valid": all(set(item["api_refs"]) <= valid_apis for item in tasks),
        "existing_api_contracts_preserved": represented_apis == valid_apis,
        "no_invented_existing_api": endpoint_literals <= api_endpoints,
        "unselected_technology_absent": not any(name.lower() in serialized_tasks.lower() for name in UNSELECTED_TECHNOLOGIES),
        "gateway_task_present": "API Gateway" not in selected_categories or any(item["category"] == "GATEWAY" for item in tasks),
        "bff_task_present": "Backend for Frontend" not in selected_categories or any(item["category"] == "BFF" for item in tasks),
        "future_bff_contract_labeled": "Backend for Frontend" not in selected_categories or any("TARGET_CONTRACT_TO_BE_DESIGNED" in value for item in tasks if item["category"] in {"BFF", "INTEGRATION"} for value in item["implementation_requirements"]),
        "playwright_task_present": "Playwright" not in selected_technologies or any(item["category"] == "TEST" and "Playwright" in item["title"] for item in tasks),
        "every_task_traceable": all(item["traceability"] and item["architecture_decision_refs"] for item in tasks),
        "design_conflicts_preserve_requirements": all(conflict["requirement_reference"] in valid_frs for conflict in context["design"].get("conflicts", [])),
    }
    blockers = [name for name, passed in checks.items() if not passed]
    return {"status": "PASS" if not blockers else "FAIL", "checks": checks, "blockers": blockers, "cycle_count": cycle_count}
