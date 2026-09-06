"""Deterministic source-capability identity and downstream coverage validation."""

from __future__ import annotations

from collections import defaultdict, deque
from hashlib import sha256
import json
import re
from typing import Literal

from pydantic import BaseModel, Field


OperationKind = Literal["LIST", "READ", "CREATE", "UPDATE", "DELETE", "NAVIGATE", "UPLOAD", "VALIDATE", "PAGE", "OTHER"]
ScopeStatus = Literal["INCLUDED", "EXCLUDED", "DEFERRED", "UNRESOLVED"]


class CapabilityEvidence(BaseModel):
    node_id: str
    source_path: str
    line_start: int = 0
    line_end: int = 0
    stage: Literal["UI", "FRONTEND", "API", "BACKEND", "PERSISTENCE"]


class InteractionSemantics(BaseModel):
    """Concrete UI semantics retained alongside a broad capability category."""

    interaction_type: Literal["ACTION", "SELECTION", "VALIDATION", "SYSTEM"]
    label: str | None = None
    trigger: str | None = None
    observable_result: str | None = None
    state_change: str | None = None
    system_initiated: bool = False
    handler_id: str | None = None
    source_evidence: list[CapabilityEvidence] = Field(default_factory=list)


def _handler_semantics(handler: dict, forward: dict[str, list[tuple[str, str]]], nodes: dict[str, dict]) -> list[InteractionSemantics]:
    """Translate handler-linked structural effects without using API or label heuristics."""
    values: list[InteractionSemantics] = []
    for edge_type, target in forward.get(handler["id"], []):
        node = nodes[target]
        props = node.get("properties", {})
        if edge_type == "MUTATES_COLLECTION":
            operation = str(props.get("operation") or "")
            collection = str(props.get("collection") or "collection")
            results = {
                "push": f"additional items are appended to {collection}",
                "unshift": f"additional items are prepended to {collection}",
                "pop": f"the final item is removed from {collection}",
                "shift": f"the first item is removed from {collection}",
                "splice": f"{collection} is modified by the splice operation",
            }
            result = results.get(operation)
            if result:
                values.append(InteractionSemantics(interaction_type="ACTION", observable_result=result, handler_id=handler["id"], source_evidence=_evidence(node, "FRONTEND")))
        elif edge_type == "NAVIGATES":
            values.append(InteractionSemantics(interaction_type="ACTION", observable_result=f"the view changes to {props.get('target')}", handler_id=handler["id"], source_evidence=_evidence(node, "FRONTEND")))
        elif edge_type == "REQUIRES_CONFIRMATION":
            values.append(InteractionSemantics(interaction_type="ACTION", observable_result="confirmation is requested before the guarded operation", handler_id=handler["id"], source_evidence=_evidence(node, "FRONTEND")))
        elif edge_type == "MUTATES":
            values.append(InteractionSemantics(interaction_type="ACTION", state_change=str(props.get("target") or ""), handler_id=handler["id"], source_evidence=_evidence(node, "FRONTEND")))
    return values


class SourceCapability(BaseModel):
    capability_id: str
    domain_context: str
    operation_kind: OperationKind
    operation_identity: str
    qualifiers: list[str] = Field(default_factory=list)
    source_evidence: list[CapabilityEvidence]
    interaction_semantics: list[InteractionSemantics] = Field(default_factory=list)
    facts_status: Literal["PRESENT", "PARTIAL"] = "PRESENT"
    kg_status: Literal["PRESENT", "PARTIAL"] = "PRESENT"
    confidence: Literal["PROVEN", "PARTIAL"]
    provenance: Literal["DETERMINISTIC_FACT"] = "DETERMINISTIC_FACT"


class CapabilityDisposition(BaseModel):
    capability_id: str
    scope_status: ScopeStatus
    feature_id: str | None = None
    reason: str | None = None
    evidence_refs: list[str] = Field(default_factory=list)
    downstream_refs: list[str] = Field(default_factory=list)


def api_operation_identity(method: str, route: str) -> str:
    """Return an API identity in which HTTP method is never optional."""
    normalized = "/" + route.strip().split("?", 1)[0].strip("/")
    return f"{method.upper()} {normalized}"


