"""Read-only, project-agnostic implementation status classification."""
from __future__ import annotations

from pathlib import Path
import re


EFFECT_PATTERNS = {
    "ACTION_VISIBILITY": (r"@if\s*\(|\*ngIf|\[hidden\]",),
    "COLLECTION_APPEND": (r"\.\.\.[A-Za-z]|\.concat\(",),
    "COLLECTION_REMOVE": (r"\.delete\s*[<(]|\.filter\s*\(|\.splice\s*\(",),
    "CONFIRMATION": (r"confirm|dialog|modal",),
    "DESTINATION_STATE": (r"paramMap|snapshot\.param|input\.required",),
    "FIXED_ORDER": (r"orderBy|sort\s*\(|fixed.order",),
    "MEDIA_BINDING": (r"FileReader|readAsDataURL|type=[\"']file",),
    "MEDIA_RENDER": (r"\[src\]|<img",),
    "NAVIGATION": (r"routerLink|\.navigate",),
    "RECORD_CREATE": (r"\.post\s*[<(]",),
    "RECORD_UPDATE": (r"\.put\s*[<(]",),
    "RENDER": (r"@for\s*\(|\*ngFor",),
    "SELECTION": (r"checkbox|selectedIds|selected\.update|selection",),
    "SYSTEM_CONTEXT": (r"tenantContext|TenantContext|withTenant",),
    "VALIDATION": (r"Validators\.|required|formControl|formGroup|ngModel",),
    "VALIDATION_GATE": (r"\.invalid|\.valid|formControl|formGroup|ngForm",),
}


def _implementation_files(repository_root: Path, implementation_paths: list[str]) -> list[Path]:
    paths = []
    for relative in implementation_paths:
        path = repository_root / "modernized" / relative
        if path.is_file() and path.suffix.lower() in {".ts", ".html", ".css", ".json", ".mjs"}:
            paths.append(path)
    return paths


def classify_tasks(repository_root: Path, implementation_paths: list[str], requirements: list[dict], tasks: list[dict]) -> list[dict]:
    files = _implementation_files(repository_root, implementation_paths)
    texts = {str(path.relative_to(repository_root)): path.read_text(encoding="utf-8", errors="replace") for path in files}
    combined = "\n".join(texts.values())

    def matches(patterns: tuple[str, ...]) -> list[str]:
        return [path for path, text in texts.items() if any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)]

    requirement_status: dict[str, tuple[str, list[str]]] = {}
    for requirement in requirements:
        capabilities = list(dict.fromkeys(
            semantic.get("effect_kind") for semantic in requirement.get("interaction_semantics", []) if semantic.get("effect_kind")
        ))
        checks: list[tuple[str, list[str]]] = [(kind, matches(EFFECT_PATTERNS.get(kind, (re.escape(kind),)))) for kind in capabilities]
        for dependency in requirement.get("api_dependencies", []):
            method, _, route = dependency.partition(" ")
            route_pattern = re.escape(route).replace(re.escape("{id}"), r"\$\{[^}]+\}|[^'\"`]+")
            checks.append((dependency, matches((rf"\.{method.lower()}\s*[<(]", route_pattern))))
        passed = [name for name, evidence in checks if evidence]
        evidence_paths = list(dict.fromkeys(path for _, evidence in checks for path in evidence))
        if checks and len(passed) == len(checks):
            status = "IMPLEMENTED"
        elif passed:
            status = "PARTIALLY_IMPLEMENTED"
        else:
            status = "NOT_IMPLEMENTED"
        requirement_status[requirement["id"]] = (status, evidence_paths)

    category_patterns = {
        "SCAFFOLD": (r"@angular/core", r"project\.json"),
        "CONFIGURATION": (r"scope:", r"sourceRoot"),
        "DESIGN_SYSTEM": (r"focus-visible|aria-|visually-hidden",),
        "API": (r"HttpClient",),
        "GATEWAY": (r"gateway",),
        "BFF": (r"backend.for.frontend|\bbff\b",),
        "INTEGRATION": (r"HttpClient",),
        "ROUTING": (r"Routes|loadChildren|routerLink",),
        "ACCESSIBILITY": (r"aria-|focus-visible|role=",),
        "OBSERVABILITY": (r"correlation|telemetry|logger",),
        "TEST": (r"describe\s*\(|test\s*\(",),
    }
    classified = []
    for task in tasks:
        refs = task["functional_requirement_refs"]
        evidence = list(dict.fromkeys(path for ref in refs for path in requirement_status.get(ref, ("NOT_IMPLEMENTED", []))[1]))
        statuses = [requirement_status[ref][0] for ref in refs if ref in requirement_status]
        category_evidence = matches(category_patterns.get(task["category"], (re.escape(task["category"]),)))
        if task["category"] in {"GATEWAY", "BFF"}:
            evidence = category_evidence
            status = "IMPLEMENTED" if evidence else "NOT_IMPLEMENTED"
        elif statuses:
            status = "IMPLEMENTED" if all(item == "IMPLEMENTED" for item in statuses) else (
                "NOT_IMPLEMENTED" if all(item == "NOT_IMPLEMENTED" for item in statuses) else "PARTIALLY_IMPLEMENTED"
            )
        else:
            evidence = category_evidence
            status = "IMPLEMENTED" if evidence else "NOT_IMPLEMENTED"
        classified.append({
            **task,
            "implementation_status": status,
            "implementation_evidence": evidence,
            "implementation_assessment": (
                "Existing Angular files contain evidence for every linked behavior." if status == "IMPLEMENTED" else
                "Existing Angular files contain evidence for part, but not all, of the linked behavior." if status == "PARTIALLY_IMPLEMENTED" else
                "No implementation evidence was found for the complete task contract."
            ),
        })
    return classified
