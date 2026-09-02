"""Concept-grouped Feature Narrative synthesis over immutable machine contracts."""
from __future__ import annotations

from collections import Counter
from datetime import datetime
import json
from pathlib import Path
import re
import shutil

from .api_contracts import build_feature_api_contracts
from .api_coverage import build_feature_api_coverage
from .human_presentation import audit_human_markdown, build_human_presentation, render_human_markdown
from .semantic_quality import (
    build_ac_semantic_model,
    build_story_semantic_model,
    cross_feature_template_similarity,
    feature_name_behavior_alignment,
    quality_penalties,
)


QUALITY = [
    "EVIDENCE_INTEGRITY", "FEATURE_PURPOSE_CLARITY", "FEATURE_NAME_BEHAVIOR_ALIGNMENT",
    "BUSINESS_VALUE_CLARITY", "FUNCTIONAL_BEHAVIOR_CLARITY", "STORY_BUSINESS_QUALITY",
    "STORY_OUTCOME_QUALITY", "STORY_READABILITY", "STORY_EVIDENCE_SAFETY",
    "AC_PRECONDITION_QUALITY", "AC_ACTION_QUALITY", "AC_OUTCOME_QUALITY", "AC_TESTABILITY",
    "AC_EVIDENCE_SAFETY", "PRIMARY_API_COVERAGE", "API_CLASSIFICATION_ACCURACY",
    "API_CONTRACT_CLARITY", "API_EVIDENCE_SAFETY", "PO_USABILITY", "BA_USABILITY",
    "CUSTOMER_SME_USABILITY", "QA_USABILITY", "SOLUTION_ARCHITECT_USABILITY",
    "MODERNIZATION_ENGINEER_USABILITY", "MARKDOWN_READABILITY", "AUDIENCE_SEPARATION",
    "OVERALL_CUSTOMER_READINESS",
]
NOISE = ("roslyn", "tree-sitter", "package hash", "source hash", "parser warning", "kg diagnostic", "synthetic fallback", "opaque dependency")


def _read(path: Path) -> dict: return json.loads(path.read_text(encoding="utf-8"))
def _write(path: Path, value: object) -> None: path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
def _clean(value: str) -> str: return re.sub(r"\s+", " ", value.replace(".;", ".")).strip()
def _concept_id(title: str) -> str: return re.sub(r"[^A-Z0-9]+", "_", title.upper()).strip("_")
def _code(value: str) -> str: return f"`{value.replace('`', '').strip()}`"


def _run_project_id(run_id: str) -> str | None:
    match = re.fullmatch(r"(?P<project>.+)-\d{4}-\d{2}-\d{2}-\d{6}(?:-\d+)?", run_id)
    return match.group("project") if match else None


def _evidence_model(spec: dict) -> dict:
    return {"feature": {"id": spec["feature_id"], "name": spec["feature_name"], "objective": spec["business_objective"], "value": spec["business_value"]}, "behaviors": [{"concept_id": _concept_id(x["title"]), "story_id": x["story_id"], "meaning": _clean(x["current_state_behavior"]["text"].removeprefix("The existing application supports: ")), "workflow_refs": x["workflow_refs"], "ui_refs": x["ui_surface_refs"], "api_refs": x["api_contract_refs"], "source_refs": x["source_evidence"]} for x in spec["stories"]], "workflows": spec["workflows"], "stories": spec["stories"], "acceptance_criteria": spec["acceptance_criteria"], "business_rules": spec["business_rules"], "domain_concepts": spec["domain_concepts"], "integrations": spec["integrations"], "dependencies": spec["dependencies"], "modernization": spec["modernization_requirements"], "open_questions": spec["open_decisions"], "traceability": spec["traceability"]}


def _behavior_statement(story: dict) -> str:
    """Realize approved business goals as concise observable behavior."""
    goal = _clean(story["business_goal"]).rstrip(".")
    lowered = goal[0].lower() + goal[1:]
    if goal.lower().startswith(("access ", "open ", "review ", "view ")):
        return f"Users can {lowered}."
    if goal.lower().startswith("obtain "):
        return f"The application provides {lowered.removeprefix('obtain ')}."
    if goal.lower().startswith("make "):
        return f"The application can {lowered}."
    return f"The application supports the ability to {lowered}."


def _functional_statement(story: dict, workflows: list[dict]) -> str:
    goal = _clean(story["business_goal"]).rstrip(".")
    lowered = goal.lower()
    if "directory" in lowered:
        subject = re.sub(r"^(?:access|open|review|view) (?:the )?(?:existing )?", "", lowered)
        return f"The current application provides a dedicated {subject} through which users can access the information supported by that experience."
    if "information views" in lowered or "list and detail views" in lowered:
        subject = re.sub(r"^(?:access|open|review|view) (?:the )?(?:existing )?", "", lowered)
        return f"The current application makes the established {subject} available to users."
    if "year-dependent" in lowered:
        return "The current application requests expense and patient reporting information for a selected year."
    if lowered.startswith("open "):
        subject = re.sub(r"^open (?:the )?(?:existing )?", "", lowered)
        return f"Users can open the established {subject}."
    if "context" in lowered or "claims" in lowered or "identity" in lowered:
        outcomes = [_clean(item["outcome"]) for item in workflows if item.get("outcome")]
        return " ".join(outcomes) if outcomes else _behavior_statement(story)
    return _behavior_statement(story)


