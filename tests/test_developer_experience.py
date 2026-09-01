from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_codex_and_copilot_interfaces_reference_shared_cli_without_source_hardcoding():
    files = [ROOT / "docs/agents/commands/create-knowledge-graph.md", ROOT / "docs/agents/commands/understand-application.md", ROOT / ".github/prompts/create-knowledge-graph.prompt.md", ROOT / ".github/prompts/understand-application.prompt.md"]
    contents = [path.read_text(encoding="utf-8") for path in files]
    assert all("HealthClinic" not in text and "source/HealthClinic" not in text for text in contents)
    assert "polaris_modernization.cli" in contents[0]
    assert "polaris_modernization.cli" in contents[1]
    assert all("create_knowledge_graph(" not in text and "analyze(" not in text for text in contents[2:])
