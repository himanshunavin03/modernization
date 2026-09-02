"""Human renderers driven by the consolidated architecture contract."""
from __future__ import annotations

from collections import defaultdict
from html import escape

from .catalog import ADR_GROUPS


def _decision_map(contract: dict) -> dict[str, dict]:
    return {item["technology"]: item for item in contract["selection"]["decisions"]}


def _bullet(items: list[str]) -> list[str]:
    return [f"- {item}" for item in items] or ["- None."]


def render_architecture_markdown(contract: dict) -> str:
    selection = contract["selection"]
    decisions = selection["decisions"]
    by_technology = _decision_map(contract)
    selected = [item for item in decisions if item["status"] in {"SELECTED", "RECOMMENDED"}]
    alternatives = [item for item in decisions if item["status"] in {"EVALUATED_ALTERNATIVE", "NOT_SELECTED", "NOT_APPLICABLE"}]
    clarifications = [item for item in decisions if item["status"] == "REQUIRES_CLARIFICATION"]
    api_lines = [f"- `{api['method']} {api['endpoint']}`: {api['response_description']}" for api in selection["existing_api_contracts"]]
    lines = [
        "# Target Architecture", "", "## 1. Executive Architecture Summary", "",
        "The selected target is an Angular 22 enterprise frontend in an Nx workspace, using standalone domain boundaries, Signals with RxJS at asynchronous edges, zoneless change detection, client-side rendering, and a provider-neutral API Gateway and BFF topology. Existing business API contracts remain unchanged behind the target integration layers.", "",
        "## 2. Selected Target Architecture", "",
        *[f"- **{item['technology']}:** {item['decision']}" for item in selected], "",
        "## 3. Architecture Diagram", "", "```text",
        "Browser", "  |", "Angular 22 / Nx / Standalone Features", "  |", "Provider-Neutral API Gateway (target)", "  |", "Backend for Frontend (target; endpoints not yet designed)", "  |", "Existing Business APIs (contracts preserved)", "```", "",
        "## 4. Angular 22 Architecture", "", by_technology["Standalone Components"]["rationale"], "", by_technology["Modern Template Control Flow"]["decision"], "",
        "## 5. Workspace / Nx Strategy", "", by_technology["Nx Monorepo"]["rationale"], "", "Angular CLI single application remains a valid alternative for smaller deployments.", "",
        "## 6. Reactivity Strategy", "", f"{by_technology['Angular Signals']['decision']} {by_technology['RxJS']['decision']} {by_technology['Signals and RxJS Interoperability']['decision']}", "",
        "## 7. Forms Strategy", "", f"**Signal Forms ({by_technology['Signal Forms']['status']}):** {by_technology['Signal Forms']['rationale']}", "", f"**Reactive Forms ({by_technology['Reactive Forms']['status']}):** {by_technology['Reactive Forms']['rationale']}", "",
        "## 8. State Strategy", "", by_technology["Feature Signal State"]["rationale"], "", f"NgRx is `{by_technology['NgRx']['status']}` because {by_technology['NgRx']['rejection_reason'].lower()}", "",
        "## 9. Routing Strategy", "", f"{by_technology['Angular Router']['decision']} {by_technology['Lazy Feature Routes']['decision']} {by_technology['Functional Guards']['decision']}", "",
        "## 10. Rendering Strategy", "", f"CSR is `{by_technology['Client-Side Rendering']['status']}`. SSR is `{by_technology['Server-Side Rendering']['status']}` and hydration is `{by_technology['Hydration']['status']}` because no approved public SEO or server-rendering requirement exists.", "",
        "## 11. Gateway / BFF Integration", "", by_technology["Provider-Neutral API Gateway"]["rationale"], "", by_technology["Backend for Frontend"]["rationale"], "", "No gateway product, BFF endpoint, response shape, or backend replacement is defined by this architecture stage.", "", "**Preserved Existing API Contracts**", "", *api_lines, "",
        "## 12. Security", "", f"{by_technology['Tenant and Organization Context Propagation']['decision']} {by_technology['Browser Security Controls']['decision']}", "", "The identity provider and browser session/token pattern require customer clarification.", "",
        "## 13. Performance", "", f"{by_technology['Lazy Loading and Code Splitting']['decision']} {by_technology['@defer']['decision']} No performance metric is asserted before measurement.", "",
        "## 14. Testing", "", f"{by_technology['Unit and Component Testing']['decision']} {by_technology['Playwright']['decision']} Accessibility combines automated and manual validation; formal compliance is not claimed before verification.", "",
        "## 15. Observability", "", by_technology["Vendor-Neutral Correlated Telemetry"]["decision"], "", "No telemetry vendor is selected.", "",
        "## 16. Alternatives Evaluated", "", *[f"- **{item['technology']} ({item['status']}):** {item['rejection_reason'] or item['rationale']}" for item in alternatives], "",
        "## 17. ADR Summary", "", *[f"- `{key}` - {title}" for key, title in ADR_GROUPS.items()], "",
        "## 18. Open Architecture Clarifications", "", *_bullet([f"**{item['technology']}:** {item['decision']}" for item in clarifications]), "",
        "## 19. Architecture Readiness", "", f"- Validation: `{contract['validation']['status']}`", f"- Selection: `{selection['status']}` from `{selection['selection_source']}`", f"- Architecture lock: `{contract['architecture_lock']['status']}`", f"- Design: `{contract['design_specification']['status']}` (optional)", "- Technical tasks: `NOT_YET_GENERATED`", "- Angular generation: `NOT_STARTED`", "- Next: optional Figma input and technical task generation.", "",
    ]
    return "\n".join(lines)


