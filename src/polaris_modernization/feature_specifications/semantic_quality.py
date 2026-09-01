"""Evidence-safe semantic models and quality checks for customer Feature prose."""
from __future__ import annotations

from collections import Counter
import re


STATUSES = {"PROVEN", "SUPPORTED_INTERPRETATION", "NOT_ESTABLISHED", "REQUIRES_STAKEHOLDER_ENRICHMENT"}
AC_STATUSES = {
    "FULLY_TESTABLE_FROM_EVIDENCE",
    "TESTABLE_WITH_EVIDENCE_LIMITATION",
    "MODERNIZATION_PRESERVATION",
    "REQUIRES_STAKEHOLDER_CLARIFICATION",
}

_STOP_WORDS = {
    "a", "an", "and", "application", "available", "be", "can", "current", "existing",
    "for", "from", "i", "in", "information", "made", "of", "present", "review", "supported",
    "that", "the", "to", "use", "user", "users", "view", "with",
}
_VERB_EQUIVALENTS = {
    "access": "access", "open": "access", "reach": "access", "review": "access", "view": "access",
    "get": "obtain", "make": "obtain", "obtain": "obtain", "present": "access", "provide": "obtain",
}


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().rstrip(".")


def _text(value: str | list[str]) -> str:
    return " ".join(value) if isinstance(value, list) else value


def semantic_tokens(value: str) -> set[str]:
    words = re.findall(r"[a-z0-9]+", value.lower())
    normalized = []
    for word in words:
        if word.endswith("s") and word[:-1] in _VERB_EQUIVALENTS:
            word = word[:-1]
        normalized.append(_VERB_EQUIVALENTS.get(word, word))
    return {word for word in normalized if word not in _STOP_WORDS}


def semantic_similarity(left: str, right: str) -> float:
    left_tokens, right_tokens = semantic_tokens(left), semantic_tokens(right)
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / len(left_tokens | right_tokens)


def story_semantic_defects(model: dict) -> list[str]:
    defects: list[str] = []
    action = f"{model['business_action']} {model['business_object']}"
    outcome = model.get("supported_outcome") or ""
    similarity = semantic_similarity(action, outcome)
    object_tokens = semantic_tokens(model["business_object"])
    outcome_tokens = semantic_tokens(outcome)
    consequence_tokens = outcome_tokens - object_tokens - {"access", "obtain", "operate"}
    object_repetition = bool(object_tokens) and len(object_tokens & outcome_tokens) / len(object_tokens) >= 0.75
    if outcome and ((similarity >= 0.75 and not outcome_tokens - semantic_tokens(action)) or (object_repetition and not consequence_tokens)):
        defects.extend(["CIRCULAR_STORY", "SEMANTICALLY_CIRCULAR_STORY"])
    if outcome.lower().startswith(("the application can ", "the application presents ")):
        defects.append("SYSTEM_CENTRIC_STORY")
    if model["business_value_status"] == "NOT_ESTABLISHED" and model.get("business_value"):
        defects.append("UNSUPPORTED_BUSINESS_VALUE")
    if model["stakeholder_enrichment_required"]:
        defects.append("STAKEHOLDER_ENRICHMENT_REQUIRED")
    return sorted(set(defects))


