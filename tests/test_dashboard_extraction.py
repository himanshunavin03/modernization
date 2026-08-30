import json
import subprocess
from pathlib import Path

from polaris_modernization.cli import analyze


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = PROJECT_ROOT / "source" / "HealthClinic.biz"


def test_dashboard_extraction_writes_evidence_backed_graph(tmp_path):
    result = analyze(SOURCE_ROOT, "dashboard", tmp_path)
    facts = [fact.to_dict() for fact in result["facts"]]
    kinds = {fact["kind"] for fact in facts}
    names = {fact["name"] for fact in facts}

    assert {"angular_module", "angular_controller", "angular_service", "angular_directive", "route"} <= kinds
    assert {"header-bar", "left-menu", "ui-view", "toaster-container", "loading-overlay"} <= names
    assert {"DashboardController", "Index", "Authorize"} <= names
    assert all(fact["evidence"]["extraction_method"] == "tree-sitter" for fact in facts)
    assert all(fact["evidence"]["confidence"] == 1.0 for fact in facts)

    graph = json.loads((tmp_path / "dashboard-graph.json").read_text(encoding="utf-8"))
    assert graph["nodes"]
    assert graph["edges"]
    assert all(node["evidence"] for node in graph["nodes"])
    assert all(edge["evidence"] for edge in graph["edges"])


def test_reference_source_is_not_modified():
    result = subprocess.run(
        ["git", "-C", str(SOURCE_ROOT), "status", "--porcelain"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert result.stdout == ""
