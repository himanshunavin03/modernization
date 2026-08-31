# Knowledge Graph Readiness Analysis

## Scope And Method

- Analyzed immutable run `legacy-dashboard-complete-application-demo-v1-2026-08-31-184436` at commit `922529974b5eb084945933befbf80faca3681e61`.
- Read only canonical `roslyn-semantic.json`, `roslyn-semantic-all.json`, `facts.json`, `knowledge-graph.json`, `knowledge-graph-validation.json`, `graph-run-status.json`, `review-metadata.json`, `framework-detection.json`, and `source-inventory.json`.
- Compared invocation signatures (source path, line, column, kind, target) with immutable run `legacy-dashboard-complete-application-demo-v1-2026-08-31-180814`. Both inventories contain 2,384 identical paths and hashes.
- No graph/fact JSON was changed, no graph was regenerated, and Neo4j was not contacted.

## Canonical Run

| Metric | Result |
| --- | ---: |
| Files | 2,384 |
| Facts | 8,847 |
| Nodes | 4,868 |
| Relationships | 5,124 |
| Review warnings | 4,453 |
| Tree-sitter warnings | 0 |
| Roslyn runtime/workspace warnings | 72 |
| Opaque dependencies | 44 |
| Coverage status | `complete_with_opaque_dependencies` |

All expected artifacts parse as JSON where applicable. Validation reports no missing artifacts or JSON errors, zero secret findings, zero nodes without evidence, and zero relationships without evidence.

## Unresolved Semantics

`unresolved_analysis` reconciles exactly: 4,344 occurrences and 4,344 unique stable diagnostics.

| Classification | Count |
| --- | ---: |
| `ANALYZER_DEFECT` | 0 |
| `PROJECT_LOAD_FAILURE` | 534 |
| `MISSING_PROJECT_REFERENCE` | 0 |
| `MISSING_PACKAGE` | 0 |
| `MISSING_ASSEMBLY` | 0 |
| `MISSING_TARGETING_PACK` | 0 |
| `MISSING_WORKLOAD` | 0 |
| `COMPILATION_ERROR` | 3,701 |
| `EXTERNAL_LIBRARY` | 0 |
| `FRAMEWORK_REFERENCE` | 0 |
| `SOURCE_NOT_PRESENT` | 0 |
| `GENERATED_CODE` | 0 |
| `DYNAMIC_OR_REFLECTION` | 0 |
| `CONDITIONAL_COMPILATION` | 0 |
| `EXTENSION_METHOD_RESOLUTION` | 0 |
| `INHERITED_MEMBER_RESOLUTION` | 0 |
| `INTERFACE_DISPATCH` | 0 |
| `GENERIC_RESOLUTION` | 0 |
| `OVERLOAD_RESOLUTION` | 107 |
| `LEGITIMATELY_UNRESOLVED` | 0 |
| `UNKNOWN` | 2 |

The two `UNKNOWN` items are `Inaccessible` candidate-symbol cases in `src/MyHealth.Client.iOS/Views/HomeView.cs` (lines 116 and 119). Each has one named, source-backed candidate converter method. They are 0.046% of unresolved semantics, not missing source or a guessed edge; no `INVOKES` relationship was created from either candidate.

Unresolved kinds are: 2,098 invocations, 1,236 type references, 533 methods, 438 properties, and 39 actions. The 4,342 non-`UNKNOWN` results are explained by partial compilation, explicit fallback, or overload resolution. No classifier category was changed during this analysis.

## Semantic Coverage

The C# inventory and Roslyn ownership records both total 384 files.

| Provenance | Files | Coverage |
| --- | ---: | ---: |
| `PROJECT_COMPILATION` | 0 | 0.00% |
| `PARTIAL_PROJECT_COMPILATION` | 277 | 72.14% |
| `SYNTHETIC_FALLBACK` | 107 | 27.86% |
| `STRUCTURAL_ONLY` | 0 | 0.00% |
| Unowned | 107 | 27.86% |