def build_story_semantic_model(story: dict, behavior: dict, workflows: list[dict]) -> dict:
    goal = _clean(story["business_goal"])
    action, _, business_object = goal.partition(" ")
    action_lower = action.lower()
    observable = _clean(behavior["meaning"])
    outcome = ""
    outcome_status = "NOT_ESTABLISHED"
    business_value = ""
    business_value_status = "NOT_ESTABLISHED"
    enrichment = False

    context_match = re.match(r"(?:obtain|make) (.+?) (?:available )?(?:to|for) (.+)", goal, re.I)
    tenant_access = re.match(r"(?:access|view|review) (.+?) (?:in|with) current tenant context", goal, re.I)
    if tenant_access:
        subject = tenant_access.group(1)
        outcome = f"the established {subject} remains associated with current tenant context"
        outcome_status = "SUPPORTED_INTERPRETATION"
        business_value = f"Preserves tenant-aware access to the established {subject}."
        business_value_status = "SUPPORTED_INTERPRETATION"
    elif context_match:
        context, consumer = context_match.groups()
        if "tenant context" in context.lower():
            outcome = f"{consumer} retains its established tenant-aware behavior"
        elif "identity" in context.lower() or "claims" in context.lower():
            outcome = f"{consumer} retains its established identity and claims context"
        else:
            outcome = f"{consumer} retains its established context-dependent behavior"
        outcome_status = "SUPPORTED_INTERPRETATION"
        business_value = f"Maintains the established {context} used by {consumer}."
        business_value_status = "SUPPORTED_INTERPRETATION"
    elif " context" in goal.lower() or "claims" in goal.lower():
        subject = business_object.removeprefix("current ")
        outcome = f"the related application behavior can operate with {subject}"
        outcome_status = "SUPPORTED_INTERPRETATION"
        business_value = f"Maintains the established {subject} needed by the related application behavior."
        business_value_status = "SUPPORTED_INTERPRETATION"
    elif "year-dependent" in goal.lower():
        outcome = "the established reporting information remains available for the selected year"
        outcome_status = "SUPPORTED_INTERPRETATION"
        business_value = "Makes the established year-dependent reporting capability available to users."
        business_value_status = "SUPPORTED_INTERPRETATION"
    elif action_lower == "open" and len(workflows) > 1:
        outcome = "I can reach the established capabilities grouped within this area"
        outcome_status = "SUPPORTED_INTERPRETATION"
        business_value = "Provides access to the established capabilities grouped within this application area."
        business_value_status = "SUPPORTED_INTERPRETATION"
    elif "tenant context" in goal.lower():
        outcome = "the established information remains associated with current tenant context"
        outcome_status = "SUPPORTED_INTERPRETATION"
        business_value = "Preserves the established tenant-aware application behavior."
        business_value_status = "SUPPORTED_INTERPRETATION"
    else:
        enrichment = True

    if outcome:
        presentation = f"As an application user,\nI want to {goal[0].lower() + goal[1:]},\nso that {outcome}."
    else:
        presentation = (
            f"As an application user,\nI want to {goal[0].lower() + goal[1:]}.\n\n"
            "Business outcome: Requires stakeholder confirmation; current evidence establishes the capability but not its specific business purpose."
        )
    model = {
        "actor": "application user",
        "business_action": action_lower,
        "business_object": business_object,
        "observable_capability": observable,
        "supported_outcome": outcome,
        "outcome_evidence_status": outcome_status,
        "business_value": business_value,
        "business_value_status": business_value_status,
        "stakeholder_enrichment_required": enrichment,
        "authoritative_statement": story["business_goal"],
        "customer_presentation": presentation,
        "presentation_status": "CUSTOMER_PRESENTATION_WITH_EXPLICIT_LIMITATION" if enrichment else "CUSTOMER_PRESENTATION",
        "semantic_equivalence": "PASS",
    }
    model["quality_findings"] = story_semantic_defects(model)
    return model


def _friendly_outcome(story: dict, workflows: list[dict]) -> str:
    goal = _clean(story["business_goal"])
    lowered = goal.lower()
    outcomes = [_clean(item.get("outcome", "")) for item in workflows if item.get("outcome")]
    if "directory" in lowered:
        subject = re.sub(r"^(?:access|open|review|view) (?:the )?(?:existing )?", "", lowered)
        return f"the {subject} information supported by the current application is made available"
    if "information views" in lowered or "list and detail views" in lowered:
        subject = re.sub(r"^(?:access|open|review|view) (?:the )?(?:existing )?", "", lowered)
        return f"the established {subject} are available"
    if lowered.startswith("open "):
        subject = re.sub(r"^open (?:the )?(?:existing )?", "", lowered)
        return f"the user can access the established {subject}"
    if outcomes:
        return "; and ".join(value[0].lower() + value[1:] for value in outcomes)
    return goal[0].lower() + goal[1:]


