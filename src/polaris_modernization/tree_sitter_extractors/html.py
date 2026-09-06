"""Deterministic HTML and Razor-host extraction through Tree-sitter HTML."""

from __future__ import annotations

from pathlib import Path
import re

import tree_sitter_html

from polaris_modernization.models import Fact
from polaris_modernization.tree_sitter_extractors.common import evidence, node_text, parser_for, walk


HOST_ELEMENTS = {"header-bar", "left-menu"}
CONTROL_ELEMENTS = {"ui-view", "toaster-container"}
ACTION_ATTRIBUTES = {"ng-click", "ng-submit", "onclick"}


def _tag_name(element, source: bytes) -> str | None:
    if element.type == "self_closing_tag":
        name = next((child for child in element.children if child.type == "tag_name"), None)
        return node_text(name, source) if name else None
    start_tag = next(
        (child for child in element.children if child.type in {"start_tag", "self_closing_start_tag"}),
        None,
    )
    if start_tag is None:
        return None
    name = next((child for child in start_tag.children if child.type == "tag_name"), None)
    return node_text(name, source) if name else None


def _attribute_names(element, source: bytes) -> set[str]:
    names: set[str] = set()
    for attribute in walk(element):
        if attribute.type != "attribute":
            continue
        name = next((child for child in attribute.children if child.type == "attribute_name"), None)
        if name:
            names.add(node_text(name, source))
    return names


def _attributes(element, source: bytes) -> dict[str, str]:
    values: dict[str, str] = {}
    attribute_root = element
    if element.type == "element":
        attribute_root = next((child for child in element.children if child.type == "start_tag"), element)
    for attribute in walk(attribute_root):
        if attribute.type != "attribute":
            continue
        name = next((child for child in attribute.children if child.type == "attribute_name"), None)
        value = next((child for child in attribute.children if child.type == "quoted_attribute_value"), None)
        if name is not None:
            values[node_text(name, source).lower()] = node_text(value, source).strip("\"'") if value else ""
    return values


def _handler(expression: str) -> str | None:
    match = re.match(r"\s*(?:\$scope\.)?([A-Za-z_$][\w$]*)\s*\(", expression)
    return match.group(1) if match else None


def extract(path: Path, source_root: Path, digest: str, project_id: str) -> list[Fact]:
    source = path.read_bytes()
    root = parser_for(tree_sitter_html.language()).parse(source).root_node
    facts: list[Fact] = []
    relative_path = path.relative_to(source_root).as_posix()

    if path.suffix == ".cshtml":
        kind = "layout" if path.name.startswith("_Layout") else "partial_view" if path.name.startswith("_") else "razor_view"
        facts.append(Fact(kind, relative_path, evidence(path, source_root, root, digest, project_id)))

    for node in walk(root):
        if node.type not in {"element", "self_closing_element", "self_closing_tag"}:
            continue
        tag_name = _tag_name(node, source)
        if not tag_name:
            continue
        node_evidence = evidence(path, source_root, node, digest, project_id)
        if tag_name in HOST_ELEMENTS:
            facts.append(Fact("client_component", tag_name, node_evidence))
        if tag_name in CONTROL_ELEMENTS:
            facts.append(Fact("ui_control", tag_name, node_evidence))
        attribute_values = _attributes(node, source)
        attributes = set(attribute_values)
        element_text = re.sub(r"<[^>]+>", " ", node_text(node, source))
        element_text = " ".join(element_text.split())
        for event in sorted(ACTION_ATTRIBUTES & attributes):
            expression = attribute_values[event]
            facts.append(Fact("ui_action", f"{relative_path}:{node.start_point.row + 1}:{event}", node_evidence, {
                "element": tag_name,
                "event": event,
                "expression": expression,
                "handler": _handler(expression),
                "text": element_text,
            }))
        for attribute, visibility in (("ng-show", "SHOW"), ("ng-hide", "HIDE"), ("ng-if", "RENDER")):
            if attribute in attributes:
                facts.append(Fact("ui_condition", f"{relative_path}:{node.start_point.row + 1}:{attribute}", node_evidence, {
                    "element": tag_name, "condition": attribute_values[attribute], "visibility": visibility,
                    "text": element_text,
                }))
        if "ng-disabled" in attributes:
            facts.append(Fact("validation_condition", f"{relative_path}:{node.start_point.row + 1}:ng-disabled", node_evidence, {
                "element": tag_name, "condition": attribute_values["ng-disabled"], "text": element_text,
            }))
        if "required" in attributes or attribute_values.get("type", "").lower() == "email":
            facts.append(Fact("ui_validation", f"{relative_path}:{node.start_point.row + 1}", node_evidence, {
                "element": tag_name,
                "required": "required" in attributes,
                "input_type": attribute_values.get("type"),
                "model": attribute_values.get("ng-model"),
            }))
        if tag_name == "input" and attribute_values.get("type", "").lower() == "file":
            facts.append(Fact("ui_action", f"{relative_path}:{node.start_point.row + 1}:upload", node_evidence, {
                "element": tag_name,
                "event": "file-select",
                "expression": attribute_values.get("on-read-file", ""),
                "handler": _handler(attribute_values.get("on-read-file", "")),
                "operation_hint": "UPLOAD",
                "text": element_text,
            }))
        if tag_name == "input" and attribute_values.get("type", "").lower() == "checkbox":
            facts.append(Fact("ui_selection", f"{relative_path}:{node.start_point.row + 1}", node_evidence, {
                "model": attribute_values.get("ng-model"),
                "change": attribute_values.get("ng-change"),
            }))
        if "ui-view" in attributes:
            facts.append(Fact("ui_control", "ui-view", node_evidence))
        if "ng-class" in attributes and "overlay" in node_text(node, source):
            facts.append(Fact("ui_control", "loading-overlay", node_evidence))

        if tag_name == "script":
            for child in walk(node):
                if child.type == "attribute" and "src" in node_text(child, source):
                    facts.append(Fact("script_asset", node_text(child, source), node_evidence))
        if tag_name == "link":
            for child in walk(node):
                if child.type == "attribute" and "href" in node_text(child, source):
                    facts.append(Fact("style_asset", node_text(child, source), node_evidence))
    return facts
