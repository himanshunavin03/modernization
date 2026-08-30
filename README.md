# Polaris Modernization POC

This repository contains the deterministic Step 2 source extractor for the Polaris modernization POC. It analyzes only configured legacy source paths and produces evidence-backed JSON; it does not generate Angular code or call an LLM/API.

## Prerequisites

- Python 3.11+
- Git
- Tree-sitter Python bindings and the JavaScript, HTML, and C# grammar packages (installed through this project's dependencies)

## Setup

```powershell
python -m pip install --user -e .
```

The source root is supplied at runtime. The extractor never assumes an absolute location and never writes into it.

## Run

From the repository root:

```powershell
python -m polaris_modernization.cli analyze --source-root "source\HealthClinic.biz" --scope dashboard --output "artifacts"
```

Expected artifacts:

- `artifacts/source-inventory.json`
- `artifacts/dashboard-facts.json`
- `artifacts/dashboard-graph.json`
- `artifacts/dashboard-analysis-summary.md`

## Deterministic Boundary

Step 2 uses Tree-sitter AST parsing for JavaScript, HTML/Razor host markup, and C#. Facts contain source paths, line ranges, source hashes, and `confidence: 1.0`. No LLM, LangChain, LangGraph, Graphiti, OpenAI, Copilot, or AI API is used.

Later steps may use the normalized graph for Neo4j loading, Roslyn/LSP enrichment, target-architecture assessment, and controlled LLM workflows. Those capabilities are intentionally not implemented here.

## Recovery

Before resuming work, read `PROJECT_MEMORY.md`, `PROGRESS.md`, `DECISIONS.md`, `AGENTS.md`, and the latest prompt under `docs/prompts/`.
