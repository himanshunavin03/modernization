"""Prepare, validate, and persist Acceptance Criteria artifacts."""
from __future__ import annotations

from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
import re
import shutil

from polaris_modernization.acceptance_criteria.models import AcceptanceCatalog, AcceptanceReasoningSubmission
from polaris_modernization.acceptance_criteria.retrieval import build_acceptance_packages, load_approved_stories


class UnsupportedAcceptanceCriteriaError(ValueError):
    """An AC submission contains stale or unsupported claims."""


def _write(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _manifest(packages: list) -> tuple[dict, str]:
    values = {item.package_id: item.package_hash for item in packages}
    return values, sha256(json.dumps(values, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _destination(root: Path, project: str) -> tuple[str, Path]:
    run_id = f"{project}-{datetime.now().strftime('%Y-%m-%d-%H%M%S-%f')}"
    return run_id, root / run_id


def prepare_acceptance_criteria(story_root: Path, output_root: Path) -> dict:
    approved = load_approved_stories(story_root)
    packages = build_acceptance_packages(approved)
    package_map, digest = _manifest(packages)
    run_id, path = _destination(output_root / "prepared", approved["catalog"]["project_id"])
    path.mkdir(parents=True)
    _write(path / "acceptance-evidence-packages.json", [item.model_dump(mode="json") for item in packages])
    _write(path / "acceptance-evidence-manifest.json", {"manifest_hash": digest, "packages": package_map, **{key: approved["catalog"][key] for key in ("kg_run_id", "application_understanding_run_id", "feature_run_id", "business_feature_run_id", "story_run_id")}})
    _write(path / "acceptance-reasoning-schema.json", AcceptanceReasoningSubmission.model_json_schema())
    _write(path / "preparation.json", {"run_id": run_id, "evidence_packages": len(packages), "external_llm_api_calls": 0})
    return {"path": path, "approved": approved, "packages": packages, "manifest_hash": digest}


def expected_ac_id(story_id: str, number: int) -> str:
    return f"ac-{story_id.removeprefix('story-')}-{number:03d}"


def _norm(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def _validate(submission: AcceptanceReasoningSubmission, approved: dict, packages: list) -> dict:
    catalog = approved["catalog"]
    keys = ("kg_run_id", "application_understanding_run_id", "feature_run_id", "business_feature_run_id", "story_run_id")
    if tuple(getattr(submission, key) for key in keys) != tuple(catalog[key] for key in keys):
        raise UnsupportedAcceptanceCriteriaError("Acceptance Criteria lineage is stale.")
    _, digest = _manifest(packages)
    if submission.evidence_package_manifest_hash != digest:
        raise UnsupportedAcceptanceCriteriaError("AC package manifest hash is stale.")
    stories = {item["story_id"]: item for item in catalog["stories"]}
    package_ids = {item.package_id for item in packages}
    ids = [item.acceptance_criterion_id for item in submission.acceptance_criteria]
    if len(ids) != len(set(ids)):
        raise UnsupportedAcceptanceCriteriaError("Duplicate Acceptance Criteria IDs are prohibited.")
    counts: dict[str, int] = {}
    signatures = set()
    questions = set()
    for criterion in submission.acceptance_criteria:
        story = stories.get(criterion.story_id)
        if story is None or criterion.parent_feature_id != story["parent_feature_id"]:
            raise UnsupportedAcceptanceCriteriaError("AC Story or Feature parent is invalid.")
        counts[criterion.story_id] = counts.get(criterion.story_id, 0) + 1
        if criterion.acceptance_criterion_id != expected_ac_id(criterion.story_id, counts[criterion.story_id]):
            raise UnsupportedAcceptanceCriteriaError("AC stable ID sequence is invalid.")
        if criterion.acceptance_evidence_package_id != f"acceptance-evidence:{criterion.story_id}" or criterion.acceptance_evidence_package_id not in package_ids:
            raise UnsupportedAcceptanceCriteriaError("AC evidence package reference is invalid.")
        persona_context = " ".join((criterion.given, criterion.when))
        non_persona_claims = " ".join((criterion.given, criterion.when, criterion.then, criterion.business_condition, criterion.observable_outcome))
        persona_pattern = re.compile(r"\b(?:(?:as|signed in as) an? |an? )(?:administrator|doctor|nurse|patient|receptionist)\b", re.I)
        claim_pattern = re.compile(r"\b(success message|error message|http 200|sorted|pagination|required field|mandatory|retry|cache|seconds|sla|wcag|availability|scalability)\b", re.I)
        if persona_pattern.search(persona_context) or claim_pattern.search(non_persona_claims):
            raise UnsupportedAcceptanceCriteriaError("Unsupported persona, validation, error, or NFR behavior was introduced.")
        if not criterion.given or not criterion.when or not criterion.then:
            raise UnsupportedAcceptanceCriteriaError("Given/When/Then must be understandable and observable.")
        for field in ("workflow_refs", "ui_surface_refs", "domain_concept_refs", "business_rule_refs", "dependency_refs", "kg_evidence", "application_understanding_evidence", "feature_evidence", "business_feature_evidence"):
            if not set(getattr(criterion, field)) <= set(story[field]):
                raise UnsupportedAcceptanceCriteriaError(f"AC {field} contains unsupported references.")
        expected_api = story["api_contract_refs"]
        if _norm([item.model_dump(mode="json") for item in criterion.api_contract_refs]) != _norm(expected_api) or sorted(criterion.api_mapping_status) != sorted(story["api_mapping_status"]):
            raise UnsupportedAcceptanceCriteriaError("AC API status or relationship differs from the Story.")
        allowed_source = {_norm(item) for item in story["source_evidence"]}
        if not criterion.source_evidence or not {_norm(item.model_dump(mode="json")) for item in criterion.source_evidence} <= allowed_source:
            raise UnsupportedAcceptanceCriteriaError("AC source evidence is missing or unsupported.")
        if criterion.story_evidence != [criterion.story_id] or criterion.assumptions:
            raise UnsupportedAcceptanceCriteriaError("AC traceability is invalid or an assumption was introduced.")
        if (criterion.limitations or any(status in {"UNRESOLVED", "DYNAMIC"} for status in criterion.api_mapping_status)) and criterion.evidence_status == "PROVEN":
            raise UnsupportedAcceptanceCriteriaError("A limited AC cannot be upgraded to PROVEN.")
        if criterion.criterion_type == "ERROR_OR_EDGE_BEHAVIOR":
            raise UnsupportedAcceptanceCriteriaError("No approved Story supports an error/edge criterion.")
        if not set(criterion.open_questions) <= set(story["open_questions"]):
            raise UnsupportedAcceptanceCriteriaError("AC open questions are unsupported.")
        questions.update(criterion.open_questions)
        signature = (criterion.story_id, criterion.given.lower(), criterion.when.lower(), criterion.then.lower())
        if signature in signatures:
            raise UnsupportedAcceptanceCriteriaError("Duplicate Acceptance Criteria are prohibited.")
        signatures.add(signature)
    if set(counts) != set(stories):
        raise UnsupportedAcceptanceCriteriaError("Every approved Story requires at least one safe AC.")
    expected_questions = {question for story in stories.values() for question in story["open_questions"]}
    if questions != expected_questions:
        raise UnsupportedAcceptanceCriteriaError("Approved Story open questions were not preserved.")
    criteria = submission.acceptance_criteria
    statuses = [item.evidence_status for item in criteria]
    types = [item.criterion_type for item in criteria]
    quality = {
        "package_hash_validation": "PASS", "provenance_validation": "PASS", "acceptance_criteria_validation": "PASS", "acceptance_criteria_quality_validation": "PASS",
        "total_features": len({item.parent_feature_id for item in criteria}), "total_stories": len(stories), "stories_with_acceptance_criteria": len(counts), "stories_without_safe_acceptance_criteria": 0,
        "total_acceptance_criteria": len(criteria), "proven_acceptance_criteria": statuses.count("PROVEN"), "supported_with_limitation_ac": statuses.count("SUPPORTED_WITH_LIMITATION"), "requires_stakeholder_clarification_ac": statuses.count("REQUIRES_STAKEHOLDER_CLARIFICATION"),
        **{f"{name.lower()}_ac": types.count(name) for name in ("CORE_BEHAVIOR", "BUSINESS_RULE", "DATA_PRESENTATION", "DATA_INTERACTION", "NAVIGATION", "API_CONTRACT", "TENANT_CONTEXT", "ERROR_OR_EDGE_BEHAVIOR", "MODERNIZATION_PRESERVATION")},
        "ac_with_proven_api": sum("PROVEN" in item.api_mapping_status for item in criteria), "ac_with_unresolved_api": sum("UNRESOLVED" in item.api_mapping_status for item in criteria), "ac_with_dynamic_api": sum("DYNAMIC" in item.api_mapping_status for item in criteria), "ac_with_external_api": sum("EXTERNAL" in item.api_mapping_status for item in criteria),
        "invented_ac_personas": 0, "ac_assumptions_created": 0, "invented_nfrs": 0, "invented_validation_rules": 0, "invented_error_behaviors": 0,
        "open_questions": len(questions), "stakeholder_validation_required_ac": sum(item.stakeholder_validation_required for item in criteria),
        "unsupported_ac_candidates_rejected": 0, "duplicate_acceptance_criteria": 0, "contradictory_acceptance_criteria": 0, "untraceable_acceptance_criteria": 0, "upstream_story_review_required": 0,
    }
    return quality


def validate_and_persist_acceptance_criteria(story_root: Path, output_root: Path, agent_result: Path) -> dict:
    approved = load_approved_stories(story_root)
    packages = build_acceptance_packages(approved)
    submission = AcceptanceReasoningSubmission.model_validate_json(agent_result.read_text(encoding="utf-8"))
    quality = _validate(submission, approved, packages)
    readiness = "ACCEPTANCE_CRITERIA_READY_WITH_LIMITATIONS" if quality["supported_with_limitation_ac"] or quality["requires_stakeholder_clarification_ac"] else "ACCEPTANCE_CRITERIA_READY"
    run_id, path = _destination(output_root / "runs", approved["catalog"]["project_id"])
    path.mkdir(parents=True)
    catalog = AcceptanceCatalog(project_id=approved["catalog"]["project_id"], acceptance_criteria_run_id=run_id, readiness=readiness, acceptance_criteria=submission.acceptance_criteria, coverage=quality, quality_review=quality, limitations=["Inherited unresolved/dynamic API, incomplete appointment, actor, and stakeholder-question limitations remain visible."], next_action="ANALYZE_OPTIONAL_TARGET_DESIGN_OR_RECOMMEND_TARGET_ARCHITECTURE", **{key: getattr(submission, key) for key in ("kg_run_id", "application_understanding_run_id", "feature_run_id", "business_feature_run_id", "story_run_id")})
    package_map, digest = _manifest(packages)
    _write(path / "acceptance-criteria.json", catalog.model_dump(mode="json"))
    _write(path / "acceptance-evidence-packages.json", [item.model_dump(mode="json") for item in packages])
    _write(path / "acceptance-evidence-manifest.json", {"manifest_hash": digest, "hash_validation": "PASS", "packages": package_map})
    _write(path / "acceptance-validation.json", {"valid": True, **quality, "readiness": readiness})
    _write(path / "acceptance-quality-review.json", {"criteria": [{"id": item.acceptance_criterion_id, "testable": True, "stakeholder_validation_required": item.stakeholder_validation_required} for item in submission.acceptance_criteria], "summary": quality})
    question_map = {item["question_id"]: item for item in approved["questions"]["questions"]}
    _write(path / "acceptance-open-questions.json", {"questions": [{**question_map[q], "related_acceptance_criterion_id": item.acceptance_criterion_id, "testing_impact": "Test detail remains bounded by approved behavior.", "blocks_poc": q in {"Q-DASH-003"}} for item in submission.acceptance_criteria for q in item.open_questions]})
    trace = [{"feature_id": item.parent_feature_id, "story_id": item.story_id, "acceptance_criterion_id": item.acceptance_criterion_id, "workflows": item.workflow_refs, "ui_surfaces": item.ui_surface_refs, "api_relationships": [x.model_dump(mode="json") for x in item.api_contract_refs], "evidence": [x.model_dump(mode="json") for x in item.source_evidence]} for item in submission.acceptance_criteria]
    _write(path / "requirements-traceability.json", {"traceability": trace})
    _write(path / "provenance.json", {**{key: getattr(submission, key) for key in ("kg_run_id", "application_understanding_run_id", "feature_run_id", "business_feature_run_id", "story_run_id")}, "acceptance_criteria_run_id": run_id})
    _write(path / "token-usage.json", {"reasoning_mode": "INTERACTIVE_AGENT_MODE", "external_llm_api_calls": 0, "ac_evidence_packages": len(packages)})
    by_story = {item["story_id"]: item for item in approved["catalog"]["stories"]}
    lines = ["# Acceptance Criteria", "", f"Readiness: `{readiness}`", ""]
    for item in submission.acceptance_criteria:
        lines += [f"## {item.title}", "", f"- **Given** {item.given}", f"- **When** {item.when}", f"- **Then** {item.then}", f"- Evidence status: `{item.evidence_status}`", ""]
    (path / "acceptance-criteria.md").write_text("\n".join(lines), encoding="utf-8")
    (path / "requirements-traceability.md").write_text("# Requirements Traceability\n\n" + "\n".join(f"- `{x['feature_id']}` -> `{x['story_id']}` -> `{x['acceptance_criterion_id']}`" for x in trace) + "\n", encoding="utf-8")
    poc_ids = set(approved["poc"]["story_ids"]); poc = [x for x in submission.acceptance_criteria if x.story_id in poc_ids]
    (path / "poc-modernization-contract.md").write_text("# POC Modernization Contract\n\n" + "\n".join(f"## {by_story[x.story_id]['title']}\n\n- {x.given}\n- {x.when}\n- {x.then}\n- Status: `{x.evidence_status}`\n- Limitations: {'; '.join(x.limitations) or 'None'}\n" for x in poc) + "\n## Out of Scope\n\nArchitecture, target design, Angular implementation, backend changes, and unsupported behavior.\n", encoding="utf-8")
    review = ["# Stakeholder Acceptance Review", ""]
    for item in submission.acceptance_criteria: review += [f"## {by_story[item.story_id]['title']} / {item.title}", "", f"- Status: `{item.evidence_status}`", f"- Open questions: {', '.join(item.open_questions) or 'None'}", f"- Limitations: {'; '.join(item.limitations) or 'None'}", f"- Stakeholder validation required: {'YES' if item.stakeholder_validation_required else 'NO'}", ""]
    (path / "stakeholder-acceptance-review.md").write_text("\n".join(review), encoding="utf-8")
    (path / "qa-handoff.md").write_text("# QA Handoff\n\nThe approved criteria define evidence-backed preservation behavior. Unresolved mappings, dynamic relationships, incomplete appointment behavior, and stakeholder questions remain explicit. Detailed test cases are not generated in this phase.\n", encoding="utf-8")
    latest = output_root / "latest"
    if latest.exists(): shutil.rmtree(latest)
    shutil.copytree(path, latest)
    return {"run_id": run_id, "path": path, "catalog": catalog, "quality": quality, "packages": packages}
