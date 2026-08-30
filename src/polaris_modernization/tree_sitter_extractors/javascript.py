"""Deterministic JavaScript AngularJS extraction through Tree-sitter AST nodes."""

from __future__ import annotations

from pathlib import Path

import tree_sitter_javascript

from polaris_modernization.models import Fact
from polaris_modernization.tree_sitter_extractors.common import evidence, node_text, parser_for, unquote, walk


def _call_property(node, source: bytes) -> str | None:
    function = node.child_by_field_name("function")
    if function is None or function.type != "member_expression":
        return None
    property_node = function.child_by_field_name("property")
    return node_text(property_node, source) if property_node else None


def _call_object(node, source: bytes, member: str) -> str | None:
    function = node.child_by_field_name("function")
    if function is None:
        return None
    text = node_text(function, source)
    return text if text == member else None


def _arguments(node):
    arguments = node.child_by_field_name("arguments")
    return list(arguments.named_children) if arguments else []


def _object_values(node, source: bytes) -> dict[str, object]:
    values: dict[str, object] = {}
    for pair in (item for item in walk(node) if item.type == "pair"):
        key = pair.child_by_field_name("key")
        value = pair.child_by_field_name("value")
        if key is not None and value is not None:
            values[node_text(key, source)] = value
    return values


def _literal_or_expression(node, source: bytes) -> str:
    return unquote(node_text(node, source))


def extract(path: Path, source_root: Path, digest: str) -> list[Fact]:
    source = path.read_bytes()
    root = parser_for(tree_sitter_javascript.language()).parse(source).root_node
    facts: list[Fact] = []
    variables: dict[str, str] = {}

    for node in walk(root):
        if node.type == "variable_declarator":
            name = node.child_by_field_name("name")
            value = node.child_by_field_name("value")
            if name is not None and value is not None:
                variables[node_text(name, source)] = _literal_or_expression(value, source)

        if node.type == "import_statement":
            source_node = node.child_by_field_name("source")
            if source_node:
                facts.append(Fact("import", unquote(node_text(source_node, source)), evidence(path, source_root, node, digest)))

        if node.type == "class_declaration":
            name = node.child_by_field_name("name")
            if name:
                class_name = node_text(name, source)
                kind = "angular_service" if "service" in path.name.lower() else "angular_controller" if "controller" in path.name.lower() else "angular_directive"
                facts.append(Fact(kind, class_name, evidence(path, source_root, node, digest)))

        if node.type != "call_expression":
            continue
        node_evidence = evidence(path, source_root, node, digest)
        property_name = _call_property(node, source)
        arguments = _arguments(node)
        if _call_object(node, source, "angular.module") and arguments:
            facts.append(Fact("angular_module", _literal_or_expression(arguments[0], source), node_evidence))
        if property_name in {"directive", "controller", "service"} and arguments:
            fact_kind = {
                "directive": "angular_directive",
                "controller": "angular_controller",
                "service": "angular_service",
            }[property_name]
            facts.append(Fact(fact_kind, _literal_or_expression(arguments[0], source), node_evidence))
            if property_name == "directive" and "chart" in _literal_or_expression(arguments[0], source).lower():
                facts.append(Fact("chart", _literal_or_expression(arguments[0], source), node_evidence))
        if property_name == "state" and len(arguments) >= 2:
            state_name = _literal_or_expression(arguments[0], source)
            values = _object_values(arguments[1], source)
            properties = {"url": _literal_or_expression(values["url"], source)} if "url" in values else {}
            if "templateUrl" in values:
                properties["template"] = _literal_or_expression(values["templateUrl"], source)
            if "controller" in values:
                properties["controller"] = _literal_or_expression(values["controller"], source)
            facts.append(Fact("route", state_name, node_evidence, properties))
        if _call_object(node, source, "$http") and arguments:
            values = _object_values(arguments[0], source)
            if "url" in values:
                value = _literal_or_expression(values["url"], source)
                facts.append(Fact("api_call", variables.get(value, value), node_evidence))
    return facts
