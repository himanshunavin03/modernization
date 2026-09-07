"""Feature-scoped Story and Acceptance Criteria generation from approved contracts."""

from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
import shutil


class FeatureLineageError(ValueError):
    """A feature-scoped artifact is not current enough for downstream use."""


def _read(path: Path) -> dict:
    if not path.is_file():
        raise FeatureLineageError(f"Required feature artifact is missing: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M%S-%f")


def resolve_approved_feature(repository_root: Path, feature: dict) -> dict:
    """Resolve a current feature contract and its immutable scope-refresh run."""
    root = repository_root.resolve()
    contract_path = root / feature["spec_path"]
    contract = _read(contract_path)
    if contract.get("feature_id") != feature["feature_id"] or not str(contract.get("status", "")).startswith("FEATURE_SCOPE_READY"):
        raise FeatureLineageError("Feature contract is not approved and current for targeted generation.")
    runs = root / "artifacts" / "feature-specifications" / "runs"
    digest = contract.get('generation_lineage',{}).get('feature_contract_hash') or sha256(contract_path.read_bytes()).hexdigest()
    candidates = []
    for candidate in runs.glob("capability-scope-*"):
        saved = candidate / contract_path.name
        if saved.is_file() and sha256(saved.read_bytes()).hexdigest() == digest:
            frozen_scope=_read(saved)
            if any(frozen_scope.get(key)!=contract.get(key) for key in ('functional_requirements','capability_api_contracts','upstream_lineage')):
                raise FeatureLineageError('Consolidated Feature differs from its immutable scope contract.')
            candidates.append(candidate)
    if not candidates:
        raise FeatureLineageError("Feature contract has no matching immutable scope-refresh run.")
    scope_run = sorted(candidates)[-1]
    kg = _read(root / "artifacts" / "knowledge-graph" / "latest" / "review-metadata.json")
    if not kg.get("run_id") or not kg.get("validation", {}).get("valid"):
        raise FeatureLineageError("Canonical Knowledge Graph is not validated.")
    if contract.get('upstream_lineage',{}).get('kg_run_id',kg['run_id'])!=kg['run_id']:
        raise FeatureLineageError('Feature was generated from a different canonical Knowledge Graph.')
    return {
        "feature": feature,
        "contract": contract,
        "contract_path": contract_path,
        "feature_run": scope_run.name,
        "feature_contract_hash": digest,
        "canonical_kg_run": kg["run_id"],
        "coverage": _read(contract_path.parent / "capability-coverage.json"),
    }


def _api_by_requirement(contract: dict) -> dict[str, list[dict]]:
    result: dict[str, list[dict]] = {}
    for item in contract.get("capability_api_contracts", []):
        for requirement_id in item.get("requirement_ids", []):
            result.setdefault(requirement_id, []).append({
                "contract_id": item["contract_id"], "method": item["method"], "route": item["route"],
            })
    return result


def _capabilities_by_requirement(contract: dict, coverage: dict) -> dict[str, list[dict]]:
    capabilities = {item["capability_id"]: item for item in coverage.get("capabilities", [])}
    result: dict[str, list[dict]] = {}
    for disposition in contract.get("capability_dispositions", []):
        if disposition.get("scope_status") != "INCLUDED":
            continue
        for reference in disposition.get("downstream_refs", []):
            if reference.startswith("FR-") and disposition["capability_id"] in capabilities:
                result.setdefault(reference, []).append(capabilities[disposition["capability_id"]])
    return result


def _qualifier_text(qualifiers: list[str]) -> str:
    phrases = {
        "BULK": "the approved bulk operation behavior",
        "FIXED_ORDER": "the approved fixed ordering",
        "TENANT_SCOPED": "the approved tenant context",
    }
    values = [phrases[item] for item in qualifiers if item in phrases]
    return f" This behavior also preserves {', '.join(values)}." if values else ""


