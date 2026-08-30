"""Shared AST traversal and evidence creation helpers."""

from __future__ import annotations

from pathlib import Path

from tree_sitter import Language, Node, Parser

from polaris_modernization.models import Evidence


def parser_for(language_capsule) -> Parser:
    return Parser(Language(language_capsule))


def walk(node: Node):
    yield node
    for child in node.children:
        yield from walk(child)


def node_text(node: Node, source: bytes) -> str:
    return source[node.start_byte : node.end_byte].decode("utf-8")


def descendant_texts(node: Node, source: bytes, node_type: str) -> list[str]:
    return [node_text(item, source) for item in walk(node) if item.type == node_type]


def evidence(path: Path, source_root: Path, node: Node, digest: str) -> Evidence:
    return Evidence(
        source_path=path.relative_to(source_root).as_posix(),
        line_start=node.start_point.row + 1,
        line_end=node.end_point.row + 1,
        extraction_method="tree-sitter",
        confidence=1.0,
        source_hash=digest,
    )


def unquote(value: str) -> str:
    if len(value) >= 2 and value[0] in "\"'" and value[-1] == value[0]:
        return value[1:-1]
    return value
