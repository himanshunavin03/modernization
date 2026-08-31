from pathlib import Path

from polaris_modernization import agent_commands


def test_project_id_is_source_root_derived_not_application_hardcoded(tmp_path):
    source = tmp_path / "Customer App"; source.mkdir()
    assert agent_commands.project_id_for(source) == "customer-app"


def test_agent_command_uses_existing_workflow_and_enables_roslyn_only_for_dotnet(monkeypatch, tmp_path):
    source = tmp_path / "customer"; source.mkdir(); (source / "Customer.csproj").write_text("<Project />", encoding="utf-8")
    captured = {}
    monkeypatch.setattr(agent_commands, "create_knowledge_graph", lambda *args, **kwargs: captured.update(args=args, kwargs=kwargs) or {"overall_status": "succeeded"})

    agent_commands.create_knowledge_graph_command(source, output=tmp_path / "out")

    assert captured["args"][0] == source.resolve()
    assert captured["kwargs"]["enable_roslyn"] is True
    assert captured["kwargs"]["load_neo4j"] is False
