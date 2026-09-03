"""Deterministic Figma response to implementation-oriented design normalization."""
from __future__ import annotations

from .models import DesignMode, DesignRequirementLink, DesignSpecification, DesignStatus, FigmaReference


def _node_ref(reference: FigmaReference, node_id: str) -> str:
    return f"figma://file/{reference.file_key}?node-id={node_id.replace(':', '%3A')}"


def _color(value: dict) -> str:
    channels = [round(float(value.get(key, 0)) * 255) for key in ("r", "g", "b")]
    return "#" + "".join(f"{max(0, min(255, channel)):02X}" for channel in channels)


def normalize_figma_response(payload: dict, reference: FigmaReference, mode: DesignMode) -> DesignSpecification:
    document = payload.get("document")
    if not isinstance(document, dict):
        raise ValueError("Figma response does not contain a document object.")
    buckets = {name: [] for name in ("pages", "screens", "components", "component_instances", "layouts", "controls", "typography", "colors", "spacing", "assets", "responsive_hints", "interactions", "navigation_hints")}
    traceability: list[str] = []

    def visit(node: dict, parent_id: str | None = None) -> None:
        node_id, kind, name = str(node.get("id", "")), str(node.get("type", "")), str(node.get("name", "Unnamed"))
        if not node_id:
            return
        ref = _node_ref(reference, node_id)
        traceability.append(ref)
        common = {"id": node_id, "name": name, "kind": kind, "parent_id": parent_id, "design_ref": ref}
        if kind == "CANVAS": buckets["pages"].append(common)
        if kind == "FRAME": buckets["screens"].append({**common, "dimensions": node.get("absoluteBoundingBox", {})})
        if kind == "COMPONENT": buckets["components"].append(common)
        if kind == "INSTANCE": buckets["component_instances"].append({**common, "component_id": node.get("componentId")})
        if node.get("layoutMode"):
            buckets["layouts"].append({**common, "direction": node["layoutMode"]})
        if kind in {"COMPONENT", "INSTANCE"} and any(word in name.lower() for word in ("button", "input", "selector", "select")):
            buckets["controls"].append(common)
        if kind == "TEXT" and isinstance(node.get("style"), dict):
            style = node["style"]
            buckets["typography"].append({**common, **{key: style[key] for key in ("fontFamily", "fontWeight", "fontSize", "lineHeightPx") if key in style}})
        for fill in node.get("fills", []) if isinstance(node.get("fills", []), list) else []:
            if fill.get("type") == "SOLID" and isinstance(fill.get("color"), dict):
                buckets["colors"].append({"design_ref": ref, "value": _color(fill["color"])})
            if fill.get("type") == "IMAGE" and fill.get("imageRef"):
                buckets["assets"].append({"design_ref": ref, "image_ref": fill["imageRef"]})
        spacing = {key: node[key] for key in ("itemSpacing", "paddingLeft", "paddingRight", "paddingTop", "paddingBottom") if key in node}
        if spacing:
            buckets["spacing"].append({**common, "values": spacing})
        if node.get("constraints") or node.get("layoutSizingHorizontal") or node.get("layoutSizingVertical"):
            buckets["responsive_hints"].append({**common, "constraints": node.get("constraints", {}), "horizontal": node.get("layoutSizingHorizontal"), "vertical": node.get("layoutSizingVertical")})
        for interaction in node.get("interactions", []) if isinstance(node.get("interactions", []), list) else []:
            action = interaction.get("actions", [])
            item = {"design_ref": ref, "trigger": interaction.get("trigger"), "actions": action}
            buckets["interactions"].append(item)
            for entry in action:
                if entry.get("destinationId"):
                    buckets["navigation_hints"].append({"from": ref, "to": _node_ref(reference, entry["destinationId"]), "action": entry.get("type")})
        for child in node.get("children", []) if isinstance(node.get("children", []), list) else []:
            if isinstance(child, dict):
                visit(child, node_id)

    visit(document)
    links = [DesignRequirementLink.model_validate(item) for item in payload.get("fixtureRequirementLinks", [])]
    tokens = [
        {"name": f"color-{index}", "value": item["value"], "source": item["design_ref"]}
        for index, item in enumerate(buckets["colors"], 1)
    ]
    status = DesignStatus.AVAILABLE if buckets["pages"] and buckets["screens"] else DesignStatus.PARTIAL
    unresolved = [] if status == DesignStatus.AVAILABLE else ["The Figma response contains no normalized page or screen inventory."]
    return DesignSpecification(
        provider="FIGMA", mode=mode, status=status,
        source_reference=reference.normalized_reference, document_name=payload.get("name"),
        design_tokens=tokens, requirement_links=links,
        unresolved_items=unresolved, traceability=list(dict.fromkeys(traceability)), **buckets,
    )
