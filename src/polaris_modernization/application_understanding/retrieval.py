"""Deterministic, compact retrieval from an already approved canonical graph."""
from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path
import re

from polaris_modernization.application_understanding.models import ConfidenceAssessment, EvidencePackage, EvidenceReference


def load_approved_graph(kg_root: Path) -> dict:
    status = json.loads((kg_root / "graph-run-status.json").read_text(encoding="utf-8"))
    graph = json.loads((kg_root / "knowledge-graph.json").read_text(encoding="utf-8"))
    validation = json.loads((kg_root / "knowledge-graph-validation.json").read_text(encoding="utf-8"))
    readiness = (kg_root / "kg-readiness-analysis.md").read_text(encoding="utf-8")
    readiness_json = json.loads((kg_root / "kg-readiness-analysis.json").read_text(encoding="utf-8")) if (kg_root / "kg-readiness-analysis.json").is_file() else {}
    review = json.loads((kg_root / "review-metadata.json").read_text(encoding="utf-8")) if (kg_root / "review-metadata.json").is_file() else {}
    readiness_state = readiness_json.get("readiness") or readiness_json.get("kg_readiness_status")
    approved = readiness_state in {"READY", "READY_WITH_EXPLAINED_LIMITATIONS"} or "KG_READINESS_STATUS: READY_WITH_EXPLAINED_LIMITATIONS" in readiness
    kg_run_id = readiness_json.get("run_id") or review.get("run_id") or "LEGACY_TEST_RUN"
    if readiness_json.get("run_id") and review.get("run_id") and readiness_json["run_id"] != review["run_id"]:
        raise ValueError("Knowledge Graph readiness and review metadata identify different runs.")
    if not validation.get("valid") or status.get("scope", {}).get("extraction_warning_count") or not approved:
        raise ValueError("Knowledge Graph is not approved for application understanding.")
    api_forensics = json.loads((kg_root / "api-mapping-forensics.json").read_text(encoding="utf-8")) if (kg_root / "api-mapping-forensics.json").is_file() else {}
    return {"graph": graph, "status": status, "validation": validation, "readiness": readiness, "readiness_json": readiness_json, "kg_run_id": kg_run_id, "api_forensics": api_forensics}


def _provenance(evidence: dict) -> str:
    method = evidence.get("extraction_method", "")
    if method == "roslyn":
        return "PROJECT_PARTIAL" if evidence.get("confidence", 0) < 1 else "COMPILER_PROVEN"
    if method == "deterministic-crash-fallback":
        return "SYNTHETIC_FALLBACK"
    return "STRUCTURAL_ONLY"


def _references(nodes: list[dict]) -> list[EvidenceReference]:
    seen: set[tuple[str, str, int]] = set(); result: list[EvidenceReference] = []
    for node in nodes:
        for evidence in node.get("evidence", []):
            key = (node["id"], evidence.get("source_path", ""), evidence.get("line_start", 0))
            if key not in seen:
                seen.add(key); result.append(EvidenceReference(node_id=node["id"], source_path=evidence.get("source_path", ""), line_start=evidence.get("line_start", 0), line_end=evidence.get("line_end", 0), provenance=_provenance(evidence)))
    return sorted(result, key=lambda item: (item.source_path, item.line_start, item.node_id))


def _confidence(refs: list[EvidenceReference]) -> ConfidenceAssessment:
    provenance = sorted(set(reference.provenance for reference in refs))
    if provenance == ["COMPILER_PROVEN"]: level = "HIGH"
    elif "SYNTHETIC_FALLBACK" in provenance or "STRUCTURAL_ONLY" in provenance: level = "LOW"
    else: level = "MEDIUM"
    return ConfidenceAssessment(level=level, provenance=provenance, rationale="Derived solely from package evidence provenance.")


def _category(node: dict) -> str | None:
    return {
        "RazorView": "RAZOR", "PartialView": "RAZOR", "Layout": "RAZOR",
        "AngularController": "ANGULAR", "AngularService": "ANGULAR", "AngularDirective": "ANGULAR", "AngularModule": "ANGULAR",
        "Route": "ROUTE", "ApiCall": "API", "Endpoint": "API",
        "Controller": "BACKEND", "Action": "BACKEND", "DTO": "DOMAIN",
    }.get(node["label"])


def build_evidence_packages(graph: dict) -> list[EvidencePackage]:
    """One stable compact package per source/technical category, never source text."""
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for node in graph["nodes"]:
        category = _category(node)
        paths = {e.get("source_path", "") for e in node.get("evidence", []) if e.get("source_path")}
        if category:
            for path in paths: grouped[(category, path)].append(node)
    packages: list[EvidencePackage] = []
    for (category, path), anchors in sorted(grouped.items()):
        anchor_ids = {node["id"] for node in anchors}
        related = [node for node in graph["nodes"] if any(e.get("source_path") == path for e in node.get("evidence", []))]
        related = sorted(related, key=lambda node: node["id"])[:24]
        neighbor_ids = {
            node_id
            for edge in graph["edges"] if edge["type"] == "IMPLEMENTED_BY" and (edge["source"] in anchor_ids or edge["target"] in anchor_ids)
            for node_id in (edge["source"], edge["target"])
        }
        neighbors = [node for node in graph["nodes"] if node["id"] in neighbor_ids]
        related = sorted({node["id"]: node for node in [*related, *neighbors]}.values(), key=lambda node: node["id"])
        ids = {node["id"] for node in related} | anchor_ids | neighbor_ids
        relationships = [edge for edge in graph["edges"] if edge["source"] in ids and edge["target"] in ids]
        refs = _references(related)
        proven_calls = {edge["source"] for edge in relationships if edge["type"] == "IMPLEMENTED_BY"}
        unresolved = ["BACKEND_MAPPING=UNRESOLVED" for node in related if node["label"] == "ApiCall" and node["id"] not in proven_calls]
        payload = {"category": category, "path": path, "node_ids": sorted(ids), "relationships": [(edge["type"], edge["source"], edge["target"]) for edge in relationships]}
        digest = sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        packages.append(EvidencePackage(package_id=f"{category.lower()}:{path}", package_hash=digest, cluster_type=category, title=path, node_ids=sorted(ids), relationships=relationships, evidence=refs, unresolved_relationships=sorted(set(unresolved)), confidence=_confidence(refs)))
    return packages


def deterministic_modules(graph: dict) -> list[tuple[str, list[dict]]]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for node in graph["nodes"]:
        for evidence in node.get("evidence", []):
            path = evidence.get("source_path", "")
            match = re.search(r"(?:components|Views)/([^/]+)", path)
            if match: groups[match.group(1)].append(node)
    return sorted(groups.items())
