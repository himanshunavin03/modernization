#!/usr/bin/env python3
"""Build presentation-only pages from approved Polaris artifacts.

This script reads existing artifacts and writes only beneath poc-dashboard/generated.
It does not regenerate or modify modernization artifacts.
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path
from typing import Any


DASHBOARD_DIR = Path(__file__).resolve().parent
REPOSITORY_ROOT = DASHBOARD_DIR.parent
GENERATED_DIR = DASHBOARD_DIR / "generated"

SOURCES = {
    "knowledge_graph": "artifacts/knowledge-graph/latest/knowledge-graph.json",
    "facts": "artifacts/knowledge-graph/latest/facts.json",
    "source_inventory": "artifacts/knowledge-graph/latest/source-inventory.json",
    "framework_detection": "artifacts/knowledge-graph/latest/framework-detection.json",
    "application_understanding_json": "artifacts/application-understanding/latest/application-understanding.json",
    "application_understanding_markdown": "artifacts/application-understanding/latest/application-understanding.md",
    "feature_specification_json": "artifacts/feature-specifications/latest/feature-doctor-directory-management.json",
    "feature_specification_markdown": "artifacts/feature-specifications/latest/feature-doctor-directory-management.md",
    "technical_tasks_json": "artifacts/technical-tasks/features/feature-doctor-directory-management/latest/technical-tasks.json",
    "technical_tasks_markdown": "artifacts/technical-tasks/features/feature-doctor-directory-management/latest/technical-tasks.md",
    "architecture": "artifacts/architecture/latest/architecture-selection.json",
    "playwright_coverage": "docs/validation/doctor-playwright-coverage.json",
}


def source_path(name: str) -> Path:
    path = REPOSITORY_ROOT / SOURCES[name]
    if not path.is_file():
        raise FileNotFoundError(f"Required approved artifact is unavailable: {SOURCES[name]}")
    return path


def read_json(name: str) -> dict[str, Any]:
    return json.loads(source_path(name).read_text(encoding="utf-8"))


def read_text(name: str) -> str:
    return source_path(name).read_text(encoding="utf-8")


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "section"


def inline_markdown(value: str) -> str:
    escaped = html.escape(value.strip())
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", escaped)
    return escaped


def markdown_to_html(markdown: str) -> tuple[str, list[tuple[int, str, str]]]:
    """Render the approved Markdown with a deliberately small offline renderer."""
    lines = markdown.replace("\r\n", "\n").split("\n")
    rendered: list[str] = []
    headings: list[tuple[int, str, str]] = []
    paragraph: list[str] = []
    list_type: str | None = None
    in_code = False
    code_lines: list[str] = []
    used_ids: dict[str, int] = {}
    index = 0

    def close_paragraph() -> None:
        if paragraph:
            rendered.append(f"<p>{inline_markdown(' '.join(paragraph))}</p>")
            paragraph.clear()

    def close_list() -> None:
        nonlocal list_type
        if list_type:
            rendered.append(f"</{list_type}>")
            list_type = None

    def heading_id(title: str) -> str:
        base = slugify(re.sub(r"[`*_]", "", title))
        count = used_ids.get(base, 0)
        used_ids[base] = count + 1
        return base if count == 0 else f"{base}-{count + 1}"

    while index < len(lines):
        line = lines[index].rstrip()
        if line.startswith("```"):
            close_paragraph()
            close_list()
            if in_code:
                rendered.append(f"<pre><code>{html.escape(chr(10).join(code_lines))}</code></pre>")
                code_lines.clear()
                in_code = False
            else:
                in_code = True
            index += 1
            continue
        if in_code:
            code_lines.append(line)
            index += 1
            continue
        heading_match = re.match(r"^(#{1,4})\s+(.+)$", line)
        if heading_match:
            close_paragraph()
            close_list()
            level = min(len(heading_match.group(1)), 4)
            title = heading_match.group(2).strip()
            identifier = heading_id(title)
            headings.append((level, re.sub(r"[`*_]", "", title), identifier))
            rendered.append(f'<h{level} id="{identifier}">{inline_markdown(title)}</h{level}>')
            index += 1
            continue
        if line.startswith(">"):
            close_paragraph()
            close_list()
            rendered.append(f"<blockquote>{inline_markdown(line.lstrip('> '))}</blockquote>")
            index += 1
            continue
        if line.startswith("|") and index + 1 < len(lines) and re.match(r"^\|?[\s:|-]+\|", lines[index + 1]):
            close_paragraph()
            close_list()
            headers = [cell.strip() for cell in line.strip("|").split("|")]
            index += 2
            rows: list[list[str]] = []
            while index < len(lines) and lines[index].lstrip().startswith("|"):
                rows.append([cell.strip() for cell in lines[index].strip("|").split("|")])
                index += 1
            table = ["<div class=\"table-shell\"><table><thead><tr>"]
            table.extend(f"<th>{inline_markdown(cell)}</th>" for cell in headers)
            table.append("</tr></thead><tbody>")
            for row in rows:
                table.append("<tr>")
                table.extend(f"<td>{inline_markdown(cell)}</td>" for cell in row)
                table.append("</tr>")
            table.append("</tbody></table></div>")
            rendered.append("".join(table))
            continue
        list_match = re.match(r"^\s*([-*]|\d+\.)\s+(.+)$", line)
        if list_match:
            close_paragraph()
            wanted = "ol" if list_match.group(1)[0].isdigit() else "ul"
            if list_type != wanted:
                close_list()
                list_type = wanted
                rendered.append(f"<{wanted}>")
            rendered.append(f"<li>{inline_markdown(list_match.group(2))}</li>")
            index += 1
            continue
        if not line.strip():
            close_paragraph()
            close_list()
        elif re.fullmatch(r"[-*_]{3,}", line.strip()):
            close_paragraph()
            close_list()
            rendered.append("<hr>")
        else:
            paragraph.append(line.strip())
        index += 1
    close_paragraph()
    close_list()
    if in_code:
        rendered.append(f"<pre><code>{html.escape(chr(10).join(code_lines))}</code></pre>")
    return "\n".join(rendered), headings


def page_shell(title: str, eyebrow: str, intro: str, body: str, nav: str = "") -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="dark">
  <title>{html.escape(title)} · Application Modernization POC</title>
  <link rel="stylesheet" href="../styles.css">
</head>
<body class="artifact-page">
  <a class="skip-link" href="#artifact-content">Skip to content</a>
  <header class="artifact-topbar">
    <a class="brand" href="../index.html" aria-label="Back to POC dashboard"><span class="brand-mark">P</span><span>POLARIS <small>MODERNIZATION</small></span></a>
    <a class="button button-quiet" href="../index.html">← Back to POC Dashboard</a>
  </header>
  <main id="artifact-content">
    <section class="artifact-hero">
      <p class="eyebrow">{html.escape(eyebrow)}</p>
      <h1>{html.escape(title)}</h1>
      <p>{html.escape(intro)}</p>
    </section>
    <div class="artifact-layout">
      {nav}
      <article class="artifact-document">{body}</article>
    </div>
  </main>
  <footer class="site-footer"><p>Polaris Application Modernization POC</p><a href="../index.html">Return to presentation</a></footer>
</body>
</html>
"""