def _domain(path: str, identity: str) -> str:
    parts = path.replace("\\", "/").split("/")
    if "components" in parts and parts.index("components") + 1 < len(parts):
        return parts[parts.index("components") + 1].casefold()
    match = re.search(r"/api/([^/{]+)", identity, re.I)
    if match:
        return match.group(1).casefold()
    owner = re.search(r"([A-Za-z][A-Za-z0-9]*?)(?:Repository|Controller|Service)\b", identity)
    return owner.group(1).casefold() if owner else "shared"


def _operation(method: str, function_name: str, query: list[str]) -> OperationKind:
    tokens = set(re.findall(r"[a-z]+", re.sub(r"(?<=[a-z])(?=[A-Z])", " ", function_name).lower()))
    if method == "DELETE" and tokens & {"delete", "remove", "destroy"}:
        return "DELETE"
    if method == "POST" and tokens & {"add", "create", "new", "register", "insert"}:
        return "CREATE"
    if method in {"PUT", "PATCH"} and tokens & {"edit", "update", "save", "replace", "patch"}:
        return "UPDATE"
    if method == "GET" and (tokens & {"list", "all", "search", "query"} or query):
        return "LIST"
    if method == "GET" and tokens & {"get", "read", "load", "find", "detail"}:
        return "READ"
    return "OTHER"


def _evidence(node: dict, stage: str) -> list[CapabilityEvidence]:
    return [CapabilityEvidence(
        node_id=node["id"], source_path=item.get("source_path", ""),
        line_start=item.get("line_start", 0), line_end=item.get("line_end", 0), stage=stage,
    ) for item in node.get("evidence", [])]


def _interaction(node: dict, handler_id: str | None = None) -> InteractionSemantics | None:
    """Retain UI-node semantics without deriving UX from an API operation."""
    props = node.get("properties", {})
    label = str(props.get("text") or "").strip() or None
    if node["label"] == "UIAction":
        return InteractionSemantics(
            interaction_type="ACTION", label=label, trigger=props.get("expression") or props.get("handler"),
            handler_id=handler_id, source_evidence=_evidence(node, "UI"),
        )
    if node["label"] == "UISelection":
        return InteractionSemantics(
            interaction_type="SELECTION", trigger=props.get("change"),
            state_change=f"selection model {props.get('model')}" if props.get("model") else None,
            handler_id=handler_id, source_evidence=_evidence(node, "UI"),
        )
    if node["label"] == "UIValidation":
        required = props.get("required")
        return InteractionSemantics(
            interaction_type="VALIDATION", trigger=props.get("model"),
            observable_result="required input" if required is True else None,
            handler_id=handler_id, source_evidence=_evidence(node, "UI"),
        )
    return None


def _reachable(start: str, adjacency: dict[str, list[tuple[str, str]]], wanted: str, nodes: dict[str, dict]) -> list[dict]:
    queue = deque([start]); visited = {start}; found = []
    while queue:
        current = queue.popleft()
        for edge_type, target in adjacency.get(current, []):
            if target in visited:
                continue
            visited.add(target)
            node = nodes[target]
            if node["label"] == wanted:
                found.append(node)
            if edge_type in {"TRIGGERS", "INVOKES", "CALLS_API", "IMPLEMENTED_BY", "HANDLED_BY", "PERFORMS"}:
                queue.append(target)
    return found


