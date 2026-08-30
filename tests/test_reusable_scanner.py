import json
import os
from pathlib import Path
import pytest
from polaris_modernization.cli import analyze
from polaris_modernization.profiles import load_profile, merge_profiles

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "healthclinic-dashboard"

def profile():
    data = merge_profiles(load_profile("default"), {"include_paths": []})
    return data

def test_arbitrary_root_is_recursive_and_isolated(tmp_path):
    result = analyze(FIXTURE, "fixture-project", "default", tmp_path)
    assert result["output"] == tmp_path / "fixture-project"
    inventory = json.loads((result["output"] / "source-inventory.json").read_text())
    assert any(item["source_path"].endswith("DashboardController.cs") for item in inventory["files"])
    graph = json.loads((result["output"] / "knowledge-graph.json").read_text())
    assert all(node["project_id"] == "fixture-project" and node["evidence"] for node in graph["nodes"])
    assert all(edge["project_id"] == "fixture-project" and edge["evidence"] for edge in graph["edges"])

def test_fixture_extracts_supported_facts(tmp_path):
    result = analyze(FIXTURE, "sample", "default", tmp_path)
    names = {fact.name for fact in result["facts"]}
    assert {"DashboardController", "Index", "Authorize", "header-bar", "ui-view", "toaster-container", "loading-overlay", "sample", "dashboardController", "dashboardService", "chart", "/api/summary"} <= names

def test_healthclinic_profile_is_configuration_only():
    profile = load_profile("healthclinic-dashboard")
    assert "src/MyHealth.Web/Views/Dashboard" in profile["include_paths"]

def test_local_reference_integration_is_optional(tmp_path):
    source = os.getenv("HEALTHCLINIC_SOURCE_ROOT")
    if not source: pytest.skip("HEALTHCLINIC_SOURCE_ROOT is not set")
    result = analyze(Path(source), "healthclinic-dashboard", "healthclinic-dashboard", tmp_path)
    assert result["facts"]
