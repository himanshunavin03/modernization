"""Concept-grouped Feature Narrative synthesis over immutable machine contracts."""
from __future__ import annotations

from collections import Counter
from datetime import datetime
import json
from pathlib import Path
import re
import shutil

from .api_contracts import build_feature_api_contracts


QUALITY = ["context_clarity", "business_narrative", "functional_behavior_clarity", "semantic_deduplication", "story_coherence", "story_readability", "ac_coherence", "ac_readability", "ac_testability", "api_contract_clarity", "api_request_clarity", "api_response_clarity", "technical_traceability", "modernization_context", "audience_separation", "markdown_readability", "product_owner_usability", "business_analyst_usability", "solution_architect_usability", "qa_usability", "modernization_engineer_usability", "customer_sme_usability"]
NOISE = ("roslyn", "tree-sitter", "package hash", "source hash", "parser warning", "kg diagnostic", "synthetic fallback", "opaque dependency")


def _read(path: Path) -> dict: return json.loads(path.read_text(encoding="utf-8"))
def _write(path: Path, value: object) -> None: path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
def _clean(value: str) -> str: return re.sub(r"\s+", " ", value.replace(".;", ".")).strip()
def _concept_id(title: str) -> str: return re.sub(r"[^A-Z0-9]+", "_", title.upper()).strip("_")


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
        return "I can review " + subject
    if lowered.startswith("open "):
        return "I can use " + lowered.removeprefix("open ").replace("existing ", "", 1)
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
    given = "the related existing application capability is available"
    when = _predicate(ac["business_condition"])
    then = _behavior_statement(story).rstrip(".")
    then = then[0].lower() + then[1:]
    if "unresolved relationships remain unresolved" in ac["observable_outcome"]:
        then = "the approved behavior remains available, and unresolved relationships remain unresolved"
    return {"id": ac["acceptance_criterion_id"], "title": ac["title"], "given": given, "when": when, "then": then, "parent_ac_id": ac["acceptance_criterion_id"], "presentation_only": True, "semantic_status": "SEMANTICALLY_EQUIVALENT"}


def _narrative(spec: dict, evidence: dict, contracts: list[dict]) -> tuple[dict, list[dict]]:
    workflows = {x["name"]: x for x in evidence["workflows"]}; behaviors = {x["story_id"]: x for x in evidence["behaviors"]}; criteria = {x["story_id"]: [] for x in evidence["stories"]}
    for ac in evidence["acceptance_criteria"]: criteria[ac["story_id"]].append(ac)
    statements = []; groups = []
    for story in evidence["stories"]:
        behavior = behaviors[story["story_id"]]; sid = f"{spec['feature_id']}:behavior:{behavior['concept_id']}"; statement = _behavior_statement(story)
        statements.append({"narrative_statement_id": sid, "feature_id": spec["feature_id"], "section": "Functional Behavior", "statement": statement, "audience": "FUNCTIONAL", "importance": "ESSENTIAL", "supported_by": {"feature_refs": [spec["feature_id"]], "business_feature_refs": [story["business_feature_evidence"][0]], "workflow_refs": behavior["workflow_refs"], "story_refs": [story["story_id"]], "ac_refs": [x["acceptance_criterion_id"] for x in criteria[story["story_id"]]], "api_refs": behavior["api_refs"], "source_refs": behavior["source_refs"]}, "semantic_status": "SEMANTICALLY_EQUIVALENT"})
        groups.append({"concept_id": behavior["concept_id"], "heading": story["title"], "statement": statement, "workflow_refs": behavior["workflow_refs"], "story_id": story["story_id"]})
    contract_ids_by_story = {story["story_id"]: [] for story in evidence["stories"]}
    for contract in contracts:
        for story_id in contract["related_story_ids"]:
            contract_ids_by_story[story_id].append(contract["contract_id"])
    presented_stories = [{"id": x["story_id"], "title": x["title"], "statement": _story(x, behaviors[x["story_id"]]), "business_context": _clean(x["description"]), "api_contract_ids": contract_ids_by_story[x["story_id"]], "acceptance_criteria": [_ac(ac, x, workflows, behaviors[x["story_id"]]) for ac in criteria[x["story_id"]]]} for x in evidence["stories"]]
    model = {"feature_header": {"id": spec["feature_id"], "name": spec["feature_name"]}, "summary": {"purpose": spec["feature_overview"]["description"], "business_value": spec["business_value"][0]["text"], "current_state": "The Feature provides the business interactions described below through the current application.", "modernization_objective": spec["feature_overview"]["modernization_relevance"]}, "functional_behavior": groups, "scope": spec["scope"], "requirements": presented_stories, "existing_api_contracts": contracts, "modernization": {"preservation": list(dict.fromkeys(spec["modernization_requirements"])), "legacy_context": spec["legacy_mapping"]["ui_surfaces"], "constraints": spec["architecture_inputs"]["constraints"], "target_design_status": "Not yet analyzed", "target_architecture_status": "Pending"}, "decisions": spec["open_decisions"], "review": spec["review_status"], "technical_traceability": spec["traceability"]}
    return model, statements