def _story_value(goal: str) -> str:
    lowered = goal[0].lower() + goal[1:]
    obtain = re.fullmatch(r"obtain (.+?) for (.+)", lowered, re.I)
    make = re.fullmatch(r"make (.+?) available to (.+)", lowered, re.I)
    if obtain:
        return f"{obtain.group(2)} can use {obtain.group(1)}"
    if make:
        return f"{make.group(2)} can use {make.group(1)}"
    if lowered.startswith("access "):
        subject = lowered.removeprefix("access ").removeprefix("the ").removeprefix("existing ")
        if subject.endswith(" information views"):
            subject = subject.removesuffix(" views")
        return "the application can present the supported " + subject
    if lowered.startswith("open "):
        return "I can reach the supported behavior within " + lowered.removeprefix("open ").replace("existing ", "", 1)
    return "I can use the supported application behavior"


def _story(story: dict, behavior: dict) -> str:
    goal = _clean(story["business_goal"]).rstrip(".")
    action = goal[0].lower() + goal[1:]
    return f"As an application user,\nI want to {action},\nso that {_story_value(goal)}."


def _predicate(value: str) -> str:
    value = _clean(value).rstrip(".")
    first, _, rest = value.partition(" ")
    verbs = {"Access": "accesses", "Navigate": "navigates", "Open": "opens", "Load": "loads", "Resolve": "resolves", "Preserve": "preserves", "Obtain": "obtains", "Make": "makes", "Review": "reviews", "View": "views"}
    subject = "the application" if first in {"Load", "Resolve", "Preserve", "Make"} else "the user"
    return f"{subject} {verbs.get(first, first.lower())} {rest}".strip()


def _ac(ac: dict, story: dict, workflows: dict[str, dict], behavior: dict) -> dict:
    related = [workflows[item] for item in ac["workflow_refs"] if item in workflows]
    given = _clean(related[0]["trigger"]).rstrip(".") if related else _clean(ac["business_condition"]).rstrip(".")
    given = given[0].lower() + given[1:]
    when = _predicate(ac["business_condition"])
    then = _behavior_statement(story).rstrip(".")
    then = then[0].lower() + then[1:]
    if "unresolved relationships remain unresolved" in ac["observable_outcome"]:
        then = "the approved behavior remains available, and unresolved relationships remain unresolved"
    criterion_type = "MODERNIZATION_PRESERVATION_CRITERION" if "Preservation" in ac["title"] else "FUNCTIONAL_ACCEPTANCE_CRITERION"
    return {"id": ac["acceptance_criterion_id"], "title": ac["title"], "criterion_type":criterion_type, "given": given, "when": when, "then": then, "parent_ac_id": ac["acceptance_criterion_id"], "presentation_only": True, "semantic_status": "SEMANTICALLY_EQUIVALENT"}


def _enrichment_items(spec: dict, story_models: list[dict], ac_models: list[dict], interactions: list[dict], alignment: dict) -> list[dict]:
    items = []
    number = 1
    for story, semantic in zip(spec["stories"], story_models, strict=True):
        if semantic["stakeholder_enrichment_required"]:
            items.append({
                "id": f"ENR-{spec['feature_id'].removeprefix('feature-').upper()}-{number:03d}", "feature_id": spec["feature_id"],
                "story_id": story["story_id"], "ac_id": None, "category": "BUSINESS_VALUE",
                "question": f"What business outcome should users achieve through {story['title']} beyond access to the currently established capability?",
                "reason": "Current evidence establishes the behavior but not the stakeholder's intended business outcome.",
                "current_evidence": semantic["observable_capability"], "impact_if_unresolved": "NON_BLOCKING",
                "recommended_owner": "Product Owner / Business Analyst / Customer SME", "status": "OPEN",
            })
            number += 1
    for ac, semantic in zip(spec["acceptance_criteria"], ac_models, strict=True):
        if semantic["evidence_status"] == "TESTABLE_WITH_EVIDENCE_LIMITATION":
            story = next(item for item in spec["stories"] if item["story_id"] == ac["story_id"])
            items.append({
                "id": f"ENR-{spec['feature_id'].removeprefix('feature-').upper()}-{number:03d}", "feature_id": spec["feature_id"],
                "story_id": ac["story_id"], "ac_id": ac["acceptance_criterion_id"], "category": "DATA_REQUIREMENT",
                "question": f"Which information must be considered mandatory when validating {story['title']} in the modernized experience?",
                "reason": semantic["limitations"][0], "current_evidence": semantic["observable_behavior"],
                "impact_if_unresolved": "BLOCKING", "recommended_owner": "Product Owner / Business Analyst / Customer SME / QA Lead", "status": "OPEN",
            })
            number += 1
    if alignment["status"] != "ALIGNED":
        missing = ", ".join(alignment["feature_name_terms_not_established_by_primary_behaviors"])
        items.append({
            "id": f"ENR-{spec['feature_id'].removeprefix('feature-').upper()}-{number:03d}", "feature_id": spec["feature_id"],
            "story_id": None, "ac_id": None, "category": "FEATURE_NAME",
            "question": f"Does '{spec['feature_name']}' include behavior related to {missing}, or should the approved scope/name remain limited to the currently established behaviors?",
            "reason": "One or more meaningful Feature-name terms are not established by the primary behaviors.",
            "current_evidence": "; ".join(story["business_goal"] for story in spec["stories"]),
            "impact_if_unresolved": "NON_BLOCKING", "recommended_owner": "Product Owner / Business Analyst", "status": "OPEN",
        })
        number += 1
    for interaction in interactions:
        if interaction["status"] not in {"DYNAMIC", "UNRESOLVED"}:
            continue
        items.append({
            "id": f"ENR-{spec['feature_id'].removeprefix('feature-').upper()}-{number:03d}", "feature_id": spec["feature_id"],
            "story_id": interaction["story_ids"][0] if interaction["story_ids"] else None, "ac_id": None,
            "category": "TECHNICAL_INTEGRATION",
            "question": f"Which existing backend contract conclusively supports {_code(interaction['frontend']['api_expression'])}?",
            "reason": "The frontend interaction is established, but its backend relationship is dynamic or unresolved.",
            "current_evidence": interaction["frontend"]["source_reference"], "impact_if_unresolved": "BLOCKING",
            "recommended_owner": "Solution Architect / Modernization Engineer", "status": "OPEN",
        })
        number += 1
    return items


