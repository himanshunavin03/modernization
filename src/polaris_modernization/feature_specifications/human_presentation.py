"""BA/SA-readable delivery view derived from the machine Feature model."""
from __future__ import annotations

import re


FORBIDDEN_TERMS = {
    "polaris_terms": ("polaris",),
    "kg_terms": ("knowledge graph", "kg node", "kg relationship"),
    "analyzer_terms": ("tree-sitter", "roslyn", " lsp ", "analyzer", "parser", "angularjs", "razor"),
    "resolver_terms": ("resolver", "proven_exact_static", "proven_exact_template", "proven_unique_parameterized", "proven_framework_semantic", "dynamic_primary", "unresolved_primary"),
    "evidence_jargon": ("evidence package", "evidence basis", "evidence quality", "evidence limitation", "source hash", "source range", "provenance", "deterministic classification", "relationship candidate", "evidence", "proven", "mapping"),
    "legacy_implementation_language": ("old application", "legacy application", "previous application", "previous frontend", "modernization", "migration", "source file", "source code", "legacy", "current-state", "existing application"),
}


def _plain(value: object) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    replacements = (
        (r"\b[Tt]he (?:current|existing) application\b", "The application"),
        (r"\bthe (?:current|existing) application\b", "the application"),
        (r"\b(?:existing|established|approved|current-state)\s+", ""),
        (r"\bmodernized experience\b", "feature"),
        (r"\bmodernization\b", "delivery"),
        (r"\btenant context\b", "organization context"),
        (r"\btenant-aware\b", "organization-specific"),
        (r"\btenant-scoped\b", "organization-specific"),
        (r"\btenant-context\b", "organization-context"),
        (r"\bUI surfaces\b", "user interface"),
        (r"\bUI areas\b", "user interface areas"),
        (r"\bAPI relationships\b", "API integrations"),
        (r"\bdatabase migration\b", "database redesign"),
        (r"\bend-to-end mapping\b", "specified integration"),
        (r"\bresolution by assumption of unresolved mappings\b", "unspecified integrations"),
        (r"\bdelivery of unrelated\b", "unrelated"),
        (r"\bnot supported by workflows\b", "not defined in this specification"),
        (r"\binferred meaning\b", "unspecified meaning"),
        (r"\bneeds\b", "requires"),
        (r"\bproven\s+", ""),
    )
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, flags=re.I)
    return re.sub(r"\s+", " ", text).strip()


def _sentence(value: object) -> str:
    text = _plain(value).strip().rstrip(".")
    return (text[:1].upper() + text[1:] + ".") if text else ""


