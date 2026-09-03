"""Real Figma REST adapter with deterministic fixture and graceful failure modes."""
from __future__ import annotations

import json
import os
import re
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, quote, urlencode, urlparse
from urllib.request import Request, urlopen

from ..fixture import FIGMA_DASHBOARD_FIXTURE
from ..models import DesignErrorCode, DesignMode, DesignSpecification, DesignStatus, FigmaReference
from ..normalizer import normalize_figma_response


def parse_figma_url(value: str | None) -> FigmaReference:
    if not value:
        raise ValueError(DesignErrorCode.INVALID_URL.value)
    parsed = urlparse(value)
    host = (parsed.hostname or "").lower()
    parts = [part for part in parsed.path.split("/") if part]
    if host not in {"figma.com", "www.figma.com"} or len(parts) < 2 or parts[0] not in {"design", "file", "proto", "board"}:
        raise ValueError(DesignErrorCode.INVALID_URL.value)
    file_key = parts[1]
    if not re.fullmatch(r"[A-Za-z0-9_-]+", file_key):
        raise ValueError(DesignErrorCode.INVALID_URL.value)
    node_id = parse_qs(parsed.query).get("node-id", [None])[0]
    if node_id and not re.fullmatch(r"[A-Za-z0-9:_-]+", node_id):
        raise ValueError(DesignErrorCode.INVALID_URL.value)
    normalized = f"figma://file/{file_key}"
    if node_id:
        normalized += "?" + urlencode({"node-id": node_id})
    return FigmaReference(file_key=file_key, node_id=node_id, normalized_reference=normalized)


def _failure(mode: DesignMode, source: str | None, status: DesignStatus, code: DesignErrorCode, message: str) -> DesignSpecification:
    return DesignSpecification(provider="FIGMA", mode=mode, status=status, source_reference=source, error_code=code, unresolved_items=[message])


class FigmaDesignProvider:
    provider_type = "FIGMA"

    def __init__(self, opener=urlopen, token: str | None = None):
        self._opener = opener
        self._token = token

    def analyze(self, source_reference: str | None, mode: DesignMode) -> DesignSpecification:
        if mode == DesignMode.FIXTURE:
            reference = FigmaReference(file_key="FIXTURE_DASHBOARD", node_id="1:1", normalized_reference="figma://file/FIXTURE_DASHBOARD?node-id=1%3A1")
            return normalize_figma_response(FIGMA_DASHBOARD_FIXTURE, reference, mode)
        try:
            reference = parse_figma_url(source_reference)
        except ValueError:
            return _failure(mode, None, DesignStatus.INVALID, DesignErrorCode.INVALID_URL, "The supplied Figma URL is invalid.")
        token = self._token if self._token is not None else os.getenv("FIGMA_ACCESS_TOKEN")
        if not token:
            return _failure(mode, reference.normalized_reference, DesignStatus.UNAVAILABLE, DesignErrorCode.AUTH_NOT_CONFIGURED, "Figma access is not configured; planning continued without design input.")
        endpoint = f"https://api.figma.com/v1/files/{quote(reference.file_key)}"
        if reference.node_id:
            endpoint += "?" + urlencode({"ids": reference.node_id})
        request = Request(endpoint, headers={"X-Figma-Token": token, "Accept": "application/json"})
        try:
            with self._opener(request, timeout=20) as response:
                payload = json.loads(response.read().decode("utf-8"))
            return normalize_figma_response(payload, reference, mode)
        except HTTPError as error:
            if error.code in {401, 403}:
                return _failure(mode, reference.normalized_reference, DesignStatus.UNAUTHORIZED, DesignErrorCode.ACCESS_DENIED, "Figma denied access to the requested document.")
            if error.code == 404:
                return _failure(mode, reference.normalized_reference, DesignStatus.UNAVAILABLE, DesignErrorCode.DOCUMENT_UNAVAILABLE, "The requested Figma document is unavailable.")
            return _failure(mode, reference.normalized_reference, DesignStatus.UNAVAILABLE, DesignErrorCode.NETWORK_ERROR, f"Figma returned HTTP status {error.code}.")
        except (URLError, TimeoutError, OSError):
            return _failure(mode, reference.normalized_reference, DesignStatus.UNAVAILABLE, DesignErrorCode.NETWORK_ERROR, "The Figma request could not be completed.")
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError, TypeError):
            return _failure(mode, reference.normalized_reference, DesignStatus.INVALID, DesignErrorCode.RESPONSE_INVALID, "The Figma response was not a valid design document.")
