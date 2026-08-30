# Polaris Modernization POC

This repository contains a project-agnostic deterministic source scanner. Any local source project can be selected with `--source-root`, `--project-id`, and a profile; source projects are read-only runtime inputs.

## Prerequisites

- Python 3.11+
- Git
- Tree-sitter Python bindings and the JavaScript, HTML, and C# grammar packages (installed through this project's dependencies)

## Setup

```powershell
python -m pip install -e ".[dev]"
python -m pytest -q
```

The source root is supplied at runtime. The extractor never assumes an absolute location and never writes into it.

## Run

From the repository root:

```powershell
python -m polaris_modernization.cli analyze --source-root "<any-project-path>" --project-id "<unique-project-id>" --profile "default" --output "artifacts"
```

Expected artifacts:

- `artifacts/<project-id>/source-inventory.json`
- `artifacts/<project-id>/framework-detection.json`
- `artifacts/<project-id>/facts.json`
- `artifacts/<project-id>/knowledge-graph.json`
- `artifacts/<project-id>/analysis-summary.md`

HealthClinic Dashboard example:

```powershell
python -m polaris_modernization.cli analyze --source-root "source\HealthClinic.biz" --project-id "healthclinic-dashboard" --profile "healthclinic-dashboard" --output "artifacts"
```

## Deterministic Boundary

The scanner uses Tree-sitter AST parsing for JavaScript, HTML/Razor host markup, and C#. Facts contain project IDs, source paths, line ranges, source hashes, and `confidence: 1.0`. No LLM, LangChain, LangGraph, Graphiti, OpenAI, Copilot, or AI API is used. Future graph loading and controlled LLM work are outside Step 2.1.

Later steps may use the normalized graph for Neo4j loading, Roslyn/LSP enrichment, target-architecture assessment, and controlled LLM workflows. Those capabilities are intentionally not implemented here.

## Recovery

Before resuming work, read `PROJECT_MEMORY.md`, `PROGRESS.md`, `DECISIONS.md`, `AGENTS.md`, and the latest prompt under `docs/prompts/`.