def section_nav(headings: list[tuple[int, str, str]], maximum: int = 12) -> str:
    relevant = [(level, title, identifier) for level, title, identifier in headings if level == 2][:maximum]
    if not relevant:
        return ""
    links = "".join(f'<a href="#{identifier}">{html.escape(title)}</a>' for _, title, identifier in relevant)
    return f'<aside class="artifact-nav" aria-label="Page sections"><strong>On this page</strong>{links}</aside>'


def build_dashboard_data() -> dict[str, Any]:
    graph = read_json("knowledge_graph")
    facts = read_json("facts")
    inventory = read_json("source_inventory")
    frameworks = read_json("framework_detection")
    understanding = read_json("application_understanding_json")
    feature = read_json("feature_specification_json")
    tasks = read_json("technical_tasks_json")
    coverage = read_json("playwright_coverage")

    framework_names = list(dict.fromkeys(item["framework"] for item in frameworks.get("frameworks", [])))
    metrics = {
        "sourceFiles": len(inventory.get("files", [])),
        "facts": len(facts.get("facts", [])),
        "graphNodes": len(graph.get("nodes", [])),
        "relationships": len(graph.get("edges", [])),
        "backendEndpoints": understanding["api_mapping_summary"]["backend_endpoints"],
        "provenApiMappings": understanding["api_mapping_summary"]["proven"],
        "functionalRequirements": len(feature.get("functional_requirements", [])),
        "stories": len(feature.get("stories", [])),
        "acceptanceCriteria": len(feature.get("acceptance_criteria", [])),
        "apiContracts": len(feature.get("capability_api_contracts", [])),
        "technicalTasks": len(tasks.get("tasks", [])),
    }
    return {
        "presentation": {
            "title": "Application Modernization POC",
            "story": ["UNDERSTAND", "MODEL", "PLAN", "MODERNIZE", "VALIDATE"],
        },
        "metrics": metrics,
        "referenceApplication": {
            "classification": understanding.get("primary_application_type"),
            "frameworks": framework_names,
        },
        "applicationUnderstanding": {
            "modules": len(understanding.get("business_modules", [])),
            "capabilities": len(understanding.get("business_capabilities", [])),
            "workflows": len(understanding.get("user_workflows", [])),
            "domainConcepts": len(understanding.get("domain_concepts", [])),
            "uiSurfaces": len(understanding.get("ui_surfaces", [])),
        },
        "angularCapabilities": [
            "Angular 22", "Standalone Components", "Signals", "computed()", "OnPush",
            "Lazy Feature Routing", "Modern @if / @for", "Strict TypeScript",
            "Typed Reactive Forms", "RxJS + HttpClient",
        ],
        "playwright": coverage.get("summary", {}),
        "sources": SOURCES,
    }


