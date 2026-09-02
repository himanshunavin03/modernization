# Target Architecture

## 1. Executive Architecture Summary

The selected target is an Angular 22 enterprise frontend in an Nx workspace, using standalone domain boundaries, Signals with RxJS at asynchronous edges, zoneless change detection, client-side rendering, and a provider-neutral API Gateway and BFF topology. Existing business API contracts remain unchanged behind the target integration layers.

## 2. Selected Target Architecture

- **Angular 22:** Use Angular 22 as the target frontend framework.
- **TypeScript:** Use strict TypeScript for application and test code.
- **Standalone Components:** Use standalone components for target features.
- **Modern Template Control Flow:** Use built-in template control flow in new templates.
- **Functional Angular APIs:** Prefer functional guards, interceptors, and providers where appropriate.
- **Nx Monorepo:** Use an Nx workspace with one initial Angular application and governed libraries.
- **Domain-Oriented Libraries:** Align domain libraries to approved Feature boundaries.
- **Shared Design-System Library:** Create a shared accessible UI and token library.
- **API Data-Access Libraries:** Separate typed API clients from presentation code.
- **Container and Presentation Separation:** Separate orchestration pages from reusable presentation components where useful.
- **Angular Signals:** Use signals for local and feature synchronous UI state.
- **Computed Signals:** Use computed values for derived presentation state.
- **Angular Effects:** Use effects only for justified external side effects.
- **RxJS:** Keep RxJS at HTTP, cancellation, event, and asynchronous boundaries.
- **Signals and RxJS Interoperability:** Bridge observable and signal boundaries deliberately.
- **Zoneless Angular:** Target zoneless signal-driven change detection.
- **Signal Forms:** Prefer signal-oriented forms for suitable new forms after target API validation.
- **Feature Signal State:** Own Dashboard state in focused injectable signal stores.
- **Angular Router:** Use Angular Router for application navigation.
- **Lazy Feature Routes:** Lazy-load route-level Feature entry points.
- **Functional Guards:** Use functional guards where approved access policy applies.
- **Lazy Loading and Code Splitting:** Use route and library boundaries for intentional code splits.
- **@defer:** Use @defer for noncritical dashboard regions when measured UX supports it.
- **Client-Side Rendering:** Use CSR for the authenticated operational application.
- **Modular Angular Application:** Deliver one modular application organized by domain libraries.
- **Typed Angular HttpClient:** Use typed Feature API clients over preserved contracts.
- **Functional HTTP Interceptors:** Use functional interceptors for transport-wide concerns.
- **Provider-Neutral API Gateway:** Place an API Gateway in the target enterprise topology.
- **Backend for Frontend:** Place a provider-neutral BFF behind the gateway.
- **Tenant and Organization Context Propagation:** Propagate approved organization context through Angular, gateway, and BFF.
- **Browser Security Controls:** Define CSP, XSS, CSRF, secure configuration, secrets, and dependency scanning controls.
- **Accessible Responsive Design System:** Build reusable accessible UI primitives with tokens and responsive rules.
- **Optional Figma Design Input:** Consume normalized DesignSpecification when a connector exists.
- **WCAG-Oriented Validation:** Use semantic HTML, keyboard support, focus management, accessible forms, and automated plus manual checks.
- **Unit and Component Testing:** Test state, services, components, and accessibility at focused boundaries.
- **Playwright:** Use Playwright for AC-traceable end-to-end journeys.
- **Vendor-Neutral Correlated Telemetry:** Correlate frontend, gateway, BFF, and API diagnostics without selecting a vendor.
- **Nx-Aware CI Quality Gates:** Run lint, format, tests, builds, E2E, and security checks with affected execution where valid.

## 3. Architecture Diagram

```text
Browser
  |
Angular 22 / Nx / Standalone Features
  |
Provider-Neutral API Gateway (target)
  |
Backend for Frontend (target; endpoints not yet designed)
  |
Existing Business APIs (contracts preserved)
```

## 4. Angular 22 Architecture

Standalone composition is the modern Angular default and supports direct lazy routes.

Use built-in template control flow in new templates.

## 5. Workspace / Nx Strategy

Five domains, reusable UI, and future applications justify scalable organization and affected build/test orchestration without making Nx technically mandatory.

Angular CLI single application remains a valid alternative for smaller deployments.

## 6. Reactivity Strategy

Use signals for local and feature synchronous UI state. Keep RxJS at HTTP, cancellation, event, and asynchronous boundaries. Bridge observable and signal boundaries deliberately.

## 7. Forms Strategy

