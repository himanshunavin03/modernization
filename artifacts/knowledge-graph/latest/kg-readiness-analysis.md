# Knowledge Graph Readiness Analysis

## Scope and identity

- Run ID: `legacy-dashboard-complete-application-demo-v1-2026-09-01-013227`
- Project ID: `legacy-dashboard-complete-application-demo-v1`
- Analysis date: 2026-08-31
- Canonical artifacts examined: `knowledge-graph.json`, `facts.json`, `roslyn-semantic-all.json`, `source-inventory.json`, `framework-detection.json`, `graph-run-status.json`, and `review-metadata.json`.
- All JSON artifacts parsed. Every project-bearing artifact has the expected project ID. `artifacts/knowledge-graph/latest/` is byte-identical to this run for every JSON artifact.
- This is a read-only forensic gate. No source file, canonical graph artifact, Neo4j data, or analyzer code was changed.

## Graph and evidence integrity

| Check | Result |
| --- | ---: |
| Nodes | 4,878 |
| Relationships | 5,148 |
| Review warnings | 4,483 |
| Broken relationship endpoints | 0 |
| Duplicate node IDs | 0 |
| Duplicate relationships (`type`, `source`, `target`) | 0 |
| Nodes without evidence | 0 |
| Relationships without evidence | 0 |
| Invalid evidence paths, hashes, or line ranges | 0 |
| Orphan nodes | 377 |
| C# nodes classified as Angular/AngularJS | 0 |
| JSON validity | PASS |

The orphan count is reported for review only. These nodes have valid evidence and are not broken relationship endpoints. The graph's own validation reports zero evidence gaps and the source inventory is complete: 2,384 selected files, zero extraction warnings, 44 explicit opaque dependencies, and `complete_with_opaque_dependencies` coverage.

## Roslyn semantic resolution

| Measure | Count |
| --- | ---: |
| Total Roslyn facts | 7,373 |
| Compiler-proven occurrences | 3,029 |
| Total unresolved occurrences | 4,344 |
| Unique unresolved diagnostics | 6 |
| `COMPILATION_ERROR` | 3,701 |
| `PROJECT_LOAD_FAILURE` | 534 |
| `OVERLOAD_RESOLUTION` | 107 |
| `UNKNOWN` | 2 |
| Roslyn analyzer defects proven by these diagnostics | 0 |
| Explained limitations | 4,342 |
| Roslyn runtime warnings | 0 |
| Roslyn analyzer-defect warnings | 0 |
| Roslyn explained warnings | 72 |
| Roslyn unknown warnings | 0 |

The 72 Roslyn warnings are 71 `PROJECT_LOAD_FAILURE` warnings for legacy project formats/dependencies and one `SYNTHETIC_FALLBACK` warning. The 3,701 compilation-error occurrences, 534 project-load failures, and 107 overload-resolution occurrences are explained limitations of the available legacy build context; they are not silently accepted as resolved. The two `UNKNOWN` unresolved occurrences remain a readiness concern.

Coverage modes, counted from the Roslyn semantic artifact, are 1,004 compiler-proven facts under partial project compilation, 3,778 partial-project occurrences, 2,591 synthetic-fallback occurrences, and 0 structural-only Roslyn occurrences. The separate canonical fact artifact has 1,383 structural facts, 91 deterministic crash-fallback facts, and 18 framework-proven facts.

## Framework and API mapping forensics

Framework detection has source evidence for ASP.NET MVC/Razor, .NET API, AngularJS, and TypeScript. No C# graph record is classified as Angular or AngularJS.

| Measure | Count |
| --- | ---: |
| Backend endpoint facts | 4 |
| Frontend API-call facts | 44 |
| Proven API mappings | 0 |
| Ambiguous API mappings | 0 |
| Dynamic API URL warnings | 22 |
| External API calls | 1 |
| No-backend-route calls | 1 |
| Unresolved API calls | 42 |

The 44 API-call facts reconcile as 32 structural Tree-sitter calls without a proven HTTP-method/route pair, 10 framework-proven literal calls to `GET /api/users/current/{tenant,user,claims}` that cannot map because the endpoint catalog is incomplete, one literal `GET /clinics` with no proven backend route, and one external placeholder URL. Dynamic URLs are represented by 22 review warnings rather than API-call facts and therefore are not added to the 44-fact total.

The zero proven mappings are an analyzer defect, not evidence that the application has no frontend-to-backend contracts. The run contains only four endpoint facts: two incorrectly normalized `UsersController` routes without their `api/users` class prefix and two `BandController` routes. Direct source evidence finds 12 controllers with `[Route("api/[controller]")]` and 55 `[Http...]` method attributes. For example, `src/MyHealth.API/Controllers/UsersController.cs` proves `[Route("api/[controller]")]`, `[HttpGet("current/user")]`, `[HttpGet("current/claims")]`, and `[HttpGet("current/tenant")]`; the frontend has ten literal calls to those normalized routes.

The generic cause is the current class-attribute regular expression: `[^\]]+` ends at the `]` inside the literal `[controller]`, so it does not retain the class route attribute. In addition, the conventional `/Api/` path fallback is case-sensitive and does not recognize `src/MyHealth.API/...`. These generic defects prevent complete endpoint discovery and contract mapping. They must be fixed and regression-tested before a new run is eligible for Phase 2.

API contracts currently present are incomplete but evidence-backed: four endpoint response contracts (`FileContentResult`, `JsonResult`, `RootObject`, and `void`) and one explicit request-parameter contract (`value` on `POST /api/Band/{value}`). No request or response contract must be inferred for endpoints omitted by the faulty catalog.

## Razor validation

Three Razor `@model` facts are present, with two corresponding `USES_VIEW_MODEL` graph relationships: `LoginViewModel`, `IEnumerable<ClinicAppointment>`, and `AppState`. There are zero Razor action-link facts and zero `CALLS_ACTION` relationships. A repository-wide search found zero static `Html.Action`, `Html.ActionLink`, or `Url.Action` invocations matching the supported literal two-argument pattern. Therefore, the zero Razor-action count is an evidenced source limitation for this rule, not an analyzer defect.

## Readiness decision

`KG_READINESS_STATUS: NOT_READY`

`ANALYZER_FIX_REQUIRED: YES`

`NEXT_ACTION: TARGETED_ANALYZER_FIX`

The graph is structurally valid and has complete evidence provenance, but it is not semantically trustworthy enough for Phase 2 because a generic route-attribute parser defect suppresses the endpoint catalog and all proven frontend-to-backend mappings. Application Understanding remains `STALE`; it must not be rerun or treated as current until the generic route analyzer is repaired, the KG is regenerated into a new immutable run, and this forensic gate passes on that new run.

## Test result

`python -m pytest -q`: **79 passed, 2 skipped, 0 failed, 0 errors**.

