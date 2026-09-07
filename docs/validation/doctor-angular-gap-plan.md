# Doctor Angular reconciliation gap plan

Execution baseline: b8e2ddb1224695acc998e72abbc8d0a0120849e0 (the original baseline plus committed preflight notes). Prompt 072 defers TT-016 without modifying its frozen contract.

Pre-edit inspection: workspace, tagged libraries, accessible presentation primitives and automatic tenant handling exist (TT-001/002/003/011). API, integration, routing, shell, state, interactions, accessibility, telemetry and unit coverage are partial (TT-004/007/008/009/010/012/013/014/015). Gateway/BFF planning deliverables are absent (TT-005/006). TT-016 has one obsolete list/detail scenario and is deferred. Counts: 4 implemented, 9 partial, 2 absent, 1 deferred.

All FR/Story/AC/API links are taken from the corresponding frozen task in technical task run legacy-dashboard-complete-application-demo-v1-2026-09-07-054315-967074; no linkage is reassigned here.

| Task | Existing implementation | Gap and files to change | Validation |
| --- | --- | --- | --- |
| TT-004 | Typed list/detail GET client | Add POST/PUT/DELETE and write type in data-access; contract specs | Method, route, payload, tenant, errors |
| TT-005 | Development proxy only | Document ingress policy/routing responsibilities in reconciliation integration report | All six existing contracts preserved |
| TT-006 | No BFF responsibility design | Document future boundary without approving new facade endpoints | TARGET_CONTRACT_TO_BE_DESIGNED |
| TT-007 | Components use state and typed API client | Extend existing client/state boundary to writes | Integration tests, no component HTTP |
| TT-008 | Lazy Doctor parent, list and detail routes | Add new-record route; extend detail navigation | Router tests; Patients destination unresolved |
| TT-009 | Standalone list/detail, empty/loading/error views | Extend existing templates for forms/actions/selection | DOM tests and strict build |
| TT-010 | Signals for list, loading, detail; RxJS requests | Add computed selection, mutation state, fixed sort, successful mutations | State tests for append/termination/deletion/success/error |
| TT-012 | Read-only list/detail and Load More | Add required fields, validation, create/update, confirmation and file preview in existing components | Component/form/media/navigation tests |
| TT-013 | Labels, semantic links, focus styles | Check new form controls, selection and confirmations | DOM label/disabled/keyboard-native controls tests |
| TT-014 | Global correlation/error interceptors | Verify Doctor writes retain correlation/error visibility; no sensitive payload logging | HTTP failure/correlation tests |
| TT-015 | Three minimal Doctor unit tests | Extend existing files and add detail component tests | Focused Angular unit suite |

TT-001/002/003/011: preserve the existing workspace, library boundaries, presentation styles and platform service. Shared package manifest/lock additions are limited to the version-matched Angular forms package. Use typed Reactive Forms with required-only validators, Signals/computed for local UI state, and RxJS for requests.

Patients navigation requires an existing destination; no Patient feature or placeholder screen is authorized by the Doctor scope. Requested the destination while independent implementation continues.