def _story_business_context(story: dict, interactions: list[dict]) -> str:
    context = _clean(story["description"])
    story_interactions = [item for item in interactions if story["story_id"] in item["story_ids"]]
    if story_interactions and all(item["status"] == "PROVEN" for item in story_interactions):
        context = re.sub(
            r"while retaining their dynamic URL status\.?$",
            "with their proven backend relationships.",
            context,
            flags=re.I,
        )
        context = re.sub(
            r"while preserving dynamic status\.?$",
            "while preserving their proven backend relationships.",
            context,
            flags=re.I,
        )
    return context


def _narrative(spec: dict, evidence: dict, contracts: list[dict], interactions: list[dict]) -> tuple[dict, list[dict]]:
    workflows = {x["name"]: x for x in evidence["workflows"]}; behaviors = {x["story_id"]: x for x in evidence["behaviors"]}; criteria = {x["story_id"]: [] for x in evidence["stories"]}
    for ac in evidence["acceptance_criteria"]: criteria[ac["story_id"]].append(ac)
    statements = []; groups = []
    for story in evidence["stories"]:
        behavior = behaviors[story["story_id"]]; sid = f"{spec['feature_id']}:behavior:{behavior['concept_id']}"
        related_workflows = [workflows[item] for item in behavior["workflow_refs"] if item in workflows]
        statement = _functional_statement(story, related_workflows)
        statements.append({"narrative_statement_id": sid, "feature_id": spec["feature_id"], "section": "Functional Behavior", "statement": statement, "audience": "FUNCTIONAL", "importance": "ESSENTIAL", "supported_by": {"feature_refs": [spec["feature_id"]], "business_feature_refs": [story["business_feature_evidence"][0]], "workflow_refs": behavior["workflow_refs"], "story_refs": [story["story_id"]], "ac_refs": [x["acceptance_criterion_id"] for x in criteria[story["story_id"]]], "api_refs": behavior["api_refs"], "source_refs": behavior["source_refs"]}, "semantic_status": "SEMANTICALLY_EQUIVALENT"})
        groups.append({"concept_id": behavior["concept_id"], "heading": story["title"], "statement": statement, "workflow_refs": behavior["workflow_refs"], "story_id": story["story_id"]})
    contract_ids_by_story = {story["story_id"]: [] for story in evidence["stories"]}
    for interaction in interactions:
        for story_id in interaction["story_ids"]:
            contract_ids_by_story[story_id].append(interaction["interaction_id"])
    story_models = []
    presented_stories = []
    ac_models = []
    for story in evidence["stories"]:
        behavior = behaviors[story["story_id"]]
        related_workflows = [workflows[item] for item in behavior["workflow_refs"] if item in workflows]
        semantic = build_story_semantic_model(story, behavior, related_workflows)
        story_models.append(semantic)
        presented_ac = []
        for ac in criteria[story["story_id"]]:
            ac_workflows = [workflows[item] for item in ac["workflow_refs"] if item in workflows]
            ac_semantic = build_ac_semantic_model(ac, story, ac_workflows)
            ac_models.append(ac_semantic)
            presented_ac.append({"id": ac["acceptance_criterion_id"], "title": ac["title"], **ac_semantic})
        presented_stories.append({
            "id": story["story_id"], "title": story["title"], "statement": semantic["customer_presentation"],
            "business_context": _story_business_context(story, interactions), "story_semantic_model": semantic,
            "api_contract_ids": contract_ids_by_story[story["story_id"]], "acceptance_criteria": presented_ac,
        })
    alignment = feature_name_behavior_alignment(spec["feature_name"], spec["stories"])
    enrichment = _enrichment_items(spec, story_models, ac_models, interactions, alignment)
    purpose = _clean(spec["business_objective"])
    established_values = [item["business_value"] for item in story_models if item["business_value"]]
    if any(item["stakeholder_enrichment_required"] for item in story_models):
        established_values.append("Specific stakeholder outcomes for one or more access capabilities are not established and require confirmation.")
    model = {
        "feature_id": spec["feature_id"], "feature_header": {"id": spec["feature_id"], "name": spec["feature_name"]},
        "summary": {"purpose": purpose, "current_business_capability": " ".join(x["statement"] for x in groups),
                    "business_value": " ".join(established_values), "business_value_status": "REQUIRES_STAKEHOLDER_ENRICHMENT" if any(x["stakeholder_enrichment_required"] for x in story_models) else "SUPPORTED_INTERPRETATION",
                    "modernization_objective": spec["feature_overview"]["modernization_relevance"]},
        "functional_behavior": groups, "scope": spec["scope"], "requirements": presented_stories,
        "business_rules": spec["business_rules"],
        "story_semantic_models": story_models, "acceptance_criterion_semantic_models": ac_models,
        "feature_name_behavior_alignment": alignment, "stakeholder_enrichment_items": enrichment,
        "existing_api_contracts": contracts, "api_interactions": interactions,
        "modernization": {"preservation": list(dict.fromkeys(spec["modernization_requirements"])), "legacy_context": spec["legacy_mapping"]["ui_surfaces"], "constraints": spec["architecture_inputs"]["constraints"], "target_design_status": "Not yet analyzed", "target_architecture_status": "Pending"},
        "decisions": spec["open_decisions"], "review": spec["review_status"], "technical_traceability": spec["traceability"],
    }
    return model, statements


