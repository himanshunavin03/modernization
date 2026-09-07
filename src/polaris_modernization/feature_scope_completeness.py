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
    if capability.get("interaction_semantics") and all(s.get("system_initiated") for s in capability["interaction_semantics"]):
        return "SYSTEM"
    if kind == "READ" and not capability.get("interaction_semantics"):
        return "SYSTEM"
    return {"READ": "DETAIL"}.get(kind, kind)


def _title(key: str, entity: str) -> str:
    values = {
        "LIST": f"Review {entity} Directory", "DETAIL": f"View {entity} Details",
        "CREATE": f"Create {entity}", "UPDATE": f"Update {entity}", "DELETE": f"Delete {entity}",
        "PAGE": f"Continue Through {entity} Results", "NAVIGATE": f"Navigate from the {entity} Experience",
        "UPLOAD": f"Maintain {entity} Profile Media", "VALIDATE": f"Validate {entity} Input",
        "SYSTEM": f"Resolve Required {entity} Context", "OTHER": f"Use {entity} Interaction Controls",
    }
    return values[key]


def _behavior_description(items: list[dict], title: str) -> str:
    """Render only UI semantics retained by the generic capability model."""
    interactions = [semantic for item in items for semantic in item.get("interaction_semantics", [])]
    labels = sorted({str(item["label"]).strip() for item in interactions if item.get("label")})
    kinds = {item.get("interaction_type") for item in interactions}
    from polaris_modernization.application_understanding.interactions import describe_semantic
    results = sorted({describe_semantic(item) for item in interactions if item.get("observable_result")})
    if results:
        return " ".join(results)
    if "VALIDATION" in kinds:
        return "The form requires the specified input."
    if "SELECTION" in kinds:
        return "The directory supports record selection and selection-state changes before related actions are used."
    if labels:
        quoted = ", ".join(f'"{label}"' for label in labels)
        results = sorted({str(item["observable_result"]).strip() for item in interactions if item.get("observable_result")})
        if results:
            return f"A user can select {quoted}; {'. '.join(results)}."
        return f"A user can select the {quoted} action{'s' if len(labels) > 1 else ''}."
    if any(item.get("operation_kind") == "READ" for item in items):
        return "The system resolves the required context before dependent feature operations run."
    return f"The feature preserves the supported {title.casefold()} interaction."


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
        interactions = capability.get("interaction_semantics", [])
        identities = sorted({s["interaction_id"] for s in interactions if s.get("interaction_id")})
        if identities:
            for identity in identities:
                subset = {**capability, "interaction_semantics": [s for s in interactions if s.get("interaction_id") == identity]}
                grouped.setdefault(identity, []).append(subset)
        else:
            grouped.setdefault(_requirement_key(capability), []).append(capability)
    entity = re.sub(r"\s+(Directory|Management|Experience|Context).*$", "", feature_name).strip() or "Feature"
    requirements = []
    requirement_by_capability = {}
    for index, (key, items) in enumerate(sorted(grouped.items(), key=lambda item: (list(("LIST", "DETAIL", "CREATE", "UPDATE", "DELETE", "PAGE", "UPLOAD", "VALIDATE", "NAVIGATE", "TENANT_CONTEXT", "OTHER")).index(item[0]) if item[0] in ("LIST", "DETAIL", "CREATE", "UPDATE", "DELETE", "PAGE", "UPLOAD", "VALIDATE", "NAVIGATE", "TENANT_CONTEXT", "OTHER") else 99)), 1):
        requirement_id = f"FR-{index:02d}"
        semantics = list({json.dumps(s,sort_keys=True):s for item in items for s in item.get("interaction_semantics", [])}.values())
        operation_key = _requirement_key(items[0])
        labels = sorted({s['label'] for s in semantics if s.get('label')})
        title = labels[0].capitalize() if len(labels)==1 else _title(operation_key, entity)
        effect_kinds={s.get('effect_kind') for s in semantics}
        if labels and any(item['operation_kind'] in {'CREATE','UPDATE','DELETE'} for item in items) and len(labels[0].split())==1:
            title=f'{labels[0].capitalize()} {entity}'
        if 'COLLECTION_REMOVE' in effect_kinds:
            arguments={s.get('trigger') for s in semantics if s.get('trigger')}
            selected=any(re.search(r'\(\s*\)\s*$',a) for a in arguments)
            title=f'Delete selected {entity} records' if selected else f'Delete an individual {entity}'
        if effect_kinds=={'VALIDATION'}:
            title='Validate '+str(semantics[0].get('state_change') or 'required input').title()
        elif effect_kinds=={'SELECTION'}:
            title='Change '+str(semantics[0].get('state_change') or 'record selection').removeprefix('selection model ').replace('.', ' ')
        elif not labels and 'NAVIGATION' in effect_kinds:
            targets=sorted({s['navigation_target'] for s in semantics if s.get('navigation_target')})
            title='Open '+', '.join(targets)+' details'
        elif 'MEDIA_BINDING' in effect_kinds:
            title=_title('UPLOAD',entity)
        api_dependencies = sorted({identity for item in items for identity in [_api_identity(item)] if identity})
        requirement = {
            "id": requirement_id, "title": title,
            "description": _behavior_description(items, title),
            "source_capability_ids": sorted({item["capability_id"] for item in items}),
            "interaction_semantics": semantics,
            "interaction_id": key if key.startswith("interaction-") else None,
            "system_initiated": operation_key == "SYSTEM",
            "api_dependencies": api_dependencies,
        }
        requirements.append(requirement)
        for item in items:
            requirement_by_capability.setdefault(item["capability_id"], []).append(requirement_id)
    api_contracts = []
    for identity in sorted({value for item in requirements for value in item["api_dependencies"]}):
        method, route = identity.split(" ", 1)
        api_contracts.append({
            "contract_id": f"API-{len(api_contracts) + 1:02d}", "method": method, "route": route,
            "requirement_ids": sorted(item["id"] for item in requirements if identity in item["api_dependencies"]),
            "source_capability_ids": sorted(item["capability_id"] for item in capabilities.values() if _api_identity(item) == identity),
            "metadata": [m for item in capabilities.values() if _api_identity(item) == identity for m in item.get('api_metadata',[])],
        })
    refreshed = deepcopy(coverage)
    for disposition in refreshed["dispositions"]:
        requirement_ids = requirement_by_capability.get(disposition["capability_id"])
        if requirement_ids:
            disposition["downstream_refs"] = sorted(set([r for r in disposition.get("downstream_refs", []) if not r.startswith("FR-")] + requirement_ids))
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
        "## Dependencies and Clarifications", "",
        "The listed API requirements are dependencies of the supported behavior. Supporting operations outside this Feature require an explicit ownership decision before they are added.", "",
        "## Definition of Done", "",
        "The functional requirements and listed API contracts are preserved, validation behavior remains available, and each supporting operation has an explicit scope disposition.", "",
        "## Delivery Status", "",
        "Stories, Acceptance Criteria, technical tasks, and implementation require regeneration after this Feature scope is approved.", "",
    ])
    return "\n".join(lines)