**Signal Forms (RECOMMENDED):** The strategy aligns with signal state, but no Dashboard form workflow should be fabricated.

**Reactive Forms (EVALUATED_ALTERNATIVE):** Reactive Forms remain a stable option for complex enterprise forms.

## 8. State Strategy

Known state is feature-scoped and does not require a global event architecture.

NgRx is `NOT_SELECTED` because current state complexity does not justify it.

## 9. Routing Strategy

Use Angular Router for application navigation. Lazy-load route-level Feature entry points. Use functional guards where approved access policy applies.

## 10. Rendering Strategy

CSR is `SELECTED`. SSR is `EVALUATED_ALTERNATIVE` and hydration is `EVALUATED_ALTERNATIVE` because no approved public SEO or server-rendering requirement exists.

## 11. Gateway / BFF Integration

It centralizes ingress, security policy, routing, rate limits, governance, TLS, observability, and correlation without rewriting business APIs.

The target boundary owns Angular-specific orchestration, aggregation, response shaping, DTO isolation, and backend isolation while preserving existing APIs behind it.

No gateway product, BFF endpoint, response shape, or backend replacement is defined by this architecture stage.

**Preserved Existing API Contracts**

- `GET /api/users/current/tenant`: Current organization identifier
- `GET /api/reports/expenses/{year}`: Expense summary information
- `GET /api/reports/patients/{year}`: Patient summary information
- `GET /api/reports/clinicsummary`: Clinic summary information

## 12. Security

Propagate approved organization context through Angular, gateway, and BFF. Define CSP, XSS, CSRF, secure configuration, secrets, and dependency scanning controls.

The identity provider and browser session/token pattern require customer clarification.

## 13. Performance

Use route and library boundaries for intentional code splits. Use @defer for noncritical dashboard regions when measured UX supports it. No performance metric is asserted before measurement.

## 14. Testing

Test state, services, components, and accessibility at focused boundaries. Use Playwright for AC-traceable end-to-end journeys. Accessibility combines automated and manual validation; formal compliance is not claimed before verification.

## 15. Observability

Correlate frontend, gateway, BFF, and API diagnostics without selecting a vendor.

No telemetry vendor is selected.

## 16. Alternatives Evaluated

- **Angular CLI Single Application (EVALUATED_ALTERNATIVE):** Selected target prioritizes governed domain growth.
- **Zone.js Compatibility Mode (EVALUATED_ALTERNATIVE):** Zoneless is the selected target.
- **Reactive Forms (EVALUATED_ALTERNATIVE):** No approved Dashboard form requires selection.
- **RxJS Service State (EVALUATED_ALTERNATIVE):** Signals are simpler for current UI state.
- **NgRx (NOT_SELECTED):** Current state complexity does not justify it.
- **Route Resolvers (EVALUATED_ALTERNATIVE):** No requirement demands blocked activation.
- **Server-Side Rendering (EVALUATED_ALTERNATIVE):** No supported SEO requirement.
- **Hydration (EVALUATED_ALTERNATIVE):** CSR is selected.
- **Prerendering and Hybrid Rendering (NOT_APPLICABLE):** No applicable public route requirement.
- **Microfrontends (NOT_SELECTED):** Current scope does not justify distribution.
- **Module Federation (NOT_SELECTED):** Microfrontends are not selected.
- **Gateway-Only Integration (EVALUATED_ALTERNATIVE):** Selected enterprise target includes a BFF.
- **Direct Browser-to-API Integration (EVALUATED_ALTERNATIVE):** Target selects gateway and BFF.

## 17. ADR Summary

- `platform` - Angular 22 and Nx Workspace Strategy
- `structure` - Standalone Domain-Oriented Frontend Architecture
- `reactivity` - Signals, RxJS, and Zoneless Reactivity
- `state` - Forms and State Management Strategy
- `routing` - Routing and Performance Boundaries
- `rendering` - Client-Side Rendering Strategy
- `integration` - API Gateway, BFF, and Existing API Integration
- `security` - Security and Correlated Observability
- `quality` - Testing, Accessibility, and Delivery Quality

## 18. Open Architecture Clarifications

- **Authentication Provider:** Select the identity provider and session/token pattern before implementation.

## 19. Architecture Readiness

- Validation: `ARCHITECTURE_READY_WITH_LIMITATIONS`
- Selection: `ARCHITECTURE_SELECTED` from `POLARIS_POC_DEFAULT`
- Architecture lock: `LOCKED`
- Design: `NOT_PROVIDED` (optional)
- Technical tasks: `NOT_YET_GENERATED`
- Angular generation: `NOT_STARTED`
- Next: optional Figma input and technical task generation.
