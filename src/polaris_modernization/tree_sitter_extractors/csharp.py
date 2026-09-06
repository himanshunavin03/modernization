"""Deterministic C# controller, action, and authorization extraction."""

from __future__ import annotations

from pathlib import Path
import re

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


def _named_child_count(node, field: str) -> int:
    value = node.child_by_field_name(field)
    return len(value.named_children) if value is not None else 0


def _namespace(node, source: bytes) -> str | None:
    current = node.parent
    while current is not None:
        if current.type in {"namespace_declaration", "file_scoped_namespace_declaration"}:
            name = current.child_by_field_name("name")
            return node_text(name, source) if name is not None else None
        current = current.parent
    return None


def _method_signature(node, source: bytes) -> str:
    type_parameters = node.child_by_field_name("type_parameters")
    parameters = node.child_by_field_name("parameters")
    syntax = "".join(
        node_text(part, source)
        for part in (type_parameters, parameters)
        if part is not None
    )
    return re.sub(r"\s+", "", syntax)


def extract(path: Path, source_root: Path, digest: str, project_id: str) -> list[Fact]:
    source = path.read_bytes()
    root = parser_for(tree_sitter_c_sharp.language()).parse(source).root_node
    facts: list[Fact] = []

    for class_node in (node for node in walk(root) if node.type == "class_declaration"):
        class_name = _first_identifier(class_node, source)
        if not class_name:
            continue
        namespace = _namespace(class_node, source)
        container_identity = f"{namespace}.{class_name}" if namespace else class_name
        class_evidence = evidence(path, source_root, class_node, digest, project_id)
        # Syntax can prove a class declaration, but only controller naming or
        # Roslyn inheritance evidence can classify it as an MVC/API controller.
        is_controller = class_name.endswith("Controller")
        facts.append(Fact("controller" if is_controller else "type", class_name, class_evidence, {
            "container_identity": container_identity,
            "namespace": namespace,
        }))
        attributes = [node_text(node, source) for node in walk(class_node) if node.type == "attribute"]
        for attribute in attributes:
            if attribute == "Authorize":
                facts.append(Fact("authorization_policy", "Authorize", class_evidence, {"controller": class_name}))

        for method_node in (node for node in walk(class_node) if node.type == "method_declaration"):
            method_name = _first_identifier(method_node, source)
            if not method_name:
                continue
            method_evidence = evidence(path, source_root, method_node, digest, project_id)
            arity = _named_child_count(method_node, "parameters")
            structural_signature = _method_signature(method_node, source)
            structural_identity = f"{container_identity}.{method_name}{structural_signature}@{path.relative_to(source_root).as_posix()}"
            facts.append(Fact("action" if is_controller else "method", method_name, method_evidence, {
                "controller": class_name,
                "owner": class_name,
                "container_identity": container_identity,
                "arity": arity,
                "structural_signature": structural_signature,
                "structural_identity": structural_identity,
            }))
            facts.append(Fact("backend_handler", f"{class_name}.{method_name}/{arity}", method_evidence, {
                "owner": class_name, "function_name": method_name, "arity": arity,
                "handler_kind": "CONTROLLER" if is_controller else "DOMAIN",
            }))
            for invocation in (node for node in walk(method_node) if node.type == "invocation_expression"):
                function = invocation.child_by_field_name("function")
                function_text = node_text(function, source) if function is not None else ""
                match = re.fullmatch(r"([A-Za-z_][\w]*)\.([A-Za-z_][\w]*)", function_text)
                if match and match.group(1).lstrip("_").lower().endswith(("repository", "service", "gateway", "context")):
                    facts.append(Fact("backend_invocation", f"{class_name}.{method_name}->{function_text}", evidence(path, source_root, invocation, digest, project_id), {
                        "caller_owner": class_name, "caller": method_name,
                        "caller_arity": arity, "target_owner_hint": match.group(1).lstrip("_"),
                        "target_function": match.group(2), "target_arity": _named_child_count(invocation, "arguments"),
                    }))
            if class_name.lower().endswith("repository") or "repositories" in path.as_posix().lower():
                for invocation in (node for node in walk(method_node) if node.type == "invocation_expression"):
                    text = node_text(invocation, source)
                    operation = next((value for value in ("OrderBy", "OrderByDescending", "Skip", "Take", "Add", "Update", "Remove", "SaveChanges", "SaveChangesAsync") if f".{value}(" in text), None)
                    if operation:
                        facts.append(Fact("persistence_operation", f"{class_name}.{method_name}:{operation}", evidence(path, source_root, invocation, digest, project_id), {
                            "repository": class_name, "handler": method_name, "handler_arity": arity, "operation": operation,
                            "expression": text,
                        }))
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
