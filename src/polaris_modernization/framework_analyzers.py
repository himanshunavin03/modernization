"""Reusable deterministic framework facts layered onto the existing extraction pipeline."""
from __future__ import annotations

from dataclasses import dataclass, field
import re
from pathlib import Path
from typing import Iterable, Protocol

from polaris_modernization.graph.api_mapping import normalize_route
from polaris_modernization.models import Evidence, Fact


@dataclass
class FrameworkFacts:
    facts: list[Fact] = field(default_factory=list)
    warnings: list[dict[str, str]] = field(default_factory=list)


class FrameworkAnalyzer(Protocol):
    def supports(self, detections: list[dict]) -> bool: ...
    def analyze(self, source_root: Path, inventory: list[dict], project_id: str) -> FrameworkFacts: ...


def _evidence(entry: dict, project_id: str, line: int, end: int | None = None) -> Evidence:
    return Evidence(project_id, entry["source_path"], line, end or line, "framework-analyzer", 1.0, entry["source_hash"])


def _literal(value: str) -> str | None:
    value = value.strip()
    match = re.fullmatch(r"['\"]([^'\"]+)['\"]", value)
    return match.group(1) if match else None


def _route(prefix: str, controller: str, action: str, suffix: str) -> tuple[str, str, dict[str, str]]:
    """Compose an ASP.NET route while retaining the source template and token evidence."""
    template = "/".join(part.strip("/") for part in (prefix, suffix) if part.strip("/"))
    tokens: dict[str, str] = {}
    if "[controller]" in template:
        tokens["controller"] = controller.removesuffix("Controller").lower()
    if "[action]" in template:
        tokens["action"] = action
    normalized = template
    for token, value in tokens.items():
        normalized = normalized.replace(f"[{token}]", value)
    return template, normalize_route(normalized), tokens


def _attribute_blocks(text: str) -> list[tuple[int, int, str]]:
    """Return balanced C# attribute blocks without treating brackets in strings as delimiters."""
    blocks: list[tuple[int, int, str]] = []
    start: int | None = None
    depth = 0
    quote: str | None = None
    escaped = False
    for index, char in enumerate(text):
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in {"'", '"'}:
            quote = char
        elif char == "[":
            if depth == 0:
                start = index
            depth += 1
        elif char == "]" and depth:
            depth -= 1
            if depth == 0 and start is not None:
                blocks.append((start, index + 1, text[start + 1:index]))
                start = None
    return blocks


def _split_top_level(value: str) -> Iterable[str]:
    start = 0
    depth = 0
    quote: str | None = None
    escaped = False
    for index, char in enumerate(value):
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in {"'", '"'}:
            quote = char
        elif char == "(":
            depth += 1
        elif char == ")" and depth:
            depth -= 1
        elif char == "," and depth == 0:
            yield value[start:index].strip()
            start = index + 1
    yield value[start:].strip()


def _attribute(name: str, attributes: list[str]) -> list[str]:
    pattern = re.compile(rf"^\s*{re.escape(name)}(?:Attribute)?\s*(?:\((?P<args>.*)\))?\s*$", re.S)
    return [match.group("args") or "" for item in attributes if (match := pattern.match(item))]


def _first_string(arguments: str) -> str | None:
    match = re.search(r"['\"]((?:\\.|[^'\"])*)['\"]", arguments, re.S)
    return bytes(match.group(1), "utf-8").decode("unicode_escape") if match else None


def _parameter_details(parameters: str) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    for parameter in [part.strip() for part in parameters.split(",") if part.strip()]:
        attributes = re.findall(r"\[([^\]]+)\]", parameter)
        cleaned = re.sub(r"\[[^\]]+\]\s*", "", parameter).strip()
        if not cleaned:
            continue
        tokens = cleaned.split()
        if len(tokens) < 2:
            continue
        name = tokens[-1].strip()
        parameter_type = " ".join(tokens[:-1]).strip()
        result.append({
            "name": name,
            "type": parameter_type,
            "from_body": any("FromBody" in attribute for attribute in attributes),
            "attributes": attributes,
        })
    return result


def _api_path_hint(source_path: str) -> bool:
    parts = re.split(r"[\\/]", source_path)
    return any(part.casefold() == "api" or part.casefold().endswith(".api") for part in parts)