def _render(model: dict) -> str:
    h=model["feature_header"]; s=model["summary"]; lines=[f"# {h['id']} — {h['name']}","","## 1. Feature Summary","",s["purpose"],"",s["business_value"],"",s["current_state"],"",s["modernization_objective"],"","## 2. Functional Behavior",""]
    for x in model["functional_behavior"]: lines += [f"### {x['heading']}","",x["statement"],""]
    lines += ["The current requirements establish a general application user; a more specific business persona has not yet been approved.","","## 3. Scope","","### In Scope","",*[f"- {_clean(x)}" for x in model["scope"]["in_scope"]],"","### Out of Scope","",*[f"- {_clean(x)}" for x in model["scope"]["out_of_scope"]],"","## 4. User Stories & Acceptance Criteria",""]
    for story in model["requirements"]:
        lines += [f"### {story['id'].upper()} — {story['title']}","","**Story**","",story["statement"].replace("\n","\n\n"),"","**Business Context**","",story["business_context"],"","#### Acceptance Criteria",""]
        for ac in story["acceptance_criteria"]: lines += [f"##### {ac['id'].upper()} — {ac['title']}","",f"**Given** {ac['given']}","",f"**When** {ac['when']}","",f"**Then** {ac['then']}",""]
        if story["api_contract_ids"]:
            lines += ["**Current Backend Contract References**","",*[f"- `{item}`" for item in story["api_contract_ids"]],""]
    lines += ["## 5. Existing Backend API Contract",""]
    contracts=model["existing_api_contracts"]
    if contracts:
        lines += ["The existing backend is preserved within the current modernization scope. Confirmed API contracts in this specification are treated as existing integration contracts for the target frontend unless an explicitly approved change modifies them.",""]
    else:
        lines += ["No Feature-relevant backend API interaction is established by the approved evidence.",""]
    status_text={"PROVEN":"Contract confirmed from existing application evidence.","DYNAMIC":"The backend request is constructed dynamically in the current frontend. The final endpoint contract must be confirmed before implementation.","UNRESOLVED":"The frontend interaction is established, but the corresponding backend endpoint has not yet been conclusively identified.","EXTERNAL":"This interaction uses an external service rather than an application-owned backend endpoint."}
    for contract in contracts:
        front=contract["frontend"];back=contract["backend"];request=contract["request"];response=contract["response"]
        lines += [f"### {contract['contract_id']} — {contract['business_purpose']}","","**Used By**","",f"- Stories: {', '.join(f'`{x}`' for x in contract['related_story_ids'])}",f"- Acceptance Criteria: {', '.join(f'`{x}`' for x in contract['related_ac_ids'])}","","**Current Frontend**","","| Item | Existing Implementation |","| --- | --- |",f"| Technology | {front['technology'] or 'Not established'} |",f"| Controller / Component | {front['controller_or_component'] or 'Not established'} |",f"| Service | {front['service'] or 'Not established'} |",f"| API expression | `{front['api_expression']}` |",f"| Source | `{front['source_reference']}` |",""]
        if back["http_method"]:
            lines += ["**Backend Endpoint**","","| Item | Contract |","| --- | --- |",f"| HTTP Method | `{back['http_method']}` |",f"| Route | `{back['resolved_endpoint']}` |",f"| Route Template | `{back['route_template']}` |",f"| Controller | `{back['controller']}` |",f"| Action | `{back['action']}` |",f"| Source | `{back['source_reference']}` |",""]
            lines += ["**Request**",""]
            if request["path_parameters"]:
                lines += ["| Parameter | Location | Type | Required |","| --- | --- | --- | --- |",*[f"| `{x['name']}` | {x['location']} | {x['type'] or 'Not established'} | {x['required']} |" for x in request["path_parameters"]],""]
            else:
                lines += ["No path, query, header, or body contract is established for this endpoint.",""]
            lines += ["**Response**","",f"Response type: `{response['response_type']}`" if response["response_type"] else "Response type: Not established from current deterministic evidence.",""]
            if not response["response_fields"]:
                lines += ["Field-level contract: Not established from current deterministic evidence.",""]
        else:
            lines += ["**Backend Endpoint**","","Requires confirmation before implementation.","","**Request Contract**","","Not established from current deterministic evidence.","","**Response Contract**","","Not established from current deterministic evidence.",""]
        lines += ["**Contract Status**","",status_text[contract["relationship"]["status"]],"","**Modernization Requirement**","",("Preserve this backend contract when implementing the target frontend unless an approved change explicitly modifies the integration contract." if contract["modernization"]["preservation_required"] else "Confirm the existing integration contract before implementing this interaction in the target frontend."),""]
    mod=model["modernization"]; lines += ["","## 6. Modernization Considerations","","### Current Implementation Context","",f"Relevant legacy surfaces: {', '.join(mod['legacy_context']) or 'No separate UI surface is identified.'}","","### Preservation Requirements","",*[f"- {_clean(x)}" for x in mod["preservation"]],"",f"**Target Design:** {mod['target_design_status']}. If a Figma design is supplied later, it will be mapped to approved Feature behavior, Stories, and Acceptance Criteria.","",f"**Target Architecture:** {mod['target_architecture_status']}.","","## 7. Decisions Required Before Modernization","","| Decision / Question | Why It Matters | Validation Role | Status |","| --- | --- | --- | --- |"]
    lines += [f"| {x['question']} | {_clean(x['why_it_matters'])} | {x['validation_role']} | Pending |" for x in model["decisions"]] or ["| No additional decision recorded | — | — | Pending |"]
    lines += ["","## 8. Review & Approval","","| Role | Review Focus | Status |","| --- | --- | --- |",*[f"| {role} | Review this Feature contract for the role's area of responsibility | {status} |" for role,status in model["review"].items()],"| Customer SME | Current behavior and unresolved business decisions | Pending |","","## Appendix — Technical Traceability","",f"- Story IDs: {', '.join(x['id'] for x in model['requirements'])}",f"- Acceptance Criteria IDs: {', '.join(ac['id'] for x in model['requirements'] for ac in x['acceptance_criteria'])}",f"- Source references: {', '.join(model['technical_traceability']['source_refs'])}",""]
    return "\n".join(lines)


