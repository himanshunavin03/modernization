# Final Knowledge Graph Readiness Analysis

## Run identity

- Immutable run: `legacy-dashboard-complete-application-demo-v1-2026-09-01-034128`
- Project ID: `legacy-dashboard-complete-application-demo-v1`
- All calculations use artifacts inside this immutable run. Canonical files in `artifacts/knowledge-graph/latest/` were byte-identical to this run before readiness reports were copied.
- Source inventory: 2,384 files. Pipeline facts: 8,929. Normalized structural/framework facts in `facts.json`: 1,556.
- No source modification, Neo4j load, Application Understanding execution, external LLM call, or modernization work occurred.

## Graph and evidence integrity

| Check | Actual result |
| --- | ---: |
| Nodes | 4,931 |
| Relationships | 5,205 |
| Duplicate node IDs | 0 |
| Duplicate relationships (`type`, `source`, `target`) | 0 |
| Broken relationship endpoints | 0 |
| Nodes without evidence | 0 |
| Relationships without evidence | 0 |
| Invalid evidence paths | 0 |
| Invalid source hashes | 0 |
| Invalid evidence line ranges | 0 |
| C# records misclassified as Angular/AngularJS | 0 |
| Orphan nodes | 377 |

`GRAPH_INTEGRITY=PASS` and `EVIDENCE_INTEGRITY=PASS`. The 377 orphan nodes are valid evidence-bearing records with no incident edge, not broken references. Extraction coverage is `complete_with_opaque_dependencies`: zero extraction failures and 44 explicitly opaque dependency records.

## Roslyn final status

| Classification | Count |
| --- | ---: |
| `COMPILATION_ERROR` | 3,701 |
| `PROJECT_LOAD_FAILURE` | 534 |
| `OVERLOAD_RESOLUTION` | 107 |
| `INACCESSIBLE` | 2 |
| `UNKNOWN` | 0 |
| Total unresolved occurrences | 4,344 |

The two inaccessible records are `MedicineToNameWithDosisConverter.Convert` at `src/MyHealth.Client.iOS/Views/HomeView.cs:116` and `TimeOfDayToStringConverter.Convert` at line 119. Roslyn reports `CandidateReason=Inaccessible` and a fully qualified candidate for each. Both converters declare `protected override Convert(...)`; `HomeView.UpdateAppleWatch` is not a derived converter context and cannot call those methods. The facts remain unresolved at confidence `0.0`. The graph contains zero guessed `INVOKES` edges to either converter method.

The remaining Roslyn limitations are explicit and evidence-backed: legacy compilation errors, unavailable/unsupported legacy project loading, overload-resolution failures, and two source-level inaccessible calls. They are not represented as proven semantics.

## Framework and API contracts

| Classification | Count |
| --- | ---: |
| Backend endpoint facts | 58 |
| Frontend API-call facts | 44 |
| Proven API mappings | 10 |
| Ambiguous mappings | 0 |
| Dynamic URL warnings | 22 |
| External API | 1 |
| No backend route | 1 |
| Unresolved structural calls | 32 |

Fifty-five endpoints across 12 controllers retain `controller_route_template=api/[controller]`; no normalized route retains an unresolved `[controller]` token. HTTP methods are 42 GET, 8 POST, 4 PUT, and 4 DELETE. Every mapping fact is `PROVEN` and has source evidence. No application-specific route, controller, URL, or source-path condition exists in the reusable analyzer.

The 44 frontend calls reconcile as 10 proven mappings, one external placeholder API, one literal route with no backend match, and 32 structural calls without a framework-proven HTTP method. The 22 dynamic URL occurrences are review warnings rather than API-call facts. None of these limitations is guessed into a mapping.

## Razor evidence

Razor evidence remains truthful: 8 Razor views, 15 partial views, 4 layouts, 3 `@model` facts, and 2 unique `USES_VIEW_MODEL` relationships. There are no supported static action-link facts and no `CALLS_ACTION` relationships; source inspection found no supported literal action-link pattern, so zero action mappings is not an analyzer defect.

## Remaining limitations and decision

- Roslyn retains 4,344 unresolved occurrences, all assigned deterministic categories; `UNKNOWN=0`.
- Legacy project/reference and partial-compilation limitations remain visible rather than being promoted to compiler-proven facts.
- API mapping retains 22 dynamic URL warnings, one external endpoint, one unmatched literal route, and 32 structural calls without a proven verb.
- Forty-four third-party/generated/minified files remain explicit opaque dependencies without claimed semantic understanding.

`GENERIC_ANALYZER_DEFECTS=0`

`UNKNOWN_BLOCKERS=0`

`READINESS=READY_WITH_EXPLAINED_LIMITATIONS`

`APPLICATION_UNDERSTANDING_STATUS=STALE`

`NEXT_ACTION=RERUN_UNDERSTAND_APPLICATION`

Application Understanding was not run in this task.

## Test evidence

- Focused Roslyn/framework suite: 17 collected, 16 passed, 1 skipped.
- Complete suite: 90 collected, 88 passed, 2 skipped, 0 failed.

