# API Relationship Resolution Summary

- Project ID: `contracts`
- Resolver version: `2026-09-02`
- Total frontend calls: 2
- Proven before: 0
- Proven after: 2
- New exact static matches: 0
- New exact template matches: 1
- New unique parameterized matches: 1
- Remaining dynamic: 0
- Remaining ambiguous: 0
- External: 0
- No backend match: 0
- Unresolved: 0

## Root Cause

The previous resolver only promoted inline literal AngularJS URLs. Calls routed through `url` variables or simple dynamic template/concatenation expressions never reached deterministic method-plus-route reconciliation, so uniquely matchable endpoints remained unresolved or dynamic.

## Promotions

- `/api/orders/42` in `web/ordersService.js` -> `PROVEN_UNIQUE_PARAMETERIZED`
- `'/api/orders/' + id` in `web/ordersService.js` -> `PROVEN_EXACT_TEMPLATE`
