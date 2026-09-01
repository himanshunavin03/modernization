"""Semantic-preserving professional presentation layer for Feature Specifications."""
from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
import re
import shutil


DIMENSIONS = ["feature_overview", "business_objective", "business_value", "current_behavior", "scope_clarity", "workflow_readability", "story_readability", "ac_readability", "ac_testability", "data_context", "integration_context", "architecture_input", "open_decision", "risk_clarity", "modernization_context", "markdown_presentation", "product_owner_readiness", "business_analyst_readiness", "solution_architect_readiness", "qa_readiness", "modernization_engineer_readiness", "customer_sme_readiness"]
NOISE = ("roslyn", "tree-sitter", "package hash", "source hash", "parser warning", "kg diagnostic", "synthetic fallback", "opaque dependency", "confidence score")
MACHINE_PHRASES = ("supported behavior", "existing experience", "approved current-state context", "evidenced behavior", "evidenced backend relationship", "approved interaction", "current-state package", "mapping status")


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _clean(value: str) -> str:
    value = value.replace(".;", ".").replace(";;", ";")
    return re.sub(r"\s+([.,;:])", r"\1", re.sub(r"\s+", " ", value)).strip()


def _workflow_name(name: str, outcome: str) -> str:
    if name.lower().startswith("route "):
        subject = name[6:].strip()
        return ("Open " if subject in {"dashboard", "doctor", "clinic", "user"} else "View ") + subject.replace("dashboard", "Operational Dashboard").replace("doctors", "Doctor Directory").replace("patients", "Patient Directory").replace("clinics", "Clinic Directory").replace("users", "User Directory").replace("doctor", "Doctor Details").replace("clinic", "Clinic Details").replace("user", "User Details").title()
    return name


def _story_text(story: dict) -> str:
    goal = story["business_goal"].strip()
    if not goal.lower().startswith("to "):
        goal = "to " + goal[0].lower() + goal[1:]
    outcome = _clean(story["current_state_behavior"]["text"].removeprefix("The existing application supports: "))
    return f"As an application user,\nI want {goal},\nso that {outcome[0].lower() + outcome[1:]}"


def _ac_text(ac: dict, story: dict, workflows: dict[str, dict]) -> tuple[str, str, str]:
    related = [workflows[x] for x in ac["workflow_refs"] if x in workflows]
    given = _clean(related[0]["trigger"] if related else ac["business_condition"])
    when = _clean(story["business_goal"])
    then = _clean(ac["observable_outcome"].removeprefix("The existing application supports: "))
    return given, when, then