def build_feature_page() -> None:
    content, headings = markdown_to_html(read_text("feature_specification_markdown"))
    page = page_shell(
        "Doctor Directory Management",
        "Example Modernized Feature · Approved Specification",
        "An evidence-backed delivery contract connecting functional requirements, stories, acceptance criteria, APIs, and readiness expectations.",
        content,
        section_nav(headings),
    )
    (GENERATED_DIR / "feature-specification.html").write_text(page, encoding="utf-8", newline="\n")


def build_tasks_page() -> None:
    content, headings = markdown_to_html(read_text("technical_tasks_markdown"))
    flow = """<div class="artifact-flow" aria-label="Delivery traceability flow">
      <span>Acceptance Criteria</span><b aria-hidden="true">→</b><span>Technical Tasks</span><b aria-hidden="true">→</b><span>Implementation</span>
    </div>"""
    page = page_shell(
        "Technical Delivery Plan",
        "Architecture-Guided Modernization",
        "Sixteen sequenced tasks translate approved behavior and architecture into an auditable Angular delivery plan.",
        flow + content,
        section_nav(headings, maximum=4),
    )
    (GENERATED_DIR / "technical-tasks.html").write_text(page, encoding="utf-8", newline="\n")


def item_cards(items: list[dict[str, Any]], limit: int | None = None) -> str:
    cards = []
    for item in items[:limit]:
        name = html.escape(str(item.get("name") or item.get("title") or "Untitled"))
        description = html.escape(str(item.get("description") or "Evidence-backed application concept."))
        cards.append(f'<article class="insight-card"><h3>{name}</h3><p>{description}</p></article>')
    return '<div class="insight-grid">' + "".join(cards) + "</div>"


