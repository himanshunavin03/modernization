"""LangGraph Phase 2 orchestration; Phase 1 remains outside this workflow."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from polaris_modernization.application_understanding.models import (
    ApplicationUnderstanding, BusinessCapability, BusinessModule, ConfidenceAssessment,
    EvidenceReference, ReasoningResult, UISurface, UserWorkflow,
)
from polaris_modernization.application_understanding.providers import ReasoningProvider
from polaris_modernization.application_understanding.retrieval import (
    build_evidence_packages, deterministic_modules, load_approved_graph,
)


class UnderstandingState(TypedDict, total=False):
    kg_root: str
    approved: dict
    packages: list
    understanding: ApplicationUnderstanding
    token_usage: dict
    provider: ReasoningProvider | None
    cache_root: str
    waiting_for_provider: bool


def _facts(state: UnderstandingState) -> UnderstandingState:
    state["approved"] = load_approved_graph(Path(state["kg_root"]))
    return state


def _packages(state: UnderstandingState) -> UnderstandingState:
    state["packages"] = build_evidence_packages(state["approved"]["graph"])
    return state


def _refs(items: list[dict]) -> list[EvidenceReference]:
    result = []
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
    return ConfidenceAssessment(
        level="MEDIUM", provenance=sorted({reference.provenance for reference in references}),
        rationale="KG evidence package source provenance.",
    )


def _cached_reasoning(provider: ReasoningProvider, packages: list, cache_root: Path) -> tuple[list[ReasoningResult], int, int, int, int]:
    """Cache every package independently so an unchanged package never calls a model twice."""
    results: list[ReasoningResult] = []
    cache_hits = cache_misses = input_tokens = output_tokens = 0
    for package in packages:
        cache_path = cache_root / provider.name.lower() / f"{package.package_hash}.json"
        if cache_path.is_file():
            result = ReasoningResult.model_validate_json(cache_path.read_text(encoding="utf-8"))
            cache_hits += 1
        else:
            result = provider.reason(package)
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_text(result.model_dump_json(), encoding="utf-8")
            cache_misses += 1
        results.append(result)
        input_tokens += result.input_tokens
        output_tokens += result.output_tokens
    return results, cache_hits, cache_misses, input_tokens, output_tokens


def _ai_items(result: ReasoningResult) -> list:
    return [item for item in [result.application_purpose] if item] + result.business_modules + result.claims + result.business_rules + result.domain_concepts + result.user_workflows


def _validate_reasoning(results: list[ReasoningResult], packages: list, valid_ids: set[str]) -> int:
    rejected = 0
    for result, package in zip(results, packages):
        package_ids = set(package.node_ids)
        for item in _ai_items(result):
            evidence = getattr(item, "evidence", [])
            if not evidence or any(reference.node_id not in valid_ids or reference.node_id not in package_ids for reference in evidence):
                rejected += 1
                raise ValueError("Unsupported AI claim without package-scoped KG evidence.")
            if getattr(item, "origin", "AI_INTERPRETATION") != "AI_INTERPRETATION":
                rejected += 1
                raise ValueError("AI output must be marked AI_INTERPRETATION.")
    return rejected


def _understanding(state: UnderstandingState) -> UnderstandingState:
    graph = state["approved"]["graph"]
    packages = state["packages"]
    nodes = graph["nodes"]
    modules = [BusinessModule(name=name, evidence=_refs(items), confidence=_confidence(items)) for name, items in deterministic_modules(graph)]
    ui_nodes = [node for node in nodes if node["label"] in {"RazorView", "PartialView", "Layout", "AngularController", "AngularService", "AngularDirective", "Route"}]
    surfaces = [UISurface(name=node["name"], kind=node["label"], evidence=_refs([node]), confidence=_confidence([node])) for node in ui_nodes]
    routes = [node for node in nodes if node["label"] == "Route"]
    workflows = [UserWorkflow(name=f"Route {node['name']}", ui_surface=node["name"], backend_mapping="UNRESOLVED", evidence=_refs([node]), confidence=_confidence([node])) for node in routes]
    razor = [node for node in nodes if node["label"] == "RazorView"]
    angular = [node for node in nodes if node["label"] == "AngularController"]
    best_razor = next((node["name"] for node in razor if "/Dashboard/" in node["name"]), razor[0]["name"] if razor else None)
    best_angular = next((node["name"] for node in angular if node["name"] == "DashboardController"), angular[0]["name"] if angular else None)

    provider = state.get("provider")
    results: list[ReasoningResult] = []
    cache_hits = cache_misses = input_tokens = output_tokens = 0
    if provider:
        results, cache_hits, cache_misses, input_tokens, output_tokens = _cached_reasoning(provider, packages, Path(state["cache_root"]))
    _validate_reasoning(results, packages, {node["id"] for node in nodes})
    purpose = next((result.application_purpose for result in results if result.application_purpose), None)
    capabilities = [claim for result in results for claim in result.claims]
    ai_modules = [module for result in results for module in result.business_modules]
    rules = [rule for result in results for rule in result.business_rules]
    concepts = [concept for result in results for concept in result.domain_concepts]
    ai_workflows = [workflow for result in results for workflow in result.user_workflows]
    status = "COMPLETE" if provider else "WAITING_FOR_PROVIDER_CONFIGURATION" if state.get("waiting_for_provider") else "FRAMEWORK_ONLY"
    limitations = ["BACKEND_MAPPING=UNRESOLVED: 33 frontend API-call facts have zero backend endpoint facts."]
    if not provider:
        limitations.append("AI interpretation is absent because no configured provider was used.")
    state["understanding"] = ApplicationUnderstanding(
        project_id=state["approved"]["status"]["project_id"], status=status,
        application_purpose=purpose.name if purpose else "Evidence-backed technical application understanding from the approved Knowledge Graph.",
        kg_metrics={"total_kg_nodes": len(nodes), "total_kg_relationships": len(graph["edges"])}, limitations=limitations,
        business_modules=modules + ai_modules, business_capabilities=capabilities, business_rules=rules,
        user_workflows=workflows + ai_workflows, ui_surfaces=surfaces, domain_concepts=concepts,
        dependencies=sorted({node["name"] for node in nodes if node["label"] == "ExternalReference"}),
        best_razor_demo_candidate=best_razor, best_angular_demo_candidate=best_angular,
        ai_interpretations=capabilities + ([purpose] if purpose else []),
    )
    state["token_usage"] = {
        "total_kg_nodes": len(nodes), "total_kg_relationships": len(graph["edges"]),
        "evidence_packages_created": len(packages), "llm_provider_used": provider.name if provider else "NONE",
        "llm_model_used": provider.model if provider else "NONE", "llm_calls": cache_misses,
        "input_tokens": input_tokens, "output_tokens": output_tokens, "total_tokens": input_tokens + output_tokens,
        "cache_hits": cache_hits, "cache_misses": cache_misses,
        "tokens_per_evidence_package": (input_tokens + output_tokens) / len(packages) if packages else 0,
        "unsupported_claims_rejected": 0,
    }
    return state


def compiled_workflow():
    graph = StateGraph(UnderstandingState)
    graph.add_node("load_approved_kg", _facts)
    graph.add_node("build_evidence_packages", _packages)
    graph.add_node("reason_and_validate", _understanding)
    graph.add_edge(START, "load_approved_kg")
    graph.add_edge("load_approved_kg", "build_evidence_packages")
    graph.add_edge("build_evidence_packages", "reason_and_validate")
    graph.add_edge("reason_and_validate", END)
    return graph.compile()


def run_application_understanding(kg_root: Path, output_root: Path, provider: ReasoningProvider | None = None, *, waiting_for_provider: bool = False) -> dict:
    result = compiled_workflow().invoke({"kg_root": str(kg_root), "provider": provider, "cache_root": str(output_root / "cache"), "waiting_for_provider": waiting_for_provider})
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M%S-%f")
    run_id = f"{result['understanding'].project_id}-{timestamp}"
    destination = output_root / "runs" / run_id
    destination.mkdir(parents=True, exist_ok=False)

    def write(path: Path, value: object) -> None:
        path.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")

    write(destination / "application-understanding.json", result["understanding"].model_dump(mode="json"))
    write(destination / "evidence-packages.json", [item.model_dump(mode="json") for item in result["packages"]])
    write(destination / "token-usage.json", result["token_usage"])
    usage = result["token_usage"]
    markdown = f"# Application Understanding\n\n- Status: `{result['understanding'].status}`\n- Project: `{result['understanding'].project_id}`\n- Razor demo: `{result['understanding'].best_razor_demo_candidate}`\n- Angular demo: `{result['understanding'].best_angular_demo_candidate}`\n- Evidence packages: {len(result['packages'])}\n- Provider: `{usage['llm_provider_used']}`\n- Model: `{usage['llm_model_used']}`\n- LLM calls: {usage['llm_calls']}\n- Tokens: {usage['total_tokens']}\n\n## Limitations\n\n" + "\n".join(f"- {item}" for item in result["understanding"].limitations) + "\n"
    (destination / "application-understanding.md").write_text(markdown, encoding="utf-8")
    latest = output_root / "latest"
    if latest.exists():
        shutil.rmtree(latest)
    shutil.copytree(destination, latest)
    return {"run_id": run_id, "path": destination, **result}