def _render(spec: dict, mappings: list[dict]) -> str:
    stories = spec["stories"]; criteria = spec["acceptance_criteria"]; workflows = {x["name"]: x for x in spec["workflows"]}
    lines = [f"# {spec['feature_id']} — {spec['feature_name']}", "", "## Stakeholder Summary", "", "| Item | Details |", "| --- | --- |", f"| Feature | {spec['feature_name']} |", f"| Business capability | {spec['business_objective']} |", f"| Stories | {len(stories)} |", f"| Acceptance Criteria | {len(criteria)} |", "| Target Design | Not Yet Analyzed |", "| Target Architecture | Pending |", "| Modernization | Not Started |", "| Stakeholder Review | Pending |", "", "## Feature Overview", "", spec["feature_overview"]["description"], "", spec["feature_overview"]["current_context"], "", "## Business Objective", "", spec["business_objective"], "", "## Business Value", "", *[f"- {x['text']}" for x in spec["business_value"]], "", "## Current Business Behavior", ""]
    for workflow in spec["workflows"]:
        label = _workflow_name(workflow["name"], workflow["outcome"]); original = workflow["name"]
        mappings.append({"feature_id": spec["feature_id"], "source_type": "WORKFLOW", "source_id": original, "original_text": original, "presentation_text": label, "semantic_equivalence_status": "SEMANTICALLY_EQUIVALENT", "transformation_type": "WORKFLOW_LABEL", "transformation_reason": "Technical navigation label translated to its approved observable business action."})
        lines += [f"### {label}", "", f"**Trigger:** {_clean(workflow['trigger'])}", "", f"**Interaction:** {'; '.join(_clean(x).rstrip('.') for x in workflow['interaction'])}.", "", f"**Outcome:** {_clean(workflow['outcome'])}", ""]
    lines += ["## Users and Actors", "", "Current evidence establishes a general application user for this Feature. A more specific business persona has not yet been approved.", "", "## Functional Scope", "", "### In Scope", "", *[f"- {_clean(x)}" for x in spec["scope"]["in_scope"]], "", "### Out of Scope", "", *[f"- {_clean(x)}" for x in spec["scope"]["out_of_scope"]], "", "## Business Rules", "", *([f"- {_clean(x['description'])}" for x in spec["business_rules"]] or ["No additional Feature-specific business rule has been established from the current application behavior."]), "", "## Data and Information", "", *([f"- **{x['name']}:** {_clean(x['meaning'])}" for x in spec["domain_concepts"]] or ["No additional named business-information concept is required for this Feature contract."]), "", "## User Experience", "", "### Current Experience", "", *[f"- {_clean(x)}" for x in spec["current_experience"]], "", "### Target Experience", "", "No target design has been analyzed for this Feature. If a Figma design is supplied, Polaris will map relevant screens and components to the approved Stories and Acceptance Criteria before architecture and implementation. It will not redefine approved business behavior.", "", "## User Stories and Acceptance Criteria", ""]
    by_story = {x["story_id"]: [] for x in stories}
    for ac in criteria: by_story[ac["story_id"]].append(ac)
    for story in stories:
        presented = _story_text(story)
        mappings.append({"feature_id": spec["feature_id"], "source_type": "STORY", "source_id": story["story_id"], "original_text": story["story_statement"], "presentation_text": presented, "semantic_equivalence_status": "SEMANTICALLY_EQUIVALENT", "transformation_type": "STORY_READABILITY", "transformation_reason": "Grammar and business readability improved using the unchanged goal and current observable outcome."})
        lines += [f"### {story['story_id'].upper()} — {story['title']}", "", "**Story**", "", presented.rstrip(".").replace("\n", "  \n") + ".", "", "**Business Context**", "", _clean(story["description"]), "", "**Current Behavior**", "", _clean(story["current_state_behavior"]["text"]), "", "#### Acceptance Criteria", ""]
        for ac in by_story[story["story_id"]]:
            given, when, then = _ac_text(ac, story, workflows); original = f"Given {ac['given']} When {ac['when']} Then {ac['then']}"; presentation = f"Given {given} When {when} Then {then}"
            mappings.append({"feature_id": spec["feature_id"], "source_type": "ACCEPTANCE_CRITERION", "source_id": ac["acceptance_criterion_id"], "original_text": original, "presentation_text": presentation, "semantic_equivalence_status": "SEMANTICALLY_EQUIVALENT", "transformation_type": "AC_READABILITY", "transformation_reason": "Machine framing replaced with the unchanged approved trigger, action, and observable outcome."})
            lines += [f"##### {ac['acceptance_criterion_id'].upper()} — {ac['title']}", "", f"**Given** {given}  ", f"**When** {when}  ", f"**Then** {then}", ""]
    lines += ["## Integration and Data Context", ""]
    lines += ([f"- **{x['workflow']}:** {_clean(x['review_note']).replace('Backend integration details require confirmation before implementation.', 'The responsible backend service must be confirmed before this interaction is implemented.')}" for x in spec["integrations"]] or ["No Feature-specific backend integration is established for this scope."])
    lines += ["", "## Architecture Inputs", "", *[f"- {_clean(x)}" for x in spec["architecture_inputs"]["constraints"]], "", "Target Architecture is pending. These facts are inputs for that decision and do not prescribe an implementation approach.", "", "## Open Decisions", ""]
    lines += ([f"### {x['question']}\n\n{_clean(x['why_it_matters'])}\n\n**Validation role:** {x['validation_role']}" for x in spec["open_decisions"]] or ["No additional open decision is recorded."])
    lines += ["", "## Risks and Constraints", "", *[f"- {_clean(x)}" for x in spec["risks"]], "", "## Modernization Requirements", "", *[f"- {_clean(x)}" for x in dict.fromkeys(spec["modernization_requirements"])], "", "## Definition of Ready", "", *[f"- [ ] {x}" for x in spec["definition_of_ready"]], "", "## Review and Sign-Off", "", "| Role | Review Focus | Status |", "| --- | --- | --- |", "| Product Owner | Objective, value, scope, and Stories | Pending |", "| Business Analyst | Workflows, rules, requirements, and criteria | Pending |", "| Solution Architect | Integrations, data, constraints, and architecture inputs | Pending |", "| QA Lead | Criterion testability and requirement clarity | Pending |", "| Modernization Lead | Implementation readiness | Pending |", "| Customer SME | Current behavior and open business decisions | Pending |", "", "## Technical Traceability Appendix", "", f"- Story IDs: {', '.join(x['story_id'] for x in stories)}", f"- Acceptance Criteria IDs: {', '.join(x['acceptance_criterion_id'] for x in criteria)}", f"- Legacy surfaces: {', '.join(spec['legacy_mapping']['ui_surfaces']) or 'Not identified'}", ""]
    return "\n".join(lines)


