"""Deterministic end-to-end context links for selected modernization flows."""
from __future__ import annotations


def add_context_flow(graph: dict, profile: dict, project_id: str) -> None:
    routes = profile.get("endpoint_routes", [])
    nodes = {node["id"]: node for node in graph["nodes"]}
    actions = {node.get("properties", {}).get("identity"): node for node in nodes.values() if node["label"] == "Action"}
    api_calls = {node["name"]: node for node in nodes.values() if node["label"] == "ApiCall"}
    edge_keys = {(edge["type"], edge["source"], edge["target"]) for edge in graph["edges"]}

    def add_edge(kind: str, source: str, target: str, evidence: dict, properties: dict | None = None) -> None:
        key = (kind, source, target)
        if key not in edge_keys:
            graph["edges"].append({"project_id": project_id, "type": kind, "source": source, "target": target, "properties": properties or {}, "evidence": [evidence]})
            edge_keys.add(key)

    boundary_id = f"{project_id}:ModernizationBoundary:TargetAngular22Ui"
    boundary_evidence = {"project_id": project_id, "source_path": "", "line_start": 0, "line_end": 0, "extraction_method": "profile", "confidence": 1.0, "source_hash": ""}
    nodes[boundary_id] = {"id": boundary_id, "project_id": project_id, "label": "ModernizationBoundary", "name": "Target Angular 22 UI boundary", "properties": {"modernization_role": "transform_ui", "eligible_for_angular_generation": True}, "evidence": [boundary_evidence]}

    resolved_calls = set()
    for route in routes:
        call = api_calls.get(route["path"])
        action = actions.get(route.get("action_identity"))
        if action is None:
            candidates = [node for node in nodes.values() if node["label"] == "Action" and node["name"] == route["action_name"] and any(item.get("source_path") == route["source_path"] and item.get("resolution_status") == "proven" for item in node["evidence"])]
            action = candidates[0] if len(candidates) == 1 else None
        if call is None or action is None:
            graph["warnings"].append({"source_path": route.get("source_path", ""), "message": f"Configured Dashboard endpoint route could not be uniquely proven: {route['path']}."})
            continue
        endpoint_id = f"{project_id}:Endpoint:{route['path']}"
        evidence = next((item for item in action["evidence"] if item.get("source_path") == route["source_path"]), action["evidence"][0])
        nodes[endpoint_id] = {"id": endpoint_id, "project_id": project_id, "label": "Endpoint", "name": route["path"], "properties": {"action_identity": route.get("action_identity", ""), "action_name": route["action_name"], "modernization_role": "preserve_backend", "eligible_for_angular_generation": False}, "evidence": [evidence]}
        add_edge("RESOLVES_TO_ENDPOINT", call["id"], endpoint_id, evidence, {"resolution": "unique_proven"})
        add_edge("EXPOSES", action["id"], endpoint_id, evidence)
        add_edge("PRESERVES_CONTRACT", boundary_id, endpoint_id, evidence, {"transform_boundary": "ui_only"})
        resolved_calls.add(call["id"])
    for call in api_calls.values():
        if call["id"] not in resolved_calls:
            graph["warnings"].append({"source_path": call["evidence"][0].get("source_path", ""), "message": f"Dashboard API call remains unresolved or dynamic: {call['name']}."})

    roles = profile.get("selection_roles", {})
    for node in nodes.values():
        paths = [item.get("source_path", "") for item in node.get("evidence", [])]
        matched = [(prefix, role) for prefix, role in roles.items() if any(path == prefix or path.startswith(prefix.rstrip("/") + "/") for path in paths)]
        role = max(matched, key=lambda item: len(item[0]))[1] if matched else node.get("properties", {}).get("modernization_role", "review_required")
        node.setdefault("properties", {})["modernization_role"] = role
        node["properties"]["eligible_for_angular_generation"] = role == "transform_ui"
    graph["nodes"] = sorted(nodes.values(), key=lambda item: item["id"])
    graph["edges"] = sorted(graph["edges"], key=lambda item: (item["type"], item["source"], item["target"]))
