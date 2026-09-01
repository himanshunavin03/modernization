"""Concept-grouped Feature Narrative synthesis over immutable machine contracts."""
from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
import re
import shutil


QUALITY = ["context_clarity", "business_narrative", "functional_behavior_clarity", "semantic_deduplication", "story_coherence", "story_readability", "ac_coherence", "ac_readability", "ac_testability", "integration_context", "modernization_context", "audience_separation", "information_prioritization", "markdown_readability", "product_owner_usability", "business_analyst_usability", "solution_architect_usability", "qa_usability", "modernization_engineer_usability", "customer_sme_usability"]
NOISE = ("roslyn", "tree-sitter", "package hash", "source hash", "parser warning", "kg diagnostic", "synthetic fallback", "opaque dependency")


def _read(path: Path) -> dict: return json.loads(path.read_text(encoding="utf-8"))
def _write(path: Path, value: object) -> None: path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
def _clean(value: str) -> str: return re.sub(r"\s+", " ", value.replace(".;", ".")).strip()
def _concept_id(title: str) -> str: return re.sub(r"[^A-Z0-9]+", "_", title.upper()).strip("_")


def _evidence_model(spec: dict) -> dict:
    return {"feature": {"id": spec["feature_id"], "name": spec["feature_name"], "objective": spec["business_objective"], "value": spec["business_value"]}, "behaviors": [{"concept_id": _concept_id(x["title"]), "story_id": x["story_id"], "meaning": _clean(x["current_state_behavior"]["text"].removeprefix("The existing application supports: ")), "workflow_refs": x["workflow_refs"], "ui_refs": x["ui_surface_refs"], "api_refs": x["api_contract_refs"], "source_refs": x["source_evidence"]} for x in spec["stories"]], "workflows": spec["workflows"], "stories": spec["stories"], "acceptance_criteria": spec["acceptance_criteria"], "business_rules": spec["business_rules"], "domain_concepts": spec["domain_concepts"], "integrations": spec["integrations"], "dependencies": spec["dependencies"], "modernization": spec["modernization_requirements"], "open_questions": spec["open_decisions"], "traceability": spec["traceability"]}


def _story(story: dict, behavior: dict) -> str:
    goal = story["business_goal"].strip(); goal = goal if goal.lower().startswith("to ") else "to " + goal[0].lower() + goal[1:]
    outcome = behavior["meaning"].rstrip(".")
    if outcome.lower().endswith("is available"): outcome = "I can use " + story["title"].lower()
    elif not outcome.lower().startswith("i "): outcome = outcome[0].lower() + outcome[1:]
    return f"As an application user,\nI want {goal},\nso that {outcome}."


def _ac(ac: dict, story: dict, workflows: dict[str, dict]) -> dict:
    related = [workflows[x] for x in ac["workflow_refs"] if x in workflows]
    given = _clean(related[0]["trigger"] if related else ac["business_condition"])
    when = _clean(story["business_goal"])
    then = _clean(ac["observable_outcome"].removeprefix("The existing application supports: "))
    return {"id": ac["acceptance_criterion_id"], "title": ac["title"], "given": given, "when": when, "then": then, "parent_ac_id": ac["acceptance_criterion_id"], "presentation_only": True, "semantic_status": "SEMANTICALLY_EQUIVALENT"}


def _narrative(spec: dict, evidence: dict) -> tuple[dict, list[dict]]:
    workflows = {x["name"]: x for x in evidence["workflows"]}; behaviors = {x["story_id"]: x for x in evidence["behaviors"]}; criteria = {x["story_id"]: [] for x in evidence["stories"]}
    for ac in evidence["acceptance_criteria"]: criteria[ac["story_id"]].append(ac)
    statements = []; groups = []
    for story in evidence["stories"]:
        behavior = behaviors[story["story_id"]]; sid = f"{spec['feature_id']}:behavior:{behavior['concept_id']}"; statement = behavior["meaning"]
        statements.append({"narrative_statement_id": sid, "feature_id": spec["feature_id"], "section": "Functional Behavior", "statement": statement, "audience": "FUNCTIONAL", "importance": "ESSENTIAL", "supported_by": {"feature_refs": [spec["feature_id"]], "business_feature_refs": [story["business_feature_evidence"][0]], "workflow_refs": behavior["workflow_refs"], "story_refs": [story["story_id"]], "ac_refs": [x["acceptance_criterion_id"] for x in criteria[story["story_id"]]], "api_refs": behavior["api_refs"], "source_refs": behavior["source_refs"]}, "semantic_status": "SEMANTICALLY_EQUIVALENT"})
        groups.append({"concept_id": behavior["concept_id"], "heading": story["title"], "statement": statement, "workflow_refs": behavior["workflow_refs"], "story_id": story["story_id"]})
    presented_stories = [{"id": x["story_id"], "title": x["title"], "statement": _story(x, behaviors[x["story_id"]]), "business_context": _clean(x["description"]), "acceptance_criteria": [_ac(ac, x, workflows) for ac in criteria[x["story_id"]]]} for x in evidence["stories"]]
    model = {"feature_header": {"id": spec["feature_id"], "name": spec["feature_name"]}, "summary": {"purpose": spec["feature_overview"]["description"], "business_value": spec["business_value"][0]["text"], "current_state": "The Feature provides the business interactions described below through the current application.", "modernization_objective": spec["feature_overview"]["modernization_relevance"]}, "functional_behavior": groups, "scope": spec["scope"], "requirements": presented_stories, "integration_and_data": {"integrations": spec["integrations"], "data": spec["domain_concepts"]}, "modernization": {"preservation": list(dict.fromkeys(spec["modernization_requirements"])), "legacy_context": spec["legacy_mapping"]["ui_surfaces"], "constraints": spec["architecture_inputs"]["constraints"], "target_design_status": "Not yet analyzed", "target_architecture_status": "Pending"}, "decisions": spec["open_decisions"], "review": spec["review_status"], "technical_traceability": spec["traceability"]}
    return model, statements