Roslyn fact provenance is 4,782 partial-project facts and 2,591 synthetic-fallback facts; there are no structural-only Roslyn facts. The artifact field named `compiler_proven_files` is 277, but its documented implementation includes partial project compilations; the explicit analysis-mode breakdown above is used for this report.

## Project Hotspots

Target framework is not emitted by the immutable artifact, so it is recorded as `not recorded`, rather than inferred.

| Project | Target framework | Load / compilation | Source files | Partial / fallback | Unresolved | Workspace warnings | Primary classification |
| --- | --- | --- | ---: | --- | ---: | ---: | --- |
| MyHealth.Client.iOS | not recorded | loaded / partial | 44 | 44 / 0 | 1,001 | 4 | `COMPILATION_ERROR` |
| MyHealth.Client.Core | not recorded | loaded / partial | 77 | 77 / 0 | 841 | 22 | `COMPILATION_ERROR` |
| synthetic-fallback | not applicable | unowned / fallback | 107 | 0 / 107 | 566 | 0 | `PROJECT_LOAD_FAILURE` |
| MyHealth.Client.Droid | not recorded | loaded / partial | 37 | 37 / 0 | 549 | 5 | `COMPILATION_ERROR` |
| MyHealth.Client.Desktop | not recorded | loaded / partial | 50 | 50 / 0 | 522 | 3 | `COMPILATION_ERROR` |
| MyHealth.MobileApp | not recorded | loaded / partial | 17 | 17 / 0 | 241 | 2 | `COMPILATION_ERROR` |
| MyHealth.Client.W10.UWP | not recorded | loaded / partial | 25 | 25 / 0 | 227 | 3 | `COMPILATION_ERROR` |
| MyHealth.Client.HealthCloudAPI | not recorded | loaded / partial | 15 | 15 / 0 | 162 | 2 | `COMPILATION_ERROR` |
| GCMClient Sample | not recorded | loaded / partial | 4 | 4 / 0 | 76 | 1 | `COMPILATION_ERROR` |
| MyHealth.UITest.Droid | not recorded | loaded / partial | 2 | 2 / 0 | 54 | 2 | `COMPILATION_ERROR` |

Unresolved results are strongly concentrated in legacy mobile, desktop, and old project-load contexts, not distributed across a normally complete modern compilation.

## Roslyn Runtime Warnings

All 72 warnings reconcile: 71 `PROJECT_LOAD_FAILURE` records and one expected `SYNTHETIC_FALLBACK` summary record.

| Warning disposition | Count |
| --- | ---: |
| `ANALYZER_DEFECT` | 0 |
| `MISSING_TARGETING_PACK` | 0 |
| `MISSING_WORKLOAD` | 0 |
| `MISSING_ASSEMBLY` | 0 |
| `MISSING_PACKAGE` | 0 |
| `MISSING_PROJECT_REFERENCE` | 23 |
| `UNSUPPORTED_PROJECT_TYPE` | 10 |
| `LEGACY_PROJECT_LOAD_LIMITATION` | 38 |
| `SOURCE_NOT_PRESENT` | 0 |
| `OTHER_EXPLAINED` (`SYNTHETIC_FALLBACK`) | 1 |
| `UNKNOWN` | 0 |

The legacy limitations are explicit `Compile`-target and MSBuild API failures; unsupported project types are `.njsproj`, `.xproj`, and `.deployproj`. This is environment/project compatibility evidence, not a hidden analyzer crash.

## Invocation Detail And Delta

Of 2,098 unresolved invocations: 1,989 have no candidates, 90 have one candidate, and 19 have multiple candidates. Candidate reasons are `NO_CANDIDATES` 1,989, `OverloadResolutionFailure` 107, and `Inaccessible` 2. Candidate symbols remain evidence only and do not create proven `INVOKES` edges.

The top unresolved targets are `set.Bind` (81), `Request.GetTenant` (25), `NotImplementedException` (16), `Build` (13), `TimeSpan.FromSeconds` (13), `context.SaveChanges` (13), `Debug.WriteLine` (12), `c.Text` (12), `string.Format` (11), and `DateTime` (10). The full top-25 extraction was inspected; these targets occur in the same partial mobile/desktop or fallback contexts summarized above. A small set of framework, external, UI binding, and data-context calls accounts for a material share, but most targets are distinct.

