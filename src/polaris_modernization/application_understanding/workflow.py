"""Interactive Phase-2 preparation and deterministic validation over an approved KG."""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import shutil
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from polaris_modernization.application_understanding.models import (
    AgentReasoningSubmission, ApplicationUnderstanding, BusinessModule, ConfidenceAssessment,
    Dependency, EvidenceBackedItem, EvidenceReference, UISurface, UserWorkflow,
)
from polaris_modernization.application_understanding.retrieval import build_evidence_packages, load_approved_graph
from polaris_modernization.capability_completeness import derive_source_capabilities


class UnsupportedAgentClaimsError(ValueError):
    """The active agent submitted claims that cannot be proven by the prepared KG evidence."""


class PreparationState(TypedDict, total=False):
    kg_root: str
    approved: dict
    packages: list


def _facts(state: PreparationState) -> PreparationState:
    state["approved"] = load_approved_graph(Path(state["kg_root"]))
    return state


def _packages(state: PreparationState) -> PreparationState:
    state["packages"] = build_evidence_packages(state["approved"]["graph"])
    return state


def compiled_preparation_workflow():
    graph = StateGraph(PreparationState)
    graph.add_node("load_approved_kg", _facts)
    graph.add_node("build_evidence_packages", _packages)
    graph.add_edge(START, "load_approved_kg")
    graph.add_edge("load_approved_kg", "build_evidence_packages")
    graph.add_edge("build_evidence_packages", END)
    return graph.compile()


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")


def _timestamped_path(root: Path, project_id: str) -> tuple[str, Path]:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M%S-%f")
    run_id = f"{project_id}-{timestamp}"
    return run_id, root / run_id


def _package_manifest(packages: list) -> tuple[dict[str, str], str]:
    manifest = {item.package_id: item.package_hash for item in packages}
    encoded = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return manifest, sha256(encoded).hexdigest()


def prepare_application_understanding(kg_root: Path, output_root: Path) -> dict:
    """Prepare compact deterministic evidence for the active chat agent; no provider is called."""
    result = compiled_preparation_workflow().invoke({"kg_root": str(kg_root)})
    project_id = result["approved"]["status"]["project_id"]
    run_id, destination = _timestamped_path(output_root / "prepared", project_id)
    destination.mkdir(parents=True, exist_ok=False)
    _write_json(destination / "evidence-packages.json", [item.model_dump(mode="json") for item in result["packages"]])
    package_manifest, manifest_hash = _package_manifest(result["packages"])
    _write_json(destination / "evidence-package-manifest.json", {
        "kg_run_id": result["approved"]["kg_run_id"], "manifest_hash": manifest_hash,
        "packages": package_manifest,
    })
    _write_json(destination / "agent-reasoning-schema.json", AgentReasoningSubmission.model_json_schema())
    instructions = """# Active Agent Reasoning Instructions

Read only `evidence-packages.json` and produce `agent-reasoning.json` matching `agent-reasoning-schema.json`.
Every agent-derived item must set `origin` to `AGENT_REASONING` and reuse exact evidence references from the packages.
Copy the exact KG run ID and evidence-package manifest hash into the submission. Do not scan source or invent source relationships.
A PROVEN backend mapping requires package evidence for an existing IMPLEMENTED_BY relationship. Preserve unresolved, dynamic, and external states.
Use only existing Dashboard candidates when present. The deterministic validator rejects malformed, unsupported, or out-of-package claims.
"""
    (destination / "agent-instructions.md").write_text(instructions, encoding="utf-8")
    _write_json(destination / "preparation.json", {
        "project_id": project_id,
        "kg_run_id": result["approved"]["kg_run_id"],
        "kg_readiness_gate": "PASS",
        "evidence_packages": len(result["packages"]),
        "evidence_package_manifest_hash": manifest_hash,
        "external_llm_calls": 0,
        "next_step": "Active Codex or Copilot agent writes agent-reasoning.json, then invoke understand-application --agent-result.",
    })
    return {"run_id": run_id, "path": destination, **result}


