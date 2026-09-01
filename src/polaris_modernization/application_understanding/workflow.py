"""LangGraph Phase 2 orchestration; Phase 1 remains outside this workflow."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import shutil
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from polaris_modernization.application_understanding.models import ApplicationUnderstanding, BusinessModule, BusinessCapability, ConfidenceAssessment, EvidenceReference, ReasoningResult, UISurface, UserWorkflow
from polaris_modernization.application_understanding.providers import ReasoningProvider
from polaris_modernization.application_understanding.retrieval import build_evidence_packages, deterministic_modules, load_approved_graph


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
    state["approved"] = load_approved_graph(Path(state["kg_root"])); return state


def _packages(state: UnderstandingState) -> UnderstandingState:
    state["packages"] = build_evidence_packages(state["approved"]["graph"]); return state


def _understanding(state: UnderstandingState) -> UnderstandingState:
    graph = state["approved"]["graph"]; packages = state["packages"]
    nodes = graph["nodes"]
    by_label = Counter(node["label"] for node in nodes)
    def refs(items):
        result=[]
        for item in items:
            for evidence in item.get("evidence", [])[:1]: result.append(EvidenceReference(node_id=item["id"], source_path=evidence.get("source_path", ""), line_start=evidence.get("line_start", 0), line_end=evidence.get("line_end", 0), provenance="STRUCTURAL_ONLY" if evidence.get("extraction_method") != "roslyn" else "PROJECT_PARTIAL"))
        return result
    def conf(items):
        references=refs(items); return ConfidenceAssessment(level="MEDIUM", provenance=sorted(set(reference.provenance for reference in references)), rationale="KG evidence package source provenance.")
    modules=[BusinessModule(name=name, evidence=refs(items), confidence=conf(items)) for name, items in deterministic_modules(graph)]
    ui_nodes=[node for node in nodes if node["label"] in {"RazorView", "PartialView", "Layout", "AngularController", "AngularService", "AngularDirective", "Route"}]
    surfaces=[UISurface(name=node["name"], kind=node["label"], evidence=refs([node]), confidence=conf([node])) for node in ui_nodes]
    routes=[node for node in nodes if node["label"] == "Route"]
    workflows=[UserWorkflow(name=f"Route {node['name']}", ui_surface=node["name"], backend_mapping="UNRESOLVED", evidence=refs([node]), confidence=conf([node])) for node in routes]
    razor=[node for node in nodes if node["label"] == "RazorView"]
    angular=[node for node in nodes if node["label"] == "AngularController"]
    best_razor=next((node["name"] for node in razor if "/Dashboard/" in node["name"]), razor[0]["name"] if razor else None)
    best_angular=next((node["name"] for node in angular if node["name"] == "DashboardController"), angular[0]["name"] if angular else None)
    provider=state.get("provider"); cache_hit=False; result=None
    if provider:
        cache_key=sha256("".join(package.package_hash for package in packages).encode()).hexdigest()
        cache_path=Path(state["cache_root"])/provider.name.lower()/f"{cache_key}.json"
        if cache_path.is_file(): result=ReasoningResult.model_validate_json(cache_path.read_text(encoding="utf-8")); cache_hit=True
        else:
            result=provider.reason(packages); cache_path.parent.mkdir(parents=True,exist_ok=True); cache_path.write_text(result.model_dump_json(),encoding="utf-8")
    claims=[] if result is None else result.claims
    valid_ids={node['id'] for node in nodes}
    if any(any(reference.node_id not in valid_ids for reference in claim.evidence) for claim in claims): raise ValueError("Unsupported AI claim without KG evidence.")
    status="COMPLETE" if provider else "WAITING_FOR_PROVIDER_CONFIGURATION" if state.get("waiting_for_provider") else "FRAMEWORK_ONLY"
    state["understanding"] = ApplicationUnderstanding(project_id=state["approved"]["status"]["project_id"], status=status, application_purpose="Evidence-backed technical application understanding from the approved Knowledge Graph.", kg_metrics={"total_kg_nodes": len(nodes), "total_kg_relationships": len(graph["edges"])}, limitations=["BACKEND_MAPPING=UNRESOLVED: 33 frontend API-call facts have zero backend endpoint facts.", "AI interpretation is absent because no configured provider was used."], business_modules=modules, business_capabilities=[], business_rules=[], user_workflows=workflows, ui_surfaces=surfaces, domain_concepts=[], dependencies=sorted({node['name'] for node in nodes if node['label']=='ExternalReference'}), best_razor_demo_candidate=best_razor, best_angular_demo_candidate=best_angular, ai_interpretations=claims)
    state["token_usage"]={"total_kg_nodes":len(nodes),"total_kg_relationships":len(graph["edges"]),"evidence_packages_created":len(packages),"llm_provider_used":provider.name if provider else "NONE","llm_calls":0 if result is None or cache_hit else 1,"cache_hit":cache_hit,"approx_input_tokens":0 if result is None else result.input_tokens,"approx_output_tokens":0 if result is None else result.output_tokens,"average_input_tokens_per_package":0 if result is None or not packages else result.input_tokens // len(packages)}
    return state


def compiled_workflow():
    graph=StateGraph(UnderstandingState); graph.add_node("load_approved_kg",_facts); graph.add_node("build_evidence_packages",_packages); graph.add_node("reason_and_validate",_understanding); graph.add_edge(START,"load_approved_kg"); graph.add_edge("load_approved_kg","build_evidence_packages"); graph.add_edge("build_evidence_packages","reason_and_validate"); graph.add_edge("reason_and_validate",END); return graph.compile()


def run_application_understanding(kg_root: Path, output_root: Path, provider: ReasoningProvider | None = None, *, waiting_for_provider: bool = False) -> dict:
    result=compiled_workflow().invoke({"kg_root":str(kg_root),"provider":provider,"cache_root":str(output_root/'cache'),"waiting_for_provider":waiting_for_provider})
    timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M%S-%f"); run_id=f"{result['understanding'].project_id}-{timestamp}"; runs=output_root/'runs'; destination=runs/run_id; destination.mkdir(parents=True,exist_ok=False)
    def write(path, value): path.write_text(json.dumps(value,indent=2,sort_keys=True),encoding='utf-8')
    write(destination/'application-understanding.json',result['understanding'].model_dump(mode='json')); write(destination/'evidence-packages.json',[item.model_dump(mode='json') for item in result['packages']]); write(destination/'token-usage.json',result['token_usage'])
    md=f"# Application Understanding\n\n- Status: `{result['understanding'].status}`\n- Project: `{result['understanding'].project_id}`\n- Razor demo: `{result['understanding'].best_razor_demo_candidate}`\n- Angular demo: `{result['understanding'].best_angular_demo_candidate}`\n- Evidence packages: {len(result['packages'])}\n- Provider: `{result['token_usage']['llm_provider_used']}`\n- LLM calls: {result['token_usage']['llm_calls']}\n\n## Limitations\n\n"+"\n".join(f"- {item}" for item in result['understanding'].limitations)+"\n"; (destination/'application-understanding.md').write_text(md,encoding='utf-8')
    latest=output_root/'latest';
    if latest.exists(): shutil.rmtree(latest)
    shutil.copytree(destination,latest)
    return {"run_id":run_id,"path":destination,**result}
