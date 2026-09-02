"""Deterministic JavaScript AngularJS extraction through Tree-sitter AST nodes."""

from __future__ import annotations

from pathlib import Path
import re

import tree_sitter_javascript

from polaris_modernization.models import Fact
from polaris_modernization.tree_sitter_extractors.common import evidence, node_text, parser_for, unquote, walk


HTTP_VERBS = {"get", "post", "put", "patch", "delete"}


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


def _variable_record(node, source: bytes) -> dict[str, str]:
    raw = _literal_or_expression(node, source)
    return {
        "raw_expression": raw,
        "resolved_expression": raw,
        "expression_type": node.type,
    }


def _resolve_expression(node, source: bytes, variables: dict[str, dict[str, str]]) -> dict[str, str]:
    raw = _literal_or_expression(node, source)
    if node.type == "identifier":
        resolved = variables.get(raw, {"resolved_expression": raw})
        return {
            "raw_expression": raw,
            "resolved_expression": str(resolved.get("resolved_expression", raw)),
            "expression_type": node.type,
        }
    return {
        "raw_expression": raw,
        "resolved_expression": raw,
        "expression_type": node.type,
    }


def _object_keys(node, source: bytes) -> list[str]:
    keys: list[str] = []
    for pair in (item for item in node.named_children if item.type == "pair"):
        key = pair.child_by_field_name("key")
        if key is not None:
            keys.append(unquote(node_text(key, source)))
    return keys


def _enclosing_named_function(node, source: bytes) -> str | None:
    current = node.parent
    while current is not None:
        if current.type == "function_declaration":
            name = current.child_by_field_name("name")
            if name is not None:
                return node_text(name, source)
        if current.type == "variable_declarator":
            name = current.child_by_field_name("name")
            value = current.child_by_field_name("value")
            if name is not None and value is not None and value.type in {"function_expression", "arrow_function"}:
                return node_text(name, source)
        current = current.parent
    return None


def _file_owner_name(root, source: bytes, suffix: str) -> str | None:
    if suffix not in {"service", "controller"}:
        return None
    pattern = re.compile(rf"{suffix}$", re.I)
    for node in walk(root):
        if node.type != "function_declaration":
            continue
        name = node.child_by_field_name("name")
        if name is None:
            continue
        value = node_text(name, source)
        if pattern.search(value):
            return value
    return None


def _api_call_fact(
    path: Path,
    source_root: Path,
    source: bytes,
    digest: str,
    project_id: str,
    node,
    method: str | None,
    url_node,
    variables: dict[str, dict[str, str]],
    file_service: str | None,
    file_controller: str | None,
    query_components: list[str] | None = None,
) -> Fact:
    node_evidence = evidence(path, source_root, node, digest, project_id)
    url_value = _resolve_expression(url_node, source, variables)
    query_components = query_components or []
    function_name = _enclosing_named_function(node, source)
    return Fact(
        "api_call",
        url_value["resolved_expression"],
        node_evidence,
        {
            "http_method": method,
            "raw_url_expression": url_value["resolved_expression"],
            "url_source_kind": "identifier" if url_value["expression_type"] == "identifier" else "inline_expression",
            "url_source_name": url_value["raw_expression"] if url_value["expression_type"] == "identifier" else None,
            "framework": "AngularJS",
            "service": file_service,
            "controller_or_component": file_controller,
            "function_name": function_name,
            "query_components": query_components,
        },
    )


def extract(path: Path, source_root: Path, digest: str, project_id: str) -> list[Fact]:
    source = path.read_bytes()
    root = parser_for(tree_sitter_javascript.language()).parse(source).root_node
    facts: list[Fact] = []
    variables: dict[str, dict[str, str]] = {}
    file_service = _file_owner_name(root, source, "service")
    file_controller = _file_owner_name(root, source, "controller")

    for node in walk(root):
        if node.type == "variable_declarator":
            name = node.child_by_field_name("name")
            value = node.child_by_field_name("value")
            if name is not None and value is not None:
                variables[node_text(name, source)] = _variable_record(value, source)

        if node.type == "import_statement":
            source_node = node.child_by_field_name("source")
            if source_node:
                facts.append(Fact("import", unquote(node_text(source_node, source)), evidence(path, source_root, node, digest, project_id)))

        if node.type == "class_declaration":
            name = node.child_by_field_name("name")
            if name:
                class_name = node_text(name, source)
                kind = "angular_service" if "service" in path.name.lower() else "angular_controller" if "controller" in path.name.lower() else "angular_directive"
                facts.append(Fact(kind, class_name, evidence(path, source_root, node, digest, project_id)))

        if node.type != "call_expression":
            continue
        node_evidence = evidence(path, source_root, node, digest, project_id)
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
                method = _literal_or_expression(values["method"], source).upper() if "method" in values else "GET"
                query_components = _object_keys(values["params"], source) if "params" in values else []
                facts.append(_api_call_fact(path, source_root, source, digest, project_id, node, method, values["url"], variables, file_service, file_controller, query_components))
        if property_name and property_name.lower() in HTTP_VERBS and _call_object(node, source, f"$http.{property_name}") and arguments:
            facts.append(
                _api_call_fact(
                    path,
                    source_root,
                    source,
                    digest,
                    project_id,
                    node,
                    property_name.upper(),
                    arguments[0],
                    variables,
                    file_service,
                    file_controller,
                )
            )
    return facts
