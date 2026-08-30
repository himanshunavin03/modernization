"""CLI for deterministic, scoped source extraction."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from polaris_modernization.framework_detection import detect_frameworks
from polaris_modernization.graph.normalizer import normalize
from polaris_modernization.graph.writer import write_json, write_summary
from polaris_modernization.models import Fact
from polaris_modernization.profiles import load_profile, merge_profiles
from polaris_modernization.source_inventory import build_inventory
from polaris_modernization.tree_sitter_extractors.registry import extractor_for
from polaris_modernization.graph.neo4j_loader import Neo4jLoader, connect, read_graph


def analyze(source_root: Path, project_id: str, profile_name: str, output: Path) -> dict:
    profile = merge_profiles(load_profile("default"), load_profile(profile_name))
    inventory, warnings = build_inventory(source_root, profile)
    facts: list[Fact] = []
    source_root = source_root.resolve()
    for entry in inventory:
        if not entry["selected_for_extraction"]: continue
        source_path = source_root / entry["source_path"]
        digest = entry["source_hash"]
        extractor = extractor_for(source_path)
        if extractor: facts.extend(extractor.extract(source_path, source_root, digest, project_id))

    graph = normalize(project_id, inventory, facts)
    run_output = output / project_id
    run_output.mkdir(parents=True, exist_ok=True)
    write_json(run_output / "source-inventory.json", {"project_id": project_id, "files": inventory, "warnings": warnings})
    write_json(run_output / "framework-detection.json", {"project_id": project_id, "frameworks": detect_frameworks(source_root, inventory)})
    write_json(run_output / "facts.json", {"project_id": project_id, "facts": [fact.to_dict() for fact in facts]})
    write_json(run_output / "knowledge-graph.json", graph)
    write_summary(run_output / "analysis-summary.md", inventory, facts, graph)
    return {"inventory": inventory, "facts": facts, "graph": graph, "warnings": warnings, "output": run_output}


def main() -> None:
    parser = argparse.ArgumentParser(description="Deterministic Tree-sitter source extractor")
    subparsers = parser.add_subparsers(dest="command", required=True)
    analyze_parser = subparsers.add_parser("analyze")
    analyze_parser.add_argument("--source-root", required=True, type=Path)
    analyze_parser.add_argument("--project-id", required=True)
    analyze_parser.add_argument("--profile", required=True)
    analyze_parser.add_argument("--output", required=True, type=Path)
    load_parser = subparsers.add_parser("load-neo4j")
    load_parser.add_argument("--graph", required=True, type=Path)
    load_parser.add_argument("--project-id", required=True)
    clear_parser = subparsers.add_parser("clear-neo4j-project")
    clear_parser.add_argument("--project-id", required=True)
    clear_parser.add_argument("--confirm-project-id", required=True)
    args = parser.parse_args()

    if args.command == "analyze":
        result = analyze(args.source_root, args.project_id, args.profile, args.output)
        print(f"Analyzed {len(result['inventory'])} files into {result['output']}")
    elif args.command in {"load-neo4j", "clear-neo4j-project"}:
        driver = connect(os.getenv("NEO4J_URI", "bolt://localhost:7687"), os.getenv("NEO4J_USERNAME", "neo4j"), os.getenv("NEO4J_PASSWORD", "change-me"))
        loader = Neo4jLoader(driver)
        try:
            if args.command == "load-neo4j":
                graph = read_graph(args.graph, args.project_id)
                print(loader.load(graph, args.project_id))
            else:
                loader.clear_project(args.project_id, args.confirm_project_id)
                print(f"Cleared project {args.project_id}")
        finally:
            driver.close()


if __name__ == "__main__":
    main()
