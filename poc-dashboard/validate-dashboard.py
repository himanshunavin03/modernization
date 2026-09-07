#!/usr/bin/env python3
"""Validate presentation links, provenance, isolation-sensitive content, and outputs."""

from __future__ import annotations

import json
import importlib.util
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

DASHBOARD = Path(__file__).resolve().parent
GENERATED = DASHBOARD / "generated"

spec = importlib.util.spec_from_file_location("build_dashboard", DASHBOARD / "build-dashboard.py")
if spec is None or spec.loader is None:
    raise RuntimeError("Unable to load the presentation generator")
build_dashboard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build_dashboard)


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.references: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag in {"a", "link"} and values.get("href"):
            self.references.append((tag, values["href"] or ""))
        if tag in {"script", "img"} and values.get("src"):
            self.references.append((tag, values["src"] or ""))


def check_html_links(path: Path) -> list[str]:
    parser = LinkParser()
    parser.feed(path.read_text(encoding="utf-8"))
    broken: list[str] = []
    for _, reference in parser.references:
        if reference.startswith(("#", "http://", "https://", "mailto:")):
            continue
        local = (path.parent / reference.split("#", 1)[0]).resolve()
        if not local.exists():
            broken.append(f"{path.relative_to(DASHBOARD)} -> {reference}")
    return broken


def main() -> int:
    required = [
        DASHBOARD / "index.html",
        DASHBOARD / "styles.css",
        DASHBOARD / "app.js",
        DASHBOARD / "README.md",
        GENERATED / "dashboard-data.json",
        GENERATED / "feature-specification.html",
        GENERATED / "technical-tasks.html",
        GENERATED / "application-understanding.html",
        GENERATED / "playwright-coverage.html",
    ]
    missing = [str(path.relative_to(DASHBOARD)) for path in required if not path.is_file()]
    if missing:
        print("MISSING_OUTPUTS=" + ",".join(missing))
        return 1

    broken: list[str] = []
    for html_file in [DASHBOARD / "index.html", *GENERATED.glob("*.html")]:
        broken.extend(check_html_links(html_file))

    app_js = (DASHBOARD / "app.js").read_text(encoding="utf-8")
    expected_links = {
        "LEGACY_APP_LINK": "http://localhost:5000/",
        "MODERN_APP_LINK": "http://localhost:4200/",
        "MODERN_DOCTORS_LINK": "http://localhost:4200/doctors",
        "MODERN_NEW_DOCTOR_LINK": "http://localhost:4200/doctors/new",
        "FEATURE_SPEC_LINK": "./generated/feature-specification.html",
        "TECHNICAL_TASKS_LINK": "./generated/technical-tasks.html",
        "APPLICATION_UNDERSTANDING_LINK": "./generated/application-understanding.html",
        "PLAYWRIGHT_COVERAGE_LINK": "./generated/playwright-coverage.html",
    }
    link_results = {label: "PASS" if target in app_js else "FAIL" for label, target in expected_links.items()}

    data = json.loads((GENERATED / "dashboard-data.json").read_text(encoding="utf-8"))
    current = build_dashboard.build_dashboard_data()
    stale = 0 if data == current else 1
    required_metrics = {
        "sourceFiles": 2384,
        "graphNodes": 71936,
        "relationships": 113562,
        "backendEndpoints": 58,
        "functionalRequirements": 21,
        "stories": 21,
        "acceptanceCriteria": 41,
        "technicalTasks": 16,
    }
    unsupported = sum(data.get("metrics", {}).get(key) != value for key, value in required_metrics.items())

    rendered_files = [DASHBOARD / "index.html", DASHBOARD / "styles.css", DASHBOARD / "app.js", *GENERATED.glob("*")]
    rendered_text = "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in rendered_files)
    local_path_patterns = [r"C:\\Users\\", r"C:/Users/", r"\\Users\\[A-Za-z0-9._-]+", r"/home/[A-Za-z0-9._-]+"]
    local_paths = sum(len(re.findall(pattern, rendered_text, flags=re.IGNORECASE)) for pattern in local_path_patterns)
    secret_patterns = [
        r"(?i)(password|secret|access[_-]?token)\s*[:=]\s*['\"][^'\"]+",
        r"(?i)bearer\s+[a-z0-9._-]{16,}",
        r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
    ]
    secret_hits = sum(len(re.findall(pattern, rendered_text)) for pattern in secret_patterns)

    report = DASHBOARD.parent / "modernized/apps/healthclinic-web-e2e/playwright-report/index.html"
    print(f"BROKEN_INTERNAL_LINKS={len(broken)}")
    for item in broken:
        print(f"BROKEN={item}")
    for label, result in link_results.items():
        print(f"{label}={result}")
    print(f"PLAYWRIGHT_REPORT_LINK={'PASS' if report.is_file() else 'NOT_CURRENTLY_GENERATED'}")
    print(f"STALE_PRESENTATION_DATA={stale}")
    print(f"UNSUPPORTED_PRESENTATION_CLAIMS={unsupported}")
    print(f"LOCAL_USER_PATHS_IN_PRESENTATION={local_paths}")
    print(f"SECRET_SCAN={'PASS' if secret_hits == 0 else 'FAIL'}")
    return 0 if not broken and all(result == "PASS" for result in link_results.values()) and not stale and not unsupported and not local_paths and not secret_hits else 1


if __name__ == "__main__":
    sys.exit(main())
