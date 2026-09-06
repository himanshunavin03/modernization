"""IDE-neutral CLI adapter for canonical Polaris commands."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from polaris_modernization.commands import CommandService, default_registry
from polaris_modernization.commands.models import CommandError, PrerequisiteError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="polaris", description="Reusable Polaris modernization command interface")
    parser.add_argument("--repository-root", type=Path, default=Path.cwd())
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in default_registry().all():
        child = subparsers.add_parser(command.name, help=command.purpose)
        if command.argument:
            child.add_argument(command.argument, nargs=None if command.argument_required else "?")
        if command.name == "create-knowledge-graph":
            child.add_argument("--source-root", type=Path)
            child.add_argument("--project-id")
            child.add_argument("--profile", default="default")
            child.add_argument("--load-neo4j", action="store_true")
        if command.name in {"understand-application", "generate-features", "generate-stories", "generate-acceptance-criteria"}:
            child.add_argument("--agent-result", type=Path)
        if command.name in {"validate-modernization", "validate-feature"}:
            child.add_argument("--static-only", action="store_true")
        if command.name == "generate-technical-tasks":
            child.add_argument("--prerequisite-only", action="store_true")
        if command.name == "modernize-feature":
            child.add_argument("--prerequisite-only", action="store_true")
    return parser


def run(argv: list[str] | None = None) -> tuple[int, dict[str, Any]]:
    args = build_parser().parse_args(argv)
    values = vars(args)
    command = values.pop("command")
    root = values.pop("repository_root")
    definition = default_registry().get(command)
    argument = values.pop(definition.argument, None) if definition.argument else None
    values = {key: value for key, value in values.items() if value is not None}
    try:
        result = CommandService(root).execute(command, argument, **values)
        return (0 if result.status not in {"BLOCKED", "FAILED"} else 2), result.to_dict()
    except PrerequisiteError as exc:
        return 2, {"command": command, "status": "BLOCKED", "message": str(exc), "next_commands": exc.next_commands}
    except CommandError as exc:
        return 2, {"command": command, "status": "ERROR", "message": str(exc)}


def main() -> None:
    code, payload = run()
    print(json.dumps(payload, indent=2, sort_keys=True, default=str))
    raise SystemExit(code)


if __name__ == "__main__":
    main()