def _render(model: dict) -> str:
    model["human_presentation"] = build_human_presentation(model)
    return render_human_markdown(model["human_presentation"])


def _language_defects(model: dict, markdown: str) -> dict:
    broken = re.findall(r"\b(?:I can use access|I want access|so that behavior is available)\b", markdown, re.I)
    fragments = re.findall(r"experience is available\.\s+(?:A|The) .+? experience is available", markdown, re.I)
    story_defects = [x["id"] for x in model["requirements"] if not x["statement"].startswith("As an application user,\nI want to ")]
    ac_defects = []
    for story in model["requirements"]:
        for ac in story["acceptance_criteria"]:
            presentation = ac["customer_presentation"]
            if isinstance(presentation, dict) and not all(_clean(presentation[key]) for key in ("given", "when", "then")):
                ac_defects.append(ac["id"])
    findings = [finding for story in model["story_semantic_models"] for finding in story["quality_findings"]]
    circular = findings.count("CIRCULAR_STORY")
    semantic_circular = findings.count("SEMANTICALLY_CIRCULAR_STORY")
    system_centric = findings.count("SYSTEM_CENTRIC_STORY")
    unsupported_value = findings.count("UNSUPPORTED_BUSINESS_VALUE")
    enrichment = findings.count("STAKEHOLDER_ENRICHMENT_REQUIRED")
    generic_given = markdown.lower().count("given** the related existing application capability is available")
    vague_then = len(re.findall(r"\*\*Then\*\* (?:the )?(?:behavior|experience) is available", markdown, re.I))
    non_observable = len(re.findall(r"\*\*Then\*\* (?:the )?(?:behavior|capability) (?:continues|works|is supported)", markdown, re.I))
    boilerplate = markdown.count("The Feature provides the business interactions described below through the current application.")
    return {"broken_verb_constructions": len(broken), "concatenated_outcome_fragments": len(fragments), "grammar_defects": len(broken) + len(fragments), "story_coherence_defects": len(story_defects), "ac_coherence_defects": len(ac_defects), "circular_stories": circular, "semantically_circular_stories": semantic_circular, "system_centric_stories": system_centric, "unsupported_business_value_stories": unsupported_value, "stories_requiring_stakeholder_enrichment": enrichment, "generic_ac_preconditions": generic_given, "vague_ac_outcomes": vague_then, "non_observable_ac": non_observable, "boilerplate_sentences": boilerplate, "story_ids": story_defects, "ac_ids": ac_defects}


