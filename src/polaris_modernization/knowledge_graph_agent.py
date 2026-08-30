"""Deterministic Create Knowledge Graph workflow orchestration."""

from __future__ import annotations

from datetime import datetime, timezone
import os
from pathlib import Path
import re
from typing import Any

from polaris_modernization.graph.neo4j_loader import Neo4jLoader, connect, read_graph
from polaris_modernization.graph.writer import write_json

PROJECT_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
NEO4J_BROWSER_URL = "http://localhost:7474"


def validate_project_id(project_id: str) -> str | None:
    if not project_id or not project_id.strip():
        return "--project-id must be non-empty."
    if project_id != project_id.strip() or project_id in {".", ".."}:
        return "--project-id must not contain surrounding whitespace or path traversal."
    if not PROJECT_ID_PATTERN.fullmatch(project_id):
        return "--project-id may contain only letters, numbers, dots, underscores, and hyphens."
    return None


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _stage(name: str, status: str, message: str) -> dict[str, str]:
    return {"name": name, "status": status, "message": message}


def _summary(status: dict[str, Any]) -> str:
    lines = [
        "# Create Knowledge Graph Run",
        "",
        f"- Overall status: `{status['overall_status']}`",
        f"- Project ID: `{status['project_id']}`",
        f"- Source root: `{status['source_root']}`",
        f"- Started: `{status['started_at']}`",
        f"- Ended: `{status['ended_at']}`",
        f"- Neo4j Browser: " + NEO4J_BROWSER_URL,
        "",
        "## Workflow Stages",
        "",
    ]
    lines.extend(f"- `{item['name']}`: `{item['status']}` - {item['message']}" for item in status["stages"])
    lines.extend([
        "",
        "## Results",
        "",
        f"- Files: {status['counts']['file_count']}",
        f"- Facts: {status['counts']['fact_count']}",
        f"- Nodes: {status['counts']['node_count']}",
        f"- Edges: {status['counts']['edge_count']}",
        f"- Warnings: {status['counts']['warning_count']}",
        f"- Extraction warnings: {status['counts'].get('extraction_warning_count', 0)}",
        f"- Roslyn: `{status['roslyn']['status']}`",
        f"- Neo4j: `{status['neo4j']['status']}`",
        "",
        "## Artifacts",
        "",
    ])
    lines.extend(f"- `{name}`: `{path}`" for name, path in status["artifact_paths"].items())
    lines.extend(["", "## Safe Next Actions", ""])
    lines.extend(f"- {action}" for action in status["next_actions"])
    return "\n".join(lines) + "\n"


