# HealthClinic Dashboard Clean Graph Validation

## Scope

- Project ID: `healthclinic-dashboard-clean-demo`
- Source root: `source/HealthClinic.biz`
- Profile: `config/profiles/healthclinic-dashboard.yaml`
- Selected paths exclude `src/MyHealth.Web/Views/Home/Index.cshtml`.

## Counts

- Files: 2,384
- Facts: 6,967
- Nodes: 4,597
- Edges: 4,095
- Total warnings: 2,055
- Extraction warnings: 0
- Roslyn: succeeded
- Neo4j: skipped

## Warning Summary

- Parser-skipped files: 0
- The profile-scoped graph is ready for Neo4j visual-demo loading.

## Relationship Examples

- `DashboardController` (Controller) `DECLARES` `Index` (Action)
- `Authorize` (AuthorizationPolicy) `PROTECTS` `DashboardController` (Controller)
- `src/MyHealth.Web/Views/Dashboard/_Content.cshtml` (File) `CONTAINS_CONTROL` `loading-overlay` (UIControl)
- `moduleName` (AngularModule) `CONFIGURES_ROUTE` `dashboard` (Route)
- `src/MyHealth.Web/content/app/components/dashboard/services/dashboardService.js` (File) `CALLS_API` `'/api/reports/expenses/' + year` (ApiCall)

## Source Integrity

- Files hashed before and after: 2,395
- SHA-256 before and after: `32622067768af05d42ef778147e5e45beae2b542fba2aba03fc9ec78fc55ea1c`
- Result: unchanged