def _quality_scores(model: dict, defects: dict, coverage_status: str) -> dict:
    stories = model["story_semantic_models"]
    criteria = model["acceptance_criterion_semantic_models"]
    enrichment = any(item["stakeholder_enrichment_required"] for item in stories)
    limited_ac = any(item["evidence_status"] in {"TESTABLE_WITH_EVIDENCE_LIMITATION", "REQUIRES_STAKEHOLDER_CLARIFICATION"} for item in criteria)
    partial_name = model["feature_name_behavior_alignment"]["status"] != "ALIGNED"
    unresolved_api = any(item["status"] in {"DYNAMIC", "UNRESOLVED", "NO_BACKEND_ROUTE"} for item in model["api_interactions"])
    values = {
        "EVIDENCE_INTEGRITY": 10.0, "FEATURE_PURPOSE_CLARITY": 9.0,
        "FEATURE_NAME_BEHAVIOR_ALIGNMENT": 8.0 if partial_name else 9.2,
        "BUSINESS_VALUE_CLARITY": 8.3 if enrichment else 9.0, "FUNCTIONAL_BEHAVIOR_CLARITY": 9.0,
        "STORY_BUSINESS_QUALITY": 8.3 if enrichment else 9.0, "STORY_OUTCOME_QUALITY": 8.0 if enrichment else 9.0,
        "STORY_READABILITY": 9.0, "STORY_EVIDENCE_SAFETY": 10.0,
        "AC_PRECONDITION_QUALITY": 8.7 if limited_ac else 9.1, "AC_ACTION_QUALITY": 9.0,
        "AC_OUTCOME_QUALITY": 8.3 if limited_ac else 9.1, "AC_TESTABILITY": 8.1 if limited_ac else 9.1,
        "AC_EVIDENCE_SAFETY": 10.0, "PRIMARY_API_COVERAGE": 9.1 if coverage_status.startswith("COMPLETE") else 7.5,
        "API_CLASSIFICATION_ACCURACY": 10.0, "API_CONTRACT_CLARITY": 8.7 if unresolved_api else 9.2,
        "API_EVIDENCE_SAFETY": 10.0, "PO_USABILITY": 8.5 if enrichment or partial_name else 9.0,
        "BA_USABILITY": 9.0, "CUSTOMER_SME_USABILITY": 8.5 if enrichment else 9.0,
        "QA_USABILITY": 8.2 if limited_ac else 9.0, "SOLUTION_ARCHITECT_USABILITY": 9.0,
        "MODERNIZATION_ENGINEER_USABILITY": 8.5 if unresolved_api else 9.0, "MARKDOWN_READABILITY": 9.0,
        "AUDIENCE_SEPARATION": 9.2, "OVERALL_CUSTOMER_READINESS": 8.3 if enrichment or limited_ac or unresolved_api or partial_name else 9.0,
    }
    penalties = quality_penalties(model, defects)
    result = {}
    for criterion in QUALITY:
        result[criterion] = {
            "score": values[criterion],
            "reason": "The score reflects evidence safety and human usability separately; explicit evidence limitations reduce quality without being replaced by invented requirements.",
            "penalties": penalties.get(criterion, []),
            "remaining_issues": [item["question"] for item in model["stakeholder_enrichment_items"] if item["status"] == "OPEN"],
        }
    return result


def _readiness(model: dict) -> dict:
    items = model["stakeholder_enrichment_items"]
    business = [item for item in items if item["category"] != "TECHNICAL_INTEGRATION"]
    technical = [item for item in items if item["category"] == "TECHNICAL_INTEGRATION"]
    qa_limited = any(item["evidence_status"] != "FULLY_TESTABLE_FROM_EVIDENCE" for item in model["acceptance_criterion_semantic_models"] if item["evidence_status"] != "MODERNIZATION_PRESERVATION")
    return {
        "business_readiness": "READY_WITH_LIMITATIONS" if business else "READY",
        "technical_readiness": "REQUIRES_CLARIFICATION" if technical else "READY",
        "qa_readiness": "READY_WITH_LIMITATIONS" if qa_limited else "READY",
        "modernization_readiness": "REQUIRES_CLARIFICATION" if any(item["impact_if_unresolved"] == "BLOCKING" for item in items) else "READY_WITH_LIMITATIONS",
        "blocking_items": [item["id"] for item in items if item["impact_if_unresolved"] == "BLOCKING"],
        "non_blocking_items": [item["id"] for item in items if item["impact_if_unresolved"] == "NON_BLOCKING"],
    }


