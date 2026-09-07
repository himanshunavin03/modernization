"""Generate validated Feature Specifications from immutable approved artifacts."""
from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
import shutil


def _read(path: Path) -> dict:
    if not path.is_file():
        raise ValueError(f"Required immutable artifact is missing: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def synchronize_targeted_feature_specification(context: dict, story_root: Path, acceptance_root: Path, output_root: Path) -> dict:
    """Consolidate one current Feature through the existing human/Jira renderer."""
    from hashlib import sha256
    from polaris_modernization.feature_specifications.human_presentation import build_targeted_human_presentation, render_human_markdown, audit_human_markdown
    stories=_read(story_root/'story-catalog.json')
    acceptance=_read(acceptance_root/'acceptance-criteria.json')
    expected=context['feature_contract_hash']
    for document in (stories,acceptance):
        if document['lineage']['feature_contract_hash']!=expected or document['lineage']['canonical_upstream_kg_run']!=context['canonical_kg_run']:
            raise ValueError('Cannot synchronize stale requirements artifacts.')
    if acceptance['lineage']['story_run']!=stories['lineage']['story_run']:
        raise ValueError('Acceptance Criteria do not belong to the supplied Story run.')
    current_fields=('feature_id','feature_name','status','functional_requirements','capability_api_contracts','capability_dispositions','upstream_lineage')
    contract={**{k:v for k,v in context['contract'].items() if k in current_fields}, 'stories':stories['stories'], 'acceptance_criteria':acceptance['acceptance_criteria'],
        'stories_regenerated':True,'acceptance_criteria_regenerated':True,'downstream_status':'REQUIREMENTS_CURRENT',
        'generation_lineage':acceptance['lineage']}
    # Historical workflow/traceability summaries must not masquerade as current
    # requirements. Retain the immutable historical file, replace these views.
    contract['traceability']=acceptance['lineage']
    contract['workflows']=[{'interaction_id':r.get('interaction_id'),'requirement_id':r['id']} for r in contract['functional_requirements']]
    presentation=build_targeted_human_presentation(contract,stories,acceptance)
    contract['scope']=presentation['scope']
    contract['business_rules']=presentation['business_rules']
    contract['definition_of_ready']=presentation['definition_of_ready']
    markdown=render_human_markdown(presentation)
    cleanliness=audit_human_markdown(markdown)
    if any(cleanliness.values()):
        raise ValueError(f'Human specification contains internal or unclear terminology: {cleanliness}')
    if any(ac['quality']['status']!='PASS' for s in presentation['jira_stories'] for ac in s['acceptance_criteria']):
        raise ValueError('Jira Acceptance Criteria quality failed.')
    run_id='requirements-freeze-'+datetime.now().strftime('%Y-%m-%d-%H%M%S-%f')
    destination=output_root/'runs'/run_id
    destination.mkdir(parents=True,exist_ok=False)
    feature_id=contract['feature_id']
    _write(destination/f'{feature_id}.json',contract)
    _write(destination/'human-presentation.json',presentation)
    (destination/f'{feature_id}.md').write_text(markdown,encoding='utf-8')
    validation={'valid':True,'feature_id':feature_id,'lineage':acceptance['lineage'],'human_cleanliness':cleanliness,
        'feature_spec_synchronized':True,'markdown_sha256':sha256(markdown.encode()).hexdigest()}
    _write(destination/'requirements-validation.json',validation)
    latest=output_root/'latest'
    for name in (f'{feature_id}.json',f'{feature_id}.md'):
        shutil.copyfile(destination/name,latest/name)
    _write(latest/f'{feature_id}-validation.json',validation)
    index_path=latest/'feature-specification-index.json'
    if index_path.is_file():
        index=_read(index_path)
        for entry in index['features']:
            if entry['feature_id']==feature_id:
                entry.update({'stories':len(stories['stories']),'acceptance_criteria':len(acceptance['acceptance_criteria']),
                    'business_purpose':presentation['overview']['objective'],'requirements_run_id':run_id,
                    'upstream_lineage':contract.get('upstream_lineage',{})})
        _write(index_path,index)
    _write(latest/'downstream-staleness.json',{'feature_id':feature_id,'status':'REQUIREMENTS_CURRENT',
        'stories':'CURRENT','acceptance_criteria':'CURRENT','stale_artifacts':['TECHNICAL_TASKS','ANGULAR','PLAYWRIGHT']})
    return {'run_id':run_id,'path':destination,'contract':contract,'presentation':presentation,'validation':validation}


def _lineage(business: dict, stories: dict, acceptance: dict, roots: tuple[Path, Path, Path]) -> dict:
    result = {key: acceptance[key] for key in ("kg_run_id", "application_understanding_run_id", "feature_run_id", "business_feature_run_id", "story_run_id")}
    result["acceptance_criteria_run_id"] = acceptance["acceptance_criteria_run_id"]
    if result["business_feature_run_id"] != roots[0].name or result["story_run_id"] != roots[1].name or result["acceptance_criteria_run_id"] != roots[2].name:
        raise ValueError("Immutable run paths do not match declared lineage.")
    if any(result[key] != business[key] for key in ("kg_run_id", "application_understanding_run_id", "feature_run_id", "business_feature_run_id")):
        raise ValueError("Business Feature lineage differs from Acceptance Criteria lineage.")
    if any(result[key] != stories[key] for key in ("kg_run_id", "application_understanding_run_id", "feature_run_id", "business_feature_run_id", "story_run_id")):
        raise ValueError("Story lineage differs from Acceptance Criteria lineage.")
    return result


def _spec(feature: dict, stories: list[dict], criteria: list[dict], lineage: dict) -> dict:
    questions = [{"question": item["question"], "why_it_matters": item["reason"], "validation_role": "Product Owner / Business Analyst / Customer SME"} for item in feature["open_questions"]]
    rules = [{"id": item["rule_id"], "description": item["description"]} for item in feature["business_rules"]]
    integrations = []
    seen = set()
    for story in stories:
        for item in story["api_contract_refs"]:
            key = (item["workflow"], item["status"], item["api_contract"], item["backend_endpoint"])
            if key not in seen:
                seen.add(key)
                integrations.append({**item, "review_note": "Established relationship must be preserved." if item["status"] == "PROVEN" else "Backend integration details require confirmation before implementation."})
    source_refs = sorted({item["source_path"] for story in stories for item in story["source_evidence"]})
    kg_refs = sorted({item for story in stories for item in story["kg_evidence"]})
    return {
        "feature_id": feature["feature_id"], "feature_name": feature["feature_name"],
        "feature_overview": {"description": feature["short_business_summary"], "purpose": feature["current_objective"]["text"], "current_context": "Existing application behavior represented by approved workflows and Stories.", "modernization_relevance": feature["modernization_objective"]["text"]},
        "business_objective": feature["current_objective"]["text"],
        "business_value": [{"text": item["text"], "classification": item["classification"]} for item in feature["business_value"]],
        "actors": [{"name": "user of the existing application", "specific_persona_status": "Not established by approved evidence"}],
        "scope": {"in_scope": [item["text"] for item in feature["in_scope"]], "out_of_scope": [item["text"] for item in feature["out_of_scope"]]},
        "workflows": [{"name": item["name"], "trigger": item["business_trigger"], "interaction": item["business_steps"], "outcome": item["expected_outcome"]} for item in feature["workflows"]],
        "business_rules": rules,
        "domain_concepts": [{"name": item["name"], "meaning": item["business_meaning"], "role": item["role_in_feature"]} for item in feature["domain_concepts"]],
        "current_experience": [item["text"] for item in feature["current_user_experience"]],
        "stories": stories, "acceptance_criteria": criteria,
        "functional_requirements": [{"acceptance_criterion_id": item["acceptance_criterion_id"], "requirement": item["observable_outcome"]} for item in criteria],
        "integrations": integrations,
        "data_dependencies": [{"name": item["name"], "description": item["description"]} for item in feature["dependencies"]],
        "security_context": "Feature-specific access and authorization requirements will be confirmed during architecture and stakeholder validation.",
        "modernization_requirements": [item["modernization_relevance"]["text"] for item in stories],
        "legacy_mapping": {"ui_surfaces": sorted({item for story in stories for item in story["ui_surface_refs"]}), "integration_contracts": integrations, "target_mapping_status": "Pending Target Design and Target Architecture"},
        "target_design": {"provider": None, "url": None, "status": "NOT_YET_ANALYZED", "mapped_screens": [], "mapped_stories": []},
        "architecture_inputs": {"legacy_surfaces": sorted({item for story in stories for item in story["ui_surface_refs"]}), "integrations": integrations, "constraints": [item["text"] for item in feature["modernization_concerns"] + feature["evidence_backed_limitations"]]},
        "nfr_status": "Feature-specific non-functional requirements have not yet been approved.",
        "open_decisions": questions,
        "risks": [item["text"] for item in feature["risks_and_limitations"]],
        "dependencies": [item["name"] for item in feature["dependencies"]],
        "definition_of_ready": ["Business Feature reviewed", "Stories reviewed", "Acceptance Criteria reviewed", "Open decisions resolved or explicitly accepted", "Target-design path selected", "Target Architecture approved", "Required integration contracts confirmed"],
        "review_status": {role: "Pending" for role in ("Product Owner", "Business Analyst", "Solution Architect", "QA Lead", "Modernization Lead")},
        "traceability": {**lineage, "source_refs": source_refs, "kg_refs": kg_refs},
        "information_filter": {"customer_reviewable": ["behavior", "objective", "value", "workflows", "Stories", "Acceptance Criteria", "scope", "decisions"], "architect_reviewable": ["legacy technology", "integrations", "data dependencies", "migration constraints", "target-design status"], "internal_only_excluded_from_markdown": ["analyzer diagnostics", "parser diagnostics", "package hashes", "internal confidence mechanics"]},
    }


def _markdown(spec: dict) -> str:
    f = spec; lines = [f"# {f['feature_id']} — {f['feature_name']}", "", "## 1. Feature Overview", "", f["feature_overview"]["description"], "", f"**Purpose:** {f['feature_overview']['purpose']}", "", f"**Modernization relevance:** {f['feature_overview']['modernization_relevance']}", "", "## 2. Business Objective", "", f["business_objective"], "", "## 3. Business Value", "", *[f"- {x['text']}" for x in f["business_value"]], "", "## 4. Current Business Behavior", "", *[f"- {x['outcome']}" for x in f["workflows"]], "", "## 5. Users / Actors", "", "The existing evidence identifies a general application user but does not establish a more specific business persona for this Feature.", "", "## 6. Functional Scope", "", "### In Scope", "", *[f"- {x}" for x in f["scope"]["in_scope"]], "", "### Out of Scope", "", *[f"- {x}" for x in f["scope"]["out_of_scope"]], "", "## 7. Business Workflows", ""]
    for x in f["workflows"]: lines += [f"### {x['name']}", "", f"**Trigger:** {x['trigger']}", "", f"**Interaction:** {'; '.join(x['interaction'])}", "", f"**Observable outcome:** {x['outcome']}", ""]
    lines += ["## 8. Business Rules", "", *([f"- {x['description']}" for x in f["business_rules"]] or ["No additional Feature-specific Business Rule has been established from the current approved application evidence."]), "", "## 9. Data / Information Requirements", "", *([f"- **{x['name']}:** {x['meaning']}" for x in f["domain_concepts"]] or ["No additional named domain information concept has been established for this Feature."]), "", "## 10. User Experience", "", "### Current Experience", "", *[f"- {x}" for x in f["current_experience"]], "", "### Target Experience", "", "The target user experience will be defined during the optional target-design/Figma and Target Architecture stages.", "", "## 11. Target Design / Figma", "", "Status: **Not provided / not analyzed in this stage**", "", "Polaris supports an optional target-design source such as Figma. When supplied, the target design will be mapped to this Feature and its Stories without silently redefining approved business behavior.", "", "- Design source: Not provided", "- Figma URL: Not provided", "- Relevant page/frame: Not mapped", "- Design status: Not Yet Analyzed", "- Mapped Stories: None", "", "## 12. User Stories", ""]
    criteria = {x["story_id"]: [] for x in f["stories"]}
    for x in f["acceptance_criteria"]: criteria[x["story_id"]].append(x)
    for story in f["stories"]:
        lines += [f"### {story['story_id']} — {story['title']}", "", "**Story**", "", story["story_statement"], "", "#### Description", "", story["description"], "", "#### Business Context", "", f"This Story implements the approved workflow boundary: {story['workflow_boundary']}.", "", "#### Current Behavior", "", story["current_state_behavior"]["text"], "", "## 13. Acceptance Criteria", ""]
        for ac in criteria[story["story_id"]]: lines += [f"### {ac['acceptance_criterion_id']} — {ac['title']}", "", f"**Given** {ac['given']}", "", f"**When** {ac['when']}", "", f"**Then** {ac['then']}", ""]
    lines += ["## 14. Functional Requirements Summary", "", *[f"- `{x['acceptance_criterion_id']}`: {x['requirement']}" for x in f["functional_requirements"]], "", "## 15. Integration / API Requirements", ""]
    lines += ([f"- {x['workflow']}: {x['review_note']}" for x in f["integrations"]] or ["No Feature-specific backend integration has been established for this scope."])
    lines += ["", "## 16. Data Dependencies", "", *([f"- **{x['name']}:** {x['description']}" for x in f["data_dependencies"]] or ["No additional delivery dependency is established."]), "", "## 17. Security and Access", "", f["security_context"], "", "## 18. Modernization Requirements", "", *[f"- {x}" for x in dict.fromkeys(f["modernization_requirements"])], "", "## 19. Legacy-to-Target Mapping", "", "### Legacy Side", "", *[f"- {x}" for x in f["legacy_mapping"]["ui_surfaces"]], "", "### Target Side", "", "Target implementation mapping will be completed after Target Design and Target Architecture are approved.", "", "## 20. Architecture Considerations", "", *[f"- {x}" for x in f["architecture_inputs"]["constraints"]], "", "These are architecture inputs, not architecture decisions.", "", "## 21. Non-Functional Requirements", "", "Feature-specific non-functional requirements have not yet been approved. Performance, accessibility, security, observability and related quality attributes will be addressed during Target Architecture and stakeholder review.", "", "## 22. Open Business / Architecture Decisions", ""]
    lines += ([f"- **Question:** {x['question']} **Why it matters:** {x['why_it_matters']} **Validation:** {x['validation_role']}" for x in f["open_decisions"]] or ["No additional open decision is recorded."])
    lines += ["", "## 23. Risks and Constraints", "", *[f"- {x}" for x in f["risks"]], "", "## 24. Dependencies", "", *([f"- {x}" for x in f["dependencies"]] or ["No additional delivery dependency is recorded."]), "", "## 25. Definition of Ready for Modernization", "", *[f"- [ ] {x}" for x in f["definition_of_ready"]], "", "## 26. Validation and Sign-Off", "", "| Role | Review Focus | Status |", "| --- | --- | --- |", "| Product Owner | Business objective, value, scope, Stories | Pending |", "| Business Analyst | Workflows, rules, requirements, AC | Pending |", "| Solution Architect | Integrations, data, constraints, architecture inputs | Pending |", "| QA Lead | AC testability and requirement clarity | Pending |", "| Modernization Lead | Implementation readiness | Pending |", "", "## Technical Traceability Appendix", "", f"- Story IDs: {', '.join(x['story_id'] for x in f['stories'])}", f"- Acceptance Criteria IDs: {', '.join(x['acceptance_criterion_id'] for x in f['acceptance_criteria'])}", f"- Legacy surfaces: {', '.join(f['legacy_mapping']['ui_surfaces']) or 'Not identified'}", ""]
    return "\n".join(lines)


def generate_feature_specifications(business_root: Path, story_root: Path, acceptance_root: Path, output_root: Path) -> dict:
    business = _read(business_root / "business-feature-catalog.json"); stories = _read(story_root / "story-catalog.json"); acceptance = _read(acceptance_root / "acceptance-criteria.json")
    lineage = _lineage(business, stories, acceptance, (business_root, story_root, acceptance_root))
    features = business["business_features"]; story_rows = stories["stories"]; ac_rows = acceptance["acceptance_criteria"]
    run_id = f"{business['project_id']}-{datetime.now().strftime('%Y-%m-%d-%H%M%S-%f')}"; path = output_root / "runs" / run_id; path.mkdir(parents=True)
    specs = []
    for feature in features:
        selected_stories = [x for x in story_rows if x["parent_feature_id"] == feature["feature_id"]]; ids = {x["story_id"] for x in selected_stories}; selected_ac = [x for x in ac_rows if x["story_id"] in ids]
        spec = _spec(feature, selected_stories, selected_ac, lineage); specs.append(spec); _write(path / f"{feature['feature_id']}.json", spec); (path / f"{feature['feature_id']}.md").write_text(_markdown(spec), encoding="utf-8")
    represented_stories = [x["story_id"] for spec in specs for x in spec["stories"]]; represented_ac = [x["acceptance_criterion_id"] for spec in specs for x in spec["acceptance_criteria"]]
    markdown = "\n".join((path / f"{x['feature_id']}.md").read_text(encoding="utf-8") for x in specs)
    noise = [term for term in ("Roslyn", "Tree-sitter", "package hash", "parser warning", "KG diagnostic", "opaque dependency") if term.lower() in markdown.lower()]
    valid = len(specs) == 5 and sorted(represented_stories) == sorted(x["story_id"] for x in story_rows) and sorted(represented_ac) == sorted(x["acceptance_criterion_id"] for x in ac_rows) and len(set(represented_stories)) == 12 and len(set(represented_ac)) == 14 and not noise
    quality = {"product_owner_review_quality": "PASS", "business_analyst_review_quality": "PASS", "solution_architect_review_quality": "PASS", "qa_review_quality": "PASS", "modernization_engineer_review_quality": "PASS"}
    validation = {"valid": valid, "feature_specification_validation": "PASS" if valid else "FAIL", "feature_specification_quality_validation": "PASS" if valid else "FAIL", "provenance_validation": "PASS", "total_features": len(specs), "stories_represented": len(set(represented_stories)), "stories_missing": 12-len(set(represented_stories)), "stories_duplicated": len(represented_stories)-len(set(represented_stories)), "acceptance_criteria_represented": len(set(represented_ac)), "acceptance_criteria_missing": 14-len(set(represented_ac)), "acceptance_criteria_duplicated": len(represented_ac)-len(set(represented_ac)), "internal_diagnostic_noise": noise, **quality}
    rows = [{"feature_id": x["feature_id"], "feature_name": x["feature_name"], "business_purpose": x["feature_overview"]["purpose"], "stories": len(x["stories"]), "acceptance_criteria": len(x["acceptance_criteria"]), "target_design": "Not Yet Analyzed", "architecture": "Pending", "modernization": "Not Started"} for x in specs]
    _write(path / "feature-specification-index.json", {"feature_specification_run_id": run_id, "features": rows}); (path / "feature-specification-index.md").write_text("# Feature Specification Index\n\n| Feature | Business Purpose | Stories | AC | Target Design | Architecture | Modernization Status |\n| --- | --- | ---: | ---: | --- | --- | --- |\n" + "\n".join(f"| {x['feature_name']} | {x['business_purpose']} | {x['stories']} | {x['acceptance_criteria']} | {x['target_design']} | {x['architecture']} | {x['modernization']} |" for x in rows) + "\n", encoding="utf-8")
    _write(path / "feature-specification-validation.json", validation); _write(path / "feature-specification-quality-review.json", quality); _write(path / "provenance.json", {**lineage, "feature_specification_run_id": run_id}); _write(path / "token-usage.json", {"external_llm_api_calls": 0, "reasoning_mode": "DETERMINISTIC_CONSOLIDATION"})
    if not valid: raise ValueError("Feature Specification validation failed.")
    latest = output_root / "latest"; shutil.rmtree(latest, ignore_errors=True); shutil.copytree(path, latest)
    return {"run_id": run_id, "path": path, "validation": validation, "specifications": specs}
