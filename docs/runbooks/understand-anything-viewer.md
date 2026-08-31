# Understand Anything Read-Only Viewer

Use this runbook only for an approved canonical Polaris graph. The viewer is a local, read-only copy; Tree-sitter/Roslyn `knowledge-graph.json` and project-scoped Neo4j remain the source of truth.

> Never run `$understand`, `/understand`, or any Understand Anything analyzer against customer source. Do not run this workflow from, or write anything under, `source/`.

## Prerequisites

- Python 3.11 or later on `PATH`.
- Node.js 18 or later and `npx` on `PATH`.
- An approved artifact at `artifacts/<project-id>/knowledge-graph.json` with `scope_complete` coverage and zero extraction warnings.
- A local non-secret access token supplied only at launch. Do not commit it.

## Validated UI-Only Graph

From the repository root, choose an unused port and a local token:

```powershell
.\tools\launch_understand_anything_viewer.ps1 `
  -ProjectId healthclinic-dashboard-scope-demo-v3 `
  -Port 5175 `
  -AccessToken 'replace-with-a-local-token'
```

The helper exports `artifacts\healthclinic-dashboard-scope-demo-v3\knowledge-graph.json` to ignored `visualization\.ua`, then prints the exact `http://127.0.0.1:<port>/?token=<token>` URL. Open that URL locally. Stop the foreground viewer safely with `Ctrl+C`.

The `healthclinic-dashboard-end-to-end-demo-v1` viewer command is deliberately not listed yet: its Roslyn and Neo4j gates were blocked in Step 3C.8, so it is not an approved viewer input.

## Manual Commands

```powershell
$projectId = 'healthclinic-dashboard-scope-demo-v3'
$port = 5175
$env:UNDERSTAND_ACCESS_TOKEN = 'replace-with-a-local-token'
python .\tools\export_understand_anything_visualization.py `
  --graph ".\artifacts\$projectId\knowledge-graph.json" `
  --output ".\artifacts\$projectId\visualization" `
  --project-id $projectId
npx --yes https://github.com/Egonex-AI/Understand-Anything/releases/download/v2.9.0/understand-anything-viewer.tgz `
  ".\artifacts\$projectId\visualization" --port $port --no-open
```

Open `http://127.0.0.1:5175/?token=replace-with-a-local-token`. Stop with `Ctrl+C` in the terminal running `npx`.

## Troubleshooting

- **Port already in use:** choose another port, for example `5176`; do not stop an unknown process.
- **`npx` or Node.js not found:** install or restore Node.js 18+ and reopen the terminal. Do not substitute an analyzer command.
- **Blank or cached view:** hard-refresh the browser, then verify the project overview shows layers. Regenerate through the helper before retrying.
- **Missing graph artifact:** rerun the deterministic graph workflow for the approved project; do not create a graph manually or point the viewer at `source/`.
