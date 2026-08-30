# HealthClinic Dashboard Scope-Complete Graph Validation v3

## Scope

- Project ID: `healthclinic-dashboard-scope-demo-v3`
- Source root: `source/HealthClinic.biz`
- Profile: `config/profiles/healthclinic-dashboard.yaml`
- Scope: `healthclinic-dashboard-modernization-flow` (`selected_modernization_flow`)
- Selected files: 24
- Out-of-scope audited files: 2,360
- Scoped graph File nodes: 24

## Counts

- Audited files: 2,384
- Facts: 88
- Nodes: 119
- Edges: 167
- Total warnings: 11
- Extraction warnings: 0
- Review warnings: 11
- Coverage: `scope_complete`
- Roslyn: succeeded
- Neo4j: skipped

## Warning Summary

- In-scope isolated extraction failures: 0
- Parser-skipped selected files: 0
- Proven out-of-scope dependency references: 0
- Out-of-scope files remain visible in `source-inventory.json` and scope metadata; none was added as a File node to `knowledge-graph.json`.

## Relationship Examples

- `DashboardController` (Controller) `DECLARES` `Index` (Action)
- `src/MyHealth.Web/Controllers/DashboardController.cs` (File) `DECLARES` `Authorize` (AuthorizationPolicy)
- `src/MyHealth.Web/Views/Dashboard/_Content.cshtml` (File) `CONTAINS_CONTROL` `loading-overlay` (UIControl)
- `moduleName` (AngularModule) `CONFIGURES_ROUTE` `dashboard` (Route)
- `src/MyHealth.Web/content/app/components/dashboard/services/dashboardService.js` (File) `CALLS_API` `'/api/reports/expenses/' + year` (ApiCall)

## Source Integrity

- Files checked: 2,395
- Per-file aggregate source-tree SHA-256 before and after the final graph-only run: `c8b0e9f1be7724d5a15bb0a6a4ccda73920c653ff65181cc39ba96adbdc795d5`
- Result: unchanged

## Readiness

- Ready for Neo4j Dashboard modernization-flow visual demo. Load only `healthclinic-dashboard-scope-demo-v3` after Docker Neo4j is installed and started.
