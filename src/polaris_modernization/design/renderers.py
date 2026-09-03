"""Lightweight design showcase generated from DesignSpecification."""
from __future__ import annotations

from html import escape


def render_design_markdown(design: dict) -> str:
    def items(name: str) -> list[str]:
        return [f"- `{item.get('id', item.get('name', 'item'))}` {item.get('name', item.get('value', ''))}" for item in design[name]] or ["- None."]
    requirement_links = [f"- `{item['design_ref']}` {item['relationship']} `{item['requirement_ref']}`" for item in design["requirement_links"]] or ["- None."]
    return "\n".join([
        "# Normalized Design Input", "", f"- Provider: `{design['provider']}`", f"- Design mode: `{design['mode']}`",
        f"- Status: `{design['status']}`", f"- Document: {design['document_name'] or 'Not available'}", "",
        "## Screens", "", *items("screens"), "", "## Components", "", *items("components"), "",
        "## Controls", "", *items("controls"), "", "## Responsive Hints", "", *items("responsive_hints"), "",
        "## Requirement Links", "", *requirement_links, "",
        "This normalized input controls presentation only. Approved requirements control functionality and locked architecture controls technical structure.", "",
    ])


def render_design_html(design: dict) -> str:
    cards = "".join(f"<article><small>{escape(item['kind'])}</small><h3>{escape(item['name'])}</h3><code>{escape(item['design_ref'])}</code></article>" for item in [*design["screens"], *design["components"], *design["controls"]])
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Normalized Design Input</title><style>
:root{{--ink:#172d32;--sea:#126b67;--sand:#f5eddd;--paper:#fffdf8;--coral:#d95f3b}}*{{box-sizing:border-box}}body{{margin:0;background:var(--sand);color:var(--ink);font:16px/1.55 "Trebuchet MS",sans-serif}}header{{padding:6rem max(5vw,2rem);color:white;background:linear-gradient(120deg,#12393d,#14786e)}}h1,h2,h3{{font-family:Georgia,serif}}h1{{font-size:clamp(3rem,8vw,6rem);margin:.15em 0}}main{{width:min(1100px,90vw);margin:auto;padding:4rem 0}}.status{{display:flex;gap:.7rem;flex-wrap:wrap}}.status span{{border:1px solid #ffffff66;padding:.45rem .7rem}}.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem}}article{{background:var(--paper);padding:1.4rem;border-top:5px solid var(--coral);overflow-wrap:anywhere}}code{{font-size:.75rem;color:var(--sea)}}@media(max-width:760px){{.grid{{grid-template-columns:1fr}}}}</style></head><body>
<header><p>OPTIONAL DESIGN ADAPTER</p><h1>{escape(design['document_name'] or 'No design supplied')}</h1><div class="status"><span>PROVIDER {escape(design['provider'])}</span><span>MODE {escape(design['mode'])}</span><span>STATUS {escape(design['status'])}</span></div></header>
<main><h2>Implementation-oriented design inventory</h2><p>Presentation guidance only. Requirements and locked architecture retain priority.</p><div class="grid">{cards or '<article><h3>No design inventory</h3><p>Technical planning continues using implementation defaults.</p></article>'}</div></main></body></html>'''
