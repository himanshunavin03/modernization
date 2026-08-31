# Knowledge Graph Improvement Report

Previous immutable run: `legacy-dashboard-complete-application-demo-v1-2026-08-31-163453`
New run: `legacy-dashboard-complete-application-demo-v1-2026-08-31-171653`

| Metric | Previous | New | Difference | Explanation |
| --- | ---: | ---: | ---: | --- |
| nodes | 5397 | 5430 | +33 | Measured deterministic graph change; review required. |
| relationships | 6068 | 5524 | -544 | -544: DECLARES decreased by 551 as ordinary C# Controller/Action misclassifications became Type/Method; INVOKES +2 and RETURNS_TYPE +5. |
| review_warning_nodes | 184 | 184 | +0 | Unchanged. |
| total_warnings | 2082 | 2082 | +0 | Unchanged. |
| roslyn_unresolved_symbols | 2045 | 2045 | +0 | Unchanged. |
| unresolved_invocation_targets | 1527 | 1527 | +0 | Unchanged. |
| unresolved_parameter_types | 239 | 239 | +0 | Unchanged. |
| unresolved_return_types | 61 | 61 | +0 | Unchanged. |
| analyzer_defect_unresolved | 2045 | 2045 | +0 | Synthetic all-source Roslyn compilation lacks project/NuGet/framework context; unresolved facts remain analyzer defects until project-aware analysis is implemented. |
| unknown_unresolved | 0 | 0 | +0 | Unchanged. |
| duplicate_nodes | 0 | 0 | +0 | Unchanged. |
| orphan_nodes | 533 | 534 | +1 | Measured deterministic graph change; review required. |
| broken_relationships | 0 | 0 | +0 | Unchanged. |
| missing_node_evidence | 0 | 0 | +0 | Unchanged. |
| missing_relationship_evidence | 0 | 0 | +0 | Unchanged. |
| framework_conflicts | 0 | 0 | +0 | C# Angular conflict check passed. |
| api_calls_discovered | 21 | 21 | +0 | Unchanged. |
| api_calls_mapped_to_backend | 0 | 0 | +0 | Unchanged. |

## Integrity

JSON parsing passed for both runs. No duplicate IDs, broken relationship targets, or missing evidence were found. Orphan nodes are reported, not removed.

## Runtime Status

Tree-sitter extraction completed with zero extraction warnings. Roslyn completed but its synthetic compilation is a known project-context defect. LSP was unavailable. Both archived secret scans passed.

## Readiness

**NOT READY.** The complete graph has no deterministic frontend API-to-backend endpoint mapping and 2,045 unresolved Roslyn facts caused by the known synthetic-compilation analyzer defect. No warning was suppressed.