class AspNetRouteAnalyzer:
    """Attribute-route and conventional-controller endpoint discovery without source-specific rules."""
    _class = re.compile(r"\b(?:(?:public|internal|protected)\s+)?(?:(?:abstract|sealed|partial)\s+)*class\s+(?P<name>\w+Controller)\b")
    _method = re.compile(r"\bpublic\s+(?:(?:static|virtual|override|async)\s+)*(?P<return>[\w<>?,.\[\]]+)\s+(?P<name>\w+)\s*\((?P<params>[^)]*)\)")

    def supports(self, detections: list[dict]) -> bool:
        return any(item["framework"] in {"ASP.NET MVC/Razor", ".NET API"} for item in detections)

    def analyze(self, source_root: Path, inventory: list[dict], project_id: str) -> FrameworkFacts:
        result = FrameworkFacts()
        for entry in inventory:
            if not entry["selected_for_extraction"] or not entry["source_path"].endswith(".cs"):
                continue
            text = (source_root / entry["source_path"]).read_text(encoding="utf-8", errors="replace")
            blocks = _attribute_blocks(text)
            def attrs_before(start: int) -> list[str]:
                result: list[str] = []
                cursor = start
                for block_start, block_end, body in reversed(blocks):
                    if block_end > cursor:
                        continue
                    if text[block_end:cursor].strip():
                        break
                    result.extend(reversed(list(_split_top_level(body))))
                    cursor = block_start
                return list(reversed(result))
            classes = list(self._class.finditer(text))
            for class_index, controller_match in enumerate(classes):
                controller = controller_match.group("name")
                controller_attrs = attrs_before(controller_match.start())
                prefix_args = _attribute("RoutePrefix", controller_attrs) or _attribute("Route", controller_attrs)
                prefix = _first_string(prefix_args[0]) if prefix_args else None
                if prefix is None and _api_path_hint(entry["source_path"]):
                    prefix = "api/[controller]"
                class_end = classes[class_index + 1].start() if class_index + 1 < len(classes) else len(text)
                for method in self._method.finditer(text, controller_match.end(), class_end):
                    method_attrs = attrs_before(method.start())
                    http = [(verb.upper(), _first_string(args)) for verb in ("Get", "Post", "Put", "Patch", "Delete") for args in _attribute(f"Http{verb}", method_attrs)]
                    accept = [value.upper() for args in _attribute("AcceptVerbs", method_attrs) for value in re.findall(r"(?:HttpVerbs\.)?(GET|POST|PUT|PATCH|DELETE)\b", args, re.I)]
                    route_args = _attribute("Route", method_attrs)
                    suffix = _first_string(route_args[0]) if route_args else ""
                    action_args = _attribute("ActionName", method_attrs)
                    action = _first_string(action_args[0]) if action_args else method.group("name")
                    if http:
                        verbs = [verb for verb, _ in http]
                        suffix = next((route for _, route in http if route is not None), suffix)
                    elif accept:
                        verbs = accept
                    elif prefix:
                        verbs = ["GET"]
                        suffix = suffix or method.group("name")
                    else:
                        continue
                    line = text.count("\n", 0, method.start()) + 1
                    response = method.group("return")
                    parameter_details = _parameter_details(method.group("params"))
                    for verb in dict.fromkeys(verbs):
                        template, route, tokens = _route(prefix or "", controller, action, suffix or "")
                        path_parameters = [match.group(1) for match in re.finditer(r"\{([^{}]+)\}", route)]
                        request_parameter = next((item for item in parameter_details if item["from_body"]), None)
                        query_parameters = [
                            {"name": item["name"], "type": item["type"]}
                            for item in parameter_details
                            if not item["from_body"] and item["name"] not in path_parameters and verb in {"GET", "DELETE"}
                        ]
                        result.facts.append(Fact("endpoint", f"{verb} {route}", _evidence(entry, project_id, line), {
                            "http_method": verb, "normalized_route": route, "route_template": template,
                            "controller_route_template": prefix or "", "method_route_template": suffix or "",
                            "route_token_resolution": tokens, "controller": controller, "action": action,
                            "response_type": response, "parameters": [item["name"] for item in parameter_details],
                            "path_parameters": path_parameters, "query_parameters": query_parameters,
                            "request_type": request_parameter["type"] if request_parameter else None,
                            "request_fields": [], "response_fields": [], "framework": "ASP.NET",
                            "provenance": "FRAMEWORK_PROVEN",
                        }))
        return result


class RazorAnalyzer:
    def supports(self, detections: list[dict]) -> bool:
        return any(item["framework"] == "ASP.NET MVC/Razor" for item in detections)

    def analyze(self, source_root: Path, inventory: list[dict], project_id: str) -> FrameworkFacts:
        result = FrameworkFacts()
        for entry in inventory:
            if not entry["selected_for_extraction"] or not entry["source_path"].endswith(".cshtml"):
                continue
            text = (source_root / entry["source_path"]).read_text(encoding="utf-8", errors="replace")
            view = entry["source_path"]
            for match in re.finditer(r"@model\s+([\w.<>,?]+)", text):
                result.facts.append(Fact("razor_model", view, _evidence(entry, project_id, text.count("\n", 0, match.start()) + 1), {"model": match.group(1)}))
            for match in re.finditer(r"(?:Html|Url)\.Action(?:Link)?\s*\(\s*['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]+)['\"]", text):
                result.facts.append(Fact("razor_action", view, _evidence(entry, project_id, text.count("\n", 0, match.start()) + 1), {"action": match.group(1), "controller": match.group(2)}))
        return result


class FrameworkAnalyzerRegistry:
    def __init__(self, analyzers: list[FrameworkAnalyzer] | None = None):
        self.analyzers = analyzers or [AspNetRouteAnalyzer(), RazorAnalyzer()]

    def analyze(self, source_root: Path, inventory: list[dict], project_id: str, detections: list[dict]) -> FrameworkFacts:
        result = FrameworkFacts()
        for analyzer in self.analyzers:
            if analyzer.supports(detections):
                facts = analyzer.analyze(source_root, inventory, project_id)
                result.facts.extend(facts.facts)
                result.warnings.extend(facts.warnings)
        return result