| Target | Count | Project | Classification | Candidate reason | Analysis mode |
| --- | ---: | --- | --- | --- | --- |
| `set.Bind` | 81 | MyHealth.Client.Droid | `COMPILATION_ERROR` | `NO_CANDIDATES` | `PARTIAL_PROJECT_COMPILATION` |
| `Request.GetTenant` | 25 | synthetic-fallback | `PROJECT_LOAD_FAILURE` | `NO_CANDIDATES` | `SYNTHETIC_FALLBACK` |
| `NotImplementedException` | 16 | MyHealth.Client.HealthCloudAPI | `COMPILATION_ERROR` | `NO_CANDIDATES` | `PARTIAL_PROJECT_COMPILATION` |
| `Build` | 13 | synthetic-fallback | `OVERLOAD_RESOLUTION` | `OverloadResolutionFailure` | `SYNTHETIC_FALLBACK` |
| `TimeSpan.FromSeconds` | 13 | MyHealth.Client.Core | `COMPILATION_ERROR` | `NO_CANDIDATES` | `PARTIAL_PROJECT_COMPILATION` |
| `context.SaveChanges` | 13 | synthetic-fallback | `PROJECT_LOAD_FAILURE` | `NO_CANDIDATES` | `SYNTHETIC_FALLBACK` |
| `Debug.WriteLine` | 12 | MyHealth.Client.Droid | `COMPILATION_ERROR` | `NO_CANDIDATES` | `PARTIAL_PROJECT_COMPILATION` |
| `c.Text` | 12 | MyHealth.UITest.Droid | `COMPILATION_ERROR` | `NO_CANDIDATES` | `PARTIAL_PROJECT_COMPILATION` |
| `string.Format` | 11 | MyHealth.Client.Droid | `COMPILATION_ERROR` | `NO_CANDIDATES` | `PARTIAL_PROJECT_COMPILATION` |
| `DateTime` | 10 | MyHealth.Client.Core | `COMPILATION_ERROR` | `NO_CANDIDATES` | `PARTIAL_PROJECT_COMPILATION` |
| `set.Apply` | 10 | MyHealth.Client.Droid | `COMPILATION_ERROR` | `NO_CANDIDATES` | `PARTIAL_PROJECT_COMPILATION` |
| `app.WaitForElement` | 9 | MyHealth.UITest.Droid | `COMPILATION_ERROR` | `NO_CANDIDATES` | `PARTIAL_PROJECT_COMPILATION` |
| `string.IsNullOrEmpty` | 9 | MyHealth.Client.iOS | `COMPILATION_ERROR` | `NO_CANDIDATES` | `PARTIAL_PROJECT_COMPILATION` |
| `HttpClient` | 8 | MyHealth.Client.HealthCloudAPI | `COMPILATION_ERROR` | `NO_CANDIDATES` | `PARTIAL_PROJECT_COMPILATION` |
| `_context.SaveChangesAsync` | 8 | synthetic-fallback | `PROJECT_LOAD_FAILURE` | `NO_CANDIDATES` | `SYNTHETIC_FALLBACK` |
| `app.Tap` | 8 | MyHealth.UITest.Droid | `COMPILATION_ERROR` | `NO_CANDIDATES` | `PARTIAL_PROJECT_COMPILATION` |
| `AndHUD.Shared.Show` | 7 | AndHUD.Sample | `COMPILATION_ERROR` | `NO_CANDIDATES` | `PARTIAL_PROJECT_COMPILATION` |
| `JObject` | 7 | MyHealth.Client.iOS | `COMPILATION_ERROR` | `NO_CANDIDATES` | `PARTIAL_PROJECT_COMPILATION` |
| `Uri.EscapeUriString` | 7 | MyHealth.Client.HealthCloudAPI | `COMPILATION_ERROR` | `NO_CANDIDATES` | `PARTIAL_PROJECT_COMPILATION` |
| `View` | 7 | synthetic-fallback | `PROJECT_LOAD_FAILURE` | `NO_CANDIDATES` | `SYNTHETIC_FALLBACK` |
| `query.AppendFormat` | 7 | MyHealth.Client.HealthCloudAPI | `COMPILATION_ERROR` | `NO_CANDIDATES` | `PARTIAL_PROJECT_COMPILATION` |
| `response.EnsureSuccessStatusCode` | 7 | MyHealth.Client.Core | `COMPILATION_ERROR` | `NO_CANDIDATES` | `PARTIAL_PROJECT_COMPILATION` |
| `string.IsNullOrWhiteSpace` | 7 | MyHealth.Client.iOS | `COMPILATION_ERROR` | `NO_CANDIDATES` | `PARTIAL_PROJECT_COMPILATION` |
| `Log.Info` | 6 | Sample | `COMPILATION_ERROR` | `NO_CANDIDATES` | `PARTIAL_PROJECT_COMPILATION` |
| `System.Diagnostics.Debug.WriteLine` | 6 | MyHealth.Client.Core | `COMPILATION_ERROR` | `NO_CANDIDATES` | `PARTIAL_PROJECT_COMPILATION` |

