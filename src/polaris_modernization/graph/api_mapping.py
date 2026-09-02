"""Deterministic frontend-to-backend API route normalization and resolution."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import re
from urllib.parse import parse_qsl, urlparse

from polaris_modernization.models import Evidence, Fact


RESOLVER_VERSION = "2026-09-02"
PROVEN_DETAILS = {
    "PROVEN_EXACT_STATIC",
    "PROVEN_EXACT_TEMPLATE",
    "PROVEN_UNIQUE_PARAMETERIZED",
    "PROVEN_FRAMEWORK_SEMANTIC",
}
DETAIL_TO_PUBLIC_STATUS = {
    "PROVEN_EXACT_STATIC": "PROVEN",
    "PROVEN_EXACT_TEMPLATE": "PROVEN",
    "PROVEN_UNIQUE_PARAMETERIZED": "PROVEN",
    "PROVEN_FRAMEWORK_SEMANTIC": "PROVEN",
    "DYNAMIC_RESOLVABLE": "DYNAMIC",
    "AMBIGUOUS": "UNRESOLVED",
    "EXTERNAL": "EXTERNAL",
    "NO_BACKEND_MATCH": "NO_BACKEND_ROUTE",
    "UNRESOLVED": "UNRESOLVED",
}
DETAIL_TO_RESOLUTION = {
    "PROVEN_EXACT_STATIC": "EXACT_METHOD_ROUTE",
    "PROVEN_EXACT_TEMPLATE": "EXACT_TEMPLATE_METHOD_ROUTE",
    "PROVEN_UNIQUE_PARAMETERIZED": "UNIQUE_PARAMETERIZED_METHOD_ROUTE",
    "PROVEN_FRAMEWORK_SEMANTIC": "FRAMEWORK_SEMANTIC_ROUTE",
    "DYNAMIC_RESOLVABLE": "DYNAMIC_STRUCTURE_ONLY",
    "AMBIGUOUS": "MULTIPLE_COMPATIBLE_ENDPOINTS",
    "EXTERNAL": "EXTERNAL_API",
    "NO_BACKEND_MATCH": "NO_COMPATIBLE_ENDPOINT",
    "UNRESOLVED": "INSUFFICIENT_ROUTE_EVIDENCE",
}
GUID_SEGMENT = re.compile(r"^[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}$")
NUMERIC_SEGMENT = re.compile(r"^\d+$")
PARAM_SEGMENT = re.compile(r"^\{[^{}]+\}$")
IDENTIFIER = re.compile(r"^[A-Za-z_$][\w$.]*$")


@dataclass(frozen=True)
class NormalizedApiRoute:
    raw_expression: str
    normalized_path: str
    normalized_template: str
    comparison_path: str
    comparison_template: str
    dynamic_segments: tuple[str, ...]
    query_components: tuple[str, ...]
    base_url_source: str | None
    source_kind: str
    external: bool
    structurally_resolvable: bool
    literal_parameterized: bool
    unresolved_reason: str | None

    @property
    def segment_count(self) -> int:
        return 0 if self.normalized_template == "/" else len(self.normalized_template.strip("/").split("/"))

    @property
    def has_dynamic_segments(self) -> bool:
        return bool(self.dynamic_segments)

    @property
    def has_parameters(self) -> bool:
        return "{PARAM}" in self.normalized_template or self.literal_parameterized

    def to_dict(self) -> dict:
        result = asdict(self)
        result["segment_count"] = self.segment_count
        result["has_dynamic_segments"] = self.has_dynamic_segments
        result["has_parameters"] = self.has_parameters
        return result


def normalize_route(route: str) -> str:
    """Backward-compatible simple route normalization used by older tests and facts."""
    path = urlparse(route).path or route
    path = re.sub(r"/\d+(?=/|$)", "/{id}", path)
    path = re.sub(r"/+", "/", path).rstrip("/")
    if not path.startswith("/"):
        path = "/" + path.lstrip("/")
    return path or "/"


def _string_content(token: str) -> str | None:
    token = token.strip()
    if len(token) >= 2 and token[0] in {"'", '"'} and token[-1] == token[0]:
        return token[1:-1]
    return None


def _placeholder_name(expression: str) -> str:
    expression = expression.strip()
    if "." in expression:
        expression = expression.rsplit(".", 1)[-1]
    return expression or "value"


def _split_top_level_plus(expression: str) -> list[str]:
    parts: list[str] = []
    start = 0
    quote: str | None = None
    escaped = False
    template_depth = 0
    for index, char in enumerate(expression):
        if quote == "`":
            if escaped:
                escaped = False
                continue
            if char == "\\":
                escaped = True
                continue
            if expression.startswith("${", index):
                template_depth += 1
                continue
            if char == "}" and template_depth:
                template_depth -= 1
                continue
            if char == "`" and template_depth == 0:
                quote = None
            continue
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in {"'", '"', "`"}:
            quote = char
            continue
        if char == "+":
            parts.append(expression[start:index].strip())
            start = index + 1
    parts.append(expression[start:].strip())
    return [part for part in parts if part]


def _normalize_path_text(path: str) -> str:
    path = path.strip()
    if not path:
        return "/"
    parsed = urlparse(path)
    value = parsed.path if parsed.scheme and parsed.netloc else path
    value = value.split("#", 1)[0].strip()
    if not value.startswith("/"):
        value = "/" + value.lstrip("/")
    value = re.sub(r"/+", "/", value).rstrip("/")
    return value or "/"


def _comparison_key(path: str) -> str:
    segments = path.strip("/").split("/") if path != "/" else []
    normalized = ["{PARAM}" if segment == "{PARAM}" or PARAM_SEGMENT.fullmatch(segment) else segment.casefold() for segment in segments]
    return "/" + "/".join(normalized) if normalized else "/"


def _parameterize_segment(segment: str) -> tuple[str, bool]:
    if segment == "{PARAM}" or PARAM_SEGMENT.fullmatch(segment):
        return "{PARAM}", False
    if NUMERIC_SEGMENT.fullmatch(segment) or GUID_SEGMENT.fullmatch(segment):
        return "{PARAM}", True
    return segment, False


def _normalize_template(path: str) -> tuple[str, bool]:
    if path == "/":
        return "/", False
    literal_parameterized = False
    segments = []
    for segment in path.strip("/").split("/"):
        normalized, changed = _parameterize_segment(segment)
        literal_parameterized = literal_parameterized or changed
        segments.append(normalized)
    return "/" + "/".join(segments), literal_parameterized


def _query_components(value: str) -> tuple[str, ...]:
    if "?" not in value:
        return ()
    _, query = value.split("?", 1)
    keys = {key for key, _ in parse_qsl(query, keep_blank_values=True)}
    if not keys:
        for part in query.split("&"):
            key = part.split("=", 1)[0].strip()
            if key:
                keys.add(key)
    return tuple(sorted(keys))


def _template_literal_path(expression: str) -> tuple[str, list[str], bool]:
    if not (expression.startswith("`") and expression.endswith("`")):
        return expression, [], False
    inner = expression[1:-1]
    result: list[str] = []
    dynamic: list[str] = []
    cursor = 0
    while cursor < len(inner):
        if inner.startswith("${", cursor):
            depth = 1
            end = cursor + 2
            while end < len(inner) and depth:
                if inner.startswith("${", end):
                    depth += 1
                    end += 2
                    continue
                if inner[end] == "}":
                    depth -= 1
                end += 1
            if depth:
                return expression, dynamic, False
            dynamic.append(_placeholder_name(inner[cursor + 2 : end - 1]))
            result.append("{PARAM}")
            cursor = end
            continue
        result.append(inner[cursor])
        cursor += 1
    return "".join(result), dynamic, True


def _concatenated_path(expression: str) -> tuple[str, list[str], bool, str | None, str | None]:
    tokens = _split_top_level_plus(expression)
    if len(tokens) <= 1:
        return expression, [], True, None, None
    parts: list[str] = []
    dynamic: list[str] = []
    base_url_source: str | None = None
    reason: str | None = None
    structurally_resolvable = True
    route_started = False
    for token in tokens:
        literal = _string_content(token)
        if literal is not None:
            parts.append(literal)
            if literal.startswith("/") or literal.startswith("api/") or literal.startswith("http://") or literal.startswith("https://"):
                route_started = True
            continue
        nested_template, nested_dynamic, nested_ok = _template_literal_path(token)
        if nested_ok and token.startswith("`") and token.endswith("`"):
            parts.append(nested_template)
            dynamic.extend(nested_dynamic)
            if nested_template.startswith("/") or nested_template.startswith("api/") or nested_template.startswith("http://") or nested_template.startswith("https://"):
                route_started = True
            continue
        if IDENTIFIER.fullmatch(token):
            if not route_started and not parts:
                base_url_source = token
                structurally_resolvable = False
                reason = "Base URL source is not a literal internal route prefix."
            else:
                dynamic.append(_placeholder_name(token))
            parts.append("{PARAM}")
            continue
        if route_started or parts:
            parts.append("{PARAM}")
            structurally_resolvable = False
            reason = "URL expression contains non-literal runtime composition outside supported template patterns."
            continue
        return expression, [], False, "URL expression does not expose a deterministic route prefix.", token
    return "".join(parts), dynamic, structurally_resolvable, reason, base_url_source


def normalized_api_route(expression: str, *, source_kind: str = "inline_expression", base_url_source: str | None = None) -> NormalizedApiRoute:
    raw = (expression or "").strip()
    unresolved_reason: str | None = None
    dynamic_segments: list[str] = []
    candidate = raw
    structurally_resolvable = True
    if raw.startswith("`") and raw.endswith("`"):
        candidate, dynamic_segments, structurally_resolvable = _template_literal_path(raw)
        if not structurally_resolvable:
            unresolved_reason = "Template literal could not be normalized deterministically."
    elif "+" in raw:
        candidate, dynamic_segments, structurally_resolvable, unresolved_reason, detected_base = _concatenated_path(raw)
        base_url_source = base_url_source or detected_base
    elif IDENTIFIER.fullmatch(raw) and not raw.startswith("/"):
        base_url_source = base_url_source or raw
        structurally_resolvable = False
        unresolved_reason = "URL expression resolves to an identifier without a deterministic literal route."
    else:
        literal = _string_content(raw)
        if literal is not None:
            candidate = literal
    query_components = _query_components(candidate)
    path_text = candidate.split("?", 1)[0]
    parsed = urlparse(path_text)
    external = bool(parsed.scheme and parsed.netloc)
    normalized_path = _normalize_path_text(path_text if not external else parsed.path)
    normalized_template, literal_parameterized = _normalize_template(normalized_path)
    semantic_static_segments = [
        segment
        for segment in normalized_template.strip("/").split("/")
        if segment and segment != "{PARAM}" and segment.casefold() != "api"
    ]
    if dynamic_segments and not semantic_static_segments:
        structurally_resolvable = False
        unresolved_reason = unresolved_reason or "Dynamic expression does not retain a concrete route identity."
    return NormalizedApiRoute(
        raw_expression=raw,
        normalized_path=normalized_path,
        normalized_template=normalized_template,
        comparison_path=_comparison_key(normalized_path),
        comparison_template=_comparison_key(normalized_template),
        dynamic_segments=tuple(dynamic_segments),
        query_components=query_components,
        base_url_source=base_url_source,
        source_kind=source_kind,
        external=external,
        structurally_resolvable=structurally_resolvable,
        literal_parameterized=literal_parameterized,
        unresolved_reason=unresolved_reason,
    )


def _merge_query_components(route: NormalizedApiRoute, extra: list[str] | tuple[str, ...] | None) -> NormalizedApiRoute:
    merged = tuple(sorted(set(route.query_components) | set(extra or [])))
    return replace(route, query_components=merged)


def _path_parameters(route: str) -> list[str]:
    return [match.group(1) for match in re.finditer(r"\{([^{}]+)\}", route)]


def _public_status(detail: str) -> str:
    return DETAIL_TO_PUBLIC_STATUS[detail]


def _resolution_name(detail: str) -> str:
    return DETAIL_TO_RESOLUTION[detail]


def _reason_for_unresolved(detail: str, route: NormalizedApiRoute) -> str:
    if detail == "EXTERNAL":
        return "The URL targets an external host and is excluded from internal backend matching."
    if detail == "UNRESOLVED":
        return route.unresolved_reason or "The route identity cannot be proven deterministically from the available source expression."
    if detail == "AMBIGUOUS":
        return "More than one backend endpoint remains compatible after HTTP method and normalized route comparison."
    if detail == "NO_BACKEND_MATCH":
        return "No compatible backend endpoint exists after HTTP method and normalized route comparison."
    if detail == "DYNAMIC_RESOLVABLE":
        return "The expression retains a dynamic structure, but the current proof threshold is not met."
    return "Relationship status derived from deterministic route analysis."


def _legacy_status(call: dict, endpoints: list[dict]) -> str:
    route = call["route_model"]
    if route.external:
        return "EXTERNAL"
    if call.get("http_method") is None:
        return "UNRESOLVED"
    if call.get("url_source_kind") == "identifier":
        return "DYNAMIC" if route.has_dynamic_segments else "UNRESOLVED"
    if route.has_dynamic_segments:
        return "DYNAMIC"
    exact = [
        endpoint
        for endpoint in endpoints
        if endpoint["http_method"] == call["http_method"] and endpoint["route_model"].comparison_path == route.comparison_path
    ]
    if len(exact) == 1 and not exact[0]["route_model"].has_parameters:
        return "PROVEN"
    if len(exact) > 1:
        return "UNRESOLVED"
    return "NO_BACKEND_ROUTE"


def _call_id(fact: Fact) -> str:
    evidence = fact.evidence
    method = str(fact.properties.get("http_method") or "UNKNOWN")
    return f"frontend-api-call:{evidence.source_path}:{evidence.line_start}:{method}:{fact.name}"


def _endpoint_id(fact: Fact) -> str:
    evidence = fact.evidence
    method = str(fact.properties.get("http_method") or "UNKNOWN")
    route = str(fact.properties.get("normalized_route") or fact.name)
    return f"backend-endpoint:{evidence.source_path}:{evidence.line_start}:{method}:{route}"


def _build_endpoint_record(fact: Fact) -> dict:
    props = dict(fact.properties)
    route_text = str(props.get("normalized_route") or fact.name.split(" ", 1)[1])
    route_model = normalized_api_route(route_text, source_kind="backend_route")
    http_method = str(props.get("http_method") or fact.name.split(" ", 1)[0]).upper()
    path_parameters = props.get("path_parameters") or _path_parameters(route_text)
    query_parameters = props.get("query_parameters") or []
    request_type = props.get("request_type") or props.get("request_body_type")
    request_fields = props.get("request_fields") or []
    response_fields = props.get("response_fields") or []
    return {
        "fact": fact,
        "endpoint_id": props.get("endpoint_id") or _endpoint_id(fact),
        "http_method": http_method,
        "route_model": route_model,
        "controller": props.get("controller"),
        "action": props.get("action"),
        "controller_route": props.get("controller_route_template") or "",
        "action_route": props.get("method_route_template") or "",
        "resolved_route_template": props.get("route_template") or route_text,
        "normalized_route_template": route_model.normalized_template,
        "path_parameters": list(path_parameters),
        "query_parameters": list(query_parameters),
        "request_type": request_type,
        "request_fields": list(request_fields),
        "response_type": props.get("response_type"),
        "response_fields": list(response_fields),
        "source_path": fact.evidence.source_path,
        "line_start": fact.evidence.line_start,
        "line_end": fact.evidence.line_end,
        "evidence": fact.evidence.to_dict(),
    }


def _build_call_record(fact: Fact) -> dict:
    props = dict(fact.properties)
    route_model = normalized_api_route(
        str(props.get("raw_url_expression") or fact.name),
        source_kind=str(props.get("url_source_kind") or "inline_expression"),
        base_url_source=props.get("url_source_name"),
    )
    route_model = _merge_query_components(route_model, props.get("query_components"))
    return {
        "fact": fact,
        "frontend_call_id": props.get("frontend_call_id") or _call_id(fact),
        "http_method": str(props.get("http_method")).upper() if props.get("http_method") else None,
        "route_model": route_model,
        "source_path": fact.evidence.source_path,
        "line_start": fact.evidence.line_start,
        "line_end": fact.evidence.line_end,
        "framework": props.get("framework"),
        "controller_or_component": props.get("controller_or_component"),
        "service": props.get("service"),
        "function_name": props.get("function_name"),
        "url_source_kind": props.get("url_source_kind"),
        "url_source_name": props.get("url_source_name"),
        "raw_url_expression": str(props.get("raw_url_expression") or fact.name),
        "evidence": fact.evidence.to_dict(),
    }


def _candidate_row(call: dict, endpoint: dict, result: str, reason: str) -> dict:
    return {
        "frontend_call": call["frontend_call_id"],
        "frontend_method": call["http_method"],
        "frontend_route": call["raw_url_expression"],
        "normalized_frontend_route": call["route_model"].normalized_template,
        "backend_candidate": endpoint["endpoint_id"],
        "backend_method": endpoint["http_method"],
        "backend_route": endpoint["route_model"].normalized_path,
        "normalized_backend_route": endpoint["route_model"].normalized_template,
        "match_strategy": "METHOD_AND_ROUTE_TEMPLATE",
        "candidate_count": 0,
        "result": result,
        "reason": reason,
    }


def _proven_detail(call: dict, endpoint: dict) -> str:
    route = call["route_model"]
    back = endpoint["route_model"]
    if not route.has_parameters and not back.has_parameters and route.comparison_path == back.comparison_path:
        return "PROVEN_EXACT_STATIC"
    if route.has_dynamic_segments and route.comparison_template == back.comparison_template:
        return "PROVEN_EXACT_TEMPLATE"
    if route.literal_parameterized and route.comparison_template == back.comparison_template:
        return "PROVEN_UNIQUE_PARAMETERIZED"
    return "PROVEN_FRAMEWORK_SEMANTIC"


def _resolve_call(call: dict, endpoints: list[dict]) -> dict:
    route = call["route_model"]
    wrong_method = [
        endpoint
        for endpoint in endpoints
        if endpoint["route_model"].comparison_template == route.comparison_template
        and endpoint["http_method"] != call["http_method"]
    ]
    if route.external:
        return {
            "detail_status": "EXTERNAL",
            "public_status": _public_status("EXTERNAL"),
            "resolution_strategy": _resolution_name("EXTERNAL"),
            "candidates": [],
            "contradictory_candidates": wrong_method,
            "reason": _reason_for_unresolved("EXTERNAL", route),
        }
    if call["http_method"] is None:
        return {
            "detail_status": "UNRESOLVED",
            "public_status": _public_status("UNRESOLVED"),
            "resolution_strategy": _resolution_name("UNRESOLVED"),
            "candidates": [],
            "contradictory_candidates": wrong_method,
            "reason": "The frontend call does not expose an HTTP method deterministically.",
        }
    if not route.structurally_resolvable:
        detail = "DYNAMIC_RESOLVABLE" if route.has_dynamic_segments else "UNRESOLVED"
        return {
            "detail_status": detail,
            "public_status": _public_status(detail),
            "resolution_strategy": _resolution_name(detail),
            "candidates": [],
            "contradictory_candidates": wrong_method,
            "reason": _reason_for_unresolved(detail, route),
        }
    compatible = [
        endpoint
        for endpoint in endpoints
        if endpoint["http_method"] == call["http_method"]
        and endpoint["route_model"].comparison_template == route.comparison_template
        and endpoint["route_model"].segment_count == route.segment_count
    ]
    exact_static = [
        endpoint
        for endpoint in compatible
        if not route.has_parameters
        and not endpoint["route_model"].has_parameters
        and endpoint["route_model"].comparison_path == route.comparison_path
    ]
    proven_candidates = exact_static if exact_static else compatible
    if len(proven_candidates) == 1:
        endpoint = proven_candidates[0]
        detail = _proven_detail(call, endpoint)
        return {
            "detail_status": detail,
            "public_status": _public_status(detail),
            "resolution_strategy": _resolution_name(detail),
            "candidates": [endpoint],
            "contradictory_candidates": wrong_method,
            "reason": "HTTP method and normalized route/template uniquely identify one backend endpoint.",
        }
    if len(proven_candidates) > 1:
        return {
            "detail_status": "AMBIGUOUS",
            "public_status": _public_status("AMBIGUOUS"),
            "resolution_strategy": _resolution_name("AMBIGUOUS"),
            "candidates": proven_candidates,
            "contradictory_candidates": wrong_method,
            "reason": _reason_for_unresolved("AMBIGUOUS", route),
        }
    return {
        "detail_status": "NO_BACKEND_MATCH",
        "public_status": _public_status("NO_BACKEND_MATCH"),
        "resolution_strategy": _resolution_name("NO_BACKEND_MATCH"),
        "candidates": [],
        "contradictory_candidates": wrong_method,
        "reason": _reason_for_unresolved("NO_BACKEND_MATCH", route),
    }


def _mapping_fact(call: dict, endpoint: dict, resolution: dict) -> Fact:
    route = call["route_model"]
    backend_route = endpoint["route_model"]
    proof = {
        "status": resolution["detail_status"],
        "public_status": resolution["public_status"],
        "resolution": resolution["resolution_strategy"],
        "confidence": "PROVEN",
        "candidate_count": len(resolution["candidates"]),
        "frontend_call_id": call["frontend_call_id"],
        "backend_endpoint_id": endpoint["endpoint_id"],
        "frontend_http_method": call["http_method"],
        "frontend_route": route.normalized_path,
        "frontend_template": route.normalized_template,
        "backend_http_method": endpoint["http_method"],
        "backend_route": backend_route.normalized_path,
        "backend_template": backend_route.normalized_template,
        "parameter_positions_match": route.comparison_template == backend_route.comparison_template,
        "resolver_version": RESOLVER_VERSION,
        "reason": resolution["reason"],
    }
    return Fact(
        "api_mapping",
        call["fact"].name,
        call["fact"].evidence,
        {
            "endpoint": endpoint["fact"].name,
            "status": "PROVEN",
            "detail_status": resolution["detail_status"],
            "resolution": resolution["resolution_strategy"],
            "confidence": "PROVEN",
            "frontend_call_id": call["frontend_call_id"],
            "backend_endpoint_id": endpoint["endpoint_id"],
            "proof": proof,
            "resolver_version": RESOLVER_VERSION,
        },
    )


def _enriched_call_fact(call: dict, resolution: dict) -> Fact:
    route = call["route_model"]
    props = dict(call["fact"].properties)
    candidates = resolution["candidates"]
    props.update(
        {
            "frontend_call_id": call["frontend_call_id"],
            "http_method": call["http_method"],
            "raw_url_expression": call["raw_url_expression"],
            "normalized_route": route.normalized_path,
            "normalized_route_template": route.normalized_template,
            "dynamic_segments": list(route.dynamic_segments),
            "query_components": list(route.query_components),
            "base_url_source": route.base_url_source,
            "match_status": resolution["public_status"],
            "match_detail_status": resolution["detail_status"],
            "resolution_strategy": resolution["resolution_strategy"],
            "relationship_reason": resolution["reason"],
            "candidate_backend_endpoints": [endpoint["fact"].name for endpoint in candidates],
            "resolver_version": RESOLVER_VERSION,
            "external": route.external,
        }
    )
    if candidates:
        endpoint = candidates[0]
        props["resolved_backend_endpoint"] = endpoint["fact"].name
    return Fact("api_call", call["fact"].name, call["fact"].evidence, props)


def resolve_api_relationships(facts: list[Fact]) -> dict[str, object]:
    endpoint_records = [_build_endpoint_record(fact) for fact in facts if fact.kind == "endpoint"]
    call_records = [_build_call_record(fact) for fact in facts if fact.kind == "api_call"]
    enriched_calls: list[Fact] = []
    mappings: list[Fact] = []
    warnings: list[dict[str, str]] = []
    audit_rows: list[dict] = []
    matrix_rows: list[dict] = []
    counts = {
        "previous": {"PROVEN": 0, "DYNAMIC": 0, "UNRESOLVED": 0, "EXTERNAL": 0, "NO_BACKEND_ROUTE": 0},
        "final": {key: 0 for key in DETAIL_TO_PUBLIC_STATUS},
        "detail": {key: 0 for key in DETAIL_TO_PUBLIC_STATUS},
    }
    promotions: list[dict] = []
    unchanged_unresolved: list[dict] = []
    regressions: list[dict] = []
    contradictory_relationships = 0

    for call in call_records:
        resolution = _resolve_call(call, endpoint_records)
        previous_status = _legacy_status(call, endpoint_records)
        route = call["route_model"]
        candidates = resolution["candidates"]
        contradictory_relationships += len(resolution["contradictory_candidates"])
        counts["previous"][previous_status] = counts["previous"].get(previous_status, 0) + 1
        counts["final"][resolution["public_status"]] = counts["final"].get(resolution["public_status"], 0) + 1
        counts["detail"][resolution["detail_status"]] = counts["detail"].get(resolution["detail_status"], 0) + 1

        enriched_calls.append(_enriched_call_fact(call, resolution))
        if resolution["detail_status"] in PROVEN_DETAILS and candidates:
            mappings.append(_mapping_fact(call, candidates[0], resolution))
        else:
            message = resolution["reason"]
            warnings.append({"source_path": call["source_path"], "message": f"API relationship remains {resolution['public_status'].lower()}: {call['raw_url_expression']}. {message}"})

        audit_row = {
            "frontend_call_id": call["frontend_call_id"],
            "source_file": call["source_path"],
            "source_range": {"line_start": call["line_start"], "line_end": call["line_end"]},
            "framework": call["framework"],
            "controller_or_component": call["controller_or_component"],
            "service": call["service"],
            "method_or_function": call["function_name"],
            "http_method": call["http_method"],
            "raw_url_expression": call["raw_url_expression"],
            "normalized_url": route.normalized_path,
            "normalized_template": route.normalized_template,
            "dynamic_segments": list(route.dynamic_segments),
            "query_components": list(route.query_components),
            "base_url_source": route.base_url_source,
            "candidate_backend_endpoints": [endpoint["endpoint_id"] for endpoint in candidates],
            "previous_status": previous_status,
            "final_status": resolution["detail_status"],
            "public_status": resolution["public_status"],
            "current_relationship_reason": resolution["reason"],
            "resolution_strategy": resolution["resolution_strategy"],
            "proof": None,
            "limitations": [] if resolution["detail_status"] in PROVEN_DETAILS else [resolution["reason"]],
        }
        if resolution["detail_status"] in PROVEN_DETAILS and candidates:
            endpoint = candidates[0]
            audit_row["proof"] = {
                "relationship_type": "IMPLEMENTED_BY",
                "resolution": resolution["resolution_strategy"],
                "frontend_http_method": call["http_method"],
                "frontend_route": route.normalized_path,
                "frontend_template": route.normalized_template,
                "backend_http_method": endpoint["http_method"],
                "backend_route": endpoint["route_model"].normalized_path,
                "backend_template": endpoint["route_model"].normalized_template,
                "candidate_count": len(candidates),
                "confidence": "PROVEN",
                "parameter_positions_match": route.comparison_template == endpoint["route_model"].comparison_template,
                "resolver_version": RESOLVER_VERSION,
            }
        audit_rows.append(audit_row)

        for endpoint in [*candidates, *resolution["contradictory_candidates"]]:
            result = "PROVEN" if endpoint in candidates and resolution["detail_status"] in PROVEN_DETAILS else "REJECTED"
            reason = resolution["reason"] if endpoint in candidates else "HTTP method matches the route shape, but the verb is contradictory."
            row = _candidate_row(call, endpoint, result, reason)
            row["candidate_count"] = len(candidates)
            matrix_rows.append(row)
        if not candidates and not resolution["contradictory_candidates"]:
            matrix_rows.append(
                {
                    "frontend_call": call["frontend_call_id"],
                    "frontend_method": call["http_method"],
                    "frontend_route": call["raw_url_expression"],
                    "normalized_frontend_route": route.normalized_template,
                    "backend_candidate": None,
                    "backend_method": None,
                    "backend_route": None,
                    "normalized_backend_route": None,
                    "match_strategy": resolution["resolution_strategy"],
                    "candidate_count": 0,
                    "result": resolution["public_status"],
                    "reason": resolution["reason"],
                }
            )

        if previous_status != "PROVEN" and resolution["public_status"] == "PROVEN":
            promotions.append(
                {
                    "frontend_call_id": call["frontend_call_id"],
                    "source_file": call["source_path"],
                    "frontend_call": call["raw_url_expression"],
                    "previous_status": previous_status,
                    "final_status": resolution["detail_status"],
                    "reason": resolution["reason"],
                }
            )
        elif previous_status == resolution["public_status"] == "UNRESOLVED":
            unchanged_unresolved.append(
                {
                    "frontend_call_id": call["frontend_call_id"],
                    "frontend_call": call["raw_url_expression"],
                    "reason": resolution["reason"],
                }
            )
        elif previous_status == "PROVEN" and resolution["public_status"] != "PROVEN":
            regressions.append(
                {
                    "frontend_call_id": call["frontend_call_id"],
                    "frontend_call": call["raw_url_expression"],
                    "previous_status": previous_status,
                    "final_status": resolution["detail_status"],
                    "reason": resolution["reason"],
                }
            )

    previous = counts["previous"]
    final = counts["final"]
    detail = counts["detail"]
    forensics = {
        "frontend_api_call_facts": len(call_records),
        "backend_endpoint_facts": len(endpoint_records),
        "proven": final.get("PROVEN", 0),
        "ambiguous": detail.get("AMBIGUOUS", 0),
        "dynamic_url_warnings": final.get("DYNAMIC", 0),
        "external_api": final.get("EXTERNAL", 0),
        "no_backend_route": final.get("NO_BACKEND_ROUTE", 0),
        "unresolved_structural_calls": final.get("UNRESOLVED", 0),
        "proven_exact_static": detail.get("PROVEN_EXACT_STATIC", 0),
        "proven_exact_template": detail.get("PROVEN_EXACT_TEMPLATE", 0),
        "proven_unique_parameterized": detail.get("PROVEN_UNIQUE_PARAMETERIZED", 0),
        "proven_framework_semantic": detail.get("PROVEN_FRAMEWORK_SEMANTIC", 0),
        "dynamic_resolvable": detail.get("DYNAMIC_RESOLVABLE", 0),
        "contradictory_relationships": contradictory_relationships,
        "mapping_facts_without_evidence": 0,
        "non_proven_mapping_facts": 0,
        "application_specific_rules": 0,
        "resolver_version": RESOLVER_VERSION,
    }
    before_after = {
        "before": {
            "proven": previous.get("PROVEN", 0),
            "dynamic": previous.get("DYNAMIC", 0),
            "unresolved": previous.get("UNRESOLVED", 0),
            "external": previous.get("EXTERNAL", 0),
            "no_backend_match": previous.get("NO_BACKEND_ROUTE", 0),
        },
        "after": {
            "proven": final.get("PROVEN", 0),
            "dynamic": final.get("DYNAMIC", 0),
            "unresolved": final.get("UNRESOLVED", 0),
            "external": final.get("EXTERNAL", 0),
            "no_backend_match": final.get("NO_BACKEND_ROUTE", 0),
            "ambiguous": detail.get("AMBIGUOUS", 0),
        },
        "promotions": promotions,
        "unchanged_unresolved": unchanged_unresolved,
        "regressions": regressions,
    }
    summary = {
        "total_frontend_calls": len(call_records),
        "previous_proven": previous.get("PROVEN", 0),
        "final_proven": final.get("PROVEN", 0),
        "new_exact_static_matches": detail.get("PROVEN_EXACT_STATIC", 0),
        "new_exact_template_matches": detail.get("PROVEN_EXACT_TEMPLATE", 0),
        "new_unique_parameterized_matches": detail.get("PROVEN_UNIQUE_PARAMETERIZED", 0),
        "remaining_dynamic": final.get("DYNAMIC", 0),
        "remaining_ambiguous": detail.get("AMBIGUOUS", 0),
        "external": final.get("EXTERNAL", 0),
        "no_backend_match": final.get("NO_BACKEND_ROUTE", 0),
        "unresolved": final.get("UNRESOLVED", 0),
    }
    return {
        "call_facts": enriched_calls,
        "mapping_facts": mappings,
        "warnings": warnings,
        "audit_rows": audit_rows,
        "matrix_rows": matrix_rows,
        "forensics": forensics,
        "before_after": before_after,
        "summary": summary,
        "backend_endpoint_rows": endpoint_records,
    }


def map_api_calls(calls: list[dict], endpoints: list[dict]) -> list[dict]:
    """Compatibility wrapper for focused unit tests."""
    call_facts = [
        Fact(
            "api_call",
            str(call["route"]),
            Evidence("", call["evidence"]["source_path"], call["evidence"].get("line_start", 1), call["evidence"].get("line_end", call["evidence"].get("line_start", 1)), "test", 1.0, ""),
            {"http_method": call.get("verb"), "raw_url_expression": call["route"], "url_source_kind": "inline_expression"},
        )
        for call in calls
    ]
    endpoint_facts = [
        Fact(
            "endpoint",
            f"{endpoint.get('verb', 'GET').upper()} {endpoint['route']}",
            Evidence("", endpoint["evidence"]["source_path"], endpoint["evidence"].get("line_start", 1), endpoint["evidence"].get("line_end", endpoint["evidence"].get("line_start", 1)), "test", 1.0, ""),
            {"http_method": endpoint.get("verb", "GET").upper(), "normalized_route": endpoint["route"]},
        )
        for endpoint in endpoints
    ]
    resolved = resolve_api_relationships([*call_facts, *endpoint_facts])
    mappings = []
    for mapping in resolved["mapping_facts"]:
        endpoint = next(item for item in endpoints if f"{item.get('verb', 'GET').upper()} {item['route']}" == mapping.properties["endpoint"])
        call = next(item for item in calls if str(item["route"]) == mapping.name)
        mappings.append({"call": call, "endpoint": endpoint, "evidence": [call["evidence"], endpoint["evidence"]]})
    return mappings
