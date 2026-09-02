"""Maintainable enterprise Angular architecture decision catalog."""
from __future__ import annotations

from dataclasses import dataclass

from .models import ArchitectureDecision, DecisionStatus as S


@dataclass(frozen=True)
class CatalogEntry:
    category: str
    technology: str
    status: S
    decision: str
    rationale: str
    benefits: tuple[str, ...]
    tradeoffs: tuple[str, ...]
    conditions: tuple[str, ...]
    rejection_reason: str | None = None
    adr_group: str | None = None
    source: str = "ENTERPRISE_ARCHITECTURE_POLICY"


def _c(category: str, technology: str, status: S, decision: str, rationale: str, benefits: tuple[str, ...], tradeoffs: tuple[str, ...], conditions: tuple[str, ...], rejection_reason: str | None = None, adr_group: str | None = None) -> CatalogEntry:
    return CatalogEntry(category, technology, status, decision, rationale, benefits, tradeoffs, conditions, rejection_reason, adr_group)


CATALOG: tuple[CatalogEntry, ...] = (
    _c("Frontend Platform", "Angular 22", S.SELECTED, "Use Angular 22 as the target frontend framework.", "Angular 22 is the approved modernization target.", ("Modern standalone and signal-first APIs",), ("Requires current tooling and team enablement",), ("Angular 22 remains the approved target",), adr_group="platform"),
    _c("Frontend Platform", "TypeScript", S.SELECTED, "Use strict TypeScript for application and test code.", "Typed implementation protects the approved API and UI contracts.", ("Safer refactoring", "Typed API integration"), ("Strict models require discipline",), ("Strict compiler settings are enabled",), adr_group="platform"),
    _c("Frontend Platform", "Standalone Components", S.SELECTED, "Use standalone components for target features.", "Standalone composition is the modern Angular default and supports direct lazy routes.", ("Explicit dependencies", "Less configuration ceremony"), ("Teams must learn current composition patterns",), ("New Angular 22 code",), adr_group="structure"),
    _c("Frontend Platform", "Modern Template Control Flow", S.SELECTED, "Use built-in template control flow in new templates.", "The target version supports concise type-aware template flow.", ("Clear templates",), ("Requires consistent conventions",), ("New templates",)),
    _c("Frontend Platform", "Functional Angular APIs", S.SELECTED, "Prefer functional guards, interceptors, and providers where appropriate.", "Functional APIs align with standalone bootstrapping and focused testing.", ("Composable configuration",), ("Not every service should become a function",), ("Use at supported extension points",)),
    _c("Workspace", "Nx Monorepo", S.SELECTED, "Use an Nx workspace with one initial Angular application and governed libraries.", "Five domains, reusable UI, and future applications justify scalable organization and affected build/test orchestration without making Nx technically mandatory.", ("Boundary enforcement", "Reusable libraries", "Affected execution"), ("Additional tooling and governance",), ("Enterprise target anticipates shared libraries and growth",), adr_group="platform"),
    _c("Workspace", "Angular CLI Single Application", S.EVALUATED_ALTERNATIVE, "Retain as the lower-complexity workspace alternative.", "A smaller isolated deployment can be delivered without Nx.", ("Minimal tooling",), ("Fewer built-in boundary controls",), ("Prefer when enterprise growth is not expected",), "Selected target prioritizes governed domain growth."),
    _c("Workspace", "Domain-Oriented Libraries", S.SELECTED, "Align domain libraries to approved Feature boundaries.", "Stable Feature domains provide meaningful ownership and dependency boundaries.", ("Clear ownership", "Controlled reuse"), ("Avoid excessive library fragmentation",), ("A stable domain boundary exists",), adr_group="structure"),
    _c("Workspace", "Shared Design-System Library", S.SELECTED, "Create a shared accessible UI and token library.", "Reusable primitives support consistent delivery and later normalized design input.", ("Consistent UX", "Central accessibility patterns"), ("Requires contribution governance",), ("Only reusable UI enters the library",), adr_group="structure"),
    _c("Workspace", "API Data-Access Libraries", S.SELECTED, "Separate typed API clients from presentation code.", "Preserved backend contracts are stable integration boundaries.", ("Contract isolation", "Focused testing"), ("Avoid abstractions that hide HTTP semantics",), ("Approved API contracts exist",), adr_group="integration"),
    _c("Component Architecture", "Container and Presentation Separation", S.RECOMMENDED, "Separate orchestration pages from reusable presentation components where useful.", "The Dashboard coordinates several services while reusable views can remain input/output focused.", ("Testable UI", "Clear state ownership"), ("Do not split trivial components mechanically",), ("Responsibilities are genuinely distinct",), adr_group="structure"),
    _c("Reactivity", "Angular Signals", S.SELECTED, "Use signals for local and feature synchronous UI state.", "Selected year, loading, context, and derived view state fit signal ownership.", ("Fine-grained reactivity",), ("Effects still need discipline",), ("State is synchronous or derived",), adr_group="reactivity"),
    _c("Reactivity", "Computed Signals", S.SELECTED, "Use computed values for derived presentation state.", "Derived values should not be duplicated or manually synchronized.", ("Declarative derivation",), ("Expensive derivations require care",), ("Value derives from signal state",), adr_group="reactivity"),
    _c("Reactivity", "Angular Effects", S.RECOMMENDED, "Use effects only for justified external side effects.", "Computed state remains preferable for ordinary derivation.", ("Explicit side-effect bridge",), ("Overuse obscures data flow",), ("An external effect follows reactive state",), adr_group="reactivity"),
    _c("Reactivity", "RxJS", S.SELECTED, "Keep RxJS at HTTP, cancellation, event, and asynchronous boundaries.", "Dashboard requests and year changes benefit from observable cancellation and composition.", ("Mature async composition",), ("Unnecessary streams add complexity",), ("Work is asynchronous or event-based",), adr_group="reactivity"),
    _c("Reactivity", "Signals and RxJS Interoperability", S.SELECTED, "Bridge observable and signal boundaries deliberately.", "HTTP remains observable while templates consume stable signal state.", ("Each model serves its strength",), ("Boundary ownership must be explicit",), ("Async results feed UI state",), adr_group="reactivity"),
    _c("Change Detection", "Zoneless Angular", S.SELECTED, "Target zoneless signal-driven change detection.", "A new Angular 22 application can adopt zoneless operation after dependency compatibility validation.", ("Reduced implicit work",), ("Third-party compatibility must be verified",), ("Selected dependencies pass compatibility tests",), adr_group="reactivity"),
    _c("Change Detection", "Zone.js Compatibility Mode", S.EVALUATED_ALTERNATIVE, "Retain compatibility mode as a fallback.", "It lowers transition risk if a required dependency is not zoneless-compatible.", ("Broad compatibility",), ("Retains implicit change detection",), ("Use only if compatibility tests require it",), "Zoneless is the selected target."),
    _c("Forms", "Signal Forms", S.RECOMMENDED, "Prefer signal-oriented forms for suitable new forms after target API validation.", "The strategy aligns with signal state, but no Dashboard form workflow should be fabricated.", ("Signal-aligned validation state",), ("Maturity and team readiness need validation",), ("Use for meaningful forms after API validation",), adr_group="state"),
    _c("Forms", "Reactive Forms", S.EVALUATED_ALTERNATIVE, "Use Reactive Forms where mature controls or complex workflows make them safer.", "Reactive Forms remain a stable option for complex enterprise forms.", ("Mature ecosystem",), ("Separate reactive model",), ("Prefer when Signal Forms suitability is insufficient",), "No approved Dashboard form requires selection."),
    _c("State Management", "Feature Signal State", S.SELECTED, "Own Dashboard state in focused injectable signal stores.", "Known state is feature-scoped and does not require a global event architecture.", ("Low ceremony", "Feature ownership"), ("Cross-domain workflows may require reevaluation",), ("State remains feature-scoped",), adr_group="state"),
    _c("State Management", "RxJS Service State", S.EVALUATED_ALTERNATIVE, "Use observable service state where stream semantics dominate.", "It remains useful for stream-centric flows but should not duplicate signal UI state.", ("Strong event composition",), ("Can create competing state models",), ("Use for stream-centric state",), "Signals are simpler for current UI state."),
    _c("State Management", "NgRx", S.NOT_SELECTED, "Do not introduce NgRx for the current target scope.", "The hero Feature lacks complex global events, cross-domain state, and reducer/effect governance needs.", ("Strong governance at scale",), ("Actions, reducers, and effects add ceremony",), ("Reconsider for sophisticated global workflows or large-team governance",), "Current state complexity does not justify it.", "state"),
    _c("Routing", "Angular Router", S.SELECTED, "Use Angular Router for application navigation.", "Approved Features map cleanly to route ownership.", ("Native lazy loading and guards",), ("Routes require governance",), ("Multiple Feature routes exist",), adr_group="routing"),
    _c("Routing", "Lazy Feature Routes", S.SELECTED, "Lazy-load route-level Feature entry points.", "Five Feature domains create intentional code-splitting boundaries.", ("Reduced initial bundle",), ("Poor chunking can delay navigation",), ("Independent route boundary exists",), adr_group="routing"),
    _c("Routing", "Functional Guards", S.SELECTED, "Use functional guards where approved access policy applies.", "They align with standalone routing while identity-provider details remain open.", ("Composable access checks",), ("Server authorization remains authoritative",), ("Approved route policy exists",), adr_group="security"),
    _c("Routing", "Route Resolvers", S.EVALUATED_ALTERNATIVE, "Use resolvers only for route-critical data.", "Most Dashboard loading can remain explicit with visible progress and cancellation.", ("Data before activation",), ("Can delay navigation",), ("Navigation must wait for essential data",), "No requirement demands blocked activation."),
    _c("Performance", "Lazy Loading and Code Splitting", S.SELECTED, "Use route and library boundaries for intentional code splits.", "Feature structure provides natural loading boundaries without invented metrics.", ("Bundle discipline",), ("Too many chunks add overhead",), ("Measure and retain useful boundaries",), adr_group="routing"),
    _c("Performance", "@defer", S.RECOMMENDED, "Use @defer for noncritical dashboard regions when measured UX supports it.", "Independent summary regions can render progressively.", ("Progressive loading",), ("Placeholder behavior needs design",), ("Only noncritical content",), adr_group="routing"),
    _c("Rendering", "Client-Side Rendering", S.SELECTED, "Use CSR for the authenticated operational application.", "No approved public SEO or server-rendering requirement exists.", ("Simple deployment",), ("Initial render requires application download",), ("Operational authenticated application",), adr_group="rendering"),
    _c("Rendering", "Server-Side Rendering", S.EVALUATED_ALTERNATIVE, "Reconsider SSR for public SEO or measured first-render requirements.", "Those requirements are not established for this application.", ("Public first-render and SEO benefits",), ("Server runtime and hydration complexity",), ("Public rendering requirements justify it",), "No supported SEO requirement.", "rendering"),
    _c("Rendering", "Hydration", S.EVALUATED_ALTERNATIVE, "Use hydration only with SSR or hybrid rendering.", "It has no independent value in the selected CSR topology.", ("Preserves server DOM",), ("Mismatch and lifecycle complexity",), ("SSR or hybrid is selected",), "CSR is selected.", "rendering"),
    _c("Rendering", "Prerendering and Hybrid Rendering", S.NOT_APPLICABLE, "Do not prerender current operational routes.", "No approved public static route set exists.", ("Useful for stable public content",), ("Freshness and build complexity",), ("Known public static routes",), "No applicable public route requirement."),
    _c("Application Topology", "Modular Angular Application", S.SELECTED, "Deliver one modular application organized by domain libraries.", "Strong boundaries are useful without distributed frontend deployment.", ("Coherent deployment",), ("Requires dependency discipline",), ("Single product deployment is appropriate",), adr_group="structure"),
    _c("Application Topology", "Microfrontends", S.NOT_SELECTED, "Do not split into independently deployed frontends.", "No autonomous team, release cadence, or deployment boundary is established.", ("Independent deployment when justified",), ("Runtime and operational complexity",), ("Reconsider for autonomous teams and deployments",), "Current scope does not justify distribution."),
    _c("Application Topology", "Module Federation", S.NOT_SELECTED, "Do not introduce federation runtime composition.", "Federation is unnecessary without selected microfrontends.", ("Runtime composition",), ("Shared-version and runtime failure complexity",), ("Requires justified microfrontends",), "Microfrontends are not selected."),
    _c("API Client", "Typed Angular HttpClient", S.SELECTED, "Use typed Feature API clients over preserved contracts.", "Four approved Dashboard contracts define the integration boundary.", ("Compile-time contract use",), ("Types must remain aligned",), ("Approved APIs exist",), adr_group="integration"),
    _c("API Client", "Functional HTTP Interceptors", S.SELECTED, "Use functional interceptors for transport-wide concerns.", "Authentication context, correlation, and technical error normalization belong at request boundaries.", ("Central policy",), ("Business logic must remain in Feature services",), ("Only cross-cutting transport concerns",), adr_group="integration"),
    _c("API Gateway", "Provider-Neutral API Gateway", S.SELECTED, "Place an API Gateway in the target enterprise topology.", "It centralizes ingress, security policy, routing, rate limits, governance, TLS, observability, and correlation without rewriting business APIs.", ("Central governance", "Consistent ingress policy"), ("Additional operations", "Product remains unselected"), ("Enterprise target accepts centralized API policy",), adr_group="integration"),
    _c("API Gateway", "Gateway-Only Integration", S.EVALUATED_ALTERNATIVE, "Retain gateway-to-existing-API routing as a simpler alternative.", "It is valid when frontend aggregation and DTO isolation are unnecessary.", ("Fewer runtime layers",), ("Browser retains backend coupling",), ("Use when BFF duties are not justified",), "Selected enterprise target includes a BFF.", "integration"),
    _c("Backend for Frontend", "Backend for Frontend", S.SELECTED, "Place a provider-neutral BFF behind the gateway.", "The target boundary owns Angular-specific orchestration, aggregation, response shaping, DTO isolation, and backend isolation while preserving existing APIs behind it.", ("Reduced browser orchestration", "Backend isolation"), ("Additional service ownership", "No endpoints are designed yet"), ("Enterprise target accepts this operational layer",), adr_group="integration"),
    _c("Backend for Frontend", "Direct Browser-to-API Integration", S.EVALUATED_ALTERNATIVE, "Retain direct API integration as the simplest alternative.", "It remains valid when enterprise policy and aggregation do not justify extra layers.", ("Fewest layers",), ("Browser couples to backend topology",), ("Use for smaller deployments",), "Target selects gateway and BFF.", "integration"),
    _c("Security", "Authentication Provider", S.REQUIRES_CLARIFICATION, "Select the identity provider and session/token pattern before implementation.", "Identity and claims APIs are known, but the target provider and protocol are not approved.", ("Avoids invented security architecture",), ("Blocks final security detail",), ("Customer security policy is required",), adr_group="security"),
    _c("Security", "Tenant and Organization Context Propagation", S.SELECTED, "Propagate approved organization context through Angular, gateway, and BFF.", "Organization context is an approved dependency across integration boundaries.", ("Consistent tenant scope",), ("Server policy must prevent client trust escalation",), ("Server validates context",), adr_group="security"),
    _c("Security", "Browser Security Controls", S.RECOMMENDED, "Define CSP, XSS, CSRF, secure configuration, secrets, and dependency scanning controls.", "Exact controls depend on the authentication/session decision.", ("Defense in depth",), ("Environment-specific validation",), ("Finalize after identity clarification",), adr_group="security"),
    _c("Design System", "Accessible Responsive Design System", S.SELECTED, "Build reusable accessible UI primitives with tokens and responsive rules.", "A shared boundary supports consistency and future design input.", ("Consistent UX",), ("Requires governance and manual validation",), ("Formal compliance follows validation",), adr_group="structure"),
    _c("Design System", "Optional Figma Design Input", S.RECOMMENDED, "Consume normalized DesignSpecification when a connector exists.", "Design remains optional and cannot override business or API truth.", ("Provider-independent design boundary",), ("Connector is not implemented",), ("Continue when design is absent",)),
    _c("Accessibility", "WCAG-Oriented Validation", S.SELECTED, "Use semantic HTML, keyboard support, focus management, accessible forms, and automated plus manual checks.", "Accessibility must be designed and validated rather than assumed.", ("Inclusive interaction",), ("Formal compliance requires completed validation",), ("Trace checks to AC",), adr_group="quality"),
    _c("Testing", "Unit and Component Testing", S.SELECTED, "Test state, services, components, and accessibility at focused boundaries.", "Layered tests provide fast feedback before E2E.", ("Fast defect localization",), ("Requires stable boundaries",), ("Tests trace to decisions and AC",), adr_group="quality"),
    _c("Testing", "Playwright", S.SELECTED, "Use Playwright for AC-traceable end-to-end journeys.", "Approved AC provide observable browser and API-backed behavior.", ("Real browser validation",), ("Higher execution cost",), ("Reserve for critical journeys",), adr_group="quality"),
    _c("Observability", "Vendor-Neutral Correlated Telemetry", S.SELECTED, "Correlate frontend, gateway, BFF, and API diagnostics without selecting a vendor.", "Target layers require latency and error visibility across boundaries.", ("Faster diagnosis",), ("Privacy and volume need governance",), ("Never log sensitive identity data",), adr_group="security"),
    _c("Delivery", "Nx-Aware CI Quality Gates", S.SELECTED, "Run lint, format, tests, builds, E2E, and security checks with affected execution where valid.", "Nx can optimize feedback while full release gates remain mandatory.", ("Efficient validation",), ("Affected checks cannot replace release validation",), ("CI provider remains configurable",), adr_group="quality"),
)


