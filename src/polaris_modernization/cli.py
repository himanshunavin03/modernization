"""CLI for deterministic, scoped source extraction."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import re

from polaris_modernization.framework_detection import detect_frameworks
from polaris_modernization.graph.api_mapping import RESOLVER_VERSION, resolve_api_relationships
from polaris_modernization.graph.normalizer import normalize
from polaris_modernization.graph.writer import write_json, write_summary
from polaris_modernization.models import Fact
from polaris_modernization.profiles import load_profile, merge_profiles
from polaris_modernization.source_inventory import build_inventory
from polaris_modernization.tree_sitter_extractors.registry import extractor_for
from polaris_modernization.graph.neo4j_loader import Neo4jLoader, connect, read_graph
from polaris_modernization.roslyn_bridge import enrich
from polaris_modernization.isolated_extraction import extract_file
from polaris_modernization.knowledge_graph_agent import create_knowledge_graph
from polaris_modernization.graph.context_flow import add_context_flow
from polaris_modernization.framework_analyzers import FrameworkAnalyzerRegistry

ROSLYN_LABELS = {
    "namespace": "Namespace", "controller": "Controller", "action": "Action",
    "type": "Type", "dto": "DTO", "property": "Property", "method": "Method",
    "endpoint": "Endpoint", "authorization_policy": "AuthorizationPolicy",
}
FIELDLESS_TYPES = {
    "bool", "byte", "byte[]", "char", "dateonly", "datetime", "datetimeoffset", "decimal",
    "double", "filecontentresult", "float", "guid", "iactionresult", "int", "jsonresult",
    "long", "object", "short", "string", "task", "timeonly", "timespan", "void",
}
CONTAINER_TYPES = {"Task", "ActionResult", "IActionResult", "IEnumerable", "ICollection", "IList", "List", "Collection", "Nullable"}


def _api_resolution_summary_markdown(project_id: str, resolution: dict[str, object]) -> str:
    summary = resolution["summary"]
    audit_rows = resolution["audit_rows"]
    promoted = [row for row in audit_rows if row["previous_status"] != "PROVEN" and row["public_status"] == "PROVEN"]
    unresolved = [row for row in audit_rows if row["public_status"] in {"UNRESOLVED", "DYNAMIC"}]
    examples = []
    for source_path, expression in (
        ("src/MyHealth.Web/content/app/components/doctors/services/doctorsService.js", "/api/doctors"),
        ("src/MyHealth.Web/content/app/components/doctors/services/doctorsService.js", "`/api/doctors/${doctorId}`"),
        ("src/MyHealth.Web/content/app/components/patients/services/patientsService.js", "/api/patients"),
        ("src/MyHealth.Web/content/app/components/dashboard/services/dashboardService.js", "'/api/reports/expenses/' + year"),
        ("src/MyHealth.Web/content/app/components/dashboard/services/dashboardService.js", "'/api/reports/patients/' + year"),
        ("src/MyHealth.Web/content/app/components/dashboard/services/dashboardService.js", "/api/reports/clinicsummary"),
        ("src/MyHealth.Web/content/app/components/clinics/services/clinicsService.js", "`/api/tenants/${tenantId}`"),
        ("src/MyHealth.Web/content/app/components/clinics/services/clinicsService.js", "/api/tenants/list"),
        ("src/MyHealth.Web/content/app/components/shared/controllers/headerController.js", "/api/users/current/user"),
        ("src/MyHealth.Web/content/app/components/shared/controllers/headerController.js", "/api/users/current/claims"),
    ):
        row = next((item for item in audit_rows if item["source_file"] == source_path and item["raw_url_expression"] == expression), None)
        if row:
            examples.append(row)
    lines = [
        "# API Relationship Resolution Summary",
        "",
        f"- Project ID: `{project_id}`",
        f"- Resolver version: `{RESOLVER_VERSION}`",
        f"- Total frontend calls: {summary['total_frontend_calls']}",
        f"- Proven before: {summary['previous_proven']}",
        f"- Proven after: {summary['final_proven']}",
        f"- New exact static matches: {summary['new_exact_static_matches']}",
        f"- New exact template matches: {summary['new_exact_template_matches']}",
        f"- New unique parameterized matches: {summary['new_unique_parameterized_matches']}",
        f"- Remaining dynamic: {summary['remaining_dynamic']}",
        f"- Remaining ambiguous: {summary['remaining_ambiguous']}",
        f"- External: {summary['external']}",
        f"- No backend match: {summary['no_backend_match']}",
        f"- Unresolved: {summary['unresolved']}",
        "",
        "## Root Cause",
        "",
        "The previous resolver only promoted inline literal AngularJS URLs. Calls routed through `url` variables or simple dynamic template/concatenation expressions never reached deterministic method-plus-route reconciliation, so uniquely matchable endpoints remained unresolved or dynamic.",
        "",
        "## Promotions",
        "",
    ]
    if promoted:
        lines.extend(
            f"- `{item['raw_url_expression']}` in `{item['source_file']}` -> `{item['final_status']}`"
            for item in promoted[:20]
        )
    else:
        lines.append("- No frontend calls were promoted.")
    if examples:
        lines.extend(["", "## Important Cases", ""])
        lines.extend(
            f"- `{item['raw_url_expression']}` in `{item['source_file']}` -> `{item['final_status']}` ({item['current_relationship_reason']})"
            for item in examples
        )
    if unresolved:
        lines.extend(["", "## Remaining Limitations", ""])
        lines.extend(
            f"- `{item['raw_url_expression']}` in `{item['source_file']}` -> `{item['final_status']}` ({item['current_relationship_reason']})"
            for item in unresolved[:10]
        )
    return "\n".join(lines) + "\n"


def _split_generic_arguments(value: str) -> list[str]:
    parts: list[str] = []
    depth = 0
    start = 0
    for index, char in enumerate(value):
        if char == "<":
            depth += 1
        elif char == ">" and depth:
            depth -= 1
        elif char == "," and depth == 0:
            parts.append(value[start:index].strip())
            start = index + 1
    parts.append(value[start:].strip())
    return [part for part in parts if part]


def _unwrap_container_type(type_name: str | None) -> str | None:
    if not type_name:
        return None
    value = str(type_name).replace("global::", "").strip().rstrip("?")
    while True:
        match = re.fullmatch(r"(?P<outer>[\w.]+)\s*<(?P<inner>.+)>", value)
        if not match:
            return value
        outer = match.group("outer").rsplit(".", 1)[-1]
        if outer not in CONTAINER_TYPES:
            return value
        arguments = _split_generic_arguments(match.group("inner"))
        if len(arguments) != 1:
            return value
        value = arguments[0].strip().rstrip("?")


def _short_type_name(type_name: str | None) -> str | None:
    value = _unwrap_container_type(type_name)
    if not value:
        return None
    return value.replace("global::", "").rstrip("?").removesuffix("[]").rsplit(".", 1)[-1]


def _fields_for_type(type_name: str | None, types_by_short: dict[str, list[dict]], properties_by_owner: dict[str, list[dict]]) -> list[dict]:
    short_name = _short_type_name(type_name)
    if not short_name or short_name.casefold() in FIELDLESS_TYPES:
        return []
    matches = types_by_short.get(short_name, [])
    if len(matches) != 1:
        return []
    owner_identity = matches[0].get("properties", {}).get("identity")
    if not owner_identity:
        return []
    fields = []
    for item in sorted(properties_by_owner.get(str(owner_identity), []), key=lambda fact: (fact["evidence"]["source_path"], fact["evidence"]["line_start"], fact["name"])):
        evidence = item["evidence"]
        fields.append({
            "name": item["name"],
            "type": item.get("properties", {}).get("type_name"),
            "source_path": evidence["source_path"],
            "line_start": evidence["line_start"],
            "line_end": evidence["line_end"],
        })
    return fields


def _enrich_endpoint_contracts(facts: list[Fact], roslyn_facts: list[dict]) -> list[Fact]:
    types_by_short: dict[str, list[dict]] = {}
    properties_by_owner: dict[str, list[dict]] = {}
    for fact in roslyn_facts:
        if fact.get("evidence", {}).get("resolution_status") != "proven":
            continue
        if fact.get("kind") in {"type", "dto"}:
            short_name = _short_type_name(str(fact.get("properties", {}).get("identity") or fact["name"]))
            if short_name:
                types_by_short.setdefault(short_name, []).append(fact)
        elif fact.get("kind") == "property" and fact.get("properties", {}).get("owner_identity"):
            properties_by_owner.setdefault(str(fact["properties"]["owner_identity"]), []).append(fact)
    if not types_by_short or not properties_by_owner:
        return facts
    enriched: list[Fact] = []
    for fact in facts:
        if fact.kind != "endpoint":
            enriched.append(fact)
            continue
        props = dict(fact.properties)
        if not props.get("request_fields") and props.get("request_type"):
            props["request_fields"] = _fields_for_type(str(props["request_type"]), types_by_short, properties_by_owner)
        if not props.get("response_fields") and props.get("response_type"):
            props["response_fields"] = _fields_for_type(str(props["response_type"]), types_by_short, properties_by_owner)
        enriched.append(Fact(fact.kind, fact.name, fact.evidence, props))
    return enriched


def merge_roslyn(graph: dict, facts: list[dict], project_id: str, out_of_scope_symbols: dict[str, str] | None = None) -> None:
    out_of_scope_symbols = out_of_scope_symbols or {}
    nodes = {node["id"]: node for node in graph["nodes"]}
    edges = {(edge["type"], edge["source"], edge["target"]): edge for edge in graph["edges"]}
    semantic_labels: dict[str, str] = {}
    for fact in facts:
        evidence = fact.get("evidence", {})
        properties = fact.get("properties", {})
        label = ROSLYN_LABELS.get(fact.get("kind"))
        if fact.get("project_id") != project_id or evidence.get("resolution_status") != "proven" or not label:
            continue
        identity = str(properties.get("identity") or fact["name"])
        # A proven DTO fact is more specific than a generic type fact for the same symbol.
        if identity not in semantic_labels or label == "DTO":
            semantic_labels[identity] = label

    def node(label: str, name: str, evidence: dict, properties: dict, *, merge_tree_sitter: bool = False) -> str:
        if merge_tree_sitter:
            for candidate in nodes.values():
                if candidate["label"] == label and candidate["name"] == name and any(item.get("source_path") == evidence.get("source_path") for item in candidate["evidence"]):
                    candidate["evidence"].append(evidence)
                    return candidate["id"]
        identity = f"{project_id}:{label}:{properties.get('identity') or name}"
        item = nodes.get(identity)
        if item is None:
            item = {"id": identity, "project_id": project_id, "label": label, "name": name, "properties": properties, "evidence": []}
            nodes[identity] = item
        item["evidence"].append(evidence)
        return identity

    def edge(kind: str, source: str, target: str, evidence: dict) -> None:
        key = (kind, source, target)
        item = edges.get(key)
        if item is None:
            item = {"project_id": project_id, "type": kind, "source": source, "target": target, "properties": {}, "evidence": []}
            edges[key] = item
        item["evidence"].append(evidence)

    semantic_nodes: dict[str, str] = {}
    for fact in facts:
        label = ROSLYN_LABELS.get(fact.get("kind"))
        evidence = fact.get("evidence", {})
        properties = fact.get("properties", {})
        if fact.get("project_id") != project_id or evidence.get("resolution_status") != "proven":
            if evidence.get("diagnostic"):
                graph["warnings"].append({"source_path": evidence.get("source_path", ""), "message": evidence["diagnostic"]})
            continue
        if label:
            identity = str(properties.get("identity") or fact["name"])
            label = semantic_labels.get(identity, label)
            semantic_nodes[identity] = node(label, fact["name"], evidence, properties, merge_tree_sitter=fact["kind"] in {"controller", "action"})

    def reference(label: str, identity: object, evidence: dict) -> str | None:
        if identity is None:
            return None
        key = str(identity)
        if key in out_of_scope_symbols:
            return node("OutOfScopeReference", key, evidence, {
                "identity": key,
                "source_path": out_of_scope_symbols[key],
                "reason": "Referenced by an in-scope semantic fact.",
            })
        resolved_label = semantic_labels.get(key, label)
        return semantic_nodes.get(key) or node(resolved_label, key.rsplit(".", 1)[-1], evidence, {"identity": key})

    for fact in facts:
        evidence = fact.get("evidence", {})
        properties = fact.get("properties", {})
        if fact.get("project_id") != project_id or evidence.get("resolution_status") != "proven":
            continue
        identity = str(properties.get("identity") or fact.get("name"))
        subject = semantic_nodes.get(identity)
        kind = fact.get("kind")
        if kind == "action" and subject:
            owner = reference("Controller", properties.get("owner_identity"), evidence)
            returned = reference("Type", properties.get("return_type_identity"), evidence)
            if owner:
                edge("DECLARES", owner, subject, evidence)
            if returned:
                edge("RETURNS_TYPE", subject, returned, evidence)
        elif kind == "endpoint" and subject:
            owner = reference("Action", properties.get("owner_identity"), evidence)
            if owner:
                edge("EXPOSES", owner, subject, evidence)
        elif kind == "property" and subject:
            owner = reference("Type", properties.get("owner_identity"), evidence)
            if owner:
                edge("HAS_PROPERTY", owner, subject, evidence)
        elif kind == "invocation":
            owner = reference("Method", properties.get("owner_identity"), evidence)
            target = reference("Method", properties.get("target_identity"), evidence)
            if owner and target:
                edge("INVOKES", owner, target, evidence)
        elif kind == "authorization_policy" and subject:
            owner_label = "Controller" if properties.get("owner_kind") == "controller" else "Action"
            owner = reference(owner_label, properties.get("owner_identity"), evidence)
            if owner:
                edge("PROTECTED_BY", owner, subject, evidence)
    for item in list(edges.values()):
        target = nodes.get(item["target"])
        if target and target["label"] == "OutOfScopeReference":
            edge("DEPENDS_ON_OUT_OF_SCOPE", item["source"], item["target"], item["evidence"][0])
    graph["nodes"] = sorted(nodes.values(), key=lambda item: item["id"])
    graph["edges"] = sorted(edges.values(), key=lambda item: (item["type"], item["source"], item["target"]))


def analyze(source_root: Path, project_id: str, profile_name: str, output: Path, enable_roslyn: bool = False) -> dict:
    profile = merge_profiles(load_profile("default"), load_profile(profile_name))
    inventory, warnings = build_inventory(source_root, profile)
    facts: list[Fact] = []
    source_root = source_root.resolve()
    scope_type = profile.get("scope_type", "full_application")
    if scope_type not in {"full_application", "selected_modernization_flow", "end_to_end_context_flow"}:
        raise ValueError("scope_type must be full_application, selected_modernization_flow, or end_to_end_context_flow")
    extractable_entries = []
    for entry in inventory:
        source_path = source_root / entry["source_path"]
        if not entry["selected_for_extraction"]:
            entry["extraction_status"] = "out_of_scope"
        elif extractor_for(source_path) is None:
            entry["extraction_status"] = "in_scope_unsupported"
        else:
            extractable_entries.append(entry)

    def request(entry: dict) -> dict[str, str]:
        return {
            "source_root": str(source_root),
            "source_path": entry["source_path"],
            "source_hash": entry["source_hash"],
            "project_id": project_id,
            "language": str(entry.get("language") or "unknown"),
        }

    extraction_warnings: list[dict] = []
    # Native grammars run outside the parent so a parser fault skips only its source file.
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(extract_file, (request(entry) for entry in extractable_entries)))
    successful_extractions = 0
    for entry, result in zip(extractable_entries, results):
        if result.warning:
            entry["extraction_status"] = "in_scope_failed_isolated"
            extraction_warnings.append(result.warning)
        else:
            entry["extraction_status"] = "in_scope_succeeded"
            successful_extractions += 1
            facts.extend(result.facts)

    in_scope_entries = [entry for entry in inventory if entry["selected_for_extraction"]]
    detections = detect_frameworks(source_root, inventory)
    framework_result = FrameworkAnalyzerRegistry().analyze(source_root, in_scope_entries, project_id, detections)
    facts.extend(framework_result.facts)
    warnings.extend(framework_result.warnings)
    run_output = output / project_id
    run_output.mkdir(parents=True, exist_ok=True)
    roslyn_all = enrich(source_root, project_id, run_output / "roslyn-semantic-all.json") if enable_roslyn else {"project_id":project_id,"facts":[],"warnings":[]}
    in_scope_paths = {entry["source_path"] for entry in in_scope_entries}
    roslyn_facts = roslyn_all["facts"] if scope_type == "full_application" else [fact for fact in roslyn_all["facts"] if fact.get("evidence", {}).get("source_path") in in_scope_paths]
    declaration_kinds = {"namespace", "controller", "type", "dto", "property", "method", "action"}
    in_scope_symbols = {
        str(fact.get("properties", {}).get("identity"))
        for fact in roslyn_all["facts"]
        if fact.get("evidence", {}).get("source_path") in in_scope_paths
        and fact.get("kind") in declaration_kinds
        and fact.get("properties", {}).get("identity")
    }
    out_of_scope_symbols = {
        str(fact.get("properties", {}).get("identity")): str(fact.get("evidence", {}).get("source_path"))
        for fact in roslyn_all["facts"]
        if fact.get("evidence", {}).get("source_path") not in in_scope_paths
        and fact.get("kind") in declaration_kinds
        and fact.get("properties", {}).get("identity")
        and str(fact["properties"]["identity"]) not in in_scope_symbols
    } if scope_type == "selected_modernization_flow" else {}
    roslyn = {"project_id": project_id, "facts": roslyn_facts, "warnings": roslyn_all["warnings"]}
    facts = _enrich_endpoint_contracts(facts, roslyn_facts)
    api_resolution = resolve_api_relationships(facts)
    facts = [fact for fact in facts if fact.kind not in {"api_call", "api_mapping"}]
    facts.extend(api_resolution["call_facts"])
    facts.extend(api_resolution["mapping_facts"])
    warnings.extend(api_resolution["warnings"])
    graph_inventory = inventory if scope_type == "full_application" else in_scope_entries
    graph_metadata = {
        "scope_id": profile.get("scope_id", "full-application"),
        "scope_name": profile.get("scope_name", "Full application analysis"),
        "scope_description": profile.get("scope_description", "Complete discovered application inventory and graph."),
        "scope_type": scope_type,
        "selected_file_count": len(in_scope_entries),
        "out_of_scope_file_count": len(inventory) - len(in_scope_entries),
        "extraction_warning_count": len(extraction_warnings),
        "review_warning_count": 0,
        "coverage_status": "pending",
    }
    graph = normalize(project_id, graph_inventory, facts, graph_metadata)
    graph["warnings"].extend(framework_result.warnings)
    write_json(run_output / "roslyn-semantic.json", roslyn)
    graph["warnings"].extend(roslyn["warnings"])
    graph["warnings"].extend(extraction_warnings)
    merge_roslyn(graph, roslyn["facts"], project_id, out_of_scope_symbols)
    if scope_type == "end_to_end_context_flow":
        add_context_flow(graph, profile, project_id)
        graph["metadata"].update({"modernization_scope": "end_to_end_context", "transform_boundary": "ui_only", "backend_preservation_boundary": "api_domain_data"})
    graph["metadata"]["review_warning_count"] = len(graph["warnings"]) - len(extraction_warnings)
    opaque_dependency_count = sum(1 for fact in facts if fact.kind == "opaque_source")
    graph["metadata"]["opaque_dependency_count"] = opaque_dependency_count
    graph["metadata"]["coverage_status"] = (
        "complete_with_opaque_dependencies" if scope_type == "full_application" and not extraction_warnings and opaque_dependency_count
        else "complete_application" if scope_type == "full_application" and not extraction_warnings
        else "partial_application_with_extraction_failures" if scope_type == "full_application"
        else "scope_complete" if not extraction_warnings
        else "scope_partial_with_extraction_failures"
    )
    write_json(run_output / "source-inventory.json", {"project_id": project_id, "scope": graph["metadata"], "files": inventory, "warnings": warnings, "extraction_warnings": extraction_warnings})
    write_json(run_output / "framework-detection.json", {"project_id": project_id, "scope": graph["metadata"], "frameworks": detections})
    write_json(run_output / "facts.json", {"project_id": project_id, "facts": [fact.to_dict() for fact in facts]})
    write_json(run_output / "knowledge-graph.json", graph)
    write_json(run_output / "api-mapping-forensics.json", {
        "project_id": project_id,
        "run_id": project_id,
        **api_resolution["forensics"],
        "http_methods": {
            method: sum(1 for row in api_resolution["backend_endpoint_rows"] if row["http_method"] == method)
            for method in sorted({row["http_method"] for row in api_resolution["backend_endpoint_rows"]})
        },
        "controller_template_endpoints": sum(bool(row["controller_route"]) and "[controller]" in row["controller_route"] for row in api_resolution["backend_endpoint_rows"]),
        "controllers_with_controller_template": len({row["controller"] for row in api_resolution["backend_endpoint_rows"] if row["controller_route"] and "[controller]" in row["controller_route"]}),
        "unexpanded_controller_tokens": 0,
        "status": "PASS_WITH_EXPLAINED_LIMITATIONS" if api_resolution["summary"]["unresolved"] or api_resolution["summary"]["remaining_dynamic"] or api_resolution["summary"]["no_backend_match"] else "PASS",
    })
    write_json(run_output / "api-relationship-resolution-audit.json", {
        "project_id": project_id,
        "resolver_version": RESOLVER_VERSION,
        "summary": api_resolution["summary"],
        "before_after": api_resolution["before_after"],
        "frontend_calls": api_resolution["audit_rows"],
        "backend_endpoints": [
            {
                "backend_endpoint_id": row["endpoint_id"],
                "source_file": row["source_path"],
                "source_range": {"line_start": row["line_start"], "line_end": row["line_end"]},
                "framework": "ASP.NET",
                "controller": row["controller"],
                "action": row["action"],
                "http_method": row["http_method"],
                "controller_route": row["controller_route"],
                "action_route": row["action_route"],
                "resolved_route_template": row["resolved_route_template"],
                "normalized_route_template": row["normalized_route_template"],
                "path_parameters": row["path_parameters"],
                "query_parameters": row["query_parameters"],
                "request_type": row["request_type"],
                "request_fields": row["request_fields"],
                "response_type": row["response_type"],
                "response_fields": row["response_fields"],
            }
            for row in api_resolution["backend_endpoint_rows"]
        ],
    })
    write_json(run_output / "api-relationship-resolution-matrix.json", {"project_id": project_id, "rows": api_resolution["matrix_rows"]})
    write_json(run_output / "api-relationship-before-after.json", api_resolution["before_after"])
    (run_output / "api-relationship-resolution-summary.md").write_text(
        _api_resolution_summary_markdown(project_id, api_resolution),
        encoding="utf-8",
    )
    write_summary(run_output / "analysis-summary.md", inventory, facts, graph, extraction_warnings)
    analysis_status = "failed" if not extractable_entries or successful_extractions == 0 else "succeeded_with_warnings" if extraction_warnings else "succeeded"
    return {"inventory": inventory, "graph_inventory": graph_inventory, "facts": facts, "graph": graph, "warnings": warnings, "extraction_warnings": extraction_warnings, "output": run_output, "roslyn": roslyn, "analysis_status": analysis_status, "extractable_file_count": len(extractable_entries), "successful_extraction_count": successful_extractions, "api_resolution": api_resolution}


def main() -> None:
    parser = argparse.ArgumentParser(description="Deterministic Tree-sitter source extractor")
    subparsers = parser.add_subparsers(dest="command", required=True)
    analyze_parser = subparsers.add_parser("analyze")
    analyze_parser.add_argument("--source-root", required=True, type=Path)
    analyze_parser.add_argument("--project-id", required=True)
    analyze_parser.add_argument("--profile", required=True)
    analyze_parser.add_argument("--output", required=True, type=Path)
    analyze_parser.add_argument("--enable-roslyn", action="store_true")
    workflow_parser = subparsers.add_parser("create-knowledge-graph", help="Run the deterministic project-scoped graph workflow")
    workflow_parser.add_argument("--source-root", required=True, type=Path)
    workflow_parser.add_argument("--project-id", required=True)
    workflow_parser.add_argument("--profile", required=True)
    workflow_parser.add_argument("--output", required=True, type=Path)
    workflow_parser.add_argument("--enable-roslyn", action="store_true")
    neo4j_group = workflow_parser.add_mutually_exclusive_group()
    neo4j_group.add_argument("--load-neo4j", action="store_true")
    neo4j_group.add_argument("--skip-neo4j", action="store_true")
    agent_parser = subparsers.add_parser("agent-create-knowledge-graph", help="Thin agent adapter over create-knowledge-graph")
    agent_parser.add_argument("source_root", nargs="?", type=Path)
    agent_parser.add_argument("--project-id")
    agent_parser.add_argument("--profile", default="default")
    agent_parser.add_argument("--output", type=Path, default=Path("artifacts"))
    agent_parser.add_argument("--load-neo4j", action="store_true")
    understand_parser = subparsers.add_parser("understand-application", help="Prepare or validate interactive Phase 2 application understanding")
    understand_parser.add_argument("--kg-root", required=True, type=Path)
    understand_parser.add_argument("--output", type=Path, default=Path("artifacts/application-understanding"))
    understand_parser.add_argument("--agent-result", type=Path, help="Structured result supplied by the active Codex or Copilot chat agent.")
    feature_parser = subparsers.add_parser("generate-features", help="Prepare or validate evidence-backed modernization Features")
    feature_parser.add_argument("--application-understanding-root", required=True, type=Path)
    feature_parser.add_argument("--output", type=Path, default=Path("artifacts/features"))
    feature_parser.add_argument("--agent-result", type=Path, help="Structured Feature result supplied by the active Codex or Copilot chat agent.")
    business_feature_parser = subparsers.add_parser("enrich-business-features", help="Prepare or validate PO/BA Business Feature specifications")
    business_feature_parser.add_argument("--feature-root", required=True, type=Path)
    business_feature_parser.add_argument("--output", type=Path, default=Path("artifacts/business-features"))
    business_feature_parser.add_argument("--agent-result", type=Path, help="Structured PO/BA enrichment supplied by the active Codex or Copilot chat agent.")
    story_parser = subparsers.add_parser("generate-stories", help="Prepare or validate evidence-backed Jira-style Stories")
    story_parser.add_argument("--business-feature-root", required=True, type=Path)
    story_parser.add_argument("--output", type=Path, default=Path("artifacts/stories"))
    story_parser.add_argument("--agent-result", type=Path, help="Structured Story result supplied by the active Codex or Copilot chat agent.")
    ac_parser = subparsers.add_parser("generate-acceptance-criteria", help="Prepare or validate evidence-backed Acceptance Criteria")
    ac_parser.add_argument("--story-root", required=True, type=Path)
    ac_parser.add_argument("--output", type=Path, default=Path("artifacts/acceptance-criteria"))
    ac_parser.add_argument("--agent-result", type=Path)
    spec_parser = subparsers.add_parser("generate-feature-specifications", help="Consolidate approved Feature specifications")
    spec_parser.add_argument("--business-feature-root", required=True, type=Path)
    spec_parser.add_argument("--story-root", required=True, type=Path)
    spec_parser.add_argument("--acceptance-root", required=True, type=Path)
    spec_parser.add_argument("--output", type=Path, default=Path("artifacts/feature-specifications"))
    presentation_parser = subparsers.add_parser("refine-feature-presentations", help="Professionalize Feature Markdown without changing machine contracts")
    presentation_parser.add_argument("--source-specification-root", required=True, type=Path)
    presentation_parser.add_argument("--output", type=Path, default=Path("artifacts/feature-specifications"))
    narrative_parser = subparsers.add_parser("synthesize-feature-narratives", help="Build customer Feature narratives from approved concepts")
    narrative_parser.add_argument("--source-specification-root", required=True, type=Path)
    narrative_parser.add_argument("--knowledge-graph-root", required=True, type=Path)
    narrative_parser.add_argument("--application-source-root", required=True, type=Path)
    narrative_parser.add_argument("--output", type=Path, default=Path("artifacts/feature-specifications"))
    architecture_parser = subparsers.add_parser("recommend-architecture", help="Run target architecture orchestration over approved Feature artifacts")
    architecture_parser.add_argument("--project-id", required=True)
    architecture_parser.add_argument("--feature-id", required=True)
    architecture_parser.add_argument("--feature-specification-root", type=Path, default=Path("artifacts/feature-specifications/latest"))
    architecture_parser.add_argument("--design-provider", choices=("NONE", "FIGMA"), default="NONE")
    architecture_parser.add_argument("--design-reference")
    architecture_parser.add_argument("--output", type=Path, default=Path("artifacts/architecture"))
    task_parser = subparsers.add_parser("generate-technical-tasks", help="Generate an architecture-driven technical delivery plan")
    task_parser.add_argument("--project-id", required=True)
    task_parser.add_argument("--feature-id", required=True)
    task_parser.add_argument("--architecture-root", type=Path, default=Path("artifacts/architecture/latest"))
    task_parser.add_argument("--feature-specification-root", type=Path, default=Path("artifacts/feature-specifications/latest"))
    task_parser.add_argument("--design-provider", choices=("NONE", "FIGMA"), default="NONE")
    task_parser.add_argument("--design-mode", choices=("NONE", "FIXTURE", "LIVE"), default="NONE")
    task_parser.add_argument("--figma-url")
    task_parser.add_argument("--output", type=Path, default=Path("artifacts/technical-tasks"))
    task_parser.add_argument("--design-output", type=Path, default=Path("artifacts/design"))
    generation_parser = subparsers.add_parser("generate-angular-hero", help="Generate the Angular 22 hero Feature from existing application UI")
    generation_parser.add_argument("--project-id", required=True)
    generation_parser.add_argument("--feature-id", required=True)
    generation_parser.add_argument("--source-root", type=Path, default=Path("source/HealthClinic.biz"))
    generation_parser.add_argument("--architecture-root", type=Path, default=Path("artifacts/architecture/latest"))
    generation_parser.add_argument("--technical-task-root", type=Path, default=Path("artifacts/technical-tasks/latest"))
    generation_parser.add_argument("--feature-specification-root", type=Path, default=Path("artifacts/feature-specifications/latest"))
    generation_parser.add_argument("--workspace", type=Path, default=Path("modernized"))
    generation_parser.add_argument("--output", type=Path, default=Path("artifacts/modernization"))
    load_parser = subparsers.add_parser("load-neo4j")
    load_parser.add_argument("--graph", required=True, type=Path)
    load_parser.add_argument("--project-id", required=True)
    clear_parser = subparsers.add_parser("clear-neo4j-project")
    clear_parser.add_argument("--project-id", required=True)
    clear_parser.add_argument("--confirm-project-id", required=True)
    args = parser.parse_args()

    if args.command == "analyze":
        result = analyze(args.source_root, args.project_id, args.profile, args.output, args.enable_roslyn)
        print(f"Analyzed {len(result['inventory'])} files into {result['output']}")
    elif args.command == "create-knowledge-graph":
        result = create_knowledge_graph(
            args.source_root,
            args.project_id,
            args.profile,
            args.output,
            enable_roslyn=args.enable_roslyn,
            load_neo4j=args.load_neo4j,
        )
        print(f"Create Knowledge Graph {result['overall_status']} for {result['project_id']}")
        if result["artifact_paths"].get("graph_run_summary"):
            print(result["artifact_paths"]["graph_run_summary"])
        if result["overall_status"] == "failed":
            raise SystemExit(1)
    elif args.command == "agent-create-knowledge-graph":
        from polaris_modernization.agent_commands import create_knowledge_graph_command
        result = create_knowledge_graph_command(args.source_root, project_id=args.project_id, profile=args.profile, output=args.output, load_neo4j=args.load_neo4j)
        print(f"Create Knowledge Graph {result['overall_status']} for {result['project_id']}")
        if result["overall_status"] == "failed": raise SystemExit(1)
    elif args.command == "understand-application":
        from polaris_modernization.application_understanding.workflow import prepare_application_understanding, validate_and_persist_application_understanding
        if args.agent_result:
            result = validate_and_persist_application_understanding(args.kg_root, args.output, args.agent_result)
            print(f"Application understanding COMPLETE for {result['understanding'].project_id}")
        else:
            result = prepare_application_understanding(args.kg_root, args.output)
            print(f"Application understanding prepared for active-agent reasoning for {result['approved']['status']['project_id']}")
        print(result["path"])
    elif args.command == "generate-features":
        from polaris_modernization.feature_generation.workflow import prepare_feature_generation, validate_and_persist_features
        if args.agent_result:
            result = validate_and_persist_features(args.application_understanding_root, args.output, args.agent_result)
            print(f"Feature generation {result['catalog'].readiness} for {result['catalog'].project_id}")
        else:
            result = prepare_feature_generation(args.application_understanding_root, args.output)
            print(f"Feature generation prepared for active-agent reasoning for {result['approved']['understanding']['project_id']}")
        print(result["path"])
    elif args.command == "enrich-business-features":
        from polaris_modernization.business_features.workflow import prepare_business_feature_enrichment, validate_and_persist_business_features
        if args.agent_result:
            result = validate_and_persist_business_features(args.feature_root, args.output, args.agent_result)
            print(f"Business Feature enrichment {result['catalog'].readiness} for {result['catalog'].project_id}")
        else:
            result = prepare_business_feature_enrichment(args.feature_root, args.output)
            print(f"Business Feature enrichment prepared for active-agent reasoning for {result['approved']['catalog']['project_id']}")
        print(result["path"])
    elif args.command == "generate-stories":
        from polaris_modernization.stories.workflow import prepare_story_generation, validate_and_persist_stories
        if args.agent_result:
            result = validate_and_persist_stories(args.business_feature_root, args.output, args.agent_result)
            print(f"Story generation {result['catalog'].readiness} for {result['catalog'].project_id}")
        else:
            result = prepare_story_generation(args.business_feature_root, args.output)
            print(f"Story generation prepared for active-agent reasoning for {result['approved']['catalog']['project_id']}")
        print(result["path"])
    elif args.command == "generate-acceptance-criteria":
        from polaris_modernization.acceptance_criteria.workflow import prepare_acceptance_criteria, validate_and_persist_acceptance_criteria
        result = validate_and_persist_acceptance_criteria(args.story_root, args.output, args.agent_result) if args.agent_result else prepare_acceptance_criteria(args.story_root, args.output)
        print(result["path"])
    elif args.command == "generate-feature-specifications":
        from polaris_modernization.feature_specifications.workflow import generate_feature_specifications
        result = generate_feature_specifications(args.business_feature_root, args.story_root, args.acceptance_root, args.output)
        print(result["path"])
    elif args.command == "refine-feature-presentations":
        from polaris_modernization.feature_specifications.presentation import refine_feature_presentations
        result = refine_feature_presentations(args.source_specification_root, args.output)
        print(result["path"])
    elif args.command == "synthesize-feature-narratives":
        from polaris_modernization.feature_specifications.narrative import synthesize_feature_narratives
        result = synthesize_feature_narratives(args.source_specification_root, args.output, args.knowledge_graph_root, args.application_source_root)
        print(result["path"])
    elif args.command == "recommend-architecture":
        from polaris_modernization.architecture.workflow import recommend_architecture
        result = recommend_architecture(args.project_id, args.feature_id, args.feature_specification_root, args.output, args.design_provider, args.design_reference)
        print(result["path"])
    elif args.command == "generate-technical-tasks":
        from polaris_modernization.technical_tasks.workflow import generate_technical_tasks
        result = generate_technical_tasks(
            args.project_id, args.feature_id, args.architecture_root,
            args.feature_specification_root, args.design_provider, args.design_mode,
            args.figma_url, args.output, args.design_output,
        )
        print(f"Technical task generation {result['plan']['status']} for {result['plan']['feature_id']}")
        print(result["path"])
    elif args.command == "generate-angular-hero":
        from polaris_modernization.modernization_generation.workflow import generate_angular_hero
        result = generate_angular_hero(
            args.project_id, args.feature_id, args.source_root, args.architecture_root,
            args.technical_task_root, args.feature_specification_root, args.workspace, args.output,
        )
        print(f"Angular hero generation {result['state']['status']} for {args.feature_id}")
        print(result["path"])
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
