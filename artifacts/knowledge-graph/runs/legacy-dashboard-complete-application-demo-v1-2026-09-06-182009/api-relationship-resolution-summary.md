# API Relationship Resolution Summary

- Project ID: `legacy-dashboard-complete-application-demo-v1`
- Resolver version: `2026-09-02`
- Total frontend calls: 6
- Proven before: 0
- Proven after: 0
- New exact static matches: 0
- New exact template matches: 0
- New unique parameterized matches: 0
- Remaining dynamic: 0
- Remaining ambiguous: 0
- External: 0
- No backend match: 6
- Unresolved: 0

## Root Cause

The previous resolver only promoted inline literal AngularJS URLs. Calls routed through `url` variables or simple dynamic template/concatenation expressions never reached deterministic method-plus-route reconciliation, so uniquely matchable endpoints remained unresolved or dynamic.

## Promotions

- No frontend calls were promoted.

## Important Cases

- `'/api/reports/expenses/' + year` in `src/MyHealth.Web/content/app/components/dashboard/services/dashboardService.js` -> `NO_BACKEND_MATCH` (No compatible backend endpoint exists after HTTP method and normalized route comparison.)
- `'/api/reports/patients/' + year` in `src/MyHealth.Web/content/app/components/dashboard/services/dashboardService.js` -> `NO_BACKEND_MATCH` (No compatible backend endpoint exists after HTTP method and normalized route comparison.)
- `/api/reports/clinicsummary` in `src/MyHealth.Web/content/app/components/dashboard/services/dashboardService.js` -> `NO_BACKEND_MATCH` (No compatible backend endpoint exists after HTTP method and normalized route comparison.)