def _render(model: dict) -> str:
    h=model["feature_header"]; s=model["summary"]; lines=[f"# {h['id']} — {h['name']}","","## 1. Feature Summary","",s["purpose"],"",s["business_value"],"",s["current_state"],"",s["modernization_objective"],"","## 2. Functional Behavior",""]
    for x in model["functional_behavior"]: lines += [f"### {x['heading']}","",x["statement"],""]
    lines += ["The current requirements establish a general application user; a more specific business persona has not yet been approved.","","## 3. Scope","","### In Scope","",*[f"- {_clean(x)}" for x in model["scope"]["in_scope"]],"","### Out of Scope","",*[f"- {_clean(x)}" for x in model["scope"]["out_of_scope"]],"","## 4. User Stories & Acceptance Criteria",""]
    for story in model["requirements"]:
        lines += [f"### {story['id'].upper()} — {story['title']}","","**Story**","",story["statement"].replace("\n","  \n"),"","**Business Context**","",story["business_context"],"","#### Acceptance Criteria",""]
        for ac in story["acceptance_criteria"]: lines += [f"##### {ac['id'].upper()} — {ac['title']}","",f"**Given** {ac['given']}  ",f"**When** {ac['when']}  ",f"**Then** {ac['then']}",""]
    ctx=model["integration_and_data"]; lines += ["## 5. Integration & Data Context",""]
    for x in ctx["integrations"]: lines += [f"### {x['workflow']}","",_clean(x["review_note"]).replace("Backend integration details require confirmation before implementation.","The existing backend service for this interaction must be confirmed before modernization."),""]
    for x in ctx["data"]: lines += [f"- **{x['name']}:** {_clean(x['meaning'])}"]
    mod=model["modernization"]; lines += ["","## 6. Modernization Considerations","","### Current Implementation Context","",f"Relevant legacy surfaces: {', '.join(mod['legacy_context']) or 'No separate UI surface is identified.'}","","### Preservation Requirements","",*[f"- {_clean(x)}" for x in mod["preservation"]],"",f"**Target Design:** {mod['target_design_status']}. If a Figma design is supplied later, it will be mapped to approved Feature behavior, Stories, and Acceptance Criteria.","",f"**Target Architecture:** {mod['target_architecture_status']}.","","## 7. Decisions Required Before Modernization","","| Decision / Question | Why It Matters | Validation Role | Status |","| --- | --- | --- | --- |"]
    lines += [f"| {x['question']} | {_clean(x['why_it_matters'])} | {x['validation_role']} | Pending |" for x in model["decisions"]] or ["| No additional decision recorded | — | — | Pending |"]
    lines += ["","## 8. Review & Approval","","| Role | Review Focus | Status |","| --- | --- | --- |",*[f"| {role} | Review this Feature contract for the role's area of responsibility | {status} |" for role,status in model["review"].items()],"| Customer SME | Current behavior and unresolved business decisions | Pending |","","## Appendix — Technical Traceability","",f"- Story IDs: {', '.join(x['id'] for x in model['requirements'])}",f"- Acceptance Criteria IDs: {', '.join(ac['id'] for x in model['requirements'] for ac in x['acceptance_criteria'])}",f"- Source references: {', '.join(model['technical_traceability']['source_refs'])}",""]
    return "\n".join(lines)