def derive_source_capabilities(graph: dict) -> list[SourceCapability]:
    """Derive independently addressable capabilities from evidence-bearing graph chains."""
    nodes = {item["id"]: item for item in graph.get("nodes", [])}
    forward: dict[str, list[tuple[str, str]]] = defaultdict(list)
    reverse: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for edge in graph.get("edges", []):
        forward[edge["source"]].append((edge["type"], edge["target"]))
        reverse[edge["target"]].append((edge["type"], edge["source"]))

    results: dict[str, SourceCapability] = {}
    for call in (node for node in nodes.values() if node["label"] == "ApiCall"):
        props = call.get("properties", {})
        method = str(props.get("http_method") or call["name"].split(" ", 1)[0]).upper()
        route = str(props.get("normalized_route_template") or props.get("normalized_route") or call["name"].split(" ", 1)[-1])
        identity = api_operation_identity(method, route)
        endpoints = [nodes[target] for edge, target in forward.get(call["id"], []) if edge == "IMPLEMENTED_BY"]
        persistence = [item for endpoint in endpoints for item in _reachable(endpoint["id"], forward, "PersistenceOperation", nodes)]
        callers = [nodes[source] for edge, source in reverse.get(call["id"], []) if edge == "CALLS_API" and nodes[source]["label"] == "FrontendFunction"]
        caller_groups: dict[str, list[dict]] = defaultdict(list)
        for caller in callers:
            path = caller.get("evidence", [{}])[0].get("source_path", "")
            caller_groups[_domain(path, identity)].append(caller)
        if not caller_groups:
            source_path = next((item.get("source_path", "") for item in call.get("evidence", [])), "")
            caller_groups[_domain(source_path, identity)] = []
        for domain, domain_callers in caller_groups.items():
            function_name = str(domain_callers[0].get("properties", {}).get("function_name") if domain_callers else props.get("function_name", ""))
            kind = _operation(method, function_name, list(props.get("query_components", [])))
            if kind == "OTHER":
                continue
            ui_actions = []
            for caller in domain_callers:
                handlers = [nodes[source] for edge, source in reverse.get(caller["id"], []) if edge == "INVOKES"]
                for handler in handlers:
                    ui_actions.extend(nodes[source] for edge, source in reverse.get(handler["id"], []) if edge == "TRIGGERS")
            api_evidence = [item for item in _evidence(call, "API") if _domain(item.source_path, identity) == domain] or _evidence(call, "API")
            evidence = [item for node, stage in [*( (x, "UI") for x in ui_actions), *( (x, "FRONTEND") for x in domain_callers), *( (x, "BACKEND") for x in endpoints), *( (x, "PERSISTENCE") for x in persistence)] for item in _evidence(node, stage)]
            evidence.extend(api_evidence)
            interactions = []
            for handler in handlers:
                actions = [nodes[source] for edge, source in reverse.get(handler["id"], []) if edge == "TRIGGERS"]
                interactions.extend(item for node in actions if (item := _interaction(node, handler["id"])))
            for handler in handlers:
                interactions.extend(_handler_semantics(handler, forward, nodes))
            qualifiers = []
            if any(str(value).casefold() == "tenantid" for value in props.get("request_header_components", [])):
                qualifiers.append("TENANT_SCOPED")
            if any(item.get("properties", {}).get("operation") in {"OrderBy", "OrderByDescending"} for item in persistence):
                qualifiers.append("FIXED_ORDER")
            selection_paths = {item.get("source_path", "") for node in nodes.values() if node["label"] == "UISelection" for item in node.get("evidence", [])}
            if kind == "DELETE" and any(item.source_path in selection_paths for item in evidence if item.stage == "UI"):
                qualifiers.append("BULK")
            digest = sha256(f"{domain}|{kind}|{identity}".encode()).hexdigest()[:12]
            capability_id = f"capability-{domain}-{kind.lower()}-{digest}"
            results[capability_id] = SourceCapability(
                capability_id=capability_id, domain_context=domain, operation_kind=kind,
                operation_identity=identity, qualifiers=qualifiers, source_evidence=evidence,
                interaction_semantics=interactions,
                facts_status="PRESENT", kg_status="PRESENT" if endpoints else "PARTIAL",
                confidence="PROVEN" if endpoints else "PARTIAL",
            )

    linked_endpoints = {target for edge in graph.get("edges", []) if edge["type"] == "IMPLEMENTED_BY" for target in [edge["target"]]}
    for endpoint in (node for node in nodes.values() if node["label"] == "Endpoint" and node["id"] not in linked_endpoints):
        props = endpoint.get("properties", {})
        method = str(props.get("http_method") or endpoint["name"].split(" ", 1)[0]).upper()
        route = str(props.get("normalized_route") or endpoint["name"].split(" ", 1)[-1])
        action = str(props.get("action", ""))
        kind = _operation(method, action, list(props.get("parameters", [])) if method == "GET" and "page" in " ".join(props.get("parameters", [])).lower() else [])
        identity = api_operation_identity(method, route)
        source_path = endpoint.get("evidence", [{}])[0].get("source_path", "")
        domain = _domain(source_path, identity)
        persistence = _reachable(endpoint["id"], forward, "PersistenceOperation", nodes)
        qualifiers = ["FIXED_ORDER"] if any(item.get("properties", {}).get("operation") in {"OrderBy", "OrderByDescending"} for item in persistence) else []
        digest = sha256(f"{domain}|{kind}|{identity}".encode()).hexdigest()[:12]
        capability_id = f"capability-{domain}-{kind.lower()}-{digest}"
        results.setdefault(capability_id, SourceCapability(
            capability_id=capability_id, domain_context=domain, operation_kind=kind,
            operation_identity=identity, qualifiers=qualifiers,
            source_evidence=[*_evidence(endpoint, "BACKEND"), *(item for node in persistence for item in _evidence(node, "PERSISTENCE"))],
            facts_status="PRESENT", kg_status="PARTIAL", confidence="PARTIAL",
        ))

    for node in nodes.values():
        if node["label"] not in {"UIAction", "UISelection", "UIValidation"}:
            continue
        props = node.get("properties", {})
        if node["label"] == "UIValidation":
            kind: OperationKind = "VALIDATE"
        elif node["label"] == "UISelection":
            kind = "OTHER"
        elif props.get("operation_hint") == "UPLOAD":
            kind = "UPLOAD"
        else:
            text = f"{props.get('handler', '')} {props.get('text', '')}".lower()
            kind = "NAVIGATE" if re.search(r"navig|nagiv|\bback\b", text) else "OTHER"
        source_path = node.get("evidence", [{}])[0].get("source_path", "")
        domain = _domain(source_path, node["name"])
        identity = f"{kind} {node['name']}"
        digest = sha256(f"{domain}|{identity}".encode()).hexdigest()[:12]
        capability_id = f"capability-{domain}-{kind.lower()}-{digest}"
        results[capability_id] = SourceCapability(
            capability_id=capability_id, domain_context=domain, operation_kind=kind,
            operation_identity=identity, source_evidence=_evidence(node, "UI"),
            interaction_semantics=[_interaction(node)] if _interaction(node) else [],
            confidence="PROVEN",
        )
    reachable_persistence = {item["id"] for endpoint in nodes.values() if endpoint["label"] == "Endpoint" for item in _reachable(endpoint["id"], forward, "PersistenceOperation", nodes)}
    for node in (item for item in nodes.values() if item["label"] == "PersistenceOperation" and item["id"] not in reachable_persistence):
        props = node.get("properties", {})
        if props.get("operation") not in {"OrderBy", "OrderByDescending"}:
            continue
        source_path = node.get("evidence", [{}])[0].get("source_path", "")
        domain = _domain(source_path, str(props.get("repository", "")))
        identity = f"ORDER {props.get('expression', node['name'])}"
        digest = sha256(f"{domain}|{identity}".encode()).hexdigest()[:12]
        capability_id = f"capability-{domain}-other-{digest}"
        results[capability_id] = SourceCapability(
            capability_id=capability_id, domain_context=domain, operation_kind="OTHER",
            operation_identity=identity, qualifiers=["FIXED_ORDER"], source_evidence=_evidence(node, "PERSISTENCE"),
            facts_status="PRESENT", kg_status="PARTIAL", confidence="PROVEN",
        )
    return sorted(results.values(), key=lambda item: item.capability_id)