def _story_for_requirement(feature: dict, requirement: dict, apis: list[dict], capabilities: list[dict]) -> dict:
    title = requirement["title"]
    story_id = f"story-{feature['slug']}-{requirement['id'].lower()}-{_slug(title)}"
    qualifiers = sorted({qualifier for capability in capabilities for qualifier in capability.get("qualifiers", [])})
    system_initiated = bool(requirement.get("system_initiated"))
    actions = [item for item in requirement.get("interaction_semantics", []) if item.get("interaction_type") == "ACTION" and item.get("label")]
    interaction_goal = f'select "{actions[0]["label"]}"' if actions else title.casefold()
    effects = list(dict.fromkeys(item['observable_result'] for item in requirement.get('interaction_semantics',[]) if item.get('observable_result') and item.get('effect_kind') not in {'ACTION_VISIBILITY','VALIDATION_GATE','MEDIA_RENDER','FIXED_ORDER','RENDER'}))
    effect_kinds={s.get('effect_kind') for s in requirement.get('interaction_semantics',[])}
    if effect_kinds=={'VALIDATION'}:
        interaction_goal='complete the '+title.removeprefix('Validate ').lower()+' input'
        effects=['missing required input is identified before the form can be submitted']
    if 'MEDIA_BINDING' in effect_kinds:
        interaction_goal='select a profile file'
    outcome = '; '.join(effects)
    statement = (
        f"The system performs {title.casefold()}: {outcome}."
        if system_initiated else
        f"As an application user, I want to {interaction_goal}" + (f", so that {outcome}." if outcome else ".")
    )
    return {
        "story_id": story_id,
        "title": title,
        "parent_feature_id": feature["feature_id"],
        "functional_requirement_ids": [requirement["id"]],
        "story_statement": statement,
        "business_outcome": requirement["description"].rstrip(".") + "." + _qualifier_text(qualifiers),
        "interaction_semantics": requirement.get("interaction_semantics", []),
        "interaction_id": requirement.get("interaction_id"),
        "goal": interaction_goal,
        "observable_outcomes": effects,
        "system_initiated": system_initiated,
        "api_contracts": apis,
        "source_capability_ids": requirement.get("source_capability_ids", []),
        "capability_qualifiers": qualifiers,
        "status": "CURRENT",
    }


def _validate_stories(context: dict, stories: list[dict]) -> dict:
    requirements = {item["id"] for item in context["contract"].get("functional_requirements", [])}
    supported_api = {(item["method"], item["route"]) for item in context["contract"].get("capability_api_contracts", [])}
    mapped = [item for story in stories for item in story["functional_requirement_ids"]]
    duplicate_ids = len({item["story_id"] for item in stories}) != len(stories)
    unsupported_api = [api for story in stories for api in story["api_contracts"] if (api["method"], api["route"]) not in supported_api]
    invalid = [story["story_id"] for story in stories if not story["story_statement"] or not story["business_outcome"]]
    orphan=sorted(set(mapped)-requirements)
    return {
        "valid": not (set(requirements) - set(mapped) or duplicate_ids or unsupported_api or invalid or orphan),
        "total_approved_frs": len(requirements), "fr_with_story_coverage": len(set(mapped)),
        "fr_without_story_coverage": sorted(requirements - set(mapped)), "orphan_stories": len(orphan),
        "duplicate_stories": int(duplicate_ids), "unsupported_story_behavior": len(unsupported_api) + len(invalid),
        "jira_story_quality": "PASS" if not invalid and not duplicate_ids else "FAIL",
    }


