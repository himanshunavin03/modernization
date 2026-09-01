import json
from pathlib import Path

import pytest

from polaris_modernization.acceptance_criteria.retrieval import build_acceptance_packages, load_approved_stories
from polaris_modernization.acceptance_criteria.workflow import UnsupportedAcceptanceCriteriaError, expected_ac_id, _validate


def test_real_approved_story_packages_are_stable():
    root = Path("artifacts/stories/runs/legacy-dashboard-complete-application-demo-v1-2026-09-01-105453-078418")
    approved = load_approved_stories(root)
    first = build_acceptance_packages(approved)
    second = build_acceptance_packages(approved)
    assert len(first) == 12
    assert [x.package_hash for x in first] == [x.package_hash for x in second]


def test_stable_ac_ids():
    assert expected_ac_id("story-view-dashboard", 1) == "ac-view-dashboard-001"
    assert expected_ac_id("story-view-dashboard", 2) == "ac-view-dashboard-002"


def test_schema_rejects_acceptance_assumptions_and_extra_fields():
    from polaris_modernization.acceptance_criteria.models import AcceptanceCriterion
    assert "extra='forbid'" in str(AcceptanceCriterion.model_config) or AcceptanceCriterion.model_config["extra"] == "forbid"


def test_engine_has_no_application_specific_conditions():
    code = "".join(path.read_text() for path in (Path(__file__).parents[1] / "src/polaris_modernization/acceptance_criteria").glob("*.py"))
    assert "HealthClinic" not in code and "MyHealth" not in code


@pytest.mark.parametrize("text,guard", [("administrator", "administrator"), ("HTTP 200", "http 200"), ("sorted alphabetically", "sorted"), ("within two seconds", "seconds"), ("required field", "required field"), ("retry the request", "retry")])
def test_unsupported_ac_language_is_guarded(text, guard):
    source = Path("src/polaris_modernization/acceptance_criteria/workflow.py").read_text()
    assert guard in source.lower(), text
