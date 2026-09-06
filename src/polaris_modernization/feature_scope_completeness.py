"""Generate a Feature scope contract from validated capability dispositions."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import shutil

from polaris_modernization.capability_completeness import validate_capability_coverage


def _requirement_key(capability: dict) -> str:
    kind = capability["operation_kind"]
    identity = capability["operation_identity"].casefold()
    if kind == "READ" and "/users/current/tenant" in identity:
        return "TENANT_CONTEXT"
    return {"READ": "DETAIL"}.get(kind, kind)


def _title(key: str, entity: str) -> str:
    values = {
        "LIST": f"Review {entity} Directory", "DETAIL": f"View {entity} Details",
        "CREATE": f"Create {entity}", "UPDATE": f"Update {entity}", "DELETE": f"Delete {entity}",
        "PAGE": f"Continue Through {entity} Results", "NAVIGATE": f"Navigate from the {entity} Experience",
        "UPLOAD": f"Maintain {entity} Profile Media", "VALIDATE": f"Validate {entity} Input",
        "TENANT_CONTEXT": "Establish Current Tenant Context", "OTHER": f"Preserve {entity} Behavior",
    }
    return values[key]


def _api_identity(capability: dict) -> str | None:
    identity = capability["operation_identity"]
    if not re.match(r"^(GET|POST|PUT|PATCH|DELETE) /api/", identity):
        return None
    method = identity.split(" ", 1)[0]
    backend = next((item["node_id"].split(":Endpoint:", 1)[1] for item in capability["source_evidence"] if item["stage"] == "BACKEND" and ":Endpoint:" in item["node_id"]), None)
    return backend if backend and backend.startswith(method + " ") else identity


def build_feature_scope_contract(feature_id: str, feature_name: str, coverage: dict) -> tuple[dict, dict]:
    validation = validate_capability_coverage(coverage.get("capabilities", []), coverage.get("dispositions", []))
    if validation["status"] == "FAIL":
        raise ValueError(f"Cannot generate Feature scope from incomplete capability coverage: {validation}")
    capabilities = {item["capability_id"]: item for item in coverage["capabilities"]}
    included = [item for item in coverage["dispositions"] if item["scope_status"] == "INCLUDED" and item.get("feature_id") == feature_id]
    grouped: dict[str, list[dict]] = {}
    for disposition in included:
        capability = capabilities[disposition["capability_id"]]
        grouped.setdefault(_requirement_key(capability), []).append(capability)
    entity = re.sub(r"\s+(Directory|Management|Experience|Context).*$", "", feature_name).strip() or "Feature"
    requirements = []
    requirement_by_capability = {}
    for index, (key, items) in enumerate(sorted(grouped.items(), key=lambda item: (list(("LIST", "DETAIL", "CREATE", "UPDATE", "DELETE", "PAGE", "UPLOAD", "VALIDATE", "NAVIGATE", "TENANT_CONTEXT", "OTHER")).index(item[0]) if item[0] in ("LIST", "DETAIL", "CREATE", "UPDATE", "DELETE", "PAGE", "UPLOAD", "VALIDATE", "NAVIGATE", "TENANT_CONTEXT", "OTHER") else 99)), 1):
        requirement_id = f"FR-{index:02d}"
        title = _title(key, entity)
        api_dependencies = sorted({identity for item in items for identity in [_api_identity(item)] if identity})
        requirement = {
            "id": requirement_id, "title": title,
            "description": f"The existing application behavior requires users to {title.lower()}.",
            "source_capability_ids": sorted(item["capability_id"] for item in items),
            "api_dependencies": api_dependencies,
        }
        requirements.append(requirement)
        for item in items:
            requirement_by_capability[item["capability_id"]] = requirement_id
    api_contracts = []
    for identity in sorted({value for item in requirements for value in item["api_dependencies"]}):
        method, route = identity.split(" ", 1)
        api_contracts.append({
            "contract_id": f"API-{len(api_contracts) + 1:02d}", "method": method, "route": route,
            "requirement_ids": sorted(item["id"] for item in requirements if identity in item["api_dependencies"]),
            "source_capability_ids": sorted(item["capability_id"] for item in capabilities.values() if _api_identity(item) == identity),
        })
    refreshed = deepcopy(coverage)
    for disposition in refreshed["dispositions"]:
        requirement_id = requirement_by_capability.get(disposition["capability_id"])
        if requirement_id:
            disposition["downstream_refs"] = sorted(set([*disposition.get("downstream_refs", []), requirement_id]))
    entity_tokens = {entity.casefold(), entity.casefold() + "s"}
    unresolved = [item for item in refreshed["dispositions"] if item["scope_status"] != "INCLUDED" and capabilities[item["capability_id"]]["domain_context"] in entity_tokens]
    contract = {
        "feature_id": feature_id, "feature_name": feature_name, "status": "FEATURE_SCOPE_READY_WITH_EXPLICIT_DISPOSITIONS" if unresolved else "FEATURE_SCOPE_READY",
        "functional_requirements": requirements, "api_contracts": api_contracts,
        "capability_dispositions": [item for item in refreshed["dispositions"] if item.get("feature_id") == feature_id or item in unresolved],
        "downstream_status": "STALE_REGENERATION_REQUIRED",
        "stories_regenerated": False, "acceptance_criteria_regenerated": False,
    }
    return contract, refreshed


def render_feature_markdown(contract: dict) -> str:
    lines = [
        f"# {contract['feature_name']}", "", "## Feature Overview", "",
        "This Feature preserves the established directory behavior selected from the existing application.", "",
        "## Functional Requirements", "",
    ]
    lines.extend(f"- **{item['id']} — {item['title']}:** {item['description']}" for item in contract["functional_requirements"])
    lines.extend(["", "## API Requirements", ""])
    lines.extend(f"- `{item['method']} {item['route']}` supports {', '.join(item['requirement_ids'])}." for item in contract["api_contracts"])
    unresolved_count = sum(item["scope_status"] != "INCLUDED" for item in contract["capability_dispositions"])
    lines.extend([
        "", "## Scope Decisions", "",
        f"{unresolved_count} supporting or cross-workflow operation(s) remain explicitly unresolved for Feature ownership; none are silently discarded.", "",
        "## Delivery Status", "",
        "Stories, Acceptance Criteria, technical tasks, and implementation require regeneration after this Feature scope is approved.", "",
    ])
    return "\n".join(lines)


def publish_feature_scope_refresh(source_root: Path, output_root: Path, feature_id: str, coverage: dict) -> dict:
    existing = json.loads((source_root / f"{feature_id}.json").read_text(encoding="utf-8"))
    contract, refreshed_coverage = build_feature_scope_contract(feature_id, existing["feature_name"], coverage)
    run_id = f"capability-scope-{datetime.now(timezone.utc).strftime('%Y-%m-%d-%H%M%S-%f')}"
    destination = output_root / "runs" / run_id
    shutil.copytree(source_root, destination)
    refreshed_specification = deepcopy(existing)
    refreshed_specification.update({
        "status": contract["status"],
        "functional_requirements": contract["functional_requirements"],
        "capability_api_contracts": contract["api_contracts"],
        "capability_dispositions": contract["capability_dispositions"],
        "downstream_status": contract["downstream_status"],
        "stories_regenerated": False,
        "acceptance_criteria_regenerated": False,
    })
    (destination / f"{feature_id}.json").write_text(json.dumps(refreshed_specification, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (destination / f"{feature_id}.md").write_text(render_feature_markdown(contract), encoding="utf-8")
    (destination / "capability-coverage.json").write_text(json.dumps(refreshed_coverage, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (destination / "downstream-staleness.json").write_text(json.dumps({
        "feature_id": feature_id, "status": "STALE_REGENERATION_REQUIRED",
        "stale_artifacts": ["STORIES", "ACCEPTANCE_CRITERIA", "TECHNICAL_TASKS", "ANGULAR", "PLAYWRIGHT"],
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    api_path = destination / "feature-api-contracts.json"
    api_document = json.loads(api_path.read_text(encoding="utf-8"))
    feature_api = next(item for item in api_document["features"] if item["feature_id"] == feature_id)
    feature_api["contracts"] = contract["api_contracts"]
    api_path.write_text(json.dumps(api_document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    latest = output_root / "latest"
    shutil.rmtree(latest)
    shutil.copytree(destination, latest)
    return {"run_id": run_id, "path": destination, "contract": contract, "coverage": refreshed_coverage}