| Metric | Previous | Current | Delta |
| --- | ---: | ---: | ---: |
| Unresolved semantics | 4,030 | 4,344 | +314 |
| Unresolved invocations | 1,784 | 2,098 | +314 |

All 314 additional invocation signatures are new representation occurrences: 306 are `PARTIAL_PROJECT_COMPILATION` / `COMPILATION_ERROR`, and 8 are `SYNTHETIC_FALLBACK` / `PROJECT_LOAD_FAILURE`. The source inventory is byte-for-byte unchanged, no delta item is `UNKNOWN`, and no delta item is a new worker failure. Classification: `PROJECT_COMPILATION_CHANGE` and `FALLBACK_CHANGE` caused the engine to represent invocation attempts previously absent from the semantic output; this is not `ANALYZER_REGRESSION`.

## API Mapping

| Metric | Count |
| --- | ---: |
| Frontend API-call facts | 33 |
| Backend endpoint facts | 0 |
| Mapped API calls | 0 |
| Unmapped API calls | 33 |
| Ambiguous API calls | 0 |

Every unmapped API fact is classified without fuzzy matching: 1 `EXTERNAL_API` (`https://YOUR_SERVER.azurewebsites.net/...`), 11 `DYNAMIC_URL` literals/templates, and 21 `NO_BACKEND_ROUTE`. Since the complete graph contains no backend endpoint facts or `RESOLVES_TO_ENDPOINT` relationships, this is an explicit graph limitation. It does not invalidate recorded frontend `CALLS_API` evidence (26 relationships), but it prevents asserting complete frontend-to-backend contract mapping.

## Graph Integrity

| Check | Result |
| --- | ---: |
| JSON integrity / required artifacts | PASS |
| Duplicate nodes | 0 |
| Duplicate relationships (stable source/target/type/properties) | 0 |
| Broken relationship endpoints | 0 |
| Nodes without evidence | 0 |
| Relationships without evidence | 0 |
| Orphan nodes | 377 |
| Framework classification conflicts | 0 |
| C# classified as Angular/AngularJS | 0 |

The 377 orphans are retained, evidenced records rather than broken references; integrity validation does not flag them as invalid. They remain a coverage/review limitation, not a graph corruption defect.

## Decision

`KG_READINESS_STATUS: READY_WITH_EXPLAINED_LIMITATIONS`

`NEXT_ACTION: PHASE_2_APPLICATION_UNDERSTANDING`

The graph is structurally valid, evidence-complete, source-complete, and has zero Tree-sitter failures. There are no analyzer defects and only two insignificant, source-backed `UNKNOWN` inaccessible-member diagnostics. The material limits are explicit: 72.14% of C# files are partial project compilations, 27.86% are fallback, and backend endpoint mapping is absent. Those limits must remain visible in any Phase 2 consumer; the graph is suitable for evidence-led understanding but not for claiming complete backend API contract resolution.