def _refs(items: list[dict]) -> list[EvidenceReference]:
    result: list[EvidenceReference] = []
    for item in items:
        for evidence in item.get("evidence", [])[:1]:
            result.append(EvidenceReference(
                node_id=item["id"], source_path=evidence.get("source_path", ""),
                line_start=evidence.get("line_start", 0), line_end=evidence.get("line_end", 0),
                provenance="STRUCTURAL_ONLY" if evidence.get("extraction_method") != "roslyn" else "PROJECT_PARTIAL",
            ))
    return result


def _confidence(items: list[dict]) -> ConfidenceAssessment:
    references = _refs(items)
    return ConfidenceAssessment(level="MEDIUM", provenance=sorted({reference.provenance for reference in references}), rationale="KG evidence package source provenance.")


def _agent_items(submission: AgentReasoningSubmission) -> list[EvidenceBackedItem]:
    return [submission.application_purpose, *submission.business_modules, *submission.business_capabilities,
            *submission.user_workflows, *submission.business_rules, *submission.domain_concepts,
            *submission.ui_surfaces, *submission.dependencies,
            *[item for item in (submission.razor_demo_capability, submission.razor_demo_workflow,
                                 submission.angular_demo_capability, submission.angular_demo_workflow) if item]]


def _validate_agent_submission(submission: AgentReasoningSubmission, graph: dict, packages: list) -> int:
    _, expected_manifest_hash = _package_manifest(packages)
    if submission.evidence_package_manifest_hash != expected_manifest_hash:
        raise UnsupportedAgentClaimsError("Agent submission package manifest hash does not match the approved KG evidence packages.")
    package_ids = {node_id for package in packages for node_id in package.node_ids}
    packages_by_node: dict[str, set[str]] = {}
    for package in packages:
        for node_id in package.node_ids:
            packages_by_node.setdefault(node_id, set()).add(package.package_id)
    available = {
        (node["id"], evidence.get("source_path", ""), evidence.get("line_start", 0), evidence.get("line_end", 0))
        for node in graph["nodes"] for evidence in node.get("evidence", [])
    }
    rejected = 0
    for item in _agent_items(submission):
        if item.origin != "AGENT_REASONING" or not item.evidence:
            rejected += 1
            raise UnsupportedAgentClaimsError("Agent items require AGENT_REASONING origin and at least one evidence reference.")
        for reference in item.evidence:
            if reference.node_id not in package_ids or (reference.node_id, reference.source_path, reference.line_start, reference.line_end) not in available:
                rejected += 1
                raise UnsupportedAgentClaimsError("Agent claim references nonexistent or unsupported KG evidence.")
        expected_package_ids = sorted({package_id for reference in item.evidence for package_id in packages_by_node[reference.node_id]})
        if item.evidence_package_ids and item.evidence_package_ids != expected_package_ids:
            raise UnsupportedAgentClaimsError("Agent claim contains stale or incomplete evidence package references.")
        item.evidence_package_ids = expected_package_ids
        if isinstance(item, UserWorkflow) and item.backend_mapping == "PROVEN":
            referenced = {reference.node_id for reference in item.evidence}
            if not any(edge["type"] == "IMPLEMENTED_BY" and edge["source"] in referenced and edge["target"] in referenced for edge in graph["edges"]):
                raise UnsupportedAgentClaimsError("PROVEN workflow lacks a referenced IMPLEMENTED_BY relationship.")
    razor = next((node["name"] for node in graph["nodes"] if node["label"] == "RazorView" and "/Dashboard/" in node["name"]), None)
    angular = next((node["name"] for node in graph["nodes"] if node["label"] == "AngularController" and node["name"] == "DashboardController"), None)
    if submission.best_razor_demo_candidate not in {None, razor} or submission.best_angular_demo_candidate not in {None, angular}:
        raise UnsupportedAgentClaimsError("Agent demo candidate is not a deterministic approved candidate.")
    return rejected


