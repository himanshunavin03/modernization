"""Human-readable delivery view derived from the machine Feature model."""
from __future__ import annotations

import re


FORBIDDEN_TERMS = {
    "polaris_terms": ("polaris",),
    "kg_terms": ("knowledge graph", "kg node", "kg relationship"),
    "analyzer_terms": ("tree-sitter", "roslyn", " lsp ", "analyzer", "parser", "angularjs", "razor"),
    "resolver_classifications": (
        "proven_exact_static",
        "proven_exact_template",
        "proven_unique_parameterized",
        "proven_framework_semantic",
        "dynamic_primary",
        "unresolved_primary",
    ),
    "evidence_jargon": (
        "evidence package",
        "evidence basis",
        "evidence quality",
        "evidence limitation",
        "source hash",
        "source range",
        "provenance",
        "deterministic classification",
        "relationship candidate",
        "resolver",
        "evidence",
        "proven",
        "mapping",
        "legacy",
        "modernization",
    ),
}


def _plain(value: str) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    replacements = (
        (r"\b[Tt]he current application\b", "The application"),
        (r"\bthe current application\b", "the application"),
        (r"\bcurrently established behaviors\b", "defined behaviors"),
        (r"\bexisting\s+", ""),
        (r"\bestablished\s+", ""),
        (r"\bapproved\s+", ""),
        (r"\bcurrent-state\s+", ""),
        (r"\bmodernized experience\b", "feature"),
        (r"\bmodernization\b", "delivery"),
        (r"\blegacy implementation technology\b", "implementation technology"),
        (r"\bevidenced backend relationship status\b", "specified backend integration"),
        (r"\bsupported by the application\b", "provided by the application"),
        (r"\bcurrent evidence establishes the capability but not its specific business purpose\b", "the specific business purpose requires stakeholder confirmation"),
        (r"\bcurrently capability\b", "capability"),
        (r"\bcurrently behaviors\b", "defined behaviors"),
        (r"\bcurrent primary behaviors\b", "defined behaviors"),
        (r"\b[A-Za-z]+ Razor and AngularJS surfaces\b", "User-facing experience"),
        (r"\bUI surfaces\b", "user interface"),
        (r"\bdomain concept\b", "information"),
        (r"\btenant-context mappings\b", "tenant context"),
        (r"\bAPI relationships\b", "API integrations"),
        (r"\bend-to-end mapping\b", "specified integration"),
        (r"\bresolution by assumption of unresolved mappings\b", "unspecified integrations"),
        (r"\bcontract preservation\b", "API contracts"),
        (r"\bnot supported by workflows\b", "not defined in this specification"),
        (r"\binferred meaning\b", "unspecified meaning"),
        (r"\bproven\s+", ""),
    )
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, flags=re.I)
    return re.sub(r"\s+", " ", text).strip()


def _sentence(value: str) -> str:
    text = _plain(value).strip().rstrip(".")
    return (text[:1].upper() + text[1:] + ".") if text else ""


def _story_statement(value: str) -> str:
    text = _plain(value)
    text = re.sub(r"\s*Business outcome:.*$", "", text, flags=re.I).strip()
    match = re.match(r"As an application user,\s*I want to (.+?)(?:,\s*so that (.+))?\.?$", text, re.I)
    if not match:
        return text
    goal = match.group(1).rstrip(".,")
    outcome = (match.group(2) or "I can use the information and functions provided by this feature").rstrip(".")
    return f"As an application user,\nI want to {goal},\nso that {outcome}."


def _path_parameters(endpoint: str) -> list[str]:
    return list(dict.fromkeys(re.findall(r"\{([^}:]+)(?::[^}]+)?\}", endpoint or "")))


def _metadata_label(value: object) -> str:
    if not isinstance(value, dict):
        return str(value)
    name = value.get("name") or value.get("property") or value.get("field")
    data_type = value.get("type") or value.get("data_type")
    if name and data_type:
        return f"{name} ({data_type})"
    return str(name or data_type or "field")


