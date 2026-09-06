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
        if current.type in {"function_declaration", "method_definition"}:
            name = current.child_by_field_name("name")
            if name is not None:
                return node_text(name, source)
        if current.type == "variable_declarator":
            name = current.child_by_field_name("name")
            value = current.child_by_field_name("value")
            if name is not None and value is not None and value.type in {"function_expression", "arrow_function"}:
                return node_text(name, source)
        if current.type == "assignment_expression":
            left = current.child_by_field_name("left")
            right = current.child_by_field_name("right")
            if left is not None and right is not None and right.type in {"function_expression", "arrow_function"}:
                return node_text(left, source).split(".")[-1]
        current = current.parent
    return None


def _qualified_function(owner: str | None, name: str) -> str:
    return f"{owner}.{name}" if owner else name


def _member_parts(node, source: bytes) -> tuple[str | None, str | None]:
    if node is None or node.type != "member_expression":
        return None, None
    obj = node.child_by_field_name("object")
    prop = node.child_by_field_name("property")
    return (node_text(obj, source) if obj is not None else None, node_text(prop, source) if prop is not None else None)


def _function_fact(path, source_root, source, digest, project_id, node, owner: str | None) -> Fact | None:
    name = None
    enclosing_name = None
    if node.type in {"function_declaration", "method_definition"}:
        name_node = node.child_by_field_name("name") or node.child_by_field_name("property")
        name = node_text(name_node, source) if name_node else None
    elif node.type == "assignment_expression":
        left = node.child_by_field_name("left")
        right = node.child_by_field_name("right")
        if left is not None and right is not None and right.type in {"function_expression", "arrow_function"}:
            name = node_text(left, source).split(".")[-1]
    elif node.type in {"function_expression", "arrow_function"}:
        enclosing_name = _enclosing_named_function(node.parent, source) or "module"
        name = f"callback@{node.start_byte}:{node.end_byte}"
    if not name:
        return None
    properties = {"function_name": name, "owner": owner}
    if enclosing_name:
        properties.update({"anonymous": True, "enclosing_function": enclosing_name})
    return Fact("frontend_function", _qualified_function(owner, name), evidence(path, source_root, node, digest, project_id), properties)


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
    request_header_components: list[str] | None = None,
) -> Fact:
    node_evidence = evidence(path, source_root, node, digest, project_id)
    url_value = _resolve_expression(url_node, source, variables)
    query_components = query_components or []
    request_header_components = request_header_components or []
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
            "request_header_components": request_header_components,
        },
    )


def extract(path: Path, source_root: Path, digest: str, project_id: str) -> list[Fact]:
    source = path.read_bytes()
    root = parser_for(tree_sitter_javascript.language()).parse(source).root_node
    facts: list[Fact] = []
    variables: dict[str, dict[str, str]] = {}
    file_service = _file_owner_name(root, source, "service")
    file_controller = _file_owner_name(root, source, "controller")
    if file_service is None and "service" in path.stem.lower():
        file_service = path.stem
    if file_controller is None and "controller" in path.stem.lower():
        file_controller = path.stem

    for node in walk(root):
        function_fact = _function_fact(path, source_root, source, digest, project_id, node, file_controller or file_service)
        if function_fact is not None:
            facts.append(function_fact)

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

        if node.type == "assignment_expression":
            left = node.child_by_field_name("left")
            right = node.child_by_field_name("right")
            target, property_name = _member_parts(left, source)
            if target and property_name and right is not None:
                facts.append(Fact("state_mutation", f"{file_controller or file_service or path.stem}.{_enclosing_named_function(node, source) or 'module'}:{target}.{property_name}", evidence(path, source_root, node, digest, project_id), {
                    "function_name": _enclosing_named_function(node, source), "owner": file_controller or file_service,
                    "target": f"{target}.{property_name}", "expression": _literal_or_expression(right, source),
                }))

        if node.type != "call_expression":
            continue
        node_evidence = evidence(path, source_root, node, digest, project_id)
        property_name = _call_property(node, source)
        arguments = _arguments(node)
        function = node.child_by_field_name("function")
        function_text = node_text(function, source) if function is not None else ""
        receiver, member = _member_parts(function, source)
        caller = _enclosing_named_function(node, source)
        if receiver and member in {"push", "pop", "shift", "unshift", "splice"}:
            facts.append(Fact("collection_mutation", f"{file_controller or file_service or path.stem}.{caller or 'module'}:{receiver}:{member}", node_evidence, {
                "function_name": caller, "owner": file_controller or file_service,
                "collection": receiver, "operation": member,
            }))
        if member in {"transitionTo", "go", "navigate"} and arguments:
            facts.append(Fact("navigation", f"{file_controller or file_service or path.stem}.{caller or 'module'}:{_literal_or_expression(arguments[0], source)}", node_evidence, {
                "function_name": caller, "owner": file_controller or file_service,
                "target": _literal_or_expression(arguments[0], source), "operation": member,
            }))
        if member in {"showConfirmModal", "confirm"}:
            facts.append(Fact("confirmation", f"{file_controller or file_service or path.stem}.{caller or 'module'}:{member}", node_evidence, {
                "function_name": caller, "owner": file_controller or file_service, "operation": member,
            }))
        if property_name and "." in function_text and not function_text.startswith(("$http.", "angular.")):
            receiver = function_text.rsplit(".", 1)[0]
            if receiver.lower().endswith(("service", "client", "gateway", "repository")):
                caller = _enclosing_named_function(node, source)
                facts.append(Fact("frontend_invocation", function_text, node_evidence, {
                    "caller": caller,
                    "caller_owner": file_controller or file_service,
                    "target_owner": receiver,
                    "target_function": property_name,
                }))
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
                request_headers = _object_keys(values["headers"], source) if "headers" in values else []
                facts.append(_api_call_fact(path, source_root, source, digest, project_id, node, method, values["url"], variables, file_service, file_controller, query_components, request_headers))
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
