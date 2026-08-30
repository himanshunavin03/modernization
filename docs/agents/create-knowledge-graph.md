# Create Knowledge Graph Agent

## Purpose

Create a project-isolated, evidence-backed `knowledge-graph.json` from a customer-selected local source folder. This is deterministic orchestration only: it uses Tree-sitter analysis, optional Roslyn enrichment, graph validation, and optional Neo4j loading. It does not use an LLM, LangChain, LangGraph, Graphiti, Figma, business-story generation, or Angular generation.

## User Inputs

- `--source-root`: an existing local source repository or folder.
- `--project-id`: a unique, safe identifier containing letters, numbers, dots, underscores, and hyphens.
- `--profile`: the extraction profile, normally `default`.
- `--output`: local artifact root, normally `artifacts`.
- `--enable-roslyn`: optional C# semantic enrichment.
- `--skip-neo4j`: graph-only execution. This is the default.
- `--load-neo4j`: load only the validated graph for this project after requiring local Neo4j configuration.

## Exact Command

```powershell
python -m polaris_modernization.cli create-knowledge-graph --source-root "<path-to-any-project>" --project-id "<unique-project-id>" --profile "default" --output "artifacts" --enable-roslyn --load-neo4j
```

For a graph-only run, use `--skip-neo4j` instead of `--load-neo4j`.

The actual executable entry point is this CLI command. This repository does not configure an automatic VS Code slash command or UI button. A future UI may map `/Create-Knowledge-Graph` or a button to the CLI command.

## Workflow Stages

1. `validate_input`: verifies the source directory and safe project ID.
2. `analyze_source`: runs each native Tree-sitter extraction in an isolated child Python process, then optional Roslyn enrichment.
3. `validate_graph`: verifies that graph records carry the requested project ID.
4. `load_neo4j`: either loads this project only, reports a controlled connection/configuration failure, or is skipped.
5. `produce_run_status`: writes the customer-facing JSON and Markdown status artifacts.

## Output Contract

The agent writes ignored local artifacts at `artifacts/<project-id>/`:

- `knowledge-graph.json`
- `graph-run-status.json`
- `graph-run-summary.md`

Run status includes timestamps, each stage status, graph counts, extraction-warning count, Roslyn and Neo4j outcomes, artifact paths, the manual Neo4j Browser URL `http://localhost:7474`, and safe next actions. It never includes Neo4j passwords, source content, worker tracebacks, or other secrets.

## Error Handling

Invalid source paths and project IDs fail before analysis. A valid project ID with an invalid source path still receives status artifacts. Each native Tree-sitter file is isolated in a child that prepends the module-derived local `src` directory to a copied `PYTHONPATH`, allowing clean source checkouts, editable installs, and installed packages to run the same worker command. Abnormal exits, timeouts, invalid worker output, startup/import failures, and Python extraction errors become a structured `failed_isolated` inventory status and a `skipped` extraction warning without source content. If at least one file succeeds, the workflow returns `succeeded_with_warnings` and writes all graph artifacts. If every selected extractable file fails, the workflow returns `failed` after writing artifacts. Neo4j is not required for graph-only operation and is blocked when extraction warnings exist. When an otherwise eligible `--load-neo4j` is requested, missing environment variables or connection failures return a controlled failed `load_neo4j` stage; no delete operation is attempted.

## Safety Rules

The source root is read-only: the workflow never modifies, copies, commits, or adds customer source to Git. Every artifact, graph node, graph edge, warning, and Neo4j load is scoped by `project_id`. The workflow contains no clear/delete operation and never issues a database-wide Neo4j delete.

## Sample Customer Response

```text
Create Knowledge Graph succeeded for shipment-modernization.
Artifacts: artifacts/shipment-modernization/knowledge-graph.json and graph-run-summary.md.
Neo4j load was skipped. Start Neo4j manually when ready, then rerun with --load-neo4j.
Neo4j Browser: http://localhost:7474
```
