# Understand Anything Read-Only Visualization

## Result

Understand Anything is installed only as a local, read-only customer viewer for the already validated `healthclinic-dashboard-scope-demo-v3` graph. Tree-sitter/Roslyn `knowledge-graph.json` and the existing project-scoped Neo4j data remain the source of truth. No Understand Anything analyzer or skill was invoked.

## Upstream Attribution and Installation

- Upstream: `https://github.com/Egonex-AI/Understand-Anything.git`
- Installed checkout: `C:\Users\himan\.understand-anything\repo`
- Installed upstream commit: `ba450c43425f3de6d43daf76526950ad8ca93536`
- Installed plugin version: `2.9.4`
- License: upstream `LICENSE` exists and is MIT.
- Codex links: `C:\Users\himan\.agents\skills\understand-dashboard` and `C:\Users\himan\.understand-anything-plugin` are junctions to the installed upstream plugin.
- The official installer reports that VS Code/Codex must restart to discover the new skills. Do not invoke `$understand` or any other Understand Anything analyzer for this POC.

The installed `2.9.4` plugin has no matching standalone viewer release asset. The official available standalone viewer is `v2.9.0`; it was used only to serve the compatible read-only export on localhost. It does not require an LLM, API key, or source analysis.

## Viewer Schema Mapping

The standalone viewer requires a project directory containing `.ua/knowledge-graph.json` with `project`, `nodes`, `edges`, `layers`, and `tour` fields.

- Canonical node `id`, `name`, evidence, properties, and project ID are copied.
- Canonical `label` is retained as `polarisLabel` and a visible `polaris-label:<label>` tag. A required viewer `type` is deterministically mapped without changing the canonical label.
- Canonical relationship `type` is retained as `polarisRelationshipType` and visible `polaris-relationship:<type>` node tags. A required viewer edge type is mapped deterministically for layout.
- Source path, source line evidence, and review warnings are included in the visible deterministic node summary and retained as metadata.
- The Project Overview displays: `Evidence-backed legacy modernization graph. Tree-sitter/Roslyn source of truth. Review warnings remain visible. No LLM inference.` It also distinguishes Legacy AngularJS 1.x from the Target Angular 22 application.

## Generated Read-Only Data

- Adapter: `tools/export_understand_anything_visualization.py`
- Input: `artifacts/healthclinic-dashboard-scope-demo-v3/knowledge-graph.json`
- Export: `artifacts/healthclinic-dashboard-scope-demo-v3/visualization/.ua/knowledge-graph.json`
- Input eligibility gate: project ID must be `healthclinic-dashboard-scope-demo-v3`, coverage must be `scope_complete`, and extraction warnings must be zero.

## Verification

- Canonical, exported, and served counts match: 123 nodes, 169 edges, and 27 review warnings.
- Exported graph records contain only project ID `healthclinic-dashboard-scope-demo-v3`.
- The full 2,395-file source fingerprint remains `0b92e1701cdd2374e259ea4fed9811b7e20e4719ff8ea70e4a8aa5023cacf2b4`; no `.ua` or `.understand-anything` directory exists under `source/`.
- No `$understand`, `/understand`, analyzer, LLM call, API key, or token was used by the adapter or viewer workflow.
- The standalone viewer returned HTTP 200 from localhost and served the exported graph successfully.

## Launch

```powershell
$env:UNDERSTAND_ACCESS_TOKEN = 'polaris-local-readonly'
npx --yes https://github.com/Egonex-AI/Understand-Anything/releases/download/v2.9.0/understand-anything-viewer.tgz artifacts\healthclinic-dashboard-scope-demo-v3\visualization --port 5174 --no-open
```

Open [http://127.0.0.1:5174/?token=polaris-local-readonly](http://127.0.0.1:5174/?token=polaris-local-readonly).

## Customer Demo Interactions

1. Search `DashboardController`, click it, and inspect the visible `DECLARES` relationship to `Index` plus the Razor source evidence.
2. Search `dashboard`, select the `Route` node, and follow `CONFIGURES_ROUTE` to the Dashboard template. Then select `ui-view` from the Razor Dashboard content to explain the Legacy ASP.NET MVC/Razor shell hosting Legacy AngularJS 1.x content.
3. Search `dashboardService`, select its source File node, and inspect the visible `CALLS_API` tags and connections to `/api/users/current/tenant`, `/api/reports/clinicsummary`, `/api/reports/expenses/` plus year, and `/api/reports/patients/` plus year.

## Tests

- `python -m pytest -q tests\test_understand_anything_visualization.py`: `4 passed`
- `python -m pytest -q`: `38 passed, 2 skipped`