ADR_GROUPS = {
    "platform": "Angular 22 and Nx Workspace Strategy",
    "structure": "Standalone Domain-Oriented Frontend Architecture",
    "reactivity": "Signals, RxJS, and Zoneless Reactivity",
    "state": "Forms and State Management Strategy",
    "routing": "Routing and Performance Boundaries",
    "rendering": "Client-Side Rendering Strategy",
    "integration": "API Gateway, BFF, and Existing API Integration",
    "security": "Security and Correlated Observability",
    "quality": "Testing, Accessibility, and Delivery Quality",
}


def load_architecture_catalog() -> tuple[CatalogEntry, ...]:
    return CATALOG


def evaluate_architecture_catalog(state: dict) -> list[ArchitectureDecision]:
    requirement_refs = [item["id"] for item in state["requirements"]]
    story_refs = [item["story_id"] for item in state["stories"]]
    api_refs = [item["api_id"] for item in state["api_contracts"]]
    groups = {group: index for index, group in enumerate(ADR_GROUPS, 1)}
    decisions = []
    for number, item in enumerate(CATALOG, 1):
        status = item.status
        if item.technology in {"RxJS", "Typed Angular HttpClient"} and not api_refs:
            status = S.NOT_APPLICABLE
        decisions.append(ArchitectureDecision(
            id=f"ARCH-{number:03d}", category=item.category, technology=item.technology, status=status,
            decision=item.decision, rationale=item.rationale, benefits=list(item.benefits), tradeoffs=list(item.tradeoffs),
            selection_conditions=list(item.conditions), rejection_reason=item.rejection_reason,
            requirement_refs=requirement_refs, feature_refs=[state["feature_id"]], story_refs=story_refs,
            api_refs=api_refs, design_refs=state["design_specification"]["traceability"],
            adr_ref=f"ADR-{groups[item.adr_group]:03d}" if item.adr_group else None,
            machine_traceability={"classification": item.source, "catalog_key": item.technology.lower().replace(" ", "-")},
        ))
    return decisions
