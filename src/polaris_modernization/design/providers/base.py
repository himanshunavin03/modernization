"""Provider boundary and the mandatory no-design implementation."""
from __future__ import annotations

from typing import Protocol

from ..models import DesignMode, DesignSpecification, DesignStatus


class DesignProvider(Protocol):
    provider_type: str

    def analyze(self, source_reference: str | None, mode: DesignMode) -> DesignSpecification: ...


class NoDesignProvider:
    provider_type = "NO_DESIGN"

    def analyze(self, source_reference: str | None = None, mode: DesignMode = DesignMode.NONE) -> DesignSpecification:
        return DesignSpecification(provider="NO_DESIGN", mode=DesignMode.NONE, status=DesignStatus.NOT_PROVIDED)
