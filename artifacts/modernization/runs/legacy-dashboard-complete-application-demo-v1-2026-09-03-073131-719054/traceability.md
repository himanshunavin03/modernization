# Angular Hero Generation Traceability

## Acceptance Criteria

### ac-operational-dashboard-insights-access-yearly-operational-reports-001
- Implementation: DashboardFeatureComponent, DashboardStore, DashboardApiClient, YearNavigatorComponent
- Tests: dashboard-api.client.spec.ts, dashboard.store.spec.ts, year-navigator.component.spec.ts, dashboard.spec.ts

### ac-operational-dashboard-insights-view-tenant-aware-dashboard-summary-001
- Implementation: DashboardFeatureComponent, SummaryCardComponent, TenantContextService
- Tests: dashboard-feature.component.spec.ts, dashboard-api.client.spec.ts, dashboard.spec.ts

### ac-operational-dashboard-insights-view-tenant-aware-dashboard-summary-002
- Implementation: DashboardApiClient, DashboardStore, TenantContextService
- Tests: dashboard-api.client.spec.ts, dashboard.store.spec.ts, dashboard.spec.ts

### ac-operational-dashboard-insights-open-operational-dashboard-001
- Implementation: appRoutes, DASHBOARD_ROUTES, DashboardFeatureComponent
- Tests: app.routes.spec.ts, dashboard-feature.component.spec.ts, dashboard.spec.ts

### ac-operational-dashboard-insights-open-operational-dashboard-002
- Implementation: PrivateShellComponent, DashboardFeatureComponent
- Tests: app.routes.spec.ts, dashboard-feature.component.spec.ts, dashboard.spec.ts

## Technical Tasks

- `TT-001`: `IMPLEMENTED` - Angular 22/Nx workspace generated with zoneless-compatible package configuration.
- `TT-002`: `IMPLEMENTED` - Five tagged Nx library boundaries define app, feature, UI, data, state, and platform responsibilities.
- `TT-003`: `IMPLEMENTED` - Shared Dashboard UI primitives and source-derived visual tokens are implemented.
- `TT-004`: `IMPLEMENTED` - Typed models and clients preserve all four existing API contracts.
- `TT-005`: `DEFERRED` - Provider-neutral Gateway implementation is DEFERRED_TO_DEPLOYMENT.
- `TT-006`: `DEFERRED` - BFF implementation is deferred; its facade remains TARGET_CONTRACT_TO_BE_DESIGNED.
- `TT-007`: `PARTIALLY_IMPLEMENTED` - Configurable API base URL and typed client boundary are implemented; the future BFF facade remains TARGET_CONTRACT_TO_BE_DESIGNED.
- `TT-008`: `IMPLEMENTED` - The /dashboard route is lazy-loaded through Angular Router.
- `TT-009`: `IMPLEMENTED` - Standalone private shell and Dashboard feature components are generated.
- `TT-010`: `IMPLEMENTED` - Signals own UI state and RxJS owns tenant-aware asynchronous loading and cancellation.
- `TT-011`: `IMPLEMENTED` - Tenant context is retrieved and propagated through the approved TenantId header behavior without an identity-provider assumption.
- `TT-012`: `IMPLEMENTED` - Clinic cards and both yearly report regions reconstruct the existing Dashboard presentation.
- `TT-013`: `IMPLEMENTED` - Semantic controls, labels, focus indicators, status regions, and responsive layouts are generated.
- `TT-014`: `PARTIALLY_IMPLEMENTED` - Frontend correlation and centralized HTTP error foundations are implemented; deployment-layer telemetry remains deferred.
- `TT-015`: `PARTIALLY_IMPLEMENTED` - Unit/component test sources are generated but not executed in this generation stage.
- `TT-016`: `PARTIALLY_IMPLEMENTED` - Playwright scenarios map all five hero AC but are not executed in this generation stage.
