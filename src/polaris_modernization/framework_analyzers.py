"""Reusable deterministic framework facts layered onto the existing extraction pipeline."""
from __future__ import annotations

from dataclasses import dataclass, field
import re
from pathlib import Path
from typing import Protocol

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


def _route(prefix: str, controller: str, suffix: str) -> str:
    value = "/".join(part.strip("/") for part in (prefix, suffix) if part.strip("/"))
    value = value.replace("[controller]", controller.removesuffix("Controller"))
    return normalize_route(value)


class AspNetRouteAnalyzer:
    """Attribute-route and conventional-controller endpoint discovery without source-specific rules."""
    _class = re.compile(r"(?P<attrs>(?:\s*\[[^\]]+\]\s*)*)\s*(?:public\s+)?class\s+(?P<name>\w+Controller)\b")
    _method = re.compile(r"(?P<attrs>(?:\s*\[[^\]]+\]\s*)*)\s*public\s+(?P<return>[\w<>?.]+)\s+(?P<name>\w+)\s*\((?P<params>[^)]*)\)")

    def supports(self, detections: list[dict]) -> bool:
        return any(item["framework"] in {"ASP.NET MVC/Razor", ".NET API"} for item in detections)

    def analyze(self, source_root: Path, inventory: list[dict], project_id: str) -> FrameworkFacts:
        result = FrameworkFacts()
        for entry in inventory:
            if not entry["selected_for_extraction"] or not entry["source_path"].endswith(".cs"):
                continue
            text = (source_root / entry["source_path"]).read_text(encoding="utf-8", errors="replace")
            controller_match = self._class.search(text)
            if not controller_match:
                continue
            controller = controller_match.group("name")
            attrs = controller_match.group("attrs")
            prefix_match = re.search(r"(?:RoutePrefix|Route)\s*\(\s*['\"]([^'\"]+)['\"]", attrs)
            prefix = prefix_match.group(1) if prefix_match else "api/[controller]" if "/Api/" in entry["source_path"] or "\\Api\\" in entry["source_path"] else ""
            for method in self._method.finditer(text, controller_match.end()):
                method_attrs = method.group("attrs")
                verb_match = re.search(r"Http(Get|Post|Put|Patch|Delete)\s*(?:\(\s*['\"]([^'\"]+)['\"]\s*\))?", method_attrs)
                accept = re.search(r"AcceptVerbs\s*\(([^)]*)\)", method_attrs)
                route_match = re.search(r"Route\s*\(\s*['\"]([^'\"]+)['\"]", method_attrs)
                if verb_match:
                    verbs = [verb_match.group(1).upper()]
                    suffix = verb_match.group(2) or (route_match.group(1) if route_match else "")
                elif accept:
                    verbs = re.findall(r"['\"](GET|POST|PUT|PATCH|DELETE)['\"]", accept.group(1), re.I)
                    suffix = route_match.group(1) if route_match else ""
                elif prefix:
                    verbs, suffix = ["GET"], route_match.group(1) if route_match else method.group("name")
                else:
                    continue
                line = text.count("\n", 0, method.start()) + 1
                response = method.group("return")
                params = [part.strip().split()[-1] for part in method.group("params").split(",") if part.strip()]
                for verb in verbs:
                    route = _route(prefix, controller, suffix)
                    result.facts.append(Fact("endpoint", f"{verb} {route}", _evidence(entry, project_id, line), {
                        "http_method": verb, "normalized_route": route, "route_template": route,
                        "controller": controller, "action": method.group("name"), "response_type": response,
                        "parameters": params, "framework": "ASP.NET", "provenance": "FRAMEWORK_PROVEN",
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


class AngularJsApiAnalyzer:
    _config = re.compile(r"\$http\s*\(\s*\{(?P<body>.*?)\}\s*\)", re.S)
    _shortcut = re.compile(r"\$http\.(get|post|put|patch|delete)\s*\(\s*(?P<url>[^,\)]+)", re.I)

    def supports(self, detections: list[dict]) -> bool:
        return any(item["framework"] == "AngularJS" for item in detections)

    def analyze(self, source_root: Path, inventory: list[dict], project_id: str) -> FrameworkFacts:
        result = FrameworkFacts()
        for entry in inventory:
            if not entry["selected_for_extraction"] or not entry["source_path"].endswith(".js"):
                continue
            text = (source_root / entry["source_path"]).read_text(encoding="utf-8", errors="replace")
            matches = []
            for match in self._config.finditer(text):
                method = re.search(r"\bmethod\s*:\s*['\"](\w+)['\"]", match.group("body"), re.I)
                url = re.search(r"\burl\s*:\s*([^,}\n]+)", match.group("body"), re.I)
                matches.append((match.start(), method.group(1).upper() if method else "GET", _literal(url.group(1)) if url else None))
            matches.extend((match.start(), match.group(1).upper(), _literal(match.group("url"))) for match in self._shortcut.finditer(text))
            for offset, verb, url in matches:
                line = text.count("\n", 0, offset) + 1
                if url is None:
                    result.warnings.append({"source_path": entry["source_path"], "message": "Dynamic AngularJS API URL remains unresolved."})
                    continue
                route = normalize_route(url)
                result.facts.append(Fact("api_call", f"{verb} {route}", _evidence(entry, project_id, line), {"http_method": verb, "normalized_route": route, "url": url, "match_status": "UNRESOLVED", "framework": "AngularJS", "provenance": "FRAMEWORK_PROVEN"}))
        return result


class FrameworkAnalyzerRegistry:
    def __init__(self, analyzers: list[FrameworkAnalyzer] | None = None):
        self.analyzers = analyzers or [AspNetRouteAnalyzer(), RazorAnalyzer(), AngularJsApiAnalyzer()]

    def analyze(self, source_root: Path, inventory: list[dict], project_id: str, detections: list[dict]) -> FrameworkFacts:
        result = FrameworkFacts()
        for analyzer in self.analyzers:
            if analyzer.supports(detections):
                facts = analyzer.analyze(source_root, inventory, project_id)
                result.facts.extend(facts.facts)
                result.warnings.extend(facts.warnings)
        endpoints = [fact for fact in result.facts if fact.kind == "endpoint"]
        for call in (fact for fact in result.facts if fact.kind == "api_call"):
            candidates = [endpoint for endpoint in endpoints if endpoint.properties["http_method"] == call.properties["http_method"] and endpoint.properties["normalized_route"] == call.properties["normalized_route"]]
            if len(candidates) == 1:
                result.facts.append(Fact("api_mapping", call.name, call.evidence, {"endpoint": candidates[0].name, "status": "PROVEN"}))
            elif len(candidates) > 1:
                result.warnings.append({"source_path": call.evidence.source_path, "message": "AngularJS API call has ambiguous backend endpoint candidates."})
        return result