def _badge(status: str) -> str:
    label = {"EVALUATED_ALTERNATIVE": "EVALUATED", "REQUIRES_CLARIFICATION": "CLARIFICATION"}.get(status, status.replace("_", " "))
    return f'<span class="badge {status.lower()}">{escape(label)}</span>'


def _decision_card(item: dict) -> str:
    benefits = "".join(f"<li>{escape(value)}</li>" for value in item["benefits"])
    tradeoffs = "".join(f"<li>{escape(value)}</li>" for value in item["tradeoffs"])
    conditions = "".join(f"<li>{escape(value)}</li>" for value in item["selection_conditions"])
    return f'''<article class="decision-card" data-status="{escape(item['status'])}">
      <div class="card-top"><p class="eyebrow">{escape(item['category'])}</p>{_badge(item['status'])}</div>
      <h3>{escape(item['technology'])}</h3><p>{escape(item['rationale'])}</p>
      <div class="card-columns"><div><h4>Benefits</h4><ul>{benefits}</ul></div><div><h4>Tradeoffs</h4><ul>{tradeoffs}</ul></div></div>
      <details><summary>Selection conditions</summary><ul>{conditions}</ul></details>
    </article>'''


def render_architecture_html(contract: dict) -> str:
    selection = contract["selection"]
    decisions = selection["decisions"]
    by_technology = _decision_map(contract)
    selected = [item for item in decisions if item["status"] in {"SELECTED", "RECOMMENDED"}]
    alternatives = [item for item in decisions if item["status"] not in {"SELECTED", "RECOMMENDED"}]
    groups: dict[str, list[dict]] = defaultdict(list)
    for item in decisions:
        groups[item["category"]].append(item)
    matrix = "".join(f'''<tr><td>{escape(item['category'])}</td><td><strong>{escape(item['technology'])}</strong></td><td>{_badge(item['status'])}</td><td>{escape(item['rationale'])}</td></tr>''' for item in decisions)
    landscape = "".join(f'''<article class="landscape-group"><h3>{escape(category)}</h3><div class="chips">{''.join(f'<span class="capability {item["status"].lower()}">{escape(item["technology"])} · {escape(item["status"].replace("_", " "))}</span>' for item in items)}</div></article>''' for category, items in groups.items())
    detail_names = ["Nx Monorepo", "Signals and RxJS Interoperability", "Zoneless Angular", "Signal Forms", "Client-Side Rendering", "NgRx", "Microfrontends", "Provider-Neutral API Gateway", "Backend for Frontend", "Playwright"]
    details = "".join(_decision_card(by_technology[name]) for name in detail_names)
    api_cards = "".join(f'''<article><span>{escape(api['method'])}</span><code>{escape(api['endpoint'])}</code><p>{escape(api['response_description'])}</p></article>''' for api in selection["existing_api_contracts"])
    counts = contract["counts"]
    alt_examples = "".join(f'''<article><h3>{escape(name)}</h3>{_badge(by_technology[name]['status'])}<p>{escape(by_technology[name]['rejection_reason'] or by_technology[name]['rationale'])}</p></article>''' for name in ("Server-Side Rendering", "NgRx", "Microfrontends"))
    selected_tags = "".join(f"<span>{escape(item['technology'])}</span>" for item in selected[:14])
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Angular 22 Target Architecture</title>
<style>
:root{{--ink:#102a2e;--navy:#153f46;--teal:#13766f;--mint:#d8eee8;--cream:#f6f0e4;--paper:#fffdf7;--orange:#e06a3b;--gold:#d49b35;--line:#c9d8d3;--muted:#587074}}*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}body{{margin:0;background:var(--cream);color:var(--ink);font-family:"Trebuchet MS",sans-serif;line-height:1.55}}body:before{{content:"";position:fixed;inset:0;pointer-events:none;opacity:.25;background-image:radial-gradient(#13766f 0.7px,transparent .7px);background-size:18px 18px}}h1,h2,h3{{font-family:Georgia,serif;line-height:1.08}}h1{{font-size:clamp(3rem,8vw,7.4rem);max-width:1000px;margin:.2em 0}}h2{{font-size:clamp(2rem,4vw,3.4rem);margin:0 0 1rem}}h3{{font-size:1.35rem}}p{{max-width:76ch}}code{{font-family:Consolas,monospace}}.wrap{{width:min(1180px,92vw);margin:auto}}.hero{{min-height:92vh;background:linear-gradient(125deg,#0d3036,#174f55 66%,#126c65);color:white;display:grid;align-items:center;position:relative;overflow:hidden}}.hero:after{{content:"22";position:absolute;right:-2vw;bottom:-12vw;font:700 42vw/1 Georgia;color:rgba(255,255,255,.045)}}.kicker,.eyebrow{{text-transform:uppercase;letter-spacing:.16em;font-size:.75rem;font-weight:700}}.hero .kicker{{color:#9fe0d2}}.lede{{font:1.35rem/1.5 Georgia;max-width:800px;color:#dcece7}}.hero-meta,.stats,.selected-tags,.chips{{display:flex;flex-wrap:wrap;gap:.65rem}}.hero-meta span,.selected-tags span{{border:1px solid rgba(255,255,255,.35);padding:.45rem .75rem;border-radius:999px}}section{{padding:6rem 0;position:relative}}section.alt{{background:var(--paper)}}.section-head{{display:grid;grid-template-columns:1fr 1fr;gap:3rem;align-items:end;margin-bottom:2.5rem}}.stats article{{background:white;border-left:5px solid var(--orange);padding:1rem 1.4rem;min-width:140px;box-shadow:0 8px 30px #173f4620}}.stats strong{{display:block;font:2.2rem Georgia}}.topology{{display:grid;grid-template-columns:repeat(4,1fr);gap:2rem;align-items:stretch}}.layer{{background:var(--navy);color:white;padding:2rem;border-radius:2px;position:relative;box-shadow:10px 10px 0 var(--mint)}}.layer:not(:last-child):after{{content:"→";position:absolute;right:-1.7rem;top:45%;color:var(--orange);font-size:2rem}}.layer.target{{background:var(--teal)}}.layer.existing{{background:white;color:var(--ink);border:2px solid var(--teal)}}.layer small{{display:block;text-transform:uppercase;letter-spacing:.12em;color:#a9ddd3}}.matrix-shell{{overflow:auto;background:white;box-shadow:0 15px 45px #173f4620}}table{{border-collapse:collapse;width:100%;min-width:800px}}th,td{{padding:1rem;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}}th{{background:var(--navy);color:white;position:sticky;top:0}}.badge{{display:inline-block;padding:.3rem .55rem;border-radius:2px;font-size:.68rem;font-weight:800;letter-spacing:.06em;background:#e8ecea;color:#304b4e;white-space:nowrap}}.badge.selected{{background:#bfe9dd;color:#075b50}}.badge.recommended{{background:#d7ead0;color:#35611e}}.badge.evaluated_alternative{{background:#ffe0bd;color:#8b451f}}.badge.not_selected{{background:#efd1cc;color:#8a3028}}.badge.not_applicable{{background:#e0e3e2}}.badge.requires_clarification{{background:#fff0a9;color:#6d5310}}.landscape{{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem}}.landscape-group{{background:white;padding:1.4rem;border-top:4px solid var(--teal)}}.capability{{font-size:.72rem;border:1px solid var(--line);padding:.35rem .55rem;background:#f4f8f6}}.capability.selected{{border-color:var(--teal)}}.capability.not_selected{{opacity:.65;text-decoration:line-through}}.cards{{display:grid;grid-template-columns:repeat(2,1fr);gap:1.3rem}}.decision-card{{background:white;padding:1.6rem;box-shadow:0 8px 30px #173f4615;border-bottom:5px solid var(--teal)}}.card-top,.card-columns{{display:flex;justify-content:space-between;gap:1rem}}.card-columns>div{{flex:1}}details{{border-top:1px solid var(--line);padding-top:.7rem}}summary{{cursor:pointer;font-weight:700}}.deep-dive{{display:grid;grid-template-columns:1fr 1fr;gap:2rem}}.responsibility{{background:var(--navy);color:white;padding:2rem}}.responsibility:nth-child(2){{background:var(--teal)}}.paths{{grid-column:1/-1;display:grid;gap:.6rem}}.path{{background:white;padding:1rem;border-left:4px solid var(--line)}}.path.selected{{border-color:var(--orange);font-weight:700}}.api-grid,.why-grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:1rem}}.api-grid article,.why-grid article{{background:white;padding:1.4rem;border:1px solid var(--line)}}.api-grid span{{background:var(--orange);color:white;font-weight:800;padding:.3rem .5rem;margin-right:.7rem}}.trace{{display:flex;flex-wrap:wrap;align-items:center;gap:.5rem;font-family:Georgia;font-weight:700}}.trace span{{background:white;padding:.8rem;border:1px solid var(--line)}}.trace i{{color:var(--orange)}}.readiness{{background:var(--navy);color:white}}.readiness-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem}}.readiness-grid article{{border-top:4px solid #91d7c7;background:#ffffff10;padding:1.2rem}}footer{{background:#09272c;color:#bad5d0;padding:2rem}}@media(max-width:800px){{.section-head,.deep-dive{{grid-template-columns:1fr}}.topology,.landscape,.cards,.api-grid,.why-grid,.readiness-grid{{grid-template-columns:1fr}}.layer:not(:last-child):after{{content:"↓";right:50%;top:auto;bottom:-2rem}}section{{padding:4rem 0}}}}
</style></head><body>
<header class="hero"><div class="wrap"><p class="kicker">Polaris Modernization · Target Application Architecture</p><h1>Angular 22<br>Enterprise Architecture</h1><p class="lede">A selected target architecture using Nx, standalone domain boundaries, Signals with RxJS, modern routing, and governed Gateway/BFF integration over preserved business APIs.</p><div class="hero-meta"><span>ARCHITECTURE SELECTED</span><span>READY WITH KNOWN LIMITATIONS</span><span>EXTERNAL LLM CALLS: 0</span></div></div></header>
<main>
<section><div class="wrap"><div class="section-head"><div><p class="eyebrow">Selected Target</p><h2>Deliberate enterprise structure</h2></div><p>The architecture selects patterns justified by the target operating model while keeping implementation products and unresolved security details explicit.</p></div><div class="stats"><article><strong>{counts['decisions']}</strong>decisions evaluated</article><article><strong>{counts['selected']}</strong>selected</article><article><strong>{counts['alternatives']}</strong>alternatives</article><article><strong>{counts['adrs']}</strong>ADRs</article></div><div class="selected-tags">{selected_tags}</div></div></section>
<section class="alt"><div class="wrap"><p class="eyebrow">Target Architecture</p><h2>Governed integration, preserved contracts</h2><div class="topology"><article class="layer"><small>Experience</small><h3>Angular 22 Application</h3><p>Nx · Standalone · Signals · RxJS · Router · Design System</p></article><article class="layer target"><small>Target layer</small><h3>API Gateway</h3><p>Ingress · Policy · Routing · Rate limits · Correlation</p></article><article class="layer target"><small>Target layer</small><h3>Backend for Frontend</h3><p>Orchestration · Aggregation · DTO isolation · Response shaping</p></article><article class="layer existing"><small>Existing contracts</small><h3>Business APIs</h3><p>Reports · Clinic · User and organization context</p></article></div></div></section>
<section><div class="wrap"><p class="eyebrow">Decision Matrix</p><h2>Selected and evaluated choices</h2><div class="matrix-shell"><table><thead><tr><th>Area</th><th>Approach</th><th>Status</th><th>Why</th></tr></thead><tbody>{matrix}</tbody></table></div></div></section>
<section class="alt"><div class="wrap"><p class="eyebrow">Angular 22 Capability Landscape</p><h2>Broad knowledge, distinct outcomes</h2><p>Capabilities are explicitly selected, recommended, evaluated, rejected, or conditional. Presence in this landscape does not imply selection.</p><div class="landscape">{landscape}</div></div></section>
<section><div class="wrap"><p class="eyebrow">Decision Details</p><h2>Judgment and tradeoffs</h2><div class="cards">{details}</div></div></section>
<section class="alt"><div class="wrap"><p class="eyebrow">Gateway / BFF Deep Dive</p><h2>Separate enterprise responsibilities</h2><div class="deep-dive"><article class="responsibility"><h3>API Gateway</h3><ul><li>Central ingress and routing</li><li>Authentication and policy enforcement</li><li>Rate limits and API governance</li><li>TLS, correlation, and observability</li></ul></article><article class="responsibility"><h3>Backend for Frontend</h3><ul><li>Angular-specific integration boundary</li><li>Orchestration and aggregation</li><li>Response shaping and DTO isolation</li><li>Backend topology isolation</li></ul></article><div class="paths"><div class="path">Angular → Existing APIs <small>evaluated direct alternative</small></div><div class="path">Angular → Gateway → Existing APIs <small>evaluated gateway-only alternative</small></div><div class="path selected">Angular → Gateway → BFF → Existing APIs <small>selected target</small></div></div></div></div></section>
<section><div class="wrap"><p class="eyebrow">Existing API Contracts</p><h2>Business interfaces remain unchanged</h2><p>These existing contracts are preserved behind the selected target integration topology. No gateway product or BFF endpoint is invented here.</p><div class="api-grid">{api_cards}</div></div></section>
<section class="alt"><div class="wrap"><p class="eyebrow">Why Not Everything?</p><h2>Complexity must earn its place</h2><p>Modern architecture is not the number of technologies selected. Options are chosen only when requirements, scale, operating needs, and delivery constraints justify them.</p><div class="why-grid">{alt_examples}</div></div></section>
<section><div class="wrap"><p class="eyebrow">Architecture Traceability</p><h2>From intent to future implementation</h2><div class="trace"><span>1 Business Feature</span><i>→</i><span>{counts['requirements']} Functional Requirements</span><i>→</i><span>{counts['stories']} Stories</span><i>→</i><span>{counts['acceptance_criteria']} Acceptance Criteria</span><i>→</i><span>{counts['decisions']} Decisions</span><i>→</i><span>{counts['adrs']} ADRs</span><i>→</i><span>Future Tasks</span><i>→</i><span>Future Angular + Tests</span></div></div></section>
<section class="readiness"><div class="wrap"><p class="eyebrow">Implementation Readiness</p><h2>Architecture selected with known limitations</h2><div class="readiness-grid"><article><h3>Architecture</h3><p>SELECTED · LOCKED AFTER VALIDATION</p></article><article><h3>Design</h3><p>{escape(contract['design_specification']['status'])} · OPTIONAL</p></article><article><h3>Technical Tasks</h3><p>NOT YET GENERATED</p></article><article><h3>Angular Generation</h3><p>NOT STARTED</p></article></div><p>Next: optional Figma input and technical task generation.</p></div></section>
</main><footer><div class="wrap">Enterprise architecture showcase · Generated from the selected machine architecture contract</div></footer>
</body></html>'''


def render_adrs(contract: dict) -> dict[str, str]:
    decisions = contract["selection"]["decisions"]
    grouped: dict[str, list[dict]] = defaultdict(list)
    for item in decisions:
        if item["adr_ref"]:
            grouped[item["adr_ref"]].append(item)
    result = {}
    for adr_ref, items in grouped.items():
        group_key = list(ADR_GROUPS)[int(adr_ref.split("-")[1]) - 1]
        title = ADR_GROUPS[group_key]
        selected = [item for item in items if item["status"] in {"SELECTED", "RECOMMENDED"}]
        alternatives = [item for item in items if item["status"] not in {"SELECTED", "RECOMMENDED"}]
        traceability = list(dict.fromkeys(value for item in items for value in item["requirement_refs"] + item["story_refs"] + item["api_refs"]))
        lines = [f"# {adr_ref}: {title}", "", "## Status", "", "Selected Target Architecture", "", "## Context", "", "This decision applies the approved requirements and target enterprise policy without changing existing business API contracts.", "", "## Decision", "", *_bullet([item["decision"] for item in selected]), "", "## Alternatives Considered", "", *_bullet([f"{item['technology']} ({item['status']}): {item['rejection_reason'] or item['rationale']}" for item in alternatives]), "", "## Why Selected", "", *_bullet([item["rationale"] for item in selected]), "", "## Consequences", "", *_bullet([value for item in selected for value in item["benefits"]]), "", "## Tradeoffs", "", *_bullet([value for item in selected for value in item["tradeoffs"]]), "", "## Traceability", "", *[f"- `{value}`" for value in traceability], ""]
        result[f"{adr_ref}.md"] = "\n".join(lines)
    return result
