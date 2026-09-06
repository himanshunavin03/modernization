"""Validate and preserve raw completed knowledge-graph runs for code review."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import re
import shutil
from typing import Any

from polaris_modernization.graph.writer import write_json
from polaris_modernization.capability_completeness import assess_graph_readiness

BASE_FILES = {
    "knowledge-graph.json", "facts.json", "source-inventory.json", "framework-detection.json",
    "graph-run-status.json", "graph-run-summary.md", "analysis-summary.md",
    "api-mapping-forensics.json", "api-relationship-resolution-audit.json",
    "api-relationship-resolution-matrix.json", "api-relationship-before-after.json",
    "api-relationship-resolution-summary.md",
}
ROSLYN_FILES = {"roslyn-semantic.json", "roslyn-semantic-all.json"}
READINESS_FILES = {"kg-readiness-analysis.json", "kg-readiness-analysis.md"}
SECRET_PATTERNS = (
    re.compile(r"(?i)[\"']?(?:password|passwd|secret|api[_-]?key|access[_-]?token)[\"']?\s*[:=]\s*['\"]?[^\s'\"]{8,}"),
    re.compile(r"(?i)(?:bolt|neo4j|postgres(?:ql)?|mongodb)://[^\s/@:]+:[^\s/@]+@"),
)


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def scan_for_secrets(run_output: Path) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for path in run_output.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".json", ".md", ".txt", ".log"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append({"path": path.relative_to(run_output).as_posix(), "pattern": pattern.pattern})
                break
    return findings


def find_bound_state_collisions(graph: dict[str, Any]) -> list[dict[str, Any]]:
    """Find state nodes joined across source files solely by expression identity."""
    nodes = {node.get("id"): node for node in graph.get("nodes", [])}
    incoming: dict[str, set[str]] = {}
    for edge in graph.get("edges", []):
        source = nodes.get(edge.get("source"), {})
        target = nodes.get(edge.get("target"), {})
        if edge.get("type") != "BINDS_STATE" or source.get("label") != "TemplateBinding" or target.get("label") != "BoundState":
            continue
        paths = incoming.setdefault(str(edge.get("target")), set())
        paths.update(
            str(item.get("source_path")) for item in edge.get("evidence", [])
            if item.get("source_path")
        )
    return [
        {"bound_state_id": node_id, "expression": nodes[node_id].get("name", ""), "source_paths": sorted(paths)}
        for node_id, paths in sorted(incoming.items()) if len(paths) > 1
    ]


def validate_run_output(run_output: Path, *, enable_roslyn: bool) -> dict[str, Any]:
    """Validate reviewability without changing or filtering raw run output."""
    expected = BASE_FILES | (ROSLYN_FILES if enable_roslyn else set())
    missing = sorted(name for name in expected if not (run_output / name).is_file())
    json_errors: list[dict[str, str]] = []
    for path in run_output.rglob("*.json"):
        try:
            _read_json(path)
        except (OSError, json.JSONDecodeError) as error:
            json_errors.append({"path": path.relative_to(run_output).as_posix(), "error": str(error)})

    graph: dict[str, Any] = {}
    graph_error: str | None = None
    try:
        graph = _read_json(run_output / "knowledge-graph.json")
    except (OSError, json.JSONDecodeError) as error:
        graph_error = str(error)
    nodes = graph.get("nodes", []) if isinstance(graph, dict) else []
    edges = graph.get("edges", []) if isinstance(graph, dict) else []
    warnings = graph.get("warnings", []) if isinstance(graph, dict) else []
    node_labels = sorted({str(node.get("label", "")) for node in nodes})
    edge_types = sorted({str(edge.get("type", "")) for edge in edges})
    warning_paths = {str(warning.get("source_path", "")) for warning in warnings if warning.get("source_path")}
    roslyn = {}
    if (run_output / "roslyn-semantic-all.json").is_file():
        roslyn = _read_json(run_output / "roslyn-semantic-all.json")
    roslyn_facts = roslyn.get("facts", []) if isinstance(roslyn, dict) else []
    unresolved = {
        "symbols": 0, "invocation_targets": 0, "parameter_types": 0, "return_types": 0,
    }
    for fact in roslyn_facts:
        evidence = fact.get("evidence", {})
        properties = fact.get("properties", {})
        if evidence.get("resolution_status") == "unresolved":
            unresolved["symbols"] += 1
            kind = fact.get("kind")
            if kind == "invocation": unresolved["invocation_targets"] += 1
            if kind in {"parameter", "action"} and not properties.get("parameter_type_identity"): unresolved["parameter_types"] += 1
            if kind == "action" and not properties.get("return_type_identity"): unresolved["return_types"] += 1
    no_node_evidence = [node.get("id", "") for node in nodes if not node.get("evidence")]
    no_edge_evidence = [edge.get("type", "") + ":" + edge.get("source", "") for edge in edges if not edge.get("evidence")]
    findings = scan_for_secrets(run_output)
    bound_state_collisions = find_bound_state_collisions(graph)
    report = {
        "valid": not missing and not json_errors and graph_error is None and not findings and not bound_state_collisions,
        "expected_artifacts": sorted(expected), "missing_artifacts": missing, "json_errors": json_errors,
        "secret_scan_findings": findings,
        "graph": {
            "nodes": len(nodes), "relationships": len(edges), "node_labels": node_labels,
            "relationship_types": edge_types, "nodes_with_review_warnings": len(warning_paths),
            "nodes_without_evidence": no_node_evidence, "relationships_without_evidence": no_edge_evidence,
            "unresolved_roslyn_symbols": unresolved["symbols"],
            "unresolved_invocation_targets": unresolved["invocation_targets"],
            "unresolved_parameter_types": unresolved["parameter_types"],
            "unresolved_return_types": unresolved["return_types"],
        },
        "semantic_integrity": {
            "bound_state_cross_file_collisions": len(bound_state_collisions),
            "bound_state_collision_examples": bound_state_collisions[:20],
        },
    }
    write_json(run_output / "knowledge-graph-validation.json", report)
    write_json(run_output / "secret-scan.json", {"findings": findings, "passed": not findings})
    return report


def publish_readiness_analysis(run_output: Path, run_id: str) -> dict[str, Any]:
    """Publish the loader-required readiness record from immutable run metadata."""
    validation = _read_json(run_output / "knowledge-graph-validation.json")
    status = _read_json(run_output / "graph-run-status.json")
    readiness = assess_graph_readiness(validation, status, run_id)
    write_json(run_output / "kg-readiness-analysis.json", readiness)
    lines = ["# Knowledge Graph Readiness", "", f"KG_READINESS_STATUS: {readiness['readiness']}", ""]
    lines.extend(f"- {item}" for item in [*readiness["blockers"], *readiness["limitations"]])
    if len(lines) == 4:
        lines.append("- No readiness blockers or limitations were identified.")
    (run_output / "kg-readiness-analysis.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return readiness


def validate_archive_output(run_output: Path, *, enable_roslyn: bool) -> dict[str, Any]:
    """Validate both raw graph output and the approved-archive contract."""
    report = validate_run_output(run_output, enable_roslyn=enable_roslyn)
    missing = sorted(name for name in READINESS_FILES if not (run_output / name).is_file())
    report["expected_artifacts"] = sorted(set(report["expected_artifacts"]) | READINESS_FILES)
    report["missing_artifacts"] = sorted(set(report["missing_artifacts"]) | set(missing))
    report["valid"] = report["valid"] and not missing
    write_json(run_output / "knowledge-graph-validation.json", report)
    return report


def preserve_completed_run(run_output: Path, project_id: str, *, enable_roslyn: bool, archive_root: Path) -> dict[str, Any]:
    """Copy validated raw output to Git-reviewable latest and immutable run paths."""
    report = validate_run_output(run_output, enable_roslyn=enable_roslyn)
    if not report["valid"]:
        raise ValueError("Knowledge-graph review archive was not created because validation or secret scanning failed.")
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M%S")
    safe_project = re.sub(r"[^A-Za-z0-9._-]", "-", project_id)
    runs = archive_root / "runs"
    run_id = f"{safe_project}-{timestamp}"
    destination = runs / run_id
    suffix = 2
    while destination.exists():
        destination = runs / f"{run_id}-{suffix}"
        suffix += 1
    runs.mkdir(parents=True, exist_ok=True)
    shutil.copytree(run_output, destination)
    metadata = {
        "application_project_id": project_id, "run_id": destination.name,
        "generation_timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "tree_sitter_completed": True, "roslyn_semantic_completed": enable_roslyn,
        "lsp_analysis_completed": False, "validation": report,
    }
    write_json(destination / "review-metadata.json", metadata)
    publish_readiness_analysis(destination, destination.name)
    report = validate_archive_output(destination, enable_roslyn=enable_roslyn)
    metadata["validation"] = report
    write_json(destination / "review-metadata.json", metadata)
    latest = archive_root / "latest"
    if latest.exists(): shutil.rmtree(latest)
    shutil.copytree(destination, latest)
    return {"run_id": destination.name, "path": str(destination), "validation": report}