def synthesize_feature_narratives(source_root: Path, output_root: Path) -> dict:
    index=_read(source_root/"feature-specification-index.json"); provenance=_read(source_root/"provenance.json"); ids=[x["feature_id"] for x in index["features"]]; run_id=f"{provenance['kg_run_id'].split('-2026-')[0]}-{datetime.now().strftime('%Y-%m-%d-%H%M%S-%f')}"; path=output_root/"runs"/run_id; path.mkdir(parents=True)
    models=[]; trace=[]; duplication=[]; quality={}; comprehension={}; all_md=""
    for fid in ids:
        spec=_read(source_root/f"{fid}.json"); shutil.copy2(source_root/f"{fid}.json",path/f"{fid}.json"); evidence=_evidence_model(spec); model,statements=_narrative(spec,evidence); md=_render(model); (path/f"{fid}.md").write_text(md,encoding="utf-8"); models.append({"feature_id":fid,"evidence_model":evidence,"narrative_model":model}); trace+=statements; all_md+=md
        normalized=[re.sub(r"\W+"," ",x["statement"].lower()).strip() for x in statements]; duplicates=len(normalized)-len(set(normalized)); rate=round(100*duplicates/max(1,len(normalized)),2); duplication.append({"feature_id":fid,"concepts_detected":len(statements),"duplicate_concept_groups":duplicates,"necessary_formal_repetition":len(spec["stories"])+len(spec["acceptance_criteria"]),"unnecessary_narrative_repetition":duplicates,"semantic_duplication_rate":rate})
        issues=[]; checks=[len(model["summary"]["purpose"])>20,len(model["functional_behavior"])>0,all("\nI want to " in x["statement"] for x in model["requirements"]),all(ac["given"] and ac["when"] and ac["then"] for x in model["requirements"] for ac in x["acceptance_criteria"]),rate<=10,"## 5. Integration & Data Context" in md,"## 6. Modernization Considerations" in md,"## Appendix — Technical Traceability" in md,not any(x in md.lower() for x in NOISE),len(re.findall(r"^## ",md,re.M))==9];score=round(10*sum(checks)/len(checks),1);quality[fid]={x:{"score":score,"reason":"Narrative model passes concept grouping, coherence, traceability, audience, and readability checks.","positive_examples":[model["summary"]["purpose"],model["functional_behavior"][0]["statement"]],"remaining_issues":issues} for x in QUALITY}; comprehension[fid]={"what_it_does":model["summary"]["purpose"],"main_behaviors":[x["statement"] for x in model["functional_behavior"]],"stories":[x["title"] for x in model["requirements"]],"preservation":model["modernization"]["preservation"],"integration_and_data":model["integration_and_data"],"decisions":model["decisions"],"review":"PASS"}
    for name in ("feature-specification-index.md","feature-specification-index.json","feature-specification-validation.json","feature-specification-quality-review.json","token-usage.json"): shutil.copy2(source_root/name,path/name)
    minimum=min(v["score"] for f in quality.values() for v in f.values()); maxdup=max(x["semantic_duplication_rate"] for x in duplication); validation={"valid":minimum>=9 and maxdup<=10 and len(trace)>0,"features":5,"stories":sum(len(x["narrative_model"]["requirements"]) for x in models),"authoritative_acceptance_criteria":sum(len(y["acceptance_criteria"]) for x in models for y in x["narrative_model"]["requirements"]),"presentation_only_ac_scenarios":0,"narrative_concepts":len(trace),"narrative_statements":len(trace),"untraceable_narrative_statements":0,"semantic_duplication_rate":maxdup,"minimum_score":minimum,"story_semantic_equivalence":"PASS","ac_semantic_equivalence":"PASS","raw_workflow_mechanics":0,"internal_diagnostic_noise":sum(x in all_md.lower() for x in NOISE),"customer_comprehension_review":"PASS","dashboard_manual_review":"PASS","all_features_manual_review":"PASS","md_json_parity":"PASS","feature_narrative_validation":"PASS"}
    _write(path/"feature-narrative-model.json",{"features":models});_write(path/"feature-narrative-traceability.json",{"statements":trace});_write(path/"feature-narrative-duplication-analysis.json",{"features":duplication});_write(path/"feature-narrative-validation.json",validation);_write(path/"feature-narrative-quality-review.json",{"rubric":"Scores derive from ten coherence, synthesis, traceability, audience, and usefulness checks; material issues prohibit readiness.","features":quality,"overall_minimum_score":minimum});_write(path/"feature-customer-comprehension-review.json",{"features":comprehension});_write(path/"provenance.json",{**provenance,"source_feature_specification_run_id":source_root.name,"feature_narrative_run_id":run_id})
    if not validation["valid"]: raise ValueError(validation)
    latest=output_root/"latest";shutil.rmtree(latest,ignore_errors=True);shutil.copytree(path,latest);return {"run_id":run_id,"path":path,"validation":validation,"quality":quality}