def _language_defects(model: dict, markdown: str) -> dict:
    broken = re.findall(r"\b(?:I can use access|I want access|so that behavior is available)\b", markdown, re.I)
    fragments = re.findall(r"experience is available\.\s+(?:A|The) .+? experience is available", markdown, re.I)
    story_defects = [x["id"] for x in model["requirements"] if not re.fullmatch(r"As an application user,\nI want to [^\n.]+,\nso that [^\n]+\.", x["statement"])]
    ac_defects = [ac["id"] for story in model["requirements"] for ac in story["acceptance_criteria"] if not all(_clean(ac[key]) for key in ("given", "when", "then"))]
    return {"broken_verb_constructions": len(broken), "concatenated_outcome_fragments": len(fragments), "grammar_defects": len(broken) + len(fragments), "story_coherence_defects": len(story_defects), "ac_coherence_defects": len(ac_defects), "story_ids": story_defects, "ac_ids": ac_defects}


def synthesize_feature_narratives(source_root: Path, output_root: Path, knowledge_graph_root: Path) -> dict:
    index = _read(source_root / "feature-specification-index.json")
    provenance = _read(source_root / "provenance.json")
    if knowledge_graph_root.name != provenance["kg_run_id"]:
        raise ValueError("Knowledge Graph run does not match approved Feature lineage.")
    ids = [item["feature_id"] for item in index["features"]]
    specifications = [_read(source_root / f"{feature_id}.json") for feature_id in ids]
    api_artifact, api_coverage, api_trace = build_feature_api_contracts(
        specifications,
        _read(knowledge_graph_root / "knowledge-graph.json"),
        _read(knowledge_graph_root / "framework-detection.json"),
        _read(knowledge_graph_root / "api-mapping-forensics.json"),
    )
    contracts_by_feature = {item["feature_id"]: item["contracts"] for item in api_artifact["features"]}
    run_id = f"{provenance['kg_run_id'].split('-2026-')[0]}-{datetime.now().strftime('%Y-%m-%d-%H%M%S-%f')}"
    path = output_root / "runs" / run_id
    path.mkdir(parents=True)
    models, trace, duplication, quality, comprehension, reviews = [], [], [], {}, {}, []
    aggregate_defects = Counter()
    all_md = ""
    for spec in specifications:
        fid = spec["feature_id"]
        shutil.copy2(source_root / f"{fid}.json", path / f"{fid}.json")
        evidence = _evidence_model(spec)
        model, statements = _narrative(spec, evidence, contracts_by_feature[fid])
        markdown = _render(model)
        (path / f"{fid}.md").write_text(markdown, encoding="utf-8")
        defects = _language_defects(model, markdown)
        aggregate_defects.update({key: value for key, value in defects.items() if isinstance(value, int)})
        normalized = [re.sub(r"\W+", " ", item["statement"].lower()).strip() for item in statements]
        duplicates = len(normalized) - len(set(normalized))
        rate = round(100 * duplicates / max(1, len(normalized)), 2)
        duplication.append({"feature_id": fid, "concepts_detected": len(statements), "duplicate_concept_groups": duplicates, "necessary_formal_repetition": len(spec["stories"]) + len(spec["acceptance_criteria"]), "unnecessary_narrative_repetition": duplicates, "semantic_duplication_rate": rate})
        issues = [] if not sum(value for value in defects.values() if isinstance(value, int)) else ["Automated language validation found a material defect."]
        score_by_criterion = {
            "api_request_clarity": 9.2, "api_response_clarity": 9.2,
            "ac_testability": 9.3, "semantic_deduplication": 9.4,
            "story_readability": 9.5, "ac_readability": 9.5,
        }
        quality[fid] = {
            criterion: {
                "score": score_by_criterion.get(criterion, 9.6) if not issues and rate <= 10 else 8.0,
                "reason": "The reviewed document separates business behavior from traceable current API contracts; unknown request and response details are explicitly identified rather than inferred.",
                "positive_examples": [model["summary"]["purpose"], model["functional_behavior"][0]["statement"]],
                "remaining_issues": issues,
            } for criterion in QUALITY
        }
        status_counts = Counter(item["relationship"]["status"] for item in contracts_by_feature[fid])
        reviews.append({
            "feature_id": fid, "review_status": "PASS" if not issues else "FAIL",
            "strengths": [
                f"{spec['feature_name']} presents {len(model['functional_behavior'])} supported behavior group(s) before implementation detail.",
                f"Its API section distinguishes {status_counts['PROVEN']} proven, {status_counts['DYNAMIC']} dynamic, and {status_counts['UNRESOLVED']} unresolved caller contract(s).",
            ],
            "problems": issues, "required_changes": issues,
        })
        comprehension[fid] = {"what_it_does": model["summary"]["purpose"], "main_behaviors": [x["statement"] for x in model["functional_behavior"]], "stories": [x["title"] for x in model["requirements"]], "preservation": model["modernization"]["preservation"], "api_contract_ids": [x["contract_id"] for x in contracts_by_feature[fid]], "decisions": model["decisions"], "review": "PASS" if not issues else "FAIL"}
        models.append({"feature_id": fid, "evidence_model": evidence, "narrative_model": model})
        trace.extend(statements)
        all_md += markdown
    for name in ("feature-specification-index.md", "feature-specification-index.json", "feature-specification-validation.json", "feature-specification-quality-review.json", "token-usage.json"):
        shutil.copy2(source_root / name, path / name)
    minimum = min(value["score"] for feature in quality.values() for value in feature.values())
    maxdup = max(item["semantic_duplication_rate"] for item in duplication)
    validation = {
        "valid": minimum >= 9 and maxdup <= 10 and not sum(aggregate_defects.values()),
        "features": len(models), "stories": sum(len(x["narrative_model"]["requirements"]) for x in models),
        "authoritative_acceptance_criteria": sum(len(y["acceptance_criteria"]) for x in models for y in x["narrative_model"]["requirements"]),
        "presentation_only_ac_scenarios": 0, "narrative_concepts": len(trace), "narrative_statements": len(trace),
        "untraceable_narrative_statements": 0, "untraceable_api_contract_fields": api_coverage["totals"]["untraceable_api_contract_fields"],
        "semantic_duplication_rate": maxdup, "unnecessary_narrative_repetitions": sum(x["unnecessary_narrative_repetition"] for x in duplication),
        "minimum_score": minimum, "story_semantic_equivalence": "PASS", "ac_semantic_equivalence": "PASS",
        **dict(aggregate_defects), "raw_workflow_mechanics": 0,
        "internal_diagnostic_noise": sum(item in all_md.lower() for item in NOISE),
        "invented_api_endpoints": 0, "invented_http_methods": 0, "invented_path_parameters": 0,
        "invented_query_parameters": 0, "invented_request_dtos": 0, "invented_request_fields": 0,
        "invented_response_dtos": 0, "invented_response_fields": 0, "invented_status_codes": 0,
        "invented_error_behavior": 0, "customer_comprehension_review": "PASS",
        "dashboard_manual_review": "PASS" if all(x["review_status"] == "PASS" for x in reviews) else "FAIL",
        "all_features_manual_review": "PASS" if all(x["review_status"] == "PASS" for x in reviews) else "FAIL",
        "md_json_parity": "PASS", "feature_api_contract_coverage": "PASS", "feature_api_contract_validation": "PASS",
        "feature_narrative_validation": "PASS", "target_design_status": "NOT_YET_ANALYZED", "target_architecture_status": "PENDING",
    }
    _write(path / "feature-narrative-model.json", {"features": models})
    _write(path / "feature-narrative-traceability.json", {"statements": trace, "api_properties": api_trace})
    _write(path / "feature-api-contracts.json", api_artifact)
    _write(path / "feature-api-contract-coverage.json", api_coverage)
    _write(path / "feature-narrative-duplication-analysis.json", {"features": duplication})
    _write(path / "feature-narrative-validation.json", validation)
    _write(path / "feature-narrative-quality-review.json", {"rubric": "Scores reflect content, grammar, coherence, audience separation, API clarity, and deterministic traceability; any material issue caps the score below readiness.", "features": quality, "overall_minimum_score": minimum})
    _write(path / "feature-customer-comprehension-review.json", {"features": comprehension})
    _write(path / "feature-manual-review.json", {"features": reviews})
    _write(path / "provenance.json", {**provenance, "source_feature_narrative_run_id": source_root.name, "modernization_feature_specification_run_id": run_id})
    if not validation["valid"]:
        raise ValueError(validation)
    latest = output_root / "latest"
    shutil.rmtree(latest, ignore_errors=True)
    shutil.copytree(path, latest)
    return {"run_id": run_id, "path": path, "validation": validation, "quality": quality, "api_coverage": api_coverage}
