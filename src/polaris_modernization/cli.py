"""CLI for deterministic, scoped source extraction."""

from __future__ import annotations

import argparse
from pathlib import Path

from polaris_modernization.config import load_scope
from polaris_modernization.graph.normalizer import normalize
from polaris_modernization.graph.writer import write_json, write_summary
from polaris_modernization.models import Fact
from polaris_modernization.source_inventory import build_inventory
from polaris_modernization.tree_sitter_extractors import csharp, html, javascript


def analyze(source_root: Path, scope: str, output: Path) -> dict:
    inventory = build_inventory(source_root, load_scope(scope))
    facts: list[Fact] = []
    source_root = source_root.resolve()
    for entry in inventory:
        source_path = source_root / entry["source_path"]
        digest = entry["source_hash"]
        if source_path.suffix == ".js":
            facts.extend(javascript.extract(source_path, source_root, digest))
        elif source_path.suffix in {".html", ".cshtml"}:
            facts.extend(html.extract(source_path, source_root, digest))
        elif source_path.suffix == ".cs":
            facts.extend(csharp.extract(source_path, source_root, digest))

    graph = normalize(inventory, facts)
    output.mkdir(parents=True, exist_ok=True)
    write_json(output / "source-inventory.json", {"scope": scope, "files": inventory})
    write_json(output / "dashboard-facts.json", {"scope": scope, "facts": [fact.to_dict() for fact in facts]})
    write_json(output / "dashboard-graph.json", graph)
    write_summary(output / "dashboard-analysis-summary.md", inventory, facts, graph)
    return {"inventory": inventory, "facts": facts, "graph": graph}


def main() -> None:
    parser = argparse.ArgumentParser(description="Deterministic Tree-sitter source extractor")
    subparsers = parser.add_subparsers(dest="command", required=True)
    analyze_parser = subparsers.add_parser("analyze")
    analyze_parser.add_argument("--source-root", required=True, type=Path)
    analyze_parser.add_argument("--scope", default="dashboard")
    analyze_parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    if args.command == "analyze":
        result = analyze(args.source_root, args.scope, args.output)
        print(f"Analyzed {len(result['inventory'])} files into {args.output}")


if __name__ == "__main__":
    main()
