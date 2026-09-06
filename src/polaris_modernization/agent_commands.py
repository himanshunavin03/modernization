"""Thin deterministic adapters used by repository-local agent commands."""
from __future__ import annotations
import re
from pathlib import Path
from typing import Any

from polaris_modernization.knowledge_graph_agent import create_knowledge_graph


def project_id_for(source_root: Path) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", source_root.resolve().name.lower()).strip("-")
    return value or "knowledge-graph"


def create_knowledge_graph_command(
    source_root: Path | None = None, *, project_id: str | None = None,
    profile: str = "default", output: Path = Path("artifacts"), load_neo4j: bool = False,
) -> dict[str, Any]:
    """Invoke the existing deterministic workflow; this function creates no graph facts."""
    root = (source_root or Path.cwd()).resolve()
    has_dotnet_projects = any(root.rglob("*.sln")) or any(root.rglob("*.csproj"))
    return create_knowledge_graph(
        root, project_id or project_id_for(root), profile, output,
        enable_roslyn=has_dotnet_projects, load_neo4j=load_neo4j,
    )


def execute_polaris_command(
    command: str,
    argument: str | None = None,
    *,
    repository_root: Path = Path.cwd(),
    **options: Any,
) -> dict[str, Any]:
    """Shared Codex/Copilot adapter; command definitions contain no engine logic."""
    from polaris_modernization.commands import CommandService

    return CommandService(repository_root).execute(command, argument, **options).to_dict()