def build_understanding_page() -> None:
    data = read_json("application_understanding_json")
    metrics = data.get("kg_metrics", {})
    api = data.get("api_mapping_summary", {})
    body = f"""
      <section><h2 id="purpose">Purpose</h2><p>{html.escape(str(data.get('application_purpose', 'Application purpose derived from approved evidence.')))}</p>
      <div class="mini-metrics"><div><strong>{metrics.get('total_kg_nodes', 0):,}</strong><span>Graph nodes</span></div><div><strong>{metrics.get('total_kg_relationships', 0):,}</strong><span>Relationships</span></div><div><strong>{api.get('proven', 0)}</strong><span>Proven API mappings</span></div></div></section>
      <section><h2 id="modules">Business Modules</h2>{item_cards(data.get('business_modules', []))}</section>
      <section><h2 id="capabilities">Capabilities</h2>{item_cards(data.get('business_capabilities', []))}</section>
      <section><h2 id="workflows">Representative Workflows</h2>{item_cards(data.get('user_workflows', []), 12)}</section>
      <section><h2 id="concepts">Domain Concepts</h2>{item_cards(data.get('domain_concepts', []))}</section>
      <section><h2 id="dependencies">Cross-Layer Dependencies</h2>{item_cards(data.get('dependencies', []))}</section>
      <section><h2 id="api">API Relationships</h2><p>The approved understanding connects {api.get('frontend_api_calls', 0)} frontend API calls with {api.get('proven', 0)} proven mappings across {api.get('backend_endpoints', 0)} discovered backend endpoints.</p></section>
    """
    nav = '<aside class="artifact-nav" aria-label="Page sections"><strong>On this page</strong><a href="#purpose">Purpose</a><a href="#modules">Modules</a><a href="#capabilities">Capabilities</a><a href="#workflows">Workflows</a><a href="#concepts">Domain Concepts</a><a href="#dependencies">Dependencies</a><a href="#api">API Relationships</a></aside>'
    page = page_shell(
        "Application Understanding",
        "Knowledge Graph → Business / Functional View",
        "Structured source evidence is synthesized into modules, capabilities, workflows, domain concepts, and cross-layer relationships.",
        body,
        nav,
    )
    (GENERATED_DIR / "application-understanding.html").write_text(page, encoding="utf-8", newline="\n")


def build_coverage_page() -> None:
    data = read_json("playwright_coverage")
    summary = data["summary"]
    rows = []
    for item in data.get("coverage", []):
        status = str(item.get("status", "EXPLICIT")).lower().replace("_", "-")
        rows.append(
            "<tr>"
            f"<td><code>{html.escape(str(item.get('ac_id', '')))}</code></td>"
            f"<td>{html.escape(str(item.get('playwright_test', '')))}</td>"
            f"<td><span class=\"status status-{status}\">{html.escape(str(item.get('status', '')))}</span></td>"
            f"<td>{html.escape(str(item.get('backend', '')))}</td>"
            "</tr>"
        )
    body = f"""
      <div class="mini-metrics coverage-metrics">
        <div><strong>{summary['ac_total']}</strong><span>Total acceptance criteria</span></div>
        <div><strong>{summary['ac_with_test_traceability']}</strong><span>Traceable to scenarios</span></div>
        <div><strong>{summary['ac_passed']}</strong><span>Passed</span></div>
        <div><strong>{summary['ac_failed']}</strong><span>Failed</span></div>
        <div><strong>{summary['ac_blocked_by_patient_feature']}</strong><span>Explicit dependency status</span></div>
      </div>
      <section><h2 id="coverage-map">Acceptance Criteria → Browser Scenarios</h2><p>Every approved criterion has an explicit automated-validation disposition.</p>
      <div class="table-shell coverage-table"><table><thead><tr><th>Acceptance Criterion</th><th>Playwright Scenario</th><th>Status</th><th>Boundary</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div></section>
    """
    nav = '<aside class="artifact-nav" aria-label="Page sections"><strong>Validation view</strong><a href="#coverage-map">AC coverage map</a><a href="../index.html#validation">Validation architecture</a></aside>'
    page = page_shell(
        "Playwright Validation Traceability",
        "Requirements → Real Browser Evidence",
        "Acceptance criteria are traceable to named Playwright scenarios and explicit validation outcomes.",
        body,
        nav,
    )
    (GENERATED_DIR / "playwright-coverage.html").write_text(page, encoding="utf-8", newline="\n")


def main() -> None:
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    data = build_dashboard_data()
    (GENERATED_DIR / "dashboard-data.json").write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    build_feature_page()
    build_tasks_page()
    build_understanding_page()
    build_coverage_page()
    print("DASHBOARD_DATA_GENERATED=YES")
    print("FEATURE_SPEC_HTML_GENERATED=YES")
    print("TECHNICAL_TASKS_HTML_GENERATED=YES")
    print("APPLICATION_UNDERSTANDING_HTML_GENERATED=YES")
    print("PLAYWRIGHT_COVERAGE_HTML_GENERATED=YES")


if __name__ == "__main__":
    main()
