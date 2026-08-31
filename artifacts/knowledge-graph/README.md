# Knowledge Graph Review Artifacts

`runs/` contains immutable, timestamped copies of successful raw Create Knowledge Graph output. `latest/` is a byte-for-byte copy of the newest validated run. The copied pipeline files are not simplified, regenerated, or filtered.

Each run includes `review-metadata.json` and `knowledge-graph-validation.json`. They identify the analyzed application/project, run ID, generation timestamp, Tree-sitter/Roslyn/LSP completion, unresolved-symbol and warning counts, graph node/edge counts, validation findings, and Neo4j status from `graph-run-status.json`.

Core artifacts: `knowledge-graph.json` is the canonical graph; `facts.json` contains Tree-sitter facts; `roslyn-semantic*.json` contain semantic facts; `source-inventory.json` is complete source coverage; `framework-detection.json` records detected technologies; and `graph-run-status.json`, `graph-run-summary.md`, and `analysis-summary.md` record workflow status. Any additional raw output is copied unchanged.
