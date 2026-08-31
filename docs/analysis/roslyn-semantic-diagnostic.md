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

## Deterministic API and Readiness Proofs

Generic route normalization and matching now prove `GET /api/customers/123` maps only to a unique `GET /api/customers/{id}` endpoint, retaining frontend and backend evidence. Query strings, base URLs, trailing slashes, route-template formatting, HTTP verb mismatches, and ambiguous endpoints are handled deterministically; ambiguous or mismatched routes produce no mapping.

The readiness model now separates pipeline execution from graph readiness. A successful pipeline is `READY` only with valid integrity and no analyzer-defect or unknown blockers; known explained limitations produce `READY_WITH_EXPLAINED_LIMITATIONS`; failed execution, integrity failures, analyzer defects, or unknowns produce `NOT_READY`.

These focused proofs pass. Multi-project project-reference and failed-project workspace/fallback fixtures are still required, so the overall pre-regeneration decision remains **NOT SAFE TO REGENERATE**.

## FINAL ENGINE PROOF

The generic offline fixtures now prove the outstanding project-aware semantic-engine gates without regenerating an application graph.

- `roslyn-multiproject` opens a solution containing `Fixture.Web -> Fixture.Business -> Fixture.Data`; all three C# files are `PROJECT_COMPILATION` with confidence `1.0` and no synthetic fallback. It proves declarations, interface dispatch (`IStore.Read`), base-method invocation (`BaseService.Format`), cross-project construction (`Service(IStore)` and `Store()`), overload selection (`Service.Load(int)`), generic extension resolution (`StoreExtensions.Identity<T>`), and parameter/return type references. Stable declaration identities are unique.
- `roslyn-fallback` retains two project-owned files. The broken referenced project is explicitly `PARTIAL_PROJECT_COMPILATION`, preserving conservative compiler facts at confidence `0.8`; its unresolved item is classified `COMPILATION_ERROR`. The single C# file outside any project receives the only `SYNTHETIC_FALLBACK`, with confidence at most `0.6` and a source-backed `PROJECT_LOAD_FAILURE` unresolved diagnostic. No missing invocation target is marked proven or guessed.
- The helper opens solutions before individual projects, preventing duplicate-project workspace failures and preserving real cross-project compilation contexts. Reduced extension symbols are normalized to their declared extension method, so relationship identities retain the defining type rather than only the receiver type.
- Focused project-aware, API mapping, and readiness tests pass: `11 passed`. The full regression suite remains required before a complete-application regeneration is authorized.

Fixture-level result: **SAFE TO REGENERATE** once the full regression suite also passes. This conclusion proves the engine behavior only; it does not claim a new application extraction, Neo4j load, or viewer export.

## Complete Regression Authorization

On the post-`1438bf7` baseline, the complete Python suite was collected with `python -m pytest --collect-only -q`: 68 tests spanning inventory, framework detection, isolated Tree-sitter extraction, facts/graph normalization and validation, project-aware Roslyn semantics, multi-project and fallback fixtures, API mapping, readiness, CLI/agent orchestration, artifact validation, and viewer launch/export safety. `& 'C:\Program Files\dotnet\dotnet.exe' build tools\Polaris.RoslynAnalyzer\Polaris.RoslynAnalyzer.csproj` succeeded with zero warnings and zero errors. `python -m pytest -q` completed with `66 passed, 2 skipped, 0 failed, 0 errors` in `17.06s`.

No failure was discovered, classified, or fixed. The four focused gates remain PASS, the complete regression suite is PASS, and there are zero known generic analyzer defects and zero unknown blockers in the verified fixture/test scope. This test-only task did not run an application create-knowledge-graph workflow, change `artifacts/knowledge-graph/latest/`, create an immutable complete-application run, or load Neo4j. **SAFE TO REGENERATE** is now authorized only for a separately approved task.
