"""Evidence-only frontend API route normalization and endpoint matching."""
from __future__ import annotations
import re
from urllib.parse import urlparse


def normalize_route(route: str) -> str:
    path = urlparse(route).path or route
    path = re.sub(r"/\d+(?=/|$)", "/{id}", path)
    path = re.sub(r"/+", "/", path).rstrip("/")
    if not path.startswith("/"):
        path = "/" + path
    return path or "/"


def map_api_calls(calls: list[dict], endpoints: list[dict]) -> list[dict]:
    """Return mappings only when verb and normalized route identify one endpoint."""
    mappings = []
    for call in calls:
        candidates = [endpoint for endpoint in endpoints if endpoint.get("verb", "GET").upper() == call.get("verb", "GET").upper() and normalize_route(str(endpoint["route"])) == normalize_route(str(call["route"]))]
        if len(candidates) == 1:
            mappings.append({"call": call, "endpoint": candidates[0], "evidence": [call["evidence"], candidates[0]["evidence"]]})
    return mappings