def generate_targeted_stories(context: dict, output_root: Path) -> dict:
    contract = context["contract"]
    api_by_requirement = _api_by_requirement(contract)
    capabilities_by_requirement = _capabilities_by_requirement(contract, context["coverage"])
    stories = [
        _story_for_requirement(context["feature"], requirement, api_by_requirement.get(requirement["id"], []), capabilities_by_requirement.get(requirement["id"], []))
        for requirement in contract.get("functional_requirements", [])
    ]
    validation = _validate_stories(context, stories)
    if not validation["valid"]:
        raise FeatureLineageError(f"Targeted Story validation failed: {validation}")
    run_id = f"{context['feature']['feature_id']}-{_stamp()}"
    destination = output_root / "features" / context["feature"]["feature_id"] / "runs" / run_id
    destination.mkdir(parents=True, exist_ok=False)
    lineage = {
        **contract.get('upstream_lineage',{}),
        "feature_id": context["feature"]["feature_id"], "feature_run": context["feature_run"],
        "feature_contract": str(context["contract_path"].relative_to(context["contract_path"].parents[3])),
        "feature_contract_hash": context["feature_contract_hash"], "canonical_upstream_kg_run": context["canonical_kg_run"],
        "story_run": run_id,
    }
    _write(destination / "story-catalog.json", {"lineage": lineage, "readiness": "STORIES_READY", "stories": stories, "validation": validation})
    _write(destination / "story-lineage.json", lineage)
    _write(destination / "story-validation.json", validation)
    _write(destination / "downstream-status.json", {"stories": "CURRENT", "acceptance_criteria": "STALE_REGENERATION_REQUIRED", "technical_tasks": "STALE_REGENERATION_REQUIRED", "angular": "STALE_REGENERATION_REQUIRED", "playwright": "STALE_REGENERATION_REQUIRED"})
    latest = destination.parents[1] / "latest"
    if latest.exists():
        shutil.rmtree(latest)
    shutil.copytree(destination, latest)
    return {"run_id": run_id, "path": destination, "stories": stories, "validation": validation, "lineage": lineage}


def _validate_acceptance(context: dict, story_catalog: dict, criteria: list[dict]) -> dict:
    stories = {item["story_id"] for item in story_catalog["stories"]}
    covered = {item["story_id"] for item in criteria}
    orphan = [item["acceptance_criterion_id"] for item in criteria if item["story_id"] not in stories]
    placeholders = [item["acceptance_criterion_id"] for item in criteria if item["given"].casefold() in {"the approved feature behavior is available", "the feature is available"}]
    non_observable = [item["acceptance_criterion_id"] for item in criteria if not item.get("then") or item["then"] == "NOT_PROVEN"]
    tautological = [item["acceptance_criterion_id"] for item in criteria if item["when"].casefold().removeprefix("the user performs ") == item["title"].casefold().removesuffix(" behavior")]
    forbidden=('interaction responds','behavior is available','supported behavior occurs','requirement is satisfied','not_proven','supported interaction')
    generic=[item['acceptance_criterion_id'] for item in criteria if any(term in item['then'].lower() for term in forbidden)]
    allowed={s['story_id']:{(v.get('interaction_id'),v.get('effect_id'),v.get('observable_result')) for v in s.get('interaction_semantics',[])} for s in story_catalog['stories']}
    unsupported=[c['acceptance_criterion_id'] for c in criteria if (c.get('interaction_id'),c.get('effect_id'),c['then']) not in allowed.get(c['story_id'],set())]
    duplicates=len(criteria)-len({c['acceptance_criterion_id'] for c in criteria})
    return {
        "valid": not (stories - covered or orphan or placeholders or non_observable or tautological or generic or unsupported or duplicates), "stories_without_ac": sorted(stories - covered),
        "orphan_ac": orphan, "placeholder_precondition": placeholders, "non_observable_outcome": non_observable,
        "tautological_ac": tautological, "ac_testability_quality": "PASS" if not (orphan or placeholders or non_observable or tautological) else "FAIL",
        "unsupported_ac_behavior":unsupported,"generic_interaction_outcome":generic,"duplicate_ac":duplicates,
    }