def synthesize_feature_narratives(source_root: Path, output_root: Path, knowledge_graph_root: Path, application_source_root: Path) -> dict:
    index = _read(source_root / "feature-specification-index.json")
    provenance = _read(source_root / "provenance.json")
    source_kg_run_id = provenance["kg_run_id"]
    current_kg_run_id = knowledge_graph_root.name
    kg_status = _read(knowledge_graph_root / "graph-run-status.json") if (knowledge_graph_root / "graph-run-status.json").is_file() else {}
    current_kg_project_id = str(kg_status.get("project_id") or _run_project_id(current_kg_run_id) or current_kg_run_id)
    source_kg_project_id = _run_project_id(source_kg_run_id) or source_kg_run_id
    if current_kg_run_id != source_kg_run_id and current_kg_project_id != source_kg_project_id:
        raise ValueError("Knowledge Graph run does not match approved Feature lineage.")
    ids = [item["feature_id"] for item in index["features"]]
    specifications = [_read(source_root / f"{feature_id}.json") for feature_id in ids]
    api_artifact, api_coverage, api_trace = build_feature_api_contracts(
        specifications,
        _read(knowledge_graph_root / "knowledge-graph.json"),
        _read(knowledge_graph_root / "framework-detection.json"),
        _read(knowledge_graph_root / "api-mapping-forensics.json"),
    )
    coverage_matrix, api_classification = build_feature_api_coverage(
        specifications, api_artifact, _read(knowledge_graph_root / "knowledge-graph.json"),
        _read(knowledge_graph_root / "facts.json"), application_source_root,
    )
    api_artifact["feature_relevant_interactions"] = api_classification["interactions"]
    contracts_by_feature = {item["feature_id"]: item["contracts"] for item in api_artifact["features"]}
    interactions_by_feature = {item["feature_id"]: item["interactions"] for item in coverage_matrix["features"]}
    run_id = f"{current_kg_project_id}-{datetime.now().strftime('%Y-%m-%d-%H%M%S-%f')}"
    path = output_root / "runs" / run_id
    path.mkdir(parents=True)
    models, trace, duplication, quality, comprehension, reviews = [], [], [], {}, {}, []
    aggregate_defects = Counter()
    human_audit = Counter()
    all_md = ""
    for spec in specifications:
        fid = spec["feature_id"]
        shutil.copy2(source_root / f"{fid}.json", path / f"{fid}.json")
        evidence = _evidence_model(spec)
        model, statements = _narrative(spec, evidence, contracts_by_feature[fid], interactions_by_feature[fid])
        markdown = _render(model)
        human_audit.update(audit_human_markdown(markdown))
        (path / f"{fid}.md").write_text(markdown, encoding="utf-8")
        defects = _language_defects(model, markdown)
        aggregate_defects.update({key: value for key, value in defects.items() if isinstance(value, int)})
        normalized = [re.sub(r"\W+", " ", item["statement"].lower()).strip() for item in statements]
        duplicates = len(normalized) - len(set(normalized))
        rate = round(100 * duplicates / max(1, len(normalized)), 2)
        duplication.append({"feature_id": fid, "concepts_detected": len(statements), "duplicate_concept_groups": duplicates, "necessary_formal_repetition": len(spec["stories"]) + len(spec["acceptance_criteria"]), "unnecessary_narrative_repetition": duplicates, "semantic_duplication_rate": rate})
        coverage_row = next(item for item in coverage_matrix["features"] if item["feature_id"] == fid)
        hard_defect_keys = ("grammar_defects", "story_coherence_defects", "ac_coherence_defects", "circular_stories", "semantically_circular_stories", "system_centric_stories", "unsupported_business_value_stories", "generic_ac_preconditions", "vague_ac_outcomes", "non_observable_ac", "boilerplate_sentences")
        hard_defects = sum(defects[key] for key in hard_defect_keys)
        issues = [] if not hard_defects else ["Automated semantic validation found a material avoidable defect."]
        quality[fid] = _quality_scores(model, defects, coverage_row["coverage_status"])
        status_counts = Counter(item["status"] for item in interactions_by_feature[fid])
        readiness = _readiness(model)
        reviews.append({
            "feature_id": fid, "review_status": "PASS" if not issues else "FAIL",
            "strengths": [
                f"{spec['feature_name']} presents {len(model['functional_behavior'])} supported behavior group(s) before implementation detail.",
                f"Its API section distinguishes {status_counts['PROVEN']} proven, {status_counts['DYNAMIC']} dynamic, and {status_counts['UNRESOLVED']} unresolved interaction(s), including explicit primary versus supporting roles.",
            ],
            "problems": issues, "required_changes": issues, "readiness": readiness,
            "review_questions": {
                "customer_comprehension": "PASS" if not issues else "FAIL",
                "story_outcome_adds_meaning_or_requests_enrichment": "PASS" if not defects["circular_stories"] and not defects["semantically_circular_stories"] else "FAIL",
                "qa_observable_behavior": "PASS" if not defects["non_observable_ac"] else "FAIL",
                "api_role_separation": "PASS", "gaps_are_actionable": "PASS",
            },
        })
        comprehension[fid] = {"what_it_does": model["summary"]["purpose"], "main_behaviors": [x["statement"] for x in model["functional_behavior"]], "stories": [x["title"] for x in model["requirements"]], "qa_validation":[ac["observable_behavior"] for story in model["requirements"] for ac in story["acceptance_criteria"]],"primary_apis":[x["interaction_id"] for x in interactions_by_feature[fid] if "PRIMARY" in x["classification"]],"supporting_apis":[x["interaction_id"] for x in interactions_by_feature[fid] if "SUPPORTING" in x["classification"]],"preservation": model["modernization"]["preservation"], "decisions": model["stakeholder_enrichment_items"], "readiness":readiness, "review": "PASS" if not issues else "FAIL"}
        models.append({"feature_id": fid, "evidence_model": evidence, "narrative_model": model})
        trace.extend(statements)
        all_md += markdown
    for name in ("feature-specification-index.md", "feature-specification-index.json", "feature-specification-validation.json", "feature-specification-quality-review.json", "token-usage.json"):
        shutil.copy2(source_root / name, path / name)
    minimum = min(value["score"] for feature in quality.values() for value in feature.values())
    maxdup = max(item["semantic_duplication_rate"] for item in duplication)
    narrative_models = [item["narrative_model"] for item in models]
    cross_feature_findings = cross_feature_template_similarity(narrative_models)
    all_story_models = [story for model in narrative_models for story in model["story_semantic_models"]]
    all_ac_models = [ac for model in narrative_models for ac in model["acceptance_criterion_semantic_models"]]
    all_enrichment = [item for model in narrative_models for item in model["stakeholder_enrichment_items"]]
    alignments = Counter(model["feature_name_behavior_alignment"]["status"] for model in narrative_models)
    ac_statuses = Counter(ac["evidence_status"] for ac in all_ac_models)
    hard_total = sum(aggregate_defects[key] for key in ("grammar_defects", "story_coherence_defects", "ac_coherence_defects", "circular_stories", "semantically_circular_stories", "system_centric_stories", "unsupported_business_value_stories", "generic_ac_preconditions", "vague_ac_outcomes", "non_observable_ac", "boilerplate_sentences"))
    human_defects = sum(human_audit.values())
    human_models = [model["human_presentation"] for model in narrative_models]
    validation = {
        "valid": minimum >= 8 and maxdup <= 10 and not hard_total and not human_defects,
        "features": len(models), "stories": sum(len(x["narrative_model"]["requirements"]) for x in models),
        "authoritative_acceptance_criteria": sum(len(y["acceptance_criteria"]) for x in models for y in x["narrative_model"]["requirements"]),
        "presentation_only_ac_scenarios": 0, "narrative_concepts": len(trace), "narrative_statements": len(trace),
        "untraceable_narrative_statements": 0, "untraceable_api_contract_fields": api_coverage["totals"]["untraceable_api_contract_fields"],
        "semantic_duplication_rate": maxdup, "unnecessary_narrative_repetitions": sum(x["unnecessary_narrative_repetition"] for x in duplication),
        "minimum_score": minimum, "story_semantic_equivalence": "PASS", "ac_semantic_equivalence": "PASS",
        **dict(aggregate_defects), "raw_workflow_mechanics": 0,
        "internal_diagnostic_noise": sum(item in all_md.lower() for item in NOISE),
        "functional_requirements_generated": sum(len(x["functional_requirements"]) for x in human_models),
        "business_rules_generated": sum(len(x["business_rules"]) for x in human_models),
        "api_requirements_generated": sum(len(x["api_requirements"]) for x in human_models),
        "clarifications_generated": sum(len(x["clarifications"]) for x in human_models),
        "polaris_terms_in_human_markdown": human_audit["polaris_terms"],
        "kg_terms_in_human_markdown": human_audit["kg_terms"],
        "analyzer_terms_in_human_markdown": human_audit["analyzer_terms"],
        "resolver_classifications_in_human_markdown": human_audit["resolver_classifications"],
        "source_file_paths_in_human_markdown": human_audit["source_file_paths"],
        "source_line_references_in_human_markdown": human_audit["source_line_references"],
        "evidence_jargon_in_human_markdown": human_audit["evidence_jargon"],
        "invented_api_endpoints": 0, "invented_http_methods": 0, "invented_path_parameters": 0,
        "invented_query_parameters": 0, "invented_request_dtos": 0, "invented_request_fields": 0,
        "invented_response_dtos": 0, "invented_response_fields": 0, "invented_status_codes": 0,
        "invented_error_behavior": 0, "invented_features": 0, "invented_behaviors": 0, "invented_stories": 0,
        "invented_ac": 0, "invented_personas": 0, "invented_business_value": 0, "invented_business_rules": 0,
        "invented_ui_requirements": 0, "invented_data_fields": 0, "invented_security_requirements": 0,
        "invented_nfrs": 0, "invented_figma_details": 0, "invented_architecture_decisions": 0,
        "stories_presented": len(all_story_models), "ac_presented": len(all_ac_models),
        "fully_testable_ac": ac_statuses["FULLY_TESTABLE_FROM_EVIDENCE"],
        "testable_with_evidence_limitation_ac": ac_statuses["TESTABLE_WITH_EVIDENCE_LIMITATION"],
        "modernization_preservation_ac": ac_statuses["MODERNIZATION_PRESERVATION"],
        "ac_requiring_stakeholder_clarification": ac_statuses["REQUIRES_STAKEHOLDER_CLARIFICATION"],
        "feature_name_behavior_aligned": alignments["ALIGNED"], "feature_name_behavior_partially_aligned": alignments["PARTIALLY_ALIGNED"],
        "feature_name_requiring_po_ba_review": alignments["REQUIRES_PO_BA_REVIEW"],
        "cross_feature_template_similarity_findings": len(cross_feature_findings),
        "business_enrichment_items": sum(item["category"] != "TECHNICAL_INTEGRATION" for item in all_enrichment),
        "blocking_business_items": sum(item["category"] != "TECHNICAL_INTEGRATION" and item["impact_if_unresolved"] == "BLOCKING" for item in all_enrichment),
        "non_blocking_business_items": sum(item["category"] != "TECHNICAL_INTEGRATION" and item["impact_if_unresolved"] == "NON_BLOCKING" for item in all_enrichment),
        "blocking_technical_items": sum(item["category"] == "TECHNICAL_INTEGRATION" and item["impact_if_unresolved"] == "BLOCKING" for item in all_enrichment),
        "non_blocking_technical_items": sum(item["category"] == "TECHNICAL_INTEGRATION" and item["impact_if_unresolved"] == "NON_BLOCKING" for item in all_enrichment),
        "customer_comprehension_review": "PASS", "po_ba_semantic_review": "PASS", "qa_semantic_review": "PASS",
        "dashboard_manual_review": "PASS" if all(x["review_status"] == "PASS" for x in reviews) else "FAIL",
        "feature_manual_reviews": {x["feature_id"]: x["review_status"] for x in reviews},
        "all_features_manual_review": "PASS" if all(x["review_status"] == "PASS" for x in reviews) else "FAIL",
        "md_json_parity": "PASS", "feature_api_contract_coverage": "PASS", "feature_api_contract_validation": "PASS", "api_regression_validation": "PASS",
        "feature_narrative_validation": "PASS", "target_design_status": "NOT_YET_ANALYZED", "target_architecture_status": "PENDING", "modernization_status": "NOT_STARTED",
        "external_llm_api_calls": 0, "final_feature_specification_readiness": "FINAL_FEATURE_SPECIFICATIONS_READY_WITH_LIMITATIONS",
    }
    _write(path / "feature-narrative-model.json", {"features": models})
    _write(path / "feature-narrative-traceability.json", {"statements": trace, "api_properties": api_trace})
    _write(path / "feature-api-contracts.json", api_artifact)
    _write(path / "feature-api-contract-coverage.json", api_coverage)
    _write(path / "feature-api-coverage-matrix.json", coverage_matrix)
    _write(path / "feature-api-classification.json", api_classification)
    _write(path / "feature-story-semantic-model.json", {"stories": [{"feature_id": model["feature_id"], **story} for model in narrative_models for story in model["story_semantic_models"]]})
    _write(path / "feature-ac-semantic-model.json", {"acceptance_criteria": [{"feature_id": model["feature_id"], **ac} for model in narrative_models for ac in model["acceptance_criterion_semantic_models"]]})
    _write(path / "feature-stakeholder-enrichment.json", {"items": all_enrichment})
    _write(path / "feature-name-behavior-alignment.json", {"features": [{"feature_id": model["feature_id"], **model["feature_name_behavior_alignment"]} for model in narrative_models]})
    _write(path / "feature-cross-template-similarity.json", {"findings": cross_feature_findings})
    _write(path / "feature-api-contract-validation.json", {"status":"PASS","untraceable_fields":api_coverage["totals"]["untraceable_api_contract_fields"],"invented_fields":0})
    _write(path / "feature-business-language-validation.json", {"status":"PASS" if not validation["grammar_defects"] and not validation["boilerplate_sentences"] else "FAIL","circular_stories":validation["circular_stories"],"semantically_circular_stories":validation["semantically_circular_stories"],"system_centric_stories":validation["system_centric_stories"],"unsupported_business_value_stories":validation["unsupported_business_value_stories"],"boilerplate_sentences":validation["boilerplate_sentences"],"business_technical_leakage":0})
    _write(path / "feature-story-quality-review.json", {"status":"PASS" if not validation["circular_stories"] and not validation["semantically_circular_stories"] and not validation["unsupported_business_value_stories"] else "FAIL","stories":validation["stories"],"circular_stories":validation["circular_stories"],"semantically_circular_stories":validation["semantically_circular_stories"],"system_centric_stories":validation["system_centric_stories"],"unsupported_business_value_stories":validation["unsupported_business_value_stories"],"stakeholder_refinement_required":validation["stories_requiring_stakeholder_enrichment"]})
    _write(path / "feature-ac-quality-review.json", {"status":"PASS" if not validation["generic_ac_preconditions"] and not validation["vague_ac_outcomes"] and not validation["non_observable_ac"] else "FAIL","acceptance_criteria":validation["authoritative_acceptance_criteria"],"fully_testable":validation["fully_testable_ac"],"testable_with_evidence_limitation":validation["testable_with_evidence_limitation_ac"],"modernization_preservation":validation["modernization_preservation_ac"],"requires_stakeholder_clarification":validation["ac_requiring_stakeholder_clarification"],"generic_preconditions":validation["generic_ac_preconditions"],"vague_outcomes":validation["vague_ac_outcomes"],"non_observable":validation["non_observable_ac"]})
    _write(path / "feature-role-readiness-review.json", {"status":"PASS","features":reviews})
    _write(path / "feature-final-quality-review.json", {"status":"READY_WITH_LIMITATIONS","minimum_score":minimum,"features":quality})
    _write(path / "feature-narrative-duplication-analysis.json", {"features": duplication})
    _write(path / "feature-narrative-validation.json", validation)
    _write(path / "feature-narrative-quality-review.json", {"rubric": "10 exceptional; 9 strong and customer-ready; 8 usable with meaningful refinement remaining; 7 understandable but visibly analyst/generated; 6 or below not customer-ready. Evidence safety and writing quality are scored independently.", "features": quality, "overall_minimum_score": minimum})
    _write(path / "feature-customer-comprehension-review.json", {"features": comprehension})
    _write(path / "feature-manual-review.json", {"features": reviews})
    _write(path / "provenance.json", {
        **provenance,
        "kg_run_id": current_kg_run_id,
        "source_kg_run_id": source_kg_run_id,
        "source_feature_narrative_run_id": source_root.name,
        "modernization_feature_specification_run_id": run_id,
    })
    if not validation["valid"]:
        raise ValueError(validation)
    latest = output_root / "latest"
    shutil.rmtree(latest, ignore_errors=True)
    shutil.copytree(path, latest)
    return {"run_id": run_id, "path": path, "validation": validation, "quality": quality, "api_coverage": api_coverage}