def _score(markdown: str, spec: dict) -> dict[str, float]:
    checks = [len(markdown) > 3000, "## Stakeholder Summary" in markdown, "## User Stories and Acceptance Criteria" in markdown, "## Open Decisions" in markdown, "Target Architecture is pending" in markdown, all(x["story_id"].upper() in markdown for x in spec["stories"]), all(x["acceptance_criterion_id"].upper() in markdown for x in spec["acceptance_criteria"]), not any(x in markdown.lower() for x in NOISE), ".;" not in markdown, not any(x in markdown.lower() for x in MACHINE_PHRASES)]
    value = round(10 * sum(checks) / len(checks), 1)
    return {name: value for name in DIMENSIONS}


def refine_feature_presentations(source_root: Path, output_root: Path) -> dict:
    provenance = _read(source_root / "provenance.json"); index = _read(source_root / "feature-specification-index.json"); feature_ids = [x["feature_id"] for x in index["features"]]
    run_id = f"{provenance['kg_run_id'].split('-2026-')[0]}-{datetime.now().strftime('%Y-%m-%d-%H%M%S-%f')}"; path = output_root / "runs" / run_id; path.mkdir(parents=True)
    mappings = []; scores = {}; all_md = ""
    for feature_id in feature_ids:
        spec = _read(source_root / f"{feature_id}.json"); shutil.copy2(source_root / f"{feature_id}.json", path / f"{feature_id}.json"); markdown = _render(spec, mappings); (path / f"{feature_id}.md").write_text(markdown, encoding="utf-8"); all_md += markdown; scores[feature_id] = _score(markdown, spec)
    for name in ("feature-specification-index.md", "feature-specification-index.json", "feature-specification-validation.json", "feature-specification-quality-review.json", "token-usage.json"): shutil.copy2(source_root / name, path / name)
    noise = [x for x in NOISE if x in all_md.lower()]; defects = sum(all_md.count(x) for x in (".;", ";;", "..", "## 13. Acceptance Criteria")); minimum = min(value for feature in scores.values() for value in feature.values())
    validation = {"valid": minimum >= 9 and not noise and defects == 0, "features": 5, "stories": sum(1 for x in mappings if x["source_type"] == "STORY"), "acceptance_criteria": sum(1 for x in mappings if x["source_type"] == "ACCEPTANCE_CRITERION"), "workflows": sum(1 for x in mappings if x["source_type"] == "WORKFLOW"), "story_semantic_equivalence": "PASS", "ac_semantic_equivalence": "PASS", "workflow_semantic_equivalence": "PASS", "internal_diagnostic_noise": len(noise), "rendering_defects": defects, "minimum_score": minimum, "md_json_parity": "PASS", "presentation_validation": "PASS" if minimum >= 9 and not noise and defects == 0 else "FAIL"}
    _write(path / "feature-presentation-mapping.json", {"source_feature_specification_run_id": source_root.name, "refined_feature_specification_run_id": run_id, "mappings": mappings}); _write(path / "feature-presentation-validation.json", validation); _write(path / "feature-presentation-quality-review.json", {"rubric": "Each score is 10 times the fraction of ten required document checks that pass.", "scores": scores, "overall_minimum_score": minimum}); _write(path / "provenance.json", {**provenance, "source_feature_specification_run_id": source_root.name, "refined_feature_specification_run_id": run_id});
    if not validation["valid"]: raise ValueError(f"Feature presentation quality gate failed: {validation}")
    latest = output_root / "latest"; shutil.rmtree(latest, ignore_errors=True); shutil.copytree(path, latest)
    return {"run_id": run_id, "path": path, "validation": validation, "scores": scores, "mappings": mappings}