def _api_requirements(model: dict) -> tuple[list[dict], dict[str, str]]:
    contracts = {item["contract_id"]: item for item in model["existing_api_contracts"]}
    grouped: dict[tuple[str, str], dict] = {}
    interaction_to_api: dict[str, str] = {}
    story_titles = {item["id"]: item["title"] for item in model["requirements"]}
    for interaction in model["api_interactions"]:
        backend = interaction["backend"]
        method = backend.get("http_method") or interaction["frontend"].get("method")
        endpoint = backend.get("resolved_endpoint") or interaction["frontend"].get("api_expression")
        if not method or not endpoint:
            continue
        endpoint = str(endpoint).replace("`", "")
        key = (str(method).upper(), endpoint)
        item = grouped.setdefault(key, {
            "source_interaction_ids": [],
            "method": key[0],
            "endpoint": endpoint,
            "story_ids": [],
            "path_parameters": [],
            "query_parameters": [],
            "request_type": None,
            "request_fields": [],
            "response_type": None,
            "response_fields": [],
            "supporting": True,
        })
        item["source_interaction_ids"].append(interaction["interaction_id"])
        item["story_ids"].extend(interaction.get("story_ids", []))
        item["supporting"] = item["supporting"] and "SUPPORTING" in interaction["classification"]
        item["path_parameters"].extend(backend.get("path_parameters", []))
        item["query_parameters"].extend(backend.get("query_parameters", []))
        item["request_type"] = backend.get("request_type")
        item["request_fields"].extend(backend.get("request_fields", []))
        item["response_type"] = backend.get("response_type")
        item["response_fields"].extend(backend.get("response_fields", []))
        contract = contracts.get(interaction["interaction_id"])
        if contract:
            request, response = contract["request"], contract["response"]
            item["path_parameters"].extend(x["name"] for x in request.get("path_parameters", []))
            item["query_parameters"].extend(x["name"] for x in request.get("query_parameters", []))
            item["request_type"] = request.get("body_type")
            item["request_fields"].extend(request.get("body_fields", []))
            item["response_type"] = response.get("response_type")
            item["response_fields"].extend(response.get("response_fields", []))
        item["path_parameters"].extend(_path_parameters(endpoint))
    result = []
    for number, item in enumerate(grouped.values(), 1):
        api_id = f"API-{number:02d}"
        item["id"] = api_id
        item["story_ids"] = list(dict.fromkeys(item["story_ids"]))
        item["used_by"] = [story_titles[x] for x in item["story_ids"] if x in story_titles]
        for name in ("path_parameters", "query_parameters", "request_fields", "response_fields"):
            item[name] = list(dict.fromkeys(_metadata_label(value) for value in item[name]))
        item["purpose"] = "Supports " + ", ".join(item["used_by"]) + "."
        if item["supporting"]:
            item["purpose"] = "Provides shared context for " + ", ".join(item["used_by"]) + "."
        for source_id in item["source_interaction_ids"]:
            interaction_to_api[source_id] = api_id
        result.append(item)
    return result, interaction_to_api