def publish_feature_scope_refresh(source_root: Path, output_root: Path, feature_id: str, coverage: dict) -> dict:
    existing = json.loads((source_root / f"{feature_id}.json").read_text(encoding="utf-8"))
    contract, refreshed_coverage = build_feature_scope_contract(feature_id, existing["feature_name"], coverage)
    run_id = f"capability-scope-{datetime.now(timezone.utc).strftime('%Y-%m-%d-%H%M%S-%f')}"
    destination = output_root / "runs" / run_id
    destination.mkdir(parents=True, exist_ok=False)
    refreshed_specification = {'feature_id':feature_id,'feature_name':existing['feature_name']}
    refreshed_specification.update({
        "status": contract["status"],
        "functional_requirements": contract["functional_requirements"],
        "capability_api_contracts": contract["api_contracts"],
        "capability_dispositions": contract["capability_dispositions"],
        "downstream_status": contract["downstream_status"],
        "stories_regenerated": False,
        "acceptance_criteria_regenerated": False,
        "upstream_lineage": coverage.get("upstream_lineage", {}),
    })
    (destination / f"{feature_id}.json").write_text(json.dumps(refreshed_specification, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (destination / "capability-coverage.json").write_text(json.dumps(refreshed_coverage, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (destination / "downstream-staleness.json").write_text(json.dumps({
        "feature_id": feature_id, "status": "STALE_REGENERATION_REQUIRED",
        "stale_artifacts": ["STORIES", "ACCEPTANCE_CRITERIA", "TECHNICAL_TASKS", "ANGULAR", "PLAYWRIGHT"],
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    api_path = destination / "feature-api-contracts.json"
    api_document = json.loads((source_root / 'feature-api-contracts.json').read_text(encoding="utf-8"))
    feature_api = next(item for item in api_document["features"] if item["feature_id"] == feature_id)
    feature_api["contracts"] = contract["api_contracts"]
    api_path.write_text(json.dumps(api_document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    latest = output_root / "latest"
    latest.mkdir(parents=True,exist_ok=True)
    for artifact in destination.iterdir():
        shutil.copyfile(artifact,latest/artifact.name)
    return {"run_id": run_id, "path": destination, "contract": contract, "coverage": refreshed_coverage}
