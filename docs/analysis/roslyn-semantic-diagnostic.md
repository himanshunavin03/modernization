# Roslyn Semantic Diagnostic

## Metric Sources

The 23 Roslyn runtime warnings in the verified baseline are workspace/project-load events. The 4,030 unresolved semantic results are per-symbol facts emitted while extracting declarations, parameters, return types, properties, and invocations. They are different populations and must not be compared as duplicate counts.

## Root Cause

Project-aware workspace loading reports legacy project limitations including unavailable `Compile` targets, unresolved project-reference metadata, and old MSBuild API incompatibilities. Those failures left source files outside a real project compilation. The earlier project-aware implementation then skipped their semantic facts, causing lower fact/node/relationship counts and more graph review warnings.

## Generic Repair

The helper now retains a controlled `SYNTHETIC_FALLBACK` only for files not owned by a loaded project compilation. Fallback facts carry `analysis_mode`, `semantic_project_identity`, and lower confidence (`0.6`); compiler-proven project facts retain confidence `1.0`. Workspace diagnostics remain explicit. Every unresolved fact now has a deterministic ID and classification; invocation failures also retain `CandidateReason` and `CandidateSymbols` when Roslyn provides them.

## Baseline Interpretation

The verified baseline had 4,030 unresolved semantic facts, 1,784 unresolved invocations, 39 unresolved parameters, no unresolved returns, 23 workspace warnings, and no evidence gaps. The invocation count can improve while total unresolved grows because project-aware loading changes which files and semantic operations are available. Neither direction is automatically an improvement.

## Readiness

No complete graph was regenerated for this diagnostic task. The new classifier has not yet been exercised on a full run, so the exact classification totals, duplicate/unique count, ownership coverage, API mapping, and remaining `UNKNOWN` count cannot be claimed. The current decision is **NOT SAFE TO REGENERATE** until those gates and dedicated project-aware regression fixtures pass.

## Quality-Gate Output Contract

The Roslyn output now includes `source_ownership` with `PROJECT_OWNED` or `UNOWNED` records, `semantic_coverage` counts for project compilation, synthetic fallback, and structural-only files, and `unresolved_analysis` with total occurrences, unique stable diagnostic IDs, classification totals, and per-occurrence evidence. Classification uses project/fallback mode and Roslyn candidate evidence; unresolved entries without supporting compiler or workspace evidence remain `UNKNOWN` rather than being relabeled.

The new contract is compiled and covered by the existing regression suite, but multi-project project-reference, failed-project fallback, API route-mapping, and readiness-gate fixtures remain required before a complete application regeneration is safe.