def build_human_presentation(model: dict) -> dict:
    apis, interaction_to_api = _api_requirements(model)
    clarifications = []
    for number, item in enumerate(model["stakeholder_enrichment_items"], 1):
        question = _plain(item["question"])
        question = re.sub(r" beyond access to the capability\?", "?", question, flags=re.I)
        question = re.sub(r" in the feature\?", "?", question, flags=re.I)
        clarifications.append({
            "id": f"Q-{number:02d}",
            "question": question,
            "owner": item["recommended_owner"].replace("Modernization Engineer", "Development Lead"),
            "required_before": "Development and QA completion" if item["impact_if_unresolved"] == "BLOCKING" else "Final stakeholder approval",
            "source_id": item["id"],
            "story_id": item.get("story_id"),
            "ac_id": item.get("ac_id"),
        })
    requirements, stories, criteria = [], [], []
    behavior_by_story = {item["story_id"]: item for item in model["functional_behavior"]}
    ac_number = 1
    for number, story in enumerate(model["requirements"], 1):
        fr_id, us_id = f"FR-{number:02d}", f"US-{number:02d}"
        behavior = behavior_by_story[story["id"]]
        story_criteria = []
        flow = []
        for ac in story["acceptance_criteria"]:
            ac_id = f"AC-{ac_number:02d}"
            ac_number += 1
            presentation = ac["customer_presentation"]
            if isinstance(presentation, dict):
                given = _sentence(presentation["given"])
                when = _sentence(presentation["when"])
                then = _sentence(presentation["then"])
            else:
                given = "The feature behavior is ready for delivery."
                when = "The feature is implemented."
                then = "The behavior and backend integrations defined in this specification remain available."
            criterion = {
                "id": ac_id,
                "title": _plain(ac["title"]).replace(" Behavior", "").replace(" Preservation", " Delivery"),
                "given": given,
                "when": when,
                "then": then,
                "source_ac_id": ac["id"],
            }
            criteria.append(criterion)
            story_criteria.append(criterion)
        functional = next((x for x in story_criteria if "Delivery" not in x["title"]), story_criteria[0])
        flow = [functional["given"], functional["when"], *[x.strip().capitalize() + "." for x in functional["then"].rstrip(".").split("; and ")]]
        api_ids = list(dict.fromkeys(interaction_to_api[x] for x in story["api_contract_ids"] if x in interaction_to_api))
        question_ids = [x["id"] for x in clarifications if x["story_id"] == story["id"]]
        requirements.append({
            "id": fr_id,
            "title": story["title"],
            "requirement": _sentence(behavior["statement"]),
            "functional_flow": flow,
            "api_ids": api_ids,
            "clarification_ids": question_ids,
            "source_story_id": story["id"],
        })
        stories.append({"id": us_id, "title": story["title"], "statement": _story_statement(story["statement"]), "source_story_id": story["id"]})
    rules = [
        {"id": f"BR-{number:02d}", "rule": _sentence(item["description"]), "source_rule_id": item["id"]}
        for number, item in enumerate(model.get("business_rules", []), 1)
    ]
    summary = model["summary"]
    business_value = summary["business_value"].replace(
        "Specific stakeholder outcomes for one or more access capabilities are not established and require confirmation.",
        "Additional business value requires confirmation from Product Owner / Business SME.",
    )
    business_value = _plain(business_value)
    if summary["business_value_status"] == "REQUIRES_STAKEHOLDER_ENRICHMENT":
        business_value = business_value or "Requires confirmation from Product Owner / Business SME."
    capabilities = [_sentence(item["statement"]) for item in model["functional_behavior"]]
    objective = _sentence(summary["purpose"])
    if model["feature_name_behavior_alignment"]["feature_name_terms_not_established_by_primary_behaviors"]:
        objective = re.sub(r"^The application makes (.+?) available to users\.$", r"Provide \1.", capabilities[0])
        if any("current tenant context" in item.lower() for item in capabilities[1:]):
            objective = objective.rstrip(".") + " within current tenant context."
    return {
        "feature": {"name": model["feature_header"]["name"], "source_feature_id": model["feature_id"]},
        "overview": {
            "objective": objective,
            "capabilities": capabilities,
            "business_value": business_value,
        },
        "functional_requirements": requirements,
        "stories": stories,
        "acceptance_criteria": criteria,
        "api_requirements": apis,
        "business_rules": rules,
        "clarifications": clarifications,
        "scope": {
            "in_scope": [_plain(x) for x in model["scope"]["in_scope"]],
            "out_of_scope": [_plain(x) for x in model["scope"]["out_of_scope"]],
        },
    }


