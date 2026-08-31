# Complete Application Extraction Failure Inventory

Baseline: `legacy-dashboard-complete-application-demo-v1` has 47 isolated extraction failures, all `abnormal_exit` with Windows exit code `3221225477`.

| Language/parser | Count | Repeatable pattern | Classification |
| --- | ---: | --- | --- |
| JavaScript Tree-sitter | 42 | Primarily large third-party Office and jQuery bundles; also application/mobile JavaScript. | Supported parser defect; must be repaired generically. |
| C# Tree-sitter | 3 | Generated resource designer and desktop view-model sources. | Supported parser defect; must be repaired generically. |
| HTML Tree-sitter | 2 | Razor view and third-party HTML. | Supported parser defect; must be repaired generically. |

No failed file is reclassified as unsupported merely to meet coverage. The common native access-violation signature means the current worker isolation is functioning, but the parser/runtime failure remains unresolved. Complete coverage, Neo4j loading, and viewer export remain blocked until a generic repair proves these supported files can be processed safely.
