# Knowledge Graph Readiness Analysis

## Run identity and scope

- Run ID: `legacy-dashboard-complete-application-demo-v1-2026-09-01-032625`
- Project ID: `legacy-dashboard-complete-application-demo-v1`
- Previous run: `legacy-dashboard-complete-application-demo-v1-2026-09-01-013227`
- This report was calculated from the new immutable run only. `artifacts/knowledge-graph/latest/` is byte-identical to the canonical JSON files in this run.
- No Neo4j load occurred. No Application Understanding work occurred. Source inventory paths and hashes are identical to the previous run (2,384 files).

## Integrity and provenance

| Check | Result |
| --- | ---: |
| Nodes | 4,931 |
| Relationships | 5,205 |
| Broken relationship endpoints | 0 |
| Duplicate node IDs | 0 |
| Duplicate relationships (`type`, `source`, `target`) | 0 |
| Nodes without evidence | 0 |
| Relationships without evidence | 0 |
| Invalid evidence paths, hashes, or line ranges | 0 |
| Orphan nodes | 377 |
| C# records classified as Angular/AngularJS | 0 |
| JSON validity | PASS |
| Source inventory/fingerprint change | None |

The 377 orphan nodes are valid evidence-bearing records with no incident relationship. They are not broken references. Extraction coverage is `complete_with_opaque_dependencies`: 2,384 selected files, zero extraction warnings, and 44 explicitly opaque dependency records.

## Targeted defect verification

`DEFECT_1_ROUTE_ATTRIBUTE_BRACKET_PARSING_FIXED: YES`

The deterministic attribute scanner now tracks balanced brackets while inside and outside quoted strings. It preserves `route_template`, `controller_route_template`, `method_route_template`, and `route_token_resolution`. The real-source run has 55 endpoint facts across 12 controllers retaining `controller_route_template = api/[controller]`; it no longer loses the class prefix at the bracket token.

`DEFECT_2_CASE_INSENSITIVE_API_PATH_FIXED: YES`

API path fallback now evaluates complete path segments case-insensitively and recognizes `api`, `.api`, and mixed-case equivalents without matching arbitrary strings containing `api`. Regression tests cover `Product.API`, `Product.Api`, and `Product.api` paths. The real source under `src/MyHealth.API/...` now yields normalized API routes.

## Before and after framework facts

| Measure | Previous | New | Difference | Explanation |
| --- | ---: | ---: | ---: | --- |
| Backend endpoint facts | 4 | 58 | +54 | Balanced class attributes retain `api/[controller]`; async actions are also recognized. |
| Frontend API-call facts | 44 | 44 | 0 | Existing source facts are preserved. |
| Proven API mappings | 0 | 10 | +10 | Literal `GET /api/users/current/{tenant,user,claims}` calls now uniquely match endpoint facts. |
| Graph nodes | 4,878 | 4,931 | +53 | Endpoint and mapping records normalized into the graph. |
| Graph relationships | 5,148 | 5,205 | +57 | Additional endpoint declarations and unique `IMPLEMENTED_BY` relationships. |
| Review warnings | 4,483 | 4,483 | 0 | No warning was suppressed. |

The 10 mapping facts collapse to three unique `IMPLEMENTED_BY` graph edges because multiple source call sites target the same API-call and endpoint nodes. This is graph deduplication, not lost evidence.

## API mapping and contracts

| Classification | Count |
| --- | ---: |
| Proven | 10 |
| Ambiguous | 0 |
| Dynamic URL warnings | 22 |
| External API | 1 |
| No backend route | 1 |
| Unresolved structural calls | 32 |

The 44 API-call facts reconcile as 10 proven, one literal no-backend-route call, one external placeholder URL, and 32 structural calls that lack a framework-proven HTTP method and therefore cannot be mapped safely. Dynamic URLs are separate warnings and are not counted as API-call facts. Remaining non-proven calls are explained by dynamic URL construction, an external placeholder URL, an unmatched literal route, or unsupported structural call syntax without a deterministically proven verb; none is converted to a mapping.

The endpoint catalog contains 49 parameter-bearing endpoint signatures and 38 distinct response-type values. These are source/structural contract fields, not inferred DTOs. The catalog remains subject to the documented Roslyn limitations below.

## Razor and Roslyn

There are three evidence-backed Razor view-model facts and two unique `USES_VIEW_MODEL` edges. There are no static supported Razor action-link calls, so Razor action mappings remain zero without indicating an analyzer defect.

Roslyn remains unchanged from the prior run: 7,373 semantic facts, 3,029 proven occurrences, and 4,344 unresolved occurrences. Of the unresolved occurrences, 3,701 are `COMPILATION_ERROR`, 534 are `PROJECT_LOAD_FAILURE`, 107 are `OVERLOAD_RESOLUTION`, and 2 are `UNKNOWN`. The first three categories are documented environment/source limitations; the two unknown unresolved invocations are in `src/MyHealth.Client.iOS/Views/HomeView.cs` and require further diagnosis. Roslyn warnings remain 71 `PROJECT_LOAD_FAILURE` plus one `SYNTHETIC_FALLBACK` warning.

## Readiness decision

`GENERIC_ANALYZER_DEFECT_REMAINING: NO` for the two targeted ASP.NET route defects.

`KG_READINESS_STATUS: NOT_READY`

`APPLICATION_UNDERSTANDING_STATUS: STALE`

`NEXT_ACTION: ADDITIONAL_DIAGNOSIS`

The targeted route defects are fixed and graph/evidence integrity pass. The graph is still not readiness-approved because two Roslyn unresolved occurrences remain classified `UNKNOWN`. Application Understanding must not be rerun until those are classified or repaired through a separate evidence-backed gate.

## Test evidence

- `python -m pytest tests/test_framework_analyzers.py -q`: **11 passed**
- `python -m pytest -q`: **87 passed, 2 skipped, 0 failed, 0 errors**