def render_human_markdown(presentation: dict) -> str:
    overview = presentation["overview"]
    lines = [
        f"# {presentation['feature']['name']}", "",
        "## 1. Feature Overview", "", "### Objective", "", overview["objective"], "",
        "### Feature Capabilities", "", *[f"- {x}" for x in overview["capabilities"]], "",
        "### Business Value", "", overview["business_value"], "",
        "### Scope", "", "**In Scope**", "", *[f"- {x}" for x in presentation["scope"]["in_scope"]], "",
    ]
    if presentation["scope"]["out_of_scope"]:
        lines += ["**Out of Scope**", "", *[f"- {x}" for x in presentation["scope"]["out_of_scope"]], ""]
    lines += ["## 2. Functional Requirements", ""]
    api_by_id = {item["id"]: item for item in presentation["api_requirements"]}
    questions_by_id = {item["id"]: item for item in presentation["clarifications"]}
    for requirement in presentation["functional_requirements"]:
        lines += [f"### {requirement['id']} - {requirement['title']}", "", "#### Requirement", "", requirement["requirement"], "", "#### Functional Flow", ""]
        lines += [f"{number}. {step}" for number, step in enumerate(requirement["functional_flow"], 1)] + [""]
        if requirement["api_ids"]:
            lines += ["#### API Integration", ""]
            for api_id in requirement["api_ids"]:
                api = api_by_id[api_id]
                lines += [f"- **{api_id}:** `{api['method']} {api['endpoint']}` - {api['purpose']}"]
            lines += [""]
        if requirement["clarification_ids"]:
            lines += ["#### Clarification Required", "", *[f"- **{qid}:** {questions_by_id[qid]['question']}" for qid in requirement["clarification_ids"]], ""]
    lines += ["## 3. User Stories", ""]
    for story in presentation["stories"]:
        lines += [f"### {story['id']} - {story['title']}", "", story["statement"].replace("\n", "\n\n"), ""]
    lines += ["## 4. Acceptance Criteria", ""]
    for criterion in presentation["acceptance_criteria"]:
        lines += [f"### {criterion['id']} - {criterion['title']}", "", f"**Given** {criterion['given']}", "", f"**When** {criterion['when']}", "", f"**Then** {criterion['then']}", ""]
    if presentation["api_requirements"]:
        lines += ["## 5. API Requirements", ""]
        for api in presentation["api_requirements"]:
            lines += [f"### {api['id']} - {', '.join(api['used_by'])}", "", f"**Method:** `{api['method']}`", "", f"**Endpoint:** `{api['endpoint']}`", "", f"**Purpose:** {api['purpose']}", ""]
            inputs = [f"`{x}` - path parameter" for x in api["path_parameters"]] + [f"`{x}` - query parameter" for x in api["query_parameters"]]
            if api["request_type"]:
                inputs.append(f"Request body: `{api['request_type']}`")
            if inputs:
                lines += ["**Required Input**", "", *[f"- {x}" for x in inputs], ""]
            if api["request_fields"]:
                lines += ["**Request Fields**", "", *[f"- `{x}`" for x in api["request_fields"]], ""]
            if api["response_type"]:
                lines += [f"**Expected Result:** `{api['response_type']}`", ""]
            if api["response_fields"]:
                lines += ["**Response Fields**", "", *[f"- `{x}`" for x in api["response_fields"]], ""]
            lines += [f"**Used By:** {', '.join(api['used_by'])}", ""]
    if presentation["business_rules"]:
        lines += ["## 6. Business Rules", ""]
        for rule in presentation["business_rules"]:
            lines += [f"### {rule['id']}", "", rule["rule"], ""]
    section = 7 if presentation["business_rules"] else 6
    lines += [f"## {section}. Development Requirements", "", "- Implement the functional requirements defined in this specification.", "- Integrate with the listed backend APIs and supply each documented input.", "- Make the returned information available to the applicable feature behavior.", "- Maintain the documented user and tenant context.", "- Satisfy every acceptance criterion.", ""]
    section += 1
    if presentation["clarifications"]:
        lines += [f"## {section}. Clarifications Required", "", "| ID | Question | Owner | Required Before |", "| --- | --- | --- | --- |"]
        lines += [f"| {x['id']} | {x['question']} | {x['owner']} | {x['required_before']} |" for x in presentation["clarifications"]] + [""]
        section += 1
    lines += [f"## {section}. Definition of Done", "", "- [ ] All functional requirements in this specification are implemented.", "- [ ] All listed APIs are integrated with their documented inputs.", "- [ ] All documented business rules are satisfied." if presentation["business_rules"] else "- [ ] The behavior stays within the documented scope.", "- [ ] All acceptance criteria pass.", "- [ ] Blocking clarifications are resolved.", "- [ ] QA validation is complete.", ""]
    section += 1
    lines += [f"## {section}. Review and Approval", "", "| Role | Review Responsibility | Status |", "| --- | --- | --- |", "| Product Owner | Objective, business value, scope, and priorities | Pending |", "| Business Analyst | Functional requirements, rules, Stories, and clarifications | Pending |", "| Solution Architect | API contracts, inputs, and integration boundaries | Pending |", "| Development Lead | Implementation clarity and delivery feasibility | Pending |", "| QA Lead | Acceptance Criteria and validation coverage | Pending |", "| Customer SME | Business terminology and unresolved decisions | Pending |", ""]
    return "\n".join(lines)


def audit_human_markdown(markdown: str) -> dict[str, int]:
    lowered = f" {markdown.lower()} "
    result = {name: sum(lowered.count(term) for term in terms) for name, terms in FORBIDDEN_TERMS.items()}
    result["source_file_paths"] = len(re.findall(r"\b(?:src|source)/[^\s`)]+", markdown, re.I))
    result["source_line_references"] = len(re.findall(r"(?:\bline\s+\d+|:[Ll]\d+\b)", markdown))
    return result