def _words(value: str) -> str:
    return re.sub(r"[_-]+", " ", re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", value or "")).strip()


def _singular(value: str) -> str:
    return value[:-1] if value.endswith("s") and not value.endswith("ss") else value


def _join(items: list[str]) -> str:
    items = list(dict.fromkeys(item for item in items if item))
    if len(items) < 2:
        return "".join(items)
    return " and ".join(items) if len(items) == 2 else ", ".join(items[:-1]) + ", and " + items[-1]


def _path_parameters(endpoint: str) -> list[str]:
    return list(dict.fromkeys(re.findall(r"\{([^}:]+)(?::[^}]+)?\}", endpoint or "")))


def _metadata_label(value: object) -> str:
    if not isinstance(value, dict):
        return str(value)
    name = value.get("name") or value.get("property") or value.get("field")
    data_type = value.get("type") or value.get("data_type")
    return f"{name} ({data_type})" if name and data_type else str(name or data_type or "field")


def _unwrap_response(value: object) -> tuple[str | None, bool]:
    raw = str(value or "").strip()
    if not raw:
        return None, False
    match = re.fullmatch(r"(?:Task|ValueTask)<(.+)>", raw)
    if match:
        raw = match.group(1).strip()
    collection = False
    match = re.fullmatch(r"(?:IEnumerable|ICollection|IList|List|Collection)<(.+)>", raw)
    if match:
        raw, collection = match.group(1).strip(), True
    if raw.endswith("[]"):
        raw, collection = raw[:-2], True
    return raw.rstrip("?"), collection


def _story_subject(titles: list[str]) -> str | None:
    stop = {"access", "view", "review", "open", "resolve", "establish", "current", "yearly", "operational", "management", "information", "details", "detail", "directory", "summary", "context", "functions", "views"}
    for title in titles:
        words = [word for word in re.findall(r"[A-Za-z]+", title) if word.lower() not in stop]
        if words:
            return words[0]
    return None


def _response_details(response_type: object, endpoint: str, story_titles: list[str]) -> dict:
    model, collection = _unwrap_response(response_type)
    route = endpoint.lower().rstrip("/")
    special = {
        "/current/tenant": ("Current organization identifier", "organization"),
        "/current/user": ("Current user identifier", "user"),
        "/current/claims": ("Current user claims", "claims"),
    }
    for suffix, (description, subject) in special.items():
        if route.endswith(suffix):
            return {"model": model, "collection": False, "description": description, "subject": subject}
    model_words = _words(model or "result")
    root = _singular(re.sub(r"\s+Summary$", "", model_words, flags=re.I).lower())
    if root == "tenant":
        root = (_story_subject(story_titles) or "organization").lower()
    if model_words.lower().endswith("summary"):
        description = f"{root} summary information"
    elif collection:
        description = f"collection of {root} records"
    else:
        description = f"{root} information"
    return {"model": model, "collection": collection, "description": description.capitalize(), "subject": root}


def _operation(api: dict) -> dict:
    route = api["endpoint"].lower().rstrip("/")
    response = _response_details(api["response_type"], api["endpoint"], api["used_by"])
    subject = response["subject"]
    if route.endswith("/current/tenant"):
        title, kind = "Establish Organization Context", "context"
    elif route.endswith("/current/user"):
        title, kind = "Resolve Current User Identity", "identity"
    elif route.endswith("/current/claims"):
        title, kind = "Resolve Current User Claims", "identity"
    elif "year" in api["path_parameters"]:
        title, kind = f"View Yearly {subject.title()} Information", "report"
    elif response["collection"]:
        title, kind = f"Review {subject.title()} Directory", "directory"
    elif api["path_parameters"]:
        title, kind = f"View {subject.title()} Details", "detail"
    elif "summary" in str(api["response_type"]).lower():
        title, kind = f"View {subject.title()} Summary", "summary"
    else:
        title, kind = f"Access {subject.title()} Information", "data"
    inputs = []
    for value in api["path_parameters"]:
        name = value.split(" ", 1)[0]
        description = "selected reporting year" if name.lower() == "year" else _words(name).lower()
        if name.lower() == "id":
            description = subject + " identifier"
        elif name.lower() == "tenantid":
            description = "organization identifier"
        elif name.lower().endswith("id"):
            description = _words(name[:-2]).lower() + " identifier"
        inputs.append({"name": value, "location": "Path", "description": description})
    for value in api["query_parameters"]:
        name = value.split(" ", 1)[0]
        descriptions = {"pagesize": "number of records per page", "pagecount": "page count"}
        inputs.append({"name": value, "location": "Query", "description": descriptions.get(name.lower(), _words(name).lower())})
    if kind == "context":
        purpose = "Retrieve the current organization identifier required by organization-specific functionality."
    elif kind == "identity":
        purpose = f"Retrieve {response['description'].lower()} for shared application functions."
    elif inputs:
        preposition = "for" if any(x["name"].split(" ", 1)[0].lower() == "year" for x in inputs) else "using"
        purpose = f"Retrieve {response['description'].lower()} {preposition} the {_join([x['description'] for x in inputs])}."
    else:
        purpose = f"Retrieve {response['description'].lower()} for the corresponding feature function."
    return {**api, **response, "title": title, "kind": kind, "inputs": inputs, "purpose": purpose}


def _api_requirements(model: dict) -> tuple[list[dict], dict[str, str]]:
    contracts = {item["contract_id"]: item for item in model["existing_api_contracts"]}
    story_titles = {item["id"]: item["title"] for item in model["requirements"]}
    grouped: dict[tuple[str, str], dict] = {}
    interaction_to_api: dict[str, str] = {}
    for interaction in model["api_interactions"]:
        backend = interaction["backend"]
        method = backend.get("http_method") or interaction["frontend"].get("method")
        endpoint = backend.get("resolved_endpoint") or interaction["frontend"].get("api_expression")
        if not method or not endpoint:
            continue
        endpoint = str(endpoint).replace("`", "")
        key = (str(method).upper(), endpoint)
        item = grouped.setdefault(key, {"source_interaction_ids": [], "method": key[0], "endpoint": endpoint, "story_ids": [], "path_parameters": [], "query_parameters": [], "request_type": None, "request_fields": [], "response_type": None, "response_fields": [], "supporting": True})
        item["source_interaction_ids"].append(interaction["interaction_id"])
        item["story_ids"].extend(interaction.get("story_ids", []))
        item["supporting"] = item["supporting"] and "SUPPORTING" in interaction["classification"]
        for name in ("path_parameters", "query_parameters", "request_fields", "response_fields"):
            item[name].extend(backend.get(name, []))
        for name in ("request_type", "response_type"):
            item[name] = backend.get(name) or item[name]
        contract = contracts.get(interaction["interaction_id"])
        if contract:
            request, response = contract["request"], contract["response"]
            item["path_parameters"].extend(x["name"] for x in request.get("path_parameters", []))
            item["query_parameters"].extend(x["name"] for x in request.get("query_parameters", []))
            item["request_type"] = request.get("body_type") or item["request_type"]
            item["request_fields"].extend(request.get("body_fields", []))
            item["response_type"] = response.get("response_type") or item["response_type"]
            item["response_fields"].extend(response.get("response_fields", []))
        item["path_parameters"].extend(_path_parameters(endpoint))
    result = []
    for number, item in enumerate(grouped.values(), 1):
        item["id"] = f"API-{number:02d}"
        item["story_ids"] = list(dict.fromkeys(item["story_ids"]))
        item["used_by"] = [story_titles[x] for x in item["story_ids"] if x in story_titles]
        for name in ("path_parameters", "query_parameters", "request_fields", "response_fields"):
            item[name] = list(dict.fromkeys(_metadata_label(value) for value in item[name]))
        realized = _operation(item)
        for source_id in item["source_interaction_ids"]:
            interaction_to_api[source_id] = item["id"]
        result.append(realized)
    return result, interaction_to_api


def _story_goal(statement: str) -> str:
    goal = _plain(statement).strip().rstrip(".")
    replacements = (
        (r"^Access year-dependent (.+?) reporting information$", r"view \1 information for a selected year"),
        (r"^Access (.+?) (?:in|with) current organization context$", r"view \1 for my organization"),
        (r"^Access the (.+?) directory$", r"review the \1 directory"),
        (r"^Access (.+?) list and detail views$", r"view \1 list and details"),
        (r"^Access (.+(?:information|views|details))$", r"view \1"),
        (r"^view the (.+?) information views$", r"view \1 information"),
        (r"^Obtain organization context for (.+)$", r"make organization context available to \1"),
        (r"^Make current organization context available to (.+)$", r"make organization context available to \1"),
        (r"^Open the (.+)$", r"open the \1"),
    )
    for pattern, replacement in replacements:
        goal = re.sub(pattern, replacement, goal, flags=re.I)
    return goal[:1].lower() + goal[1:]


def _action_phrase(title: str) -> str:
    match = re.match(r"(Open|Access|View|Review)\s+(.+)", title)
    if not match:
        return title.lower()
    verb, subject = match.groups()
    verb = "access" if verb == "Open" else verb.lower()
    article = "the " if verb in {"access", "review"} else ""
    return f"{verb} {article}{subject.lower()}"


def _story_outcome(semantic: dict, apis: list[dict]) -> str | None:
    if semantic["business_value_status"] == "NOT_ESTABLISHED":
        return None
    data = [api for api in apis if api["kind"] not in {"context", "identity"}]
    context = [api for api in apis if api["kind"] == "context"]
    if any(any(item["name"].split(" ", 1)[0].lower() == "year" for item in api["inputs"]) for api in data):
        return "I can review information for the required reporting period"
    if data and context:
        return "I can review information relevant to the organization I am working with"
    if context:
        return "the applicable functions use the required organization context"
    if any(api["kind"] == "identity" for api in apis):
        return "shared application functions receive the required identity and claims context"
    return None


def _navigation_requirement(story: dict, behavior: dict) -> dict:
    title = re.sub(r"^Open\s+", "Access ", re.sub(r"\bExisting\b\s*", "", story["title"], flags=re.I))
    subject = re.sub(r"^(?:Open|Access|View|Review)\s+", "", title, flags=re.I).lower()
    return {"title": title, "requirement": f"The user must be able to {_action_phrase(title)}.", "functional_steps": [_sentence(story["acceptance_criteria"][0]["customer_presentation"]["given"]), f"The user requests access to the {subject}.", f"The {subject} becomes available to the user."], "api_ids": [], "source_story_ids": [story["id"]], "source_behavior_ids": [behavior["concept_id"]]}


def _api_requirement(api: dict, behavior_ids: list[str]) -> dict:
    if api["kind"] in {"context", "identity"}:
        requirement = f"The application must {api['purpose'][0].lower() + api['purpose'][1:]}"
        verb = "are" if api["description"].lower().endswith("claims") else "is"
        steps = [f"{api['description']} {verb} required by the applicable functionality.", f"The application calls `{api['method']} {api['endpoint']}`.", f"{api['description']} {verb} returned and made available to the applicable functionality."]
    else:
        requirement = f"The user must be able to {_action_phrase(api['title'])}."
        steps = [f"The user requests {api['description'].lower()}."]
        if api["inputs"]:
            steps.append(f"The application supplies the {_join([item['description'] for item in api['inputs']])}.")
        steps += [f"The application calls `{api['method']} {api['endpoint']}`.", f"{api['description']} is returned and made available to the user."]
    return {"title": api["title"], "requirement": requirement, "functional_steps": steps, "api_ids": [api["id"]], "source_story_ids": api["story_ids"], "source_behavior_ids": behavior_ids}


def _question_for_api(api: dict) -> str:
    subject = api["subject"]
    templates = {
        "report": f"Which {subject} fields and metrics must be displayed for the selected reporting year?",
        "directory": f"Which {subject} fields must be displayed in the directory?",
        "detail": f"Which {subject} fields must be displayed in the detail view?",
        "summary": f"Which {subject} information must be displayed in the summary?",
    }
    return templates.get(api["kind"], f"Which {subject} information must be available to the user?")


def _clarifications(model: dict, apis: list[dict]) -> list[dict]:
    story_titles = {item["id"]: item["title"] for item in model["requirements"]}
    result = []
    for source in model["stakeholder_enrichment_items"]:
        story_id = source.get("story_id")
        title = story_titles.get(story_id, model["feature_header"]["name"])
        if source["category"] == "BUSINESS_VALUE":
            questions = [(f"What business outcome should {title} support?", None)]
        elif source["category"] == "DATA_REQUIREMENT":
            evidence = _plain(source.get("current_evidence", "")).lower()
            candidates = [api for api in apis if api["kind"] not in {"context", "identity"}]
            if "detail" in evidence or "directory" in evidence or " list " in f" {evidence} ":
                selected = []
                if "detail" in evidence:
                    selected += [api for api in candidates if api["kind"] == "detail"]
                if "directory" in evidence or " list " in f" {evidence} ":
                    selected += [api for api in candidates if api["kind"] == "directory"]
                candidates = selected
            else:
                matched = [api for api in candidates if any(word in evidence for word in api["subject"].split())]
                candidates = matched
            questions = [(_question_for_api(api), api["id"]) for api in candidates]
            if not questions:
                access = re.search(r"user can access (?:the )?(.+?)(?: is available)?$", evidence)
                question = f"What information must be available when users access the {access.group(1)}?" if access else f"What information and presentation details are required for {title}?"
                questions = [(question, None)]
        else:
            question = re.sub(r"\b(?:currently )?(?:defined )?behaviors\b", "defined scope", _plain(source["question"]), flags=re.I)
            question = re.sub(r"or should the scope/name remain limited to the defined scope", "or should the Feature remain limited to the defined scope", question, flags=re.I)
            questions = [(question, None)]
        for split_index, (question, api_id) in enumerate(questions, 1):
            duplicate = next((item for item in result if item["question"] == question), None)
            if duplicate:
                duplicate["source_ids"].append(source["id"])
                continue
            result.append({"id": f"Q-{len(result) + 1:02d}", "question": question, "owner": source["recommended_owner"].replace("Modernization Engineer", "Development Lead"), "required_before": "Development and QA completion" if source["impact_if_unresolved"] == "BLOCKING" else "Final stakeholder approval", "source_id": source["id"], "source_ids": [source["id"]], "source_split_index": split_index, "story_id": story_id, "ac_id": source.get("ac_id"), "api_id": api_id})
    return result


def _relevant_apis(story: dict, apis: list[dict]) -> list[dict]:
    linked = [api for api in apis if story["id"] in api["story_ids"]]
    semantic = story["story_semantic_model"]
    text = f"{story['title']} {semantic['authoritative_statement']} {semantic['observable_capability']}".lower()
    selected = []
    if "detail" in text:
        selected += [api for api in linked if api["kind"] == "detail"]
    if "directory" in text or " list " in f" {text} ":
        selected += [api for api in linked if api["kind"] == "directory"]
    if "report" in text or "selected year" in text or "year-dependent" in text:
        selected += [api for api in linked if api["kind"] == "report"]
    if "summary" in text:
        selected += [api for api in linked if api["kind"] == "summary"]
    if "identity" in text or "claims" in text:
        selected += [api for api in linked if api["kind"] == "identity"]
    if "context" in text or "tenant" in text or "organization" in text:
        selected += [api for api in linked if api["kind"] == "context"]
    return list({api["id"]: api for api in (selected or linked)}.values())


def _criterion(story: dict, ac: dict, linked_apis: list[dict], ac_id: str) -> dict:
    preservation = ac["evidence_status"] == "MODERNIZATION_PRESERVATION"
    data = [api for api in linked_apis if api["kind"] not in {"context", "identity"}]
    contexts = [api for api in linked_apis if api["kind"] == "context"]
    inputs = [item for api in data for item in api["inputs"]]
    if any(item["name"].split(" ", 1)[0].lower() == "year" for item in inputs):
        given = ["A reporting year has been selected."]
    elif inputs:
        verb = "are" if len(inputs) > 1 else "is"
        given = [f"The required {_join([item['description'] for item in inputs])} {verb} available."]
    elif contexts and data:
        given = ["The application can determine the current organization context."]
    elif contexts:
        given = ["The applicable functionality requires the current organization context."]
    else:
        presentation = ac.get("customer_presentation")
        source_given = presentation.get("given") if isinstance(presentation, dict) else story["acceptance_criteria"][0]["customer_presentation"]["given"]
        given = [_sentence(source_given)]
    goal = _story_goal(story["story_semantic_model"]["authoritative_statement"])
    subject = goal.removeprefix("view ").removeprefix("review ").removeprefix("open ").removeprefix("access ").removeprefix("the ")
    subject = subject.replace("my organization", "their organization")
    if preservation and data:
        when = "The application loads " + subject + "."
    elif goal.startswith("make "):
        when = "The application resolves " + subject.removeprefix("make ").replace("available to ", "for ") + "."
    elif goal.startswith(("open ", "access ")):
        when = "The user requests access to the " + subject + "."
    elif goal.startswith("review "):
        when = "The user reviews the " + subject + "."
    elif goal.startswith("view "):
        when = "The user views " + subject + "."
    else:
        when = "The user requests " + subject + "."
    expected = []
    for api in data:
        suffix = " for the selected reporting year" if any(item["name"].split(" ", 1)[0].lower() == "year" for item in api["inputs"]) else ""
        expected.append(f"{api['description']} is retrieved{suffix}.")
    for api in linked_apis:
        if api["kind"] == "identity":
            verb = "are" if api["description"].lower().endswith("claims") else "is"
            expected.append(f"{api['description']} {verb} available to the applicable application functions.")
    if contexts:
        expected.append("The retrieved information is associated with the current organization." if data else "The current organization identifier is available to the applicable functionality.")
    if not expected:
        expected.append(f"The {subject} is available to the user.")
    title = re.sub(r"\s+(?:Behavior|Preservation)$", "", ac["title"], flags=re.I).replace("Tenant-Aware", "Organization-Specific")
    title = re.sub(r"\bTenant\b", "Organization", title)
    if preservation:
        title += " Service Integration" if linked_apis else " Availability"
    return {"id": ac_id, "title": title, "given": given, "when": _sentence(when), "expected_results": list(dict.fromkeys(_sentence(item) for item in expected)), "source_ac_id": ac["id"], "source_story_id": story["id"]}


def _objective(requirements: list[dict]) -> str:
    user = [item["title"] for item in requirements if not item["title"].startswith(("Establish", "Resolve"))]
    clauses = [_action_phrase(title) for title in user]
    text = "Enable users to " + _join(clauses) if clauses else "Provide the required application context"
    identity = [re.sub(r"^Resolve\s+", "", item["title"]).lower() for item in requirements if item["title"].startswith("Resolve")]
    if identity:
        identity_text = _join(identity).replace("current user identity and current user claims", "current user identity and claims")
        text += f" while the application provides {identity_text}"
    if any(item["title"] == "Establish Organization Context" for item in requirements):
        text += " within the applicable organization context"
    return _sentence(text)


def build_human_presentation(model: dict) -> dict:
    apis, interaction_to_api = _api_requirements(model)
    behavior_by_story = {item["story_id"]: item for item in model["functional_behavior"]}
    requirements = []
    for story in model["requirements"]:
        api_ids = list(dict.fromkeys(interaction_to_api[x] for x in story["api_contract_ids"] if x in interaction_to_api))
        if not api_ids:
            requirements.append(_navigation_requirement(story, behavior_by_story[story["id"]]))
    for api in sorted(apis, key=lambda item: (item["kind"] in {"context", "identity"}, item["id"])):
        behavior_ids = [behavior_by_story[x]["concept_id"] for x in api["story_ids"] if x in behavior_by_story]
        requirements.append(_api_requirement(api, behavior_ids))
    for number, requirement in enumerate(requirements, 1):
        requirement["id"] = f"FR-{number:02d}"

    clarifications = _clarifications(model, apis)
    assigned_general_questions: set[str] = set()
    for requirement in requirements:
        requirement["clarification_ids"] = []
        for item in clarifications:
            api_match = item.get("api_id") in requirement["api_ids"]
            story_match = not item.get("api_id") and item.get("story_id") in requirement["source_story_ids"] and item["id"] not in assigned_general_questions
            if api_match or story_match:
                requirement["clarification_ids"].append(item["id"])
                if story_match:
                    assigned_general_questions.add(item["id"])

    stories, criteria, ac_number = [], [], 1
    for number, story in enumerate(model["requirements"], 1):
        semantic = story["story_semantic_model"]
        linked_apis = _relevant_apis(story, apis)
        outcome = _story_outcome(semantic, linked_apis)
        stories.append({"id": f"US-{number:02d}", "title": story["title"], "goal": _story_goal(semantic["authoritative_statement"]), "outcome": outcome, "business_outcome_status": "CONFIRMATION_REQUIRED" if outcome is None else "SUPPORTED", "source_story_id": story["id"]})
        for ac in story["acceptance_criteria"]:
            criteria.append(_criterion(story, ac, linked_apis, f"AC-{ac_number:02d}"))
            ac_number += 1

    rules = []
    for number, item in enumerate(model.get("business_rules", []), 1):
        rule = re.sub(r"Organization-specific frontend flows obtain current organization context before continuing", "Functionality that requires organization context must obtain it before continuing", _plain(item["description"]), flags=re.I)
        rules.append({"id": f"BR-{number:02d}", "rule": _sentence(rule), "source_rule_id": item["id"]})
    scope_out = [_sentence(item).replace("Delivery of unrelated UI areas", "Unrelated user interface areas") for item in model["scope"]["out_of_scope"]]
    return {
        "feature": {"name": model["feature_header"]["name"], "source_feature_id": model["feature_id"]},
        "overview": {"objective": _objective(requirements), "capabilities": [item["requirement"] for item in requirements], "business_value": "Requires confirmation from Product Owner / Business SME." if model["summary"]["business_value_status"] == "REQUIRES_STAKEHOLDER_ENRICHMENT" else _sentence(model["summary"]["business_value"])},
        "functional_requirements": requirements, "stories": stories, "acceptance_criteria": criteria, "api_requirements": apis, "business_rules": rules, "clarifications": clarifications,
        "scope": {"in_scope": [f"{item['title']}." for item in requirements], "out_of_scope": scope_out},
    }


def render_human_markdown(presentation: dict) -> str:
    overview = presentation["overview"]
    lines = [f"# {presentation['feature']['name']}", "", "## 1. Feature Overview", "", "### Objective", "", overview["objective"], "", "### Feature Capabilities", "", *[f"- {x}" for x in overview["capabilities"]], "", "### Business Value", "", overview["business_value"], "", "### Scope", "", "**In Scope**", "", *[f"- {x}" for x in presentation["scope"]["in_scope"]], ""]
    if presentation["scope"]["out_of_scope"]:
        lines += ["**Out of Scope**", "", *[f"- {x}" for x in presentation["scope"]["out_of_scope"]], ""]
    lines += ["## 2. Functional Requirements", ""]
    api_by_id = {item["id"]: item for item in presentation["api_requirements"]}
    questions_by_id = {item["id"]: item for item in presentation["clarifications"]}
    for requirement in presentation["functional_requirements"]:
        lines += [f"### {requirement['id']} - {requirement['title']}", "", "#### Requirement", "", requirement["requirement"], "", "#### Functional Flow", "", *[f"{number}. {step}" for number, step in enumerate(requirement["functional_steps"], 1)], ""]
        if requirement["api_ids"]:
            api = api_by_id[requirement["api_ids"][0]]
            lines += ["#### API Integration", "", f"- **Method:** `{api['method']}`", f"- **Endpoint:** `{api['endpoint']}`"]
            lines += [f"- **Input:** `{item['name']}` - {item['description']} ({item['location'].lower()} parameter)" for item in api["inputs"]]
            lines += [f"- **Purpose:** {api['purpose']}", f"- **Response:** {api['description']}.", ""]
        if requirement["clarification_ids"]:
            lines += ["#### Clarification Required", "", *[f"- **{qid}:** {questions_by_id[qid]['question']}" for qid in requirement["clarification_ids"]], ""]
    lines += ["## 3. User Stories", ""]
    for story in presentation["stories"]:
        ending = "," if story["outcome"] else "."
        lines += [f"### {story['id']} - {story['title']}", "", "As an application user,", "", f"I want to {story['goal']}{ending}"]
        lines += (["", f"so that {story['outcome']}.", ""] if story["outcome"] else ["", "**Business Outcome:** Requires confirmation from Product Owner / Business SME.", ""])
    lines += ["## 4. Acceptance Criteria", ""]
    for criterion in presentation["acceptance_criteria"]:
        lines += [f"### {criterion['id']} - {criterion['title']}", "", f"**Given** {criterion['given'][0]}", *[f"**And** {item}" for item in criterion["given"][1:]], "", f"**When** {criterion['when']}", "", f"**Then** {criterion['expected_results'][0]}", *[f"**And** {item}" for item in criterion["expected_results"][1:]], ""]
    if presentation["api_requirements"]:
        lines += ["## 5. API Requirements", ""]
        for api in presentation["api_requirements"]:
            inputs = "None" if not api["inputs"] and not api["request_type"] else "; ".join([f"`{item['name']}` - {item['description']} ({item['location'].lower()})" for item in api["inputs"]] + ([f"Request body: `{api['request_type']}`"] if api["request_type"] else []))
            lines += [f"### {api['id']} - {api['title']}", "", "| Property | Details |", "| --- | --- |", f"| Method | `{api['method']}` |", f"| Endpoint | `{api['endpoint']}` |", f"| Input | {inputs} |", f"| Purpose | {api['purpose']} |", f"| Response | {api['description']} |", f"| Response Model | `{api['model'] or 'Not specified'}` |", f"| Used By | {', '.join(api['used_by'])} |", ""]
            if api["response_fields"]:
                lines += ["**Response Fields**", "", *[f"- `{item}`" for item in api["response_fields"]], ""]
    if presentation["business_rules"]:
        lines += ["## 6. Business Rules", ""]
        for rule in presentation["business_rules"]:
            lines += [f"### {rule['id']}", "", rule["rule"], ""]
    section = 7 if presentation["business_rules"] else 6
    lines += [f"## {section}. Development Requirements", "", "- Implement the functionality defined by this Feature.", "- Integrate with the specified backend APIs.", "- Supply every documented API parameter.", "- Use each API result for the corresponding functionality.", "- Maintain required user and organization context.", "- Satisfy all authoritative Acceptance Criteria.", ""]
    section += 1
    if presentation["clarifications"]:
        lines += [f"## {section}. Clarifications Required", "", "| ID | Question | Owner | Required Before |", "| --- | --- | --- | --- |", *[f"| {x['id']} | {x['question']} | {x['owner']} | {x['required_before']} |" for x in presentation["clarifications"]], ""]
        section += 1
    lines += [f"## {section}. Definition of Done", "", *[f"- [ ] Implementation is complete for {item['title']}." for item in presentation["functional_requirements"]]]
    if presentation["api_requirements"]:
        lines += ["- [ ] All specified backend APIs are integrated."]
    if any(api["inputs"] for api in presentation["api_requirements"]):
        lines += ["- [ ] Required API parameters are supplied as documented."]
    if presentation["business_rules"]:
        lines += ["- [ ] All documented business rules are satisfied."]
    lines += ["- [ ] All authoritative Acceptance Criteria pass.", "- [ ] Blocking business clarifications are resolved.", "- [ ] QA validation is complete.", ""]
    section += 1
    lines += [f"## {section}. Review and Approval", "", "| Role | Review Responsibility | Status |", "| --- | --- | --- |", "| Product Owner | Objective, business value, scope, and priorities | Pending |", "| Business Analyst | Functional requirements, rules, Stories, and clarifications | Pending |", "| Solution Architect | API contracts, inputs, responses, and integration boundaries | Pending |", "| Development Lead | Implementation clarity and delivery feasibility | Pending |", "| QA Lead | Acceptance Criteria and validation coverage | Pending |", "| Customer SME | Business terminology and unresolved decisions | Pending |", ""]
    return "\n".join(lines)


def audit_human_markdown(markdown: str) -> dict[str, int]:
    lowered = f" {markdown.lower()} "
    result = {name: sum(lowered.count(term) for term in terms) for name, terms in FORBIDDEN_TERMS.items()}
    result["source_paths"] = len(re.findall(r"\b(?:src|source)/[^\s`)]+", markdown, re.I))
    result["source_line_references"] = len(re.findall(r"(?:\bline\s+\d+|:[Ll]\d+\b)", markdown))
    result["semantically_circular_stories"] = len(re.findall(r"I want to ([^\n]+).*?so that (?:I can )?\1|so that [^.]+ remains (?:available|associated|visible)", markdown, re.I | re.S))
    result["vague_human_ac"] = sum(lowered.count(term) for term in ("behavior remains available", "feature works correctly", "information is supported", "functionality is maintained", "requirements are preserved", "feature behavior is ready", "feature is implemented"))
    result["generic_clarification_questions"] = sum(lowered.count(term) for term in ("which information must be considered mandatory", "what contract detail is required", "what details are required"))
    result["backend_task_wrappers_as_primary_response"] = len(re.findall(r"\| Response \| `?(?:Task|ValueTask)<", markdown))
    return result
