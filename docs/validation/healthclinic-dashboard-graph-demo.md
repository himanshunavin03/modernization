# HealthClinic Dashboard Graph Demo Validation

## Scope And Artifacts

- Project ID: `healthclinic-dashboard-demo`
- Source root: `source/HealthClinic.biz/src/MyHealth.Web`
- Graph run summary: `artifacts/healthclinic-dashboard-demo/graph-run-summary.md`
- Framework detection: `artifacts/healthclinic-dashboard-demo/framework-detection.json`
- Knowledge graph: `artifacts/healthclinic-dashboard-demo/knowledge-graph.json`

## Counts

- Files: 326
- Facts: 321
- Nodes: 518
- Edges: 604
- Total warnings: 120
- Extraction warnings: 1
- Roslyn: succeeded
- Neo4j: skipped

## Framework Detection

- ASP.NET MVC/Razor, deterministic file evidence at `Views/O365Integration/Index.cshtml`

## Relationship Examples

- `DashboardController` (Controller) `DECLARES` `Index` (Action)
- `Authorize` (AuthorizationPolicy) `PROTECTS` `DashboardController` (Controller)
- `moduleName` (AngularModule) `CONFIGURES_ROUTE` `dashboard` (Route)
- `Views/Dashboard/_Content.cshtml` (File) `CONTAINS_CONTROL` `loading-overlay` (UIControl)
- `content/app/components/dashboard/services/dashboardService.js` (File) `CALLS_API` `/api/reports/clinicsummary` (ApiCall)

## Warning Review

- Parser-skipped files: 1
- `Views/Home/Index.cshtml`: HTML worker `abnormal_exit`, diagnostic `Extraction worker exited with code 3221225477.`, status `skipped`.
- Neo4j was not loaded. Review the isolated parser warning before approving any visual demo load.

## Source Integrity

- Files hashed before and after: 326
- SHA-256 before and after: `36548b6c82f3c7e63e988737791fa01deeef5118402b26c38800bc2d00f6fc22`
- Result: unchanged
