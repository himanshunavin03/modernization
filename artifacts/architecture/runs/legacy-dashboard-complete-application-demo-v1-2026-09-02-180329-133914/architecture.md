# Target Architecture

## Executive Summary

Use Angular 22 with standalone, lazy Feature boundaries for `feature-operational-dashboard-insights` while preserving all approved backend APIs.

## Architecture Goals

- Deliver the approved Feature behavior without redefining requirements.
- Keep state, API integration, and UI composition testable and Feature-scoped.

## Constraints

- Existing backend APIs remain authoritative.
- Story clarifications limit final UI detail but do not block architecture.
- Angular generation is outside this stage.

## Target Technology

- Angular 22 standalone architecture
- Signals for UI state and RxJS for asynchronous boundaries
- Typed HttpClient and Playwright

## Application Structure

Use route-level Feature folders containing pages, presentation components, API services, and focused Signal-backed state services.

## Feature Architecture

- `FR-02`: The user must be able to view yearly expense information.
- `FR-03`: The user must be able to view yearly patient information.
- `FR-05`: The application must retrieve the current organization identifier required by organization-specific functionality.
- `FR-04`: The user must be able to view clinic summary.
- `FR-01`: The user must be able to access the operational dashboard.

## State Management

Keep Feature state in focused injectable services backed by Signals.

## API Integration

- `GET /api/users/current/tenant`: Current organization identifier
- `GET /api/reports/expenses/{year}`: Expense summary information
- `GET /api/reports/patients/{year}`: Patient summary information
- `GET /api/reports/clinicsummary`: Clinic summary information

## Routing

Use lazy route boundaries for approved Features and functional guards where access checks apply.

## Security / Tenant Context

Resolve organization context through the approved tenant endpoint and propagate it through Feature services without changing backend contracts.

## Design System and Optional Figma Input

Design status: `NOT_PROVIDED`. Target UI design input is optional and normalized through `DesignSpecification`; Figma is recognized, but its connector is not implemented.

## Error Handling

Use a functional HTTP interceptor, user-safe Feature error states, and structured client diagnostics.

## Testing Strategy

Use unit tests for state/services, HTTP contract tests for approved routes, and Playwright for critical AC-backed journeys.

## Observability

Record structured client diagnostics at API boundaries without exposing sensitive user or organization data.

## Architecture Decisions

- **ARCH-001 - Angular 22 (USE):** Angular 22 is the explicit POC target.
- **ARCH-002 - Standalone architecture (USE):** The target is a new Angular frontend with independently scoped approved Features.
- **ARCH-003 - Signals (USE):** The dashboard requires reactive selected-year, context, loading, and derived presentation state.
- **ARCH-004 - RxJS (USE):** Approved APIs require cancellation and stream composition; Observables need not replace local Signal state.
- **ARCH-006 - Service and Signal stores (USE):** The approved scope does not establish cross-domain complexity requiring a global event store.
- **ARCH-007 - Router with lazy feature routes (USE):** Multiple approved Feature boundaries map naturally to route-level loading.
- **ARCH-008 - Typed HttpClient (USE):** Approved request parameters and response models are available and must remain authoritative.
- **ARCH-014 - Playwright (USE):** The approved AC provide observable end-to-end behavior.
- **ARCH-015 - Error handling and observability (USE):** API-backed workflows require consistent technical failure handling without inventing business outcomes.
- **ARCH-016 - Accessible component strategy (USE):** Shared presentation and accessibility are architecture concerns while design input remains optional.

## Technologies Evaluated but Not Selected

- **Zoneless change detection (EVALUATE):** Angular 22 supports the target model, but third-party and future design-system compatibility is not yet known.
- **SSR and hydration (NOT_APPLICABLE):** No public discovery, SEO, or server-rendering requirement is present.
- **Backend for Frontend (DO_NOT_USE):** The explicit frontend-modernization constraint does not justify a replacement or aggregation backend.
- **Nx (DO_NOT_USE):** The approved scope does not establish a multi-application monorepo need.
- **Microfrontends (DO_NOT_USE):** Independent deployment and team-autonomy requirements are absent.
- **NgRx (DO_NOT_USE):** Signals and focused services cover the known state without global event-store overhead.
- **Signal Forms (NOT_APPLICABLE):** The approved Dashboard has a single year selection and no multi-field form workflow requiring a forms architecture.

## Known Limitations / Clarifications

- Implementation clarifications remain, but they do not block architecture decisions.

## Next Step

Review the architecture and approved clarifications before technical task generation.