def generate_targeted_acceptance_criteria(context: dict, story_root: Path, output_root: Path) -> dict:
    story_catalog = _read(story_root / "story-catalog.json")
    lineage = story_catalog.get("lineage", {})
    if lineage.get("feature_id") != context["feature"]["feature_id"] or lineage.get("feature_run") != context["feature_run"] or lineage.get("feature_contract_hash") != context["feature_contract_hash"]:
        raise FeatureLineageError("Targeted Stories are stale for the approved Feature contract.")
    criteria = []
    for story in story_catalog["stories"]:
        semantics = story.get('interaction_semantics', [])
        outcomes = []
        seen=set()
        for semantic in semantics:
            result=semantic.get('observable_result')
            if not result or semantic.get('unresolved_reason'):
                continue
            identity=semantic.get('interaction_id')
            if story.get('interaction_id') and identity!=story['interaction_id']:
                raise FeatureLineageError('An effect belongs to a different interaction.')
            key=(identity,semantic.get('effect_kind'),result,semantic.get('system_event'),semantic.get('condition'))
            if key in seen:continue
            seen.add(key)
            given=semantic.get('context') or 'the related view is displayed'
            if semantic.get('condition') and semantic.get('effect_kind')=='ACTION_VISIBILITY':
                from polaris_modernization.application_understanding.interactions import words
                condition=semantic['condition'];given=semantic.get('condition_description') or f"{words(condition.lstrip('!'))} is {'inactive' if condition.startswith('!') else 'active'}"
                when='the view evaluates which actions to display'
            elif semantic.get('system_event'):
                label=semantic.get('label')
                given += f' after the user selects "{label}"' if label and not semantic.get('system_initiated') and semantic.get('effect_kind')!='VALIDATION_GATE' else ''
                when=semantic['system_event']
            elif semantic.get('label') and not semantic.get('system_initiated'):
                when=f'the user selects "{semantic["label"]}"'
            else:
                when=semantic.get('trigger') or 'the related view opens'
                if not semantic.get('system_initiated') and semantic.get('interaction_type')=='ACTION' and '(' in when:
                    kinds={s.get('effect_kind') for s in semantics}
                    when="the user selects the record's delete control" if 'CONFIRMATION' in kinds else "the user selects the record's detail control" if 'NAVIGATION' in kinds else 'the user activates the specified record control'
            if any(s.get('effect_kind')=='CONFIRMATION' for s in semantics) and semantic.get('effect_kind') in {'COLLECTION_REMOVE','NAVIGATION'}:
                given += ' and the user has confirmed the action'
            if semantic.get('effect_kind') in {'MEDIA_BINDING','MEDIA_RENDER'}:
                when='the selected file finishes reading' if semantic['effect_kind']=='MEDIA_BINDING' else 'the profile file value changes'
            outcomes.append((given,when,result,semantic))
        # Legacy contracts can attach one outcome directly to their action. They
        # are accepted above, without matching unrelated null handler identities.
        if not outcomes:
            raise FeatureLineageError(f"Story {story['story_id']} has no observable interaction-owned outcome.")
        for number,(given,when,then,semantic) in enumerate(outcomes,1):
          criteria.append({
            "acceptance_criterion_id": f"ac-{story['story_id'].removeprefix('story-')}-{number:03d}",
            "story_id": story["story_id"], "functional_requirement_ids": story["functional_requirement_ids"],
            "title": f"{story['title']} behavior", "given": given, "when": when, "then": then,
            "api_contracts": story["api_contracts"], "source_capability_ids": story["source_capability_ids"],
            "capability_qualifiers": story["capability_qualifiers"], "testable": True,
            "interaction_id":semantic.get('interaction_id'), "handler_id":semantic.get('handler_id'),
            "effect_id":semantic.get('effect_id'), "effect_kind":semantic.get('effect_kind'),
            "lineage_node_ids":semantic.get('lineage_node_ids',[]),
          })
    validation = _validate_acceptance(context, story_catalog, criteria)
    if not validation["valid"]:
        raise FeatureLineageError(f"Targeted Acceptance Criteria validation failed: {validation}")
    run_id = f"{context['feature']['feature_id']}-{_stamp()}"
    destination = output_root / "features" / context["feature"]["feature_id"] / "runs" / run_id
    destination.mkdir(parents=True, exist_ok=False)
    ac_lineage = {**lineage, "acceptance_criteria_run": run_id}
    _write(destination / "acceptance-criteria.json", {"lineage": ac_lineage, "readiness": "ACCEPTANCE_CRITERIA_READY", "acceptance_criteria": criteria, "validation": validation})
    _write(destination / "acceptance-lineage.json", ac_lineage)
    _write(destination / "acceptance-validation.json", validation)
    _write(destination / "downstream-status.json", {"stories": "CURRENT", "acceptance_criteria": "CURRENT", "technical_tasks": "STALE_REGENERATION_REQUIRED", "angular": "STALE_REGENERATION_REQUIRED", "playwright": "STALE_REGENERATION_REQUIRED"})
    latest = destination.parents[1] / "latest"
    if latest.exists():
        shutil.rmtree(latest)
    shutil.copytree(destination, latest)
    return {"run_id": run_id, "path": destination, "criteria": criteria, "validation": validation, "lineage": ac_lineage}
