# HealthClinic Dashboard End-to-End Context Graph

## Current Result

The reusable `end_to_end_context_flow` profile and deterministic context-linking implementation are complete. The new isolated graph was generated as `healthclinic-dashboard-end-to-end-demo-v1` with `scope_complete` coverage and zero extraction warnings. It was **not** loaded into Neo4j and no visualization export was generated, because this terminal cannot resolve `dotnet` or `docker`.

## Scope

- Selected UI files: 24, role `transform_ui`.
- Selected backend/API files: 2, role `preserve_backend`: `ReportsController.cs` and `UsersController.cs`.
- Selected domain/data files: 6, role `preserve_domain_data`: `ReportsRepository.cs`, `MyHealthContext.cs`, `ClinicSummary.cs`, `ExpensesSummary.cs`, `PatientsSummary.cs`, and `ApplicationUser.cs`.
- No unrelated API controller or data project path is selected by `config/profiles/healthclinic-dashboard-end-to-end.yaml`.

## Proven and Unresolved Paths

Source evidence establishes the Dashboard service calls `/api/reports/clinicsummary`, `/api/users/current/tenant`, and dynamic year-concatenated reports paths. Source route evidence identifies the corresponding Reports and Users controller actions.

The required Roslyn semantic enrichment was skipped because `dotnet` is unavailable in this terminal. Therefore no controller-to-repository/context link is claimed as proven, no `RESOLVES_TO_ENDPOINT` or `PRESERVES_CONTRACT` link is accepted for the new graph, and all four Dashboard API calls remain review warnings. This is intentional: no relationship was inferred.

## Boundaries

Only `transform_ui` records are eligible for Angular generation. API, domain, and data records are marked `preserve_backend` or `preserve_domain_data` with `eligible_for_angular_generation: false`. The graph metadata records `modernization_scope: end_to_end_context`, `transform_boundary: ui_only`, and `backend_preservation_boundary: api_domain_data`.

## Verification

- Generated graph: 150 nodes, 217 edges, 17 review warnings.
- Coverage: `scope_complete`; extraction warnings: 0.
- Neo4j: not attempted because `docker` is unavailable in this terminal.
- Visualization: not generated; the generalized adapter requires a specified project ID and gates on coverage, extraction warnings, and project isolation, but export is deferred until Roslyn and Neo4j verification are complete.
- Source integrity: all 2,384 saved-inventory source hashes match after the run.
- Tests: `python -m pytest -q` returned `42 passed, 2 skipped`.

## Customer Explanation

This graph preserves the Legacy ASP.NET MVC/Razor and Legacy AngularJS 1.x Dashboard modernization boundary while showing only verified read-only backend context. It will not represent API/domain/data code as Angular work. The backend path must be rerun with Roslyn and Neo4j available before it can be used as an end-to-end customer graph.

## Repository and Data Flow Update

The selected Reports flow now exposes three source-backed read-only paths: `GetClinicSummaryAsync`, `GetExpensesSummaryAsync`, and `GetPatientsSummaryAsync`. Each controller action invokes a distinct `RepositoryMethod` record, which executes an `EF/LINQ query` record in `ReportsRepository`, returns its selected model (`ClinicSummary`, `ExpensesSummary`, or `PatientsSummary`), and depends on `MyHealthContext`. Source evidence is `Where` plus `OrderBy` and `FirstOrDefaultAsync` or `ToListAsync`; no literal raw SQL or SQL execution evidence was found, so no SQL node is shown.

The regenerated graph has 156 nodes, 232 edges, 17 warnings, `scope_complete` coverage, and zero extraction warnings. The read-only visualization export was regenerated. Neo4j reload remains blocked by the previously recorded local authentication failure; no load claim is made.

Final validation: Roslyn succeeded and Neo4j loaded `healthclinic-dashboard-end-to-end-demo-v1` after the local password was corrected. The earlier unavailable-CLI and authentication failures are historical only.