def _deterministic_understanding(graph: dict, packages: list) -> tuple[list[UISurface], list[UserWorkflow]]:
    package_ids_by_node: dict[str, list[str]] = {}
    for package in packages:
        for node_id in package.node_ids:
            package_ids_by_node.setdefault(node_id, []).append(package.package_id)
    ui_nodes = [node for node in graph["nodes"] if node["label"] in {"RazorView", "PartialView", "Layout", "AngularController", "AngularService", "AngularDirective", "Route"}]
    surfaces = [UISurface(name=node["name"], kind=node["label"], evidence_package_ids=sorted(package_ids_by_node[node["id"]]), evidence=_refs([node]), confidence=_confidence([node])) for node in ui_nodes]
    workflows = [UserWorkflow(name=f"Route {node['name']}", ui_surface=node["name"], backend_mapping="UNRESOLVED", evidence_package_ids=sorted(package_ids_by_node[node["id"]]), evidence=_refs([node]), confidence=_confidence([node])) for node in graph["nodes"] if node["label"] == "Route"]
    return surfaces, workflows


def _api_summary(approved: dict) -> dict[str, int]:
    values = approved.get("api_forensics", {})
    return {
        "backend_endpoints": int(values.get("backend_endpoint_facts", 0)),
        "frontend_api_calls": int(values.get("frontend_api_call_facts", 0)),
        "proven": int(values.get("proven", 0)),
        "ambiguous": int(values.get("ambiguous", 0)),
        "dynamic": int(values.get("dynamic_url_warnings", 0)),
        "external": int(values.get("external_api", 0)),
        "no_backend_route": int(values.get("no_backend_route", 0)),
        "unresolved": int(values.get("unresolved_structural_calls", 0)),
    }


