from pathlib import Path

import pytest

from polaris_modernization.feature_specifications.semantic_quality import (
    build_ac_semantic_model,
    build_story_semantic_model,
    cross_feature_template_similarity,
    feature_name_behavior_alignment,
    story_semantic_defects,
)


@pytest.mark.parametrize(
    ("action", "business_object", "outcome"),
    [
        ("access", "doctor directory", "the application presents the doctor directory"),
        ("access", "patient directory", "I can review the patient directory"),
        ("open", "reporting area", "I can use the reporting area"),
        ("access", "clinic information", "I can access clinic information"),
    ],
)
def test_semantically_circular_story_patterns_are_rejected(action, business_object, outcome):
    model = {
        "business_action": action, "business_object": business_object, "supported_outcome": outcome,
        "business_value": "", "business_value_status": "NOT_ESTABLISHED", "stakeholder_enrichment_required": False,
    }
    findings = story_semantic_defects(model)
    assert "SEMANTICALLY_CIRCULAR_STORY" in findings


def test_story_model_requests_enrichment_instead_of_inventing_value():
    story = {"business_goal": "Access the existing item directory"}
    behavior = {"meaning": "An item directory experience is available"}
    model = build_story_semantic_model(story, behavior, [])
    assert model["business_value_status"] == "NOT_ESTABLISHED"
    assert model["stakeholder_enrichment_required"] is True
    assert "Business outcome: Requires stakeholder confirmation" in model["customer_presentation"]
    assert "so that the application" not in model["customer_presentation"]


def test_supported_context_interpretation_is_explicit_and_evidence_safe():
    story = {"business_goal": "Obtain tenant context for item functionality"}
    behavior = {"meaning": "Item functionality has current tenant context"}
    model = build_story_semantic_model(story, behavior, [])
    assert model["outcome_evidence_status"] == "SUPPORTED_INTERPRETATION"
    assert model["business_value_status"] == "SUPPORTED_INTERPRETATION"
    assert model["stakeholder_enrichment_required"] is False


def test_acceptance_criterion_retains_unknown_fields_as_limitation():
    ac = {"title": "Directory Behavior", "given": "Given source", "when": "When source", "then": "Then source", "business_condition": "Access item directory"}
    story = {"business_goal": "Access the existing item directory"}
    workflow = {"trigger": "Item navigation is initiated", "interaction": ["Resolve item route", "Present item surface"], "outcome": "Item directory is available"}
    model = build_ac_semantic_model(ac, story, [workflow])
    assert model["evidence_status"] == "TESTABLE_WITH_EVIDENCE_LIMITATION"
    assert model["limitations"]
    assert model["known_data_characteristics"] == []
    assert all(field not in model["customer_presentation"]["then"] for field in ("phone", "email", "specialty"))


def test_preservation_criterion_is_not_presented_as_business_behavior():
    ac = {"title": "Modernization Preservation", "given": "baseline", "when": "the frontend experience is modernized", "then": "behavior remains available", "business_condition": "the frontend experience is modernized"}
    model = build_ac_semantic_model(ac, {"business_goal": "Access item directory"}, [])
    assert model["evidence_status"] == "MODERNIZATION_PRESERVATION"
    assert model["presentation_status"] == "SEPARATE_PRESERVATION_REQUIREMENT"


def test_feature_name_does_not_create_missing_behavior():
    alignment = feature_name_behavior_alignment("Location Appointment Experience", [{"business_goal": "Access location information"}])
    assert alignment["status"] == "PARTIALLY_ALIGNED"
    assert alignment["feature_name_terms_not_established_by_primary_behaviors"] == ["appointment"]


def test_cross_feature_template_similarity_is_visible_for_review():
    models = [
        {"feature_id": "feature-one", "story_semantic_models": [{"customer_presentation": "As a user I want to access the item directory"}]},
        {"feature_id": "feature-two", "story_semantic_models": [{"customer_presentation": "As a user I want to access the item directory"}]},
    ]
    assert cross_feature_template_similarity(models)[0]["status"] == "REVIEWED_STRUCTURAL_SIMILARITY"


def test_reusable_semantic_code_has_no_application_specific_condition():
    source = Path("src/polaris_modernization/feature_specifications/semantic_quality.py").read_text(encoding="utf-8")
    assert "HealthClinic" not in source and "MyHealth" not in source
