"""Deterministic C# controller, action, and authorization extraction."""

from __future__ import annotations

from pathlib import Path

import tree_sitter_c_sharp

from polaris_modernization.models import Fact
from polaris_modernization.tree_sitter_extractors.common import evidence, node_text, parser_for, walk


def _first_identifier(node, source: bytes) -> str | None:
    name = node.child_by_field_name("name")
    if name is not None:
        return node_text(name, source)
    for child in walk(node):
        if child.type == "identifier":
            return node_text(child, source)
    return None


def extract(path: Path, source_root: Path, digest: str, project_id: str) -> list[Fact]:
    source = path.read_bytes()
    root = parser_for(tree_sitter_c_sharp.language()).parse(source).root_node
    facts: list[Fact] = []

    for class_node in (node for node in walk(root) if node.type == "class_declaration"):
        class_name = _first_identifier(class_node, source)
        if not class_name:
            continue
        class_evidence = evidence(path, source_root, class_node, digest, project_id)
        facts.append(Fact("controller", class_name, class_evidence))
        attributes = [node_text(node, source) for node in walk(class_node) if node.type == "attribute"]
        for attribute in attributes:
            if attribute == "Authorize":
                facts.append(Fact("authorization_policy", "Authorize", class_evidence, {"controller": class_name}))

        for method_node in (node for node in walk(class_node) if node.type == "method_declaration"):
            method_name = _first_identifier(method_node, source)
            if not method_name:
                continue
            method_evidence = evidence(path, source_root, method_node, digest, project_id)
            facts.append(Fact("action", method_name, method_evidence, {"controller": class_name}))
            for return_node in (node for node in walk(method_node) if node.type == "return_statement"):
                invocation = next((node for node in walk(return_node) if node.type == "invocation_expression"), None)
                if invocation is None or _first_identifier(invocation, source) != "View":
                    continue
                properties = {"controller": class_name}
                literal = next((node for node in walk(invocation) if node.type == "string_literal"), None)
                if literal is not None:
                    properties["view_name"] = node_text(literal, source)[1:-1]
                else:
                    properties["unresolved"] = "implicit View() cannot be matched deterministically"
                facts.append(Fact("returns_view", method_name, evidence(path, source_root, return_node, digest, project_id), properties))
    return facts