def validate_and_persist_application_understanding(kg_root: Path, output_root: Path, agent_result: Path) -> dict:
    """Validate a Codex/Copilot submission and publish only an evidence-backed result."""
    prepared = compiled_preparation_workflow().invoke({"kg_root": str(kg_root)})
    graph = prepared["approved"]["graph"]
    submission = AgentReasoningSubmission.model_validate_json(agent_result.read_text(encoding="utf-8"))
    if submission.kg_run_id != prepared["approved"]["kg_run_id"]:
        raise UnsupportedAgentClaimsError("Agent submission references a different KG run.")
    rejected = _validate_agent_submission(submission, graph, prepared["packages"])
    surfaces, workflows = _deterministic_understanding(graph, prepared["packages"])
    project_id = prepared["approved"]["status"]["project_id"]
    razor = next((node["name"] for node in graph["nodes"] if node["label"] == "RazorView" and "/Dashboard/" in node["name"]), None)
    angular = next((node["name"] for node in graph["nodes"] if node["label"] == "AngularController" and node["name"] == "DashboardController"), None)
    api_summary = _api_summary(prepared["approved"])
    source_capabilities = derive_source_capabilities(graph)
    understanding = ApplicationUnderstanding(
        project_id=project_id, kg_run_id=prepared["approved"]["kg_run_id"], status="COMPLETE", application_purpose=submission.application_purpose.name,
        primary_application_type=submission.primary_application_type,
        technical_composition=submission.technical_composition,
        major_user_facing_areas=submission.major_user_facing_areas,
        major_backend_areas=submission.major_backend_areas,
        kg_metrics={"total_kg_nodes": len(graph["nodes"]), "total_kg_relationships": len(graph["edges"])},
        limitations=[f"API evidence retains {api_summary['unresolved']} unresolved structural calls, {api_summary['dynamic']} dynamic URLs, {api_summary['external']} external API, and {api_summary['no_backend_route']} call without a backend route.", "Roslyn and opaque-dependency limitations remain as approved by the KG readiness gate."],
        api_mapping_summary=api_summary, readiness="APPLICATION_UNDERSTANDING_READY_WITH_LIMITATIONS",
        business_modules=submission.business_modules, business_capabilities=submission.business_capabilities,
        user_workflows=workflows + submission.user_workflows, source_capabilities=source_capabilities,
        business_rules=submission.business_rules,
        ui_surfaces=surfaces + submission.ui_surfaces, domain_concepts=submission.domain_concepts,
        dependencies=submission.dependencies, best_razor_demo_candidate=submission.best_razor_demo_candidate or razor,
        razor_demo_capability=submission.razor_demo_capability, razor_demo_workflow=submission.razor_demo_workflow,
        best_angular_demo_candidate=submission.best_angular_demo_candidate or angular,
        angular_demo_capability=submission.angular_demo_capability, angular_demo_workflow=submission.angular_demo_workflow,
        agent_reasoning=submission,
    )
    run_id, destination = _timestamped_path(output_root / "runs", project_id)
    destination.mkdir(parents=True, exist_ok=False)
    _write_json(destination / "application-understanding.json", understanding.model_dump(mode="json"))
    _write_json(destination / "source-capabilities.json", {
        "project_id": project_id, "kg_run_id": prepared["approved"]["kg_run_id"],
        "capabilities": [item.model_dump(mode="json") for item in source_capabilities],
    })
    _write_json(destination / "agent-reasoning.json", submission.model_dump(mode="json"))
    _write_json(destination / "evidence-packages.json", [item.model_dump(mode="json") for item in prepared["packages"]])
    package_manifest, manifest_hash = _package_manifest(prepared["packages"])
    _write_json(destination / "evidence-package-manifest.json", {"kg_run_id": prepared["approved"]["kg_run_id"], "manifest_hash": manifest_hash, "hash_validation": "PASS", "packages": package_manifest})
    _write_json(destination / "agent-reasoning-validation.json", {"valid": True, "unsupported_claims_rejected": rejected, "kg_readiness_gate": "PASS", "kg_run_id": prepared["approved"]["kg_run_id"], "package_hash_validation": "PASS", "provenance_validation": "PASS", "claim_validation": "PASS", "api_mapping_summary": api_summary})
    _write_json(destination / "token-usage.json", {"reasoning_mode": "INTERACTIVE_AGENT_MODE", "active_agent": "EXTERNAL_TO_POLARIS", "external_llm_api_calls": 0, "evidence_packages_created": len(prepared["packages"])})
    def section(title: str, items: list[EvidenceBackedItem]) -> str:
        rows = [f"- **{item.name}**: {item.description or 'Evidence-backed claim.'}" for item in items]
        return f"\n## {title}\n\n" + ("\n".join(rows) if rows else "None supported by the prepared evidence packages.") + "\n"

    markdown = f"""# Application Understanding

- Status: `COMPLETE`
- Readiness: `APPLICATION_UNDERSTANDING_READY_WITH_LIMITATIONS`
- Project: `{project_id}`
- KG run: `{prepared['approved']['kg_run_id']}`
- Reasoning mode: `INTERACTIVE_AGENT_MODE`
- Evidence packages: {len(prepared['packages'])}
- Evidence manifest validation: `PASS`
- Agent claims rejected: {rejected}
- Independently addressable source capabilities: {len(source_capabilities)}

## Application Purpose

{submission.application_purpose.name}: {submission.application_purpose.description}

- Primary application type: {submission.primary_application_type}
- Technical composition: {', '.join(submission.technical_composition)}
- Major user-facing areas: {', '.join(submission.major_user_facing_areas)}
- Major backend areas: {', '.join(submission.major_backend_areas)}
{section('Business Modules', submission.business_modules)}{section('Business Capabilities', submission.business_capabilities)}{section('User Workflows', submission.user_workflows)}{section('Domain Concepts', submission.domain_concepts)}{section('Business Rules', submission.business_rules)}{section('Dependencies', submission.dependencies)}
## API Mapping

- Backend endpoints visible: `{api_summary['backend_endpoints']}`
- Frontend API calls visible: `{api_summary['frontend_api_calls']}`
- Proven API mappings used: `{api_summary['proven']}`
- Unresolved structural calls retained: `{api_summary['unresolved']}`
- Dynamic API relationships retained: `{api_summary['dynamic']}`
- External API relationships retained: `{api_summary['external']}`

## Demonstration Candidates

- Razor: `{understanding.best_razor_demo_candidate}`
- AngularJS: `{understanding.best_angular_demo_candidate}`

## Limitations

""" + "\n".join(f"- {item}" for item in understanding.limitations) + "\n"
    (destination / "application-understanding.md").write_text(markdown, encoding="utf-8")
    latest = output_root / "latest"
    if latest.exists():
        shutil.rmtree(latest)
    shutil.copytree(destination, latest)
    return {"run_id": run_id, "path": destination, "understanding": understanding, "packages": prepared["packages"], "unsupported_claims_rejected": rejected}
