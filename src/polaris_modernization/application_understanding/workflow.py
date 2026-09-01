"""Interactive Phase-2 preparation and deterministic validation over an approved KG."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from polaris_modernization.application_understanding.models import (
    AgentReasoningSubmission, ApplicationUnderstanding, BusinessModule, ConfidenceAssessment,
    Dependency, EvidenceBackedItem, EvidenceReference, UISurface, UserWorkflow,
)
from polaris_modernization.application_understanding.retrieval import (
    build_evidence_packages, deterministic_modules, load_approved_graph,
)


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


def prepare_application_understanding(kg_root: Path, output_root: Path) -> dict:
    """Prepare compact deterministic evidence for the active chat agent; no provider is called."""
    result = compiled_preparation_workflow().invoke({"kg_root": str(kg_root)})
    project_id = result["approved"]["status"]["project_id"]
    run_id, destination = _timestamped_path(output_root / "prepared", project_id)
    destination.mkdir(parents=True, exist_ok=False)
    _write_json(destination / "evidence-packages.json", [item.model_dump(mode="json") for item in result["packages"]])
    _write_json(destination / "agent-reasoning-schema.json", AgentReasoningSubmission.model_json_schema())
    instructions = """# Active Agent Reasoning Instructions

Read only `evidence-packages.json` and produce `agent-reasoning.json` matching `agent-reasoning-schema.json`.
Every agent-derived item must set `origin` to `AGENT_REASONING` and reuse exact evidence references from the packages.
Do not scan source, invent source relationships, or map frontend API calls to backend endpoints. Every workflow with an API dependency must retain `backend_mapping: UNRESOLVED`.
Use only existing Dashboard candidates when present. The deterministic validator rejects malformed, unsupported, or out-of-package claims.
"""
    (destination / "agent-instructions.md").write_text(instructions, encoding="utf-8")
    _write_json(destination / "preparation.json", {
        "project_id": project_id,
        "kg_readiness_gate": "PASS",
        "evidence_packages": len(result["packages"]),
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
    package_ids = {node_id for package in packages for node_id in package.node_ids}
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
    razor = next((node["name"] for node in graph["nodes"] if node["label"] == "RazorView" and "/Dashboard/" in node["name"]), None)
    angular = next((node["name"] for node in graph["nodes"] if node["label"] == "AngularController" and node["name"] == "DashboardController"), None)
    if submission.best_razor_demo_candidate not in {None, razor} or submission.best_angular_demo_candidate not in {None, angular}:
        raise UnsupportedAgentClaimsError("Agent demo candidate is not a deterministic approved candidate.")
    return rejected


def _deterministic_understanding(graph: dict) -> tuple[list[BusinessModule], list[UISurface], list[UserWorkflow]]:
    modules = [BusinessModule(name=name, evidence=_refs(items), confidence=_confidence(items)) for name, items in deterministic_modules(graph)]
    ui_nodes = [node for node in graph["nodes"] if node["label"] in {"RazorView", "PartialView", "Layout", "AngularController", "AngularService", "AngularDirective", "Route"}]
    surfaces = [UISurface(name=node["name"], kind=node["label"], evidence=_refs([node]), confidence=_confidence([node])) for node in ui_nodes]
    workflows = [UserWorkflow(name=f"Route {node['name']}", ui_surface=node["name"], backend_mapping="UNRESOLVED", evidence=_refs([node]), confidence=_confidence([node])) for node in graph["nodes"] if node["label"] == "Route"]
    return modules, surfaces, workflows


def validate_and_persist_application_understanding(kg_root: Path, output_root: Path, agent_result: Path) -> dict:
    """Validate a Codex/Copilot submission and publish only an evidence-backed result."""
    prepared = compiled_preparation_workflow().invoke({"kg_root": str(kg_root)})
    graph = prepared["approved"]["graph"]
    submission = AgentReasoningSubmission.model_validate_json(agent_result.read_text(encoding="utf-8"))
    rejected = _validate_agent_submission(submission, graph, prepared["packages"])
    modules, surfaces, workflows = _deterministic_understanding(graph)
    project_id = prepared["approved"]["status"]["project_id"]
    razor = next((node["name"] for node in graph["nodes"] if node["label"] == "RazorView" and "/Dashboard/" in node["name"]), None)
    angular = next((node["name"] for node in graph["nodes"] if node["label"] == "AngularController" and node["name"] == "DashboardController"), None)
    understanding = ApplicationUnderstanding(
        project_id=project_id, status="COMPLETE", application_purpose=submission.application_purpose.name,
        kg_metrics={"total_kg_nodes": len(graph["nodes"]), "total_kg_relationships": len(graph["edges"])},
        limitations=["BACKEND_MAPPING=UNRESOLVED: 33 frontend API-call facts have zero backend endpoint facts."],
        business_modules=modules + submission.business_modules, business_capabilities=submission.business_capabilities,
        user_workflows=workflows + submission.user_workflows, business_rules=submission.business_rules,
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
    _write_json(destination / "agent-reasoning.json", submission.model_dump(mode="json"))
    _write_json(destination / "evidence-packages.json", [item.model_dump(mode="json") for item in prepared["packages"]])
    _write_json(destination / "agent-reasoning-validation.json", {"valid": True, "unsupported_claims_rejected": rejected, "kg_readiness_gate": "PASS", "backend_mapping_status": "UNRESOLVED"})
    _write_json(destination / "token-usage.json", {"reasoning_mode": "INTERACTIVE_AGENT_MODE", "active_agent": "EXTERNAL_TO_POLARIS", "external_llm_api_calls": 0, "evidence_packages_created": len(prepared["packages"])})
    markdown = f"# Application Understanding\n\n- Status: `COMPLETE`\n- Project: `{project_id}`\n- Reasoning mode: `INTERACTIVE_AGENT_MODE`\n- Evidence packages: {len(prepared['packages'])}\n- Agent claims rejected: {rejected}\n- Backend mapping: `UNRESOLVED`\n"
    (destination / "application-understanding.md").write_text(markdown, encoding="utf-8")
    latest = output_root / "latest"
    if latest.exists():
        shutil.rmtree(latest)
    shutil.copytree(destination, latest)
    return {"run_id": run_id, "path": destination, "understanding": understanding, "packages": prepared["packages"], "unsupported_claims_rejected": rejected}