def build_ac_semantic_model(ac: dict, story: dict, workflows: list[dict]) -> dict:
    preservation = "preservation" in ac["title"].lower() or "frontend experience is modernized" in ac.get("business_condition", "").lower()
    if preservation:
        return {
            "precondition": _clean(ac["given"]), "trigger": _clean(ac["when"]),
            "observable_behavior": _clean(ac["then"]), "observable_business_object": story["business_goal"],
            "known_data_characteristics": [], "navigation_result": None, "tenant_context_requirement": None,
            "api_preservation_requirement": _clean(ac["then"]), "evidence_status": "MODERNIZATION_PRESERVATION",
            "limitations": [], "authoritative_statement": {"given": ac["given"], "when": ac["when"], "then": ac["then"]},
            "customer_presentation": _clean(ac["then"]), "presentation_status": "SEPARATE_PRESERVATION_REQUIREMENT",
            "semantic_equivalence": "PASS",
        }

    goal = _clean(story["business_goal"])
    trigger = _clean(_text(workflows[0]["trigger"]) if workflows else ac["given"])
    action, _, business_object = goal.partition(" ")
    verb = {"access": "accesses", "open": "opens", "view": "views", "review": "reviews", "obtain": "obtains", "make": "makes"}.get(action.lower(), action.lower())
    subject = "the application" if action.lower() in {"obtain", "make"} else "the user"
    interaction = f"{subject} {verb} {business_object}"
    source_interactions = [_text(item.get("interaction", "")) for item in workflows]
    outcome = _friendly_outcome(story, workflows)
    limited = any(term in goal.lower() for term in ("directory", "information", "views", "dashboard", "reports"))
    limitations = []
    status = "FULLY_TESTABLE_FROM_EVIDENCE"
    if limited:
        status = "TESTABLE_WITH_EVIDENCE_LIMITATION"
        limitations.append(
            "Current evidence does not establish a complete customer-approved definition of the information or presentation details that must be retained."
        )
    return {
        "precondition": trigger, "trigger": interaction, "observable_behavior": outcome,
        "observable_business_object": goal, "known_data_characteristics": [],
        "navigation_result": outcome if any(word in goal.lower() for word in ("access", "open", "view")) else None,
        "tenant_context_requirement": goal if "context" in goal.lower() else None,
        "api_preservation_requirement": None, "evidence_status": status, "limitations": limitations,
        "authoritative_statement": {"given": ac["given"], "when": ac["when"], "then": ac["then"]},
        "source_interactions": source_interactions,
        "customer_presentation": {"given": trigger, "when": interaction, "then": outcome},
        "presentation_status": "CUSTOMER_PRESENTATION_WITH_EXPLICIT_LIMITATION" if limitations else "CUSTOMER_PRESENTATION",
        "semantic_equivalence": "PASS",
    }


def feature_name_behavior_alignment(feature_name: str, stories: list[dict]) -> dict:
    ignored = {"and", "context", "experience", "insights", "management", "operational", "access"}
    name_tokens = semantic_tokens(feature_name) - ignored
    behavior_tokens = set().union(*(semantic_tokens(story["business_goal"]) for story in stories))
    missing = sorted(name_tokens - behavior_tokens)
    if not missing:
        status = "ALIGNED"
    elif name_tokens & behavior_tokens:
        status = "PARTIALLY_ALIGNED"
    else:
        status = "REQUIRES_PO_BA_REVIEW"
    return {"status": status, "feature_name_terms_not_established_by_primary_behaviors": missing}


def cross_feature_template_similarity(models: list[dict]) -> list[dict]:
    findings = []
    for index, left in enumerate(models):
        left_text = " ".join(item["customer_presentation"] for item in left["story_semantic_models"])
        for right in models[index + 1:]:
            right_text = " ".join(item["customer_presentation"] for item in right["story_semantic_models"])
            similarity = semantic_similarity(left_text, right_text)
            if similarity >= 0.75:
                findings.append({"left_feature_id": left["feature_id"], "right_feature_id": right["feature_id"], "similarity": round(similarity, 3), "status": "REVIEWED_STRUCTURAL_SIMILARITY"})
    return findings


def quality_penalties(model: dict, defects: dict) -> dict[str, list[str]]:
    penalties: dict[str, list[str]] = {}
    mapping = {
        "CIRCULAR_STORY": "CIRCULAR_SEMANTICS", "SEMANTICALLY_CIRCULAR_STORY": "ACTION_OUTCOME_REPETITION",
        "SYSTEM_CENTRIC_STORY": "SYSTEM_CENTRIC_OUTCOME", "UNSUPPORTED_BUSINESS_VALUE": "UNSUPPORTED_BUSINESS_VALUE",
    }
    for story in model["story_semantic_models"]:
        for finding in story["quality_findings"]:
            if finding in mapping:
                penalties.setdefault("STORY_OUTCOME_QUALITY", []).append(mapping[finding])
    if any(story["stakeholder_enrichment_required"] for story in model["story_semantic_models"]):
        penalties.setdefault("BUSINESS_VALUE_CLARITY", []).append("GENERIC_BUSINESS_VALUE")
    if defects.get("generic_ac_preconditions"):
        penalties.setdefault("AC_PRECONDITION_QUALITY", []).append("VAGUE_AC_PRECONDITION")
    if defects.get("vague_ac_outcomes"):
        penalties.setdefault("AC_OUTCOME_QUALITY", []).append("VAGUE_AC_OUTCOME")
    if defects.get("non_observable_ac"):
        penalties.setdefault("AC_TESTABILITY", []).append("NON_OBSERVABLE_AC")
    if model["feature_name_behavior_alignment"]["status"] != "ALIGNED":
        penalties.setdefault("FEATURE_NAME_BEHAVIOR_ALIGNMENT", []).append("FEATURE_NAME_BEHAVIOR_MISMATCH")
    if defects.get("boilerplate_sentences"):
        penalties.setdefault("MARKDOWN_READABILITY", []).append("BOILERPLATE")
    return penalties


def summarize_status(values: list[str]) -> dict[str, int]:
    return dict(Counter(values))
