# Understand Anything Read-Only Viewer

Use this runbook only for an approved canonical Polaris graph. The viewer is a local, read-only copy; Tree-sitter/Roslyn `knowledge-graph.json` and project-scoped Neo4j remain the source of truth.

> Never run `$understand`, `/understand`, or any Understand Anything analyzer against customer source. Do not run this workflow from, or write anything under, `source/`.

## Prerequisites

- Python 3.11 or later on `PATH`.
- Node.js 18 or later, `npm.cmd` for one-time installation, and Node.js on `PATH` for normal launch.
- An approved artifact at `artifacts/<project-id>/knowledge-graph.json` with `scope_complete` coverage and zero extraction warnings.
- A local non-secret access token supplied only at launch. Do not commit it.

## One-Time Local Installation

This is the only command that downloads the pinned official viewer package. It installs ignored local files under `tools/vendor/understand-anything-viewer/`.

```powershell
.\tools\install_understand_anything_viewer.ps1
```

The installer verifies the local package during launch: name `understand-anything-viewer`, version `2.9.0`, MIT license, executable, and upstream `Egonex-AI/Understand-Anything` repository metadata.

## Normal Offline Launch

Normal customer-demo launch makes no GitHub, npm registry, or other package request. It uses only the local pinned executable.

From the repository root, choose an unused port and a local token:

```powershell
.\tools\launch_understand_anything_viewer.ps1 `
  -ProjectId healthclinic-dashboard-scope-demo-v3 `
  -Port 5175 `
  -AccessToken 'replace-with-a-local-token'
```

The helper exports `artifacts\healthclinic-dashboard-scope-demo-v3\knowledge-graph.json` to ignored `visualization\.ua`, then prints the exact `http://127.0.0.1:<port>/?token=<token>` URL. Open that URL locally. Stop the foreground viewer safely with `Ctrl+C`.

The `healthclinic-dashboard-end-to-end-demo-v1` viewer command is deliberately not listed yet: its Roslyn and Neo4j gates were blocked in Step 3C.8, so it is not an approved viewer input.

## Troubleshooting

- **Port already in use:** choose another port, for example `5176`; do not stop an unknown process.
- **Local viewer missing:** run `.\tools\install_understand_anything_viewer.ps1` once. Do not substitute `npx`, a URL, or an analyzer command.
- **Node.js not found:** install or restore Node.js 18+ and reopen the terminal.
- **Blank or cached view:** hard-refresh the browser, then verify the project overview shows layers. Regenerate through the helper before retrying.
- **Missing graph artifact:** rerun the deterministic graph workflow for the approved project; do not create a graph manually or point the viewer at `source/`.