def _write_status(status: dict[str, Any], output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    status_path = output / "graph-run-status.json"
    summary_path = output / "graph-run-summary.md"
    status["artifact_paths"]["graph_run_status"] = str(status_path)
    status["artifact_paths"]["graph_run_summary"] = str(summary_path)
    write_json(status_path, status)
    summary_path.write_text(_summary(status), encoding="utf-8")


def create_knowledge_graph(
    source_root: Path,
    project_id: str,
    profile_name: str,
    output: Path,
    *,
    enable_roslyn: bool = False,
    load_neo4j: bool = False,
) -> dict[str, Any]:
    """Run the project-isolated graph workflow and always return safe status data."""
    started_at = _timestamp()
    project_error = validate_project_id(project_id)
    source_path = Path(source_root)
    run_output = Path(output) / project_id if not project_error else None
    status: dict[str, Any] = {
        "project_id": project_id,
        "source_root": str(source_path.resolve(strict=False)),
        "started_at": started_at,
        "ended_at": started_at,
        "overall_status": "failed",
        "stages": [],
        "counts": {"file_count": 0, "fact_count": 0, "node_count": 0, "edge_count": 0, "warning_count": 0},
        "roslyn": {"status": "skipped", "enabled": enable_roslyn},
        "neo4j": {"status": "skipped", "requested": load_neo4j},
        "artifact_paths": {},
        "neo4j_browser_url": NEO4J_BROWSER_URL,
        "next_actions": [],
    }

    if project_error:
        status["stages"].append(_stage("validate_input", "failed", project_error))
        status["next_actions"] = ["Choose a unique project ID using letters, numbers, dots, underscores, or hyphens."]
        return status
    if not source_path.exists() or not source_path.is_dir():
        status["stages"].append(_stage("validate_input", "failed", "--source-root must exist and be a directory."))
        status["next_actions"] = ["Choose an existing local source repository or folder."]
        status["ended_at"] = _timestamp()
        _write_status(status, run_output)
        return status

    status["stages"].append(_stage("validate_input", "succeeded", "Source root and project ID are valid."))
    try:
        # Imported lazily to keep this module independently testable without CLI setup.
        from polaris_modernization.cli import analyze

        result = analyze(source_path, project_id, profile_name, Path(output), enable_roslyn)
        graph = result["graph"]
        status["counts"] = {
            "file_count": len(result["inventory"]),
            "fact_count": len(result["facts"]) + len(result["roslyn"]["facts"]),
            "node_count": len(graph["nodes"]),
            "edge_count": len(graph["edges"]),
            "warning_count": len(result["warnings"]) + len(graph["warnings"]),
            "extraction_warning_count": len(result["extraction_warnings"]),
        }
        status["artifact_paths"].update({
            "knowledge_graph": str(result["output"] / "knowledge-graph.json"),
            "source_inventory": str(result["output"] / "source-inventory.json"),
            "facts": str(result["output"] / "facts.json"),
        })
        roslyn_warnings = result["roslyn"]["warnings"]
        if enable_roslyn and not roslyn_warnings:
            status["roslyn"] = {"status": "succeeded", "enabled": True}
        elif enable_roslyn:
            status["roslyn"] = {"status": "warning", "enabled": True, "warning_count": len(roslyn_warnings)}
        analysis_status = result["analysis_status"]
        if analysis_status == "failed":
            status["stages"].append(_stage("analyze_source", "failed", "Every selected extractable file failed in isolated extraction."))
            status["next_actions"] = ["Review extraction warnings and retry after the affected parser boundary is repaired."]
            status["ended_at"] = _timestamp()
            _write_status(status, run_output)
            return status
        if analysis_status == "succeeded_with_warnings":
            status["stages"].append(_stage("analyze_source", "warning", "Analysis completed with isolated file extraction warnings."))
        else:
            status["stages"].append(_stage("analyze_source", "succeeded", "Deterministic analysis completed."))
    except Exception as error:
        status["stages"].append(_stage("analyze_source", "failed", f"Analysis failed: {error}"))
        status["next_actions"] = ["Correct the source or selected profile, then run the command again."]
        status["ended_at"] = _timestamp()
        _write_status(status, run_output)
        return status

    try:
        graph_path = Path(status["artifact_paths"]["knowledge_graph"])
        read_graph(graph_path, project_id)
        status["stages"].append(_stage("validate_graph", "succeeded", "Knowledge graph is project-scoped and valid."))
    except Exception as error:
        status["stages"].append(_stage("validate_graph", "failed", f"Graph validation failed: {error}"))
        status["next_actions"] = ["Review the generated graph artifact and rerun after correcting the issue."]
        status["ended_at"] = _timestamp()
        _write_status(status, run_output)
        return status

    has_extraction_warnings = bool(result["extraction_warnings"])
    if has_extraction_warnings and load_neo4j:
        status["stages"].append(_stage("load_neo4j", "warning", "Neo4j load blocked because isolated extraction warnings require review."))
        status["neo4j"] = {"status": "blocked", "requested": True}
        status["next_actions"] = ["Review skipped-file extraction warnings before any future Neo4j load approval."]
    elif not load_neo4j:
        status["stages"].append(_stage("load_neo4j", "warning", "Neo4j load skipped by --skip-neo4j or default graph-only mode."))
        status["neo4j"] = {"status": "skipped", "requested": False}
        status["next_actions"] = [
            "Review knowledge-graph.json locally.",
            "Start Neo4j with `docker compose up -d` when ready; this command does not start Docker.",
            "Rerun with --load-neo4j after setting NEO4J_URI, NEO4J_USERNAME, and NEO4J_PASSWORD.",
            f"Open Neo4j Browser manually at {NEO4J_BROWSER_URL}.",
        ]
    else:
        missing = [name for name in ("NEO4J_URI", "NEO4J_USERNAME", "NEO4J_PASSWORD") if not os.getenv(name)]
        if missing:
            status["stages"].append(_stage("load_neo4j", "failed", "Neo4j configuration is unavailable."))
            status["neo4j"] = {"status": "failed", "requested": True, "message": f"Missing environment variables: {', '.join(missing)}"}
            status["next_actions"] = ["Set the required Neo4j environment variables locally, then rerun with --load-neo4j."]
        else:
            driver = None
            try:
                driver = connect(os.environ["NEO4J_URI"], os.environ["NEO4J_USERNAME"], os.environ["NEO4J_PASSWORD"])
                loaded = Neo4jLoader(driver).load(graph, project_id)
                status["stages"].append(_stage("load_neo4j", "succeeded", "Loaded only this project graph into Neo4j."))
                status["neo4j"] = {"status": "succeeded", "requested": True, "loaded": loaded}
                status["next_actions"] = [f"Open Neo4j Browser manually at {NEO4J_BROWSER_URL} and run a read-only demo query."]
            except Exception as error:
                status["stages"].append(_stage("load_neo4j", "failed", f"Neo4j load failed: {error}"))
                status["neo4j"] = {"status": "failed", "requested": True, "message": "Connection or load failed; no delete operation was attempted."}
                status["next_actions"] = ["Verify Neo4j is running and the local connection configuration, then rerun with --load-neo4j."]
            finally:
                if driver is not None:
                    driver.close()

    status["overall_status"] = "failed" if any(item["status"] == "failed" for item in status["stages"]) else "succeeded_with_warnings" if any(item["status"] == "warning" for item in status["stages"] if item["name"] == "analyze_source") else "succeeded"
    status["ended_at"] = _timestamp()
    status["stages"].append(_stage("produce_run_status", "succeeded", "Customer-facing run status artifacts were created."))
    _write_status(status, run_output)
    return status
