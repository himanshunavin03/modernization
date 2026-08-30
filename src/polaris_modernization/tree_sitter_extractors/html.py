"""Deterministic HTML and Razor-host extraction through Tree-sitter HTML."""

from __future__ import annotations

from pathlib import Path

import tree_sitter_html

from polaris_modernization.models import Fact
from polaris_modernization.tree_sitter_extractors.common import evidence, node_text, parser_for, walk


HOST_ELEMENTS = {"header-bar", "left-menu"}
CONTROL_ELEMENTS = {"ui-view", "toaster-container"}


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


def extract(path: Path, source_root: Path, digest: str) -> list[Fact]:
    source = path.read_bytes()
    root = parser_for(tree_sitter_html.language()).parse(source).root_node
    facts: list[Fact] = []
    relative_path = path.relative_to(source_root).as_posix()

    if path.suffix == ".cshtml":
        kind = "layout" if path.name.startswith("_Layout") else "partial_view" if path.name.startswith("_") else "razor_view"
        facts.append(Fact(kind, relative_path, evidence(path, source_root, root, digest)))

    for node in walk(root):
        if node.type not in {"element", "self_closing_element", "self_closing_tag"}:
            continue
        tag_name = _tag_name(node, source)
        if not tag_name:
            continue
        node_evidence = evidence(path, source_root, node, digest)
        if tag_name in HOST_ELEMENTS:
            facts.append(Fact("client_component", tag_name, node_evidence))
        if tag_name in CONTROL_ELEMENTS:
            facts.append(Fact("ui_control", tag_name, node_evidence))
        attributes = _attribute_names(node, source)
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