def validate_capability_coverage(capabilities: list[SourceCapability | dict], dispositions: list[CapabilityDisposition | dict]) -> dict:
    capabilities = [item if isinstance(item, SourceCapability) else SourceCapability.model_validate(item) for item in capabilities]
    dispositions = [item if isinstance(item, CapabilityDisposition) else CapabilityDisposition.model_validate(item) for item in dispositions]
    expected = {item.capability_id for item in capabilities}
    grouped: dict[str, list[CapabilityDisposition]] = defaultdict(list)
    for item in dispositions:
        grouped[item.capability_id].append(item)
    missing = sorted(expected - set(grouped))
    duplicates = sorted(key for key, values in grouped.items() if len(values) != 1)
    invalid = sorted(item.capability_id for item in dispositions if item.capability_id in expected and (
        (item.scope_status == "INCLUDED" and (not item.feature_id or not item.downstream_refs))
        or (item.scope_status != "INCLUDED" and (not item.reason or not item.evidence_refs))
    ))
    unknown = sorted(set(grouped) - {item.capability_id for item in capabilities})
    excluded = sorted(item.capability_id for item in dispositions if item.scope_status != "INCLUDED")
    if missing or duplicates or invalid or unknown:
        status = "FAIL"
    elif excluded:
        status = "PASS_WITH_EXCLUSION"
    else:
        status = "PASS"
    return {
        "status": status, "source_capability_count": len(expected), "covered_capability_count": len(expected) - len(missing),
        "silently_dropped_capabilities": missing, "duplicate_dispositions": duplicates,
        "invalid_dispositions": invalid, "unknown_capabilities": unknown, "explicit_non_inclusions": excluded,
        "capabilities": [item.model_dump(mode="json") for item in capabilities],
        "dispositions": [item.model_dump(mode="json") for item in dispositions],
    }


