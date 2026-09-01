"""Prepare, validate, and persist evidence-backed Jira-style Stories."""
from __future__ import annotations

from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
import re
import shutil

from polaris_modernization.stories.models import StoryCatalog, StoryReasoningSubmission
from polaris_modernization.stories.retrieval import build_story_packages, load_approved_business_features, stable_slug


class UnsupportedStoryClaimsError(ValueError):
    """A Story submission is stale, unsafe, or unsupported by approved evidence."""


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _run_path(root: Path, project_id: str) -> tuple[str, Path]:
    stamp = datetime.now().strftime("%Y-%m-%d-%H%M%S-%f")
    run_id = f"{project_id}-{stamp}"
    return run_id, root / run_id


def _manifest(packages: list) -> tuple[dict[str, str], str]:
    package_map = {item.package_id: item.package_hash for item in packages}
    encoded = json.dumps(package_map, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return package_map, sha256(encoded).hexdigest()


def prepare_story_generation(business_feature_root: Path, output_root: Path) -> dict:
    approved = load_approved_business_features(business_feature_root)
    packages = build_story_packages(approved)
    package_map, manifest_hash = _manifest(packages)
    run_id, destination = _run_path(output_root / "prepared", approved["catalog"]["project_id"])
    destination.mkdir(parents=True, exist_ok=False)
    _write_json(destination / "story-evidence-packages.json", [item.model_dump(mode="json") for item in packages])
    _write_json(destination / "story-evidence-manifest.json", {
        "kg_run_id": approved["catalog"]["kg_run_id"],
        "application_understanding_run_id": approved["catalog"]["application_understanding_run_id"],
        "feature_run_id": approved["catalog"]["feature_run_id"],
        "business_feature_run_id": approved["run_id"], "manifest_hash": manifest_hash, "packages": package_map,
    })
    _write_json(destination / "story-reasoning-schema.json", StoryReasoningSubmission.model_json_schema())
    _write_json(destination / "preparation.json", {"run_id": run_id, "reasoning_mode": "INTERACTIVE_AGENT_MODE", "external_llm_api_calls": 0, "story_evidence_packages": len(packages)})
    (destination / "agent-instructions.md").write_text(
        "# Active-agent Story reasoning\n\nCreate exactly one business Story for each workflow-boundary package. "
        "Use only the package facts and the neutral actor `user of the existing application`. Preserve inferred value, API status, questions, and limitations. "
        "Do not produce technical tasks, assumptions, Acceptance Criteria, Given/When/Then, Story Points, architecture, or code.\n",
        encoding="utf-8",
    )
    return {"path": destination, "approved": approved, "packages": packages, "manifest_hash": manifest_hash}


def expected_story_id(parent_feature_id: str, title: str) -> str:
    feature = parent_feature_id.removeprefix("feature-")
    return f"story-{feature}-{stable_slug(title)}"


def _norm(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def _validate_submission(submission: StoryReasoningSubmission, approved: dict, packages: list) -> dict:
    catalog = approved["catalog"]
    lineage = (submission.kg_run_id, submission.application_understanding_run_id, submission.feature_run_id, submission.business_feature_run_id)
    expected_lineage = (catalog["kg_run_id"], catalog["application_understanding_run_id"], catalog["feature_run_id"], approved["run_id"])
    if lineage != expected_lineage:
        raise UnsupportedStoryClaimsError("Story submission has stale upstream lineage.")
    package_map, manifest_hash = _manifest(packages)
    if submission.evidence_package_manifest_hash != manifest_hash:
        raise UnsupportedStoryClaimsError("Story evidence package manifest hash is stale.")
    by_package = {item.package_id: item for item in packages}
    feature_map = {item["feature_id"]: item for item in catalog["business_features"]}
    if len(submission.stories) != len(packages) or {item.story_evidence_package_id for item in submission.stories} != set(package_map):
        raise UnsupportedStoryClaimsError("Every approved Story boundary must produce exactly one traceable Story.")
    story_ids = [item.story_id for item in submission.stories]
    if len(story_ids) != len(set(story_ids)):
        raise UnsupportedStoryClaimsError("Duplicate Story IDs are not allowed.")
    title_keys = [stable_slug(item.title) for item in submission.stories]
    if len(title_keys) != len(set(title_keys)):
        raise UnsupportedStoryClaimsError("Duplicate Story semantics are not allowed.")
    forbidden_titles = re.compile(r"\b(controller|endpoint|dto|angular|razor|component|service|refactor|migrate|convert)\b", re.I)
    all_question_ids: set[str] = set()
    stories_with_questions = 0
    low_confidence = 0
    for story in submission.stories:
        package = by_package[story.story_evidence_package_id]
        feature = feature_map.get(story.parent_feature_id)
        if feature is None or story.parent_feature_name != feature["feature_name"] or package.parent_feature_id != story.parent_feature_id:
            raise UnsupportedStoryClaimsError("Story parent Feature identity is invalid.")
        if story.story_id != expected_story_id(story.parent_feature_id, story.title) or story.story_key_candidate != story.story_id.upper().replace("-", "_"):
            raise UnsupportedStoryClaimsError("Story stable ID or Jira key candidate is invalid.")
        if forbidden_titles.search(story.title):
            raise UnsupportedStoryClaimsError("Technical-artifact Story candidates cannot be accepted.")
        if story.actor != "user of the existing application" or story.actor_confidence.level != "LOW":
            raise UnsupportedStoryClaimsError("Story actor is not evidence-safe; invented personas are prohibited.")
        if not story.story_statement.startswith("As a user of the existing application,") or "I want " not in story.story_statement or "so that " not in story.story_statement:
            raise UnsupportedStoryClaimsError("Story statement is not the required evidence-safe Jira formulation.")
        if story.business_capability not in package.business_capabilities:
            raise UnsupportedStoryClaimsError("Story references an unsupported business capability.")
        expected_workflows = [item["name"] for item in package.workflows]
        if story.workflow_refs != expected_workflows or story.workflow_boundary != package.boundary or story.workflow_boundary_rationale != package.boundary_rationale:
            raise UnsupportedStoryClaimsError("Story workflow boundary is not the approved decomposition boundary.")
        if not set(story.ui_surface_refs) <= set(package.ui_surfaces):
            raise UnsupportedStoryClaimsError("Story references unsupported UI surfaces.")
        if not set(story.domain_concept_refs) <= set(package.domain_concepts):
            raise UnsupportedStoryClaimsError("Story references unsupported domain concepts.")
        expected_rules = set(package.business_rules) or {"NO_EVIDENCE_BACKED_BUSINESS_RULE"}
        if set(story.business_rule_refs) != expected_rules:
            raise UnsupportedStoryClaimsError("Story business-rule references are unsupported.")
        if not set(story.dependency_refs) <= set(package.dependencies):
            raise UnsupportedStoryClaimsError("Story dependency references are unsupported.")
        expected_api = [item.model_dump(mode="json") for item in package.api_relationships]
        actual_api = [item.model_dump(mode="json") for item in story.api_contract_refs]
        if _norm(actual_api) != _norm(expected_api):
            raise UnsupportedStoryClaimsError("Story API references or statuses differ from approved evidence.")
        expected_statuses = sorted({item["status"] for item in expected_api})
        if sorted(story.api_mapping_status) != expected_statuses:
            raise UnsupportedStoryClaimsError("Story API mapping status was upgraded or lost.")
        allowed_evidence = {_norm(item.model_dump(mode="json")) for item in package.source_evidence}
        if not story.source_evidence or not {_norm(item.model_dump(mode="json")) for item in story.source_evidence} <= allowed_evidence:
            raise UnsupportedStoryClaimsError("Story source evidence is missing or unsupported.")
        if not set(story.kg_evidence) <= set(package.kg_evidence):
            raise UnsupportedStoryClaimsError("Story KG evidence is unsupported.")
        allowed_nodes = {item.node_id for item in package.source_evidence}
        if not story.application_understanding_evidence or not set(story.application_understanding_evidence) <= allowed_nodes:
            raise UnsupportedStoryClaimsError("Story Application Understanding evidence is unsupported.")
        if story.feature_evidence != [story.parent_feature_id] or story.business_feature_evidence != [package.business_feature_evidence]:
            raise UnsupportedStoryClaimsError("Story Feature or Business Feature traceability is invalid.")
        inherited_values = {item["text"]: item["classification"] for item in package.business_value}
        if inherited_values.get(story.business_value) != story.business_value_status:
            raise UnsupportedStoryClaimsError("Story business value or inferred-value status is unsupported.")
        if story.assumptions:
            raise UnsupportedStoryClaimsError("Story generation introduced assumptions without approved evidence.")
        allowed_questions = {item["question_id"] for item in package.open_questions}
        if not set(story.open_questions) <= allowed_questions:
            raise UnsupportedStoryClaimsError("Story open-question references are unsupported.")
        all_question_ids.update(story.open_questions)
        stories_with_questions += bool(story.open_questions)
        low_confidence += story.confidence.level == "LOW"
        if story.current_state_behavior.classification != "PROVEN" or story.modernization_relevance.classification != "MODERNIZATION_CONCERN":
            raise UnsupportedStoryClaimsError("Current-state and modernization claims are not clearly separated.")
        for statement in (story.current_state_behavior, story.modernization_relevance):
            if not statement.evidence or not {_norm(item.model_dump(mode="json")) for item in statement.evidence} <= allowed_evidence:
                raise UnsupportedStoryClaimsError("Story statement evidence is unsupported.")
        serialized = _norm(story.model_dump(mode="json"))
        if re.search(r"acceptance[_ -]?criteria|given\s+.+\s+when\s+.+\s+then", serialized, re.I):
            raise UnsupportedStoryClaimsError("Acceptance Criteria content is prohibited in Story generation.")
        if story.story_points != "UNESTIMATED":
            raise UnsupportedStoryClaimsError("Story Points must remain UNESTIMATED.")
    expected_questions = {item["question_id"] for feature in feature_map.values() for item in feature["open_questions"]}
    if all_question_ids != expected_questions:
        raise UnsupportedStoryClaimsError("Approved open questions were not fully preserved across Stories.")
    poc_feature_id = approved["poc_feature_id"]
    poc_ids = set(submission.poc_story_ids)
    if not poc_ids or not poc_ids <= set(story_ids) or any(item.parent_feature_id != poc_feature_id for item in submission.stories if item.story_id in poc_ids):
        raise UnsupportedStoryClaimsError("POC Story selection is invalid.")
    parent_ids = {item.parent_feature_id for item in submission.stories}
    workflow_count = sum(len(item.workflow_refs) for item in submission.stories)
    api_statuses = [status for item in submission.stories for status in item.api_mapping_status]
    priorities = [item.story_priority for item in submission.stories]
    return {
        "package_hash_validation": "PASS", "provenance_validation": "PASS", "story_validation": "PASS", "story_quality_validation": "PASS",
        "total_business_features": len(feature_map), "business_features_with_stories": len(parent_ids), "business_features_without_stories": len(feature_map) - len(parent_ids),
        "total_stories": len(submission.stories), "high_priority_stories": priorities.count("HIGH"), "medium_priority_stories": priorities.count("MEDIUM"), "low_priority_stories": priorities.count("LOW"),
        "capabilities_represented": len({item.business_capability for item in submission.stories}), "workflows_covered": workflow_count, "workflows_intentionally_uncovered": 0,
        "stories_with_proven_api": sum("PROVEN" in item.api_mapping_status for item in submission.stories),
        "stories_with_unresolved_api": sum("UNRESOLVED" in item.api_mapping_status for item in submission.stories),
        "stories_with_dynamic_api": sum("DYNAMIC" in item.api_mapping_status for item in submission.stories),
        "stories_with_external_api": sum("EXTERNAL" in item.api_mapping_status for item in submission.stories),
        "stories_with_open_questions": stories_with_questions, "low_confidence_stories": low_confidence,
        "actor_mode": "EVIDENCE_SAFE_GENERIC_APPLICATION_USER", "invented_personas": 0, "story_assumptions_created": 0,
        "inferred_business_value_stories": sum(item.business_value_status == "INFERRED_BUSINESS_VALUE" for item in submission.stories),
        "duplicate_stories": 0, "technical_story_candidates_rejected": 0, "unsupported_story_claims_rejected": 0, "untraceable_stories": 0,
        "poc_stories_selected": len(poc_ids),
    }


def _story_markdown(story) -> list[str]:
    return [
        f"### {story.title}", "", story.story_statement, "", f"**Story ID:** `{story.story_id}`  ",
        f"**Priority:** `{story.story_priority}`  ", f"**Confidence:** `{story.confidence.level}`  ",
        f"**Business value:** `{story.business_value_status}` - {story.business_value}", "",
        story.description, "", f"**Current state:** {story.current_state_behavior.text}", "",
        f"**Modernization relevance:** {story.modernization_relevance.text}", "",
        f"**Workflows:** {', '.join(story.workflow_refs)}", "",
        f"**Open questions:** {', '.join(story.open_questions) or 'None'}", "",
        f"**Limitations:** {'; '.join(story.limitations) or 'None beyond approved evidence'}", "",
    ]


def validate_and_persist_stories(business_feature_root: Path, output_root: Path, agent_result: Path) -> dict:
    approved = load_approved_business_features(business_feature_root)
    packages = build_story_packages(approved)
    submission = StoryReasoningSubmission.model_validate_json(agent_result.read_text(encoding="utf-8"))
    quality = _validate_submission(submission, approved, packages)
    readiness = "STORIES_READY_WITH_LIMITATIONS" if any(item.limitations or item.open_questions for item in submission.stories) else "STORIES_READY"
    project_id = approved["catalog"]["project_id"]
    run_id, destination = _run_path(output_root / "runs", project_id)
    destination.mkdir(parents=True, exist_ok=False)
    catalog = StoryCatalog(
        project_id=project_id, kg_run_id=submission.kg_run_id, application_understanding_run_id=submission.application_understanding_run_id,
        feature_run_id=submission.feature_run_id, business_feature_run_id=submission.business_feature_run_id, story_run_id=run_id,
        readiness=readiness, stories=submission.stories, poc_story_ids=submission.poc_story_ids,
        coverage={key: value for key, value in quality.items() if key.startswith(("total_", "business_features_", "capabilities_", "workflows_", "stories_with_", "low_confidence"))},
        quality_review=quality, limitations=["Inherited unresolved/dynamic API mappings, incomplete appointment evidence, and actor uncertainty remain visible."],
        next_action="GENERATE_ACCEPTANCE_CRITERIA",
    )
    package_map, manifest_hash = _manifest(packages)
    _write_json(destination / "story-catalog.json", catalog.model_dump(mode="json"))
    _write_json(destination / "story-evidence-packages.json", [item.model_dump(mode="json") for item in packages])
    _write_json(destination / "story-evidence-manifest.json", {
        "kg_run_id": submission.kg_run_id, "application_understanding_run_id": submission.application_understanding_run_id,
        "feature_run_id": submission.feature_run_id, "business_feature_run_id": submission.business_feature_run_id,
        "manifest_hash": manifest_hash, "hash_validation": "PASS", "packages": package_map,
    })
    _write_json(destination / "story-validation.json", {"valid": True, **quality, "readiness": readiness, "acceptance_criteria_generated": False, "story_points": "UNESTIMATED"})
    _write_json(destination / "story-quality-review.json", {"stories": [{"story_id": item.story_id, "invest_assessment": item.invest_assessment.model_dump(mode="json"), "stakeholder_validation_required": bool(item.open_questions or item.limitations or item.business_value_status == "INFERRED_BUSINESS_VALUE")} for item in submission.stories], "summary": quality})
    questions = []
    feature_map = {item["feature_id"]: item for item in approved["catalog"]["business_features"]}
    for story in submission.stories:
        source_questions = {item["question_id"]: item for item in feature_map[story.parent_feature_id]["open_questions"]}
        for question_id in story.open_questions:
            question = source_questions[question_id]
            questions.append({"question_id": question_id, "parent_feature_id": story.parent_feature_id, "related_story_id": story.story_id, "question": question["question"], "why_clarification_is_needed": question["reason"], "evidence": question["evidence"], "impact_if_unresolved": "Story refinement remains limited to approved current-state evidence.", "stakeholder_role_required": "UNKNOWN"})
    _write_json(destination / "story-open-questions.json", {"questions": questions})
    poc_stories = [item for item in submission.stories if item.story_id in set(submission.poc_story_ids)]
    _write_json(destination / "poc-story-selection.json", {"feature_id": approved["poc_feature_id"], "story_ids": submission.poc_story_ids, "stories": [{"story_id": item.story_id, "title": item.title, "rationale": item.poc_relevance, "workflows": item.workflow_refs, "ui_surfaces": item.ui_surface_refs, "api_statuses": item.api_mapping_status, "limitations": item.limitations} for item in poc_stories]})
    _write_json(destination / "provenance.json", {"kg_run_id": submission.kg_run_id, "application_understanding_run_id": submission.application_understanding_run_id, "feature_run_id": submission.feature_run_id, "business_feature_run_id": submission.business_feature_run_id, "story_run_id": run_id})
    _write_json(destination / "token-usage.json", {"reasoning_mode": "INTERACTIVE_AGENT_MODE", "external_llm_api_calls": 0, "story_evidence_packages": len(packages)})
    lines = ["# Jira-Style User Story Catalog", "", f"Readiness: `{readiness}`", "", "Acceptance Criteria are intentionally excluded from this stage.", ""]
    for feature in approved["catalog"]["business_features"]:
        lines.extend([f"## {feature['feature_name']}", "", feature["short_business_summary"], ""])
        for story in [item for item in submission.stories if item.parent_feature_id == feature["feature_id"]]:
            lines.extend(_story_markdown(story))
    (destination / "story-catalog.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    review = ["# Stakeholder Story Review", "", "All proposed actors use the evidence-safe generic application-user formulation. Values marked inferred require stakeholder validation.", ""]
    for story in submission.stories:
        review.extend([f"## {story.title}", "", story.story_statement, "", f"- Parent Feature: {story.parent_feature_name}", f"- Confidence: {story.confidence.level}", f"- Value status: {story.business_value_status}", f"- Open questions: {', '.join(story.open_questions) or 'None'}", f"- Limitations: {'; '.join(story.limitations) or 'None'}", f"- Stakeholder validation required: {'YES' if story.open_questions or story.limitations or story.business_value_status == 'INFERRED_BUSINESS_VALUE' else 'NO'}", ""])
    (destination / "stakeholder-story-review.md").write_text("\n".join(review) + "\n", encoding="utf-8")
    latest = output_root / "latest"
    if latest.exists():
        shutil.rmtree(latest)
    shutil.copytree(destination, latest)
    return {"run_id": run_id, "path": destination, "catalog": catalog, "quality": quality, "packages": packages}