def coverage_hash(value: dict) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def assess_graph_readiness(validation: dict, run_status: dict, run_id: str) -> dict:
    blockers = []
    if not validation.get("valid"):
        blockers.append("KNOWLEDGE_GRAPH_VALIDATION_FAILED")
    if run_status.get("scope", {}).get("extraction_warning_count"):
        blockers.append("DETERMINISTIC_EXTRACTION_WARNINGS")
    limitations = []
    if run_status.get("scope", {}).get("opaque_dependency_count"):
        limitations.append("Opaque dependencies remain visible and are not treated as proven relationships.")
    readiness = "NOT_READY" if blockers else "READY_WITH_EXPLAINED_LIMITATIONS" if limitations else "READY"
    return {"run_id": run_id, "readiness": readiness, "blockers": blockers, "limitations": limitations}


def assign_feature_dispositions(capabilities: list[SourceCapability | dict], features: list[dict]) -> list[CapabilityDisposition]:
    """Assign only evidence-backed UI capabilities; retain uncertain ownership explicitly."""
    capabilities = [item if isinstance(item, SourceCapability) else SourceCapability.model_validate(item) for item in capabilities]
    feature_tokens = {
        feature["feature_id"]: set(re.findall(r"[a-z0-9]+", f"{feature.get('title', '')} {feature.get('module', '')}".lower()))
        for feature in features
    }
    dispositions: list[CapabilityDisposition] = []
    for capability in capabilities:
        domain_tokens = {capability.domain_context, capability.domain_context.removesuffix("s")}
        owners = [feature for feature in features if domain_tokens & feature_tokens[feature["feature_id"]]]
        evidence_refs = [item.node_id for item in capability.source_evidence]
        stages = {item.stage for item in capability.source_evidence}
        workflow_proven = "UI" in stages or {"FRONTEND", "API", "BACKEND"} <= stages
        if len(owners) == 1 and workflow_proven:
            feature_id = owners[0]["feature_id"]
            dispositions.append(CapabilityDisposition(
                capability_id=capability.capability_id, scope_status="INCLUDED", feature_id=feature_id,
                evidence_refs=evidence_refs, downstream_refs=[f"feature:{feature_id}"],
            ))
        else:
            reason = "No UI-to-workflow evidence establishes a single owning Feature."
            if len(owners) > 1:
                reason = "Evidence overlaps multiple Features; ownership requires an explicit scope decision."
            dispositions.append(CapabilityDisposition(
                capability_id=capability.capability_id, scope_status="UNRESOLVED", reason=reason,
                evidence_refs=evidence_refs,
            ))
    return dispositions
