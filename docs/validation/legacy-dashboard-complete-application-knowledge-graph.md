# Legacy Dashboard POC Complete Application Graph

The generic `full_application` workflow ran under isolated project ID `legacy-dashboard-complete-application-demo-v1` with Roslyn enabled. It audited 2,384 files and produced 3,298 nodes, 4,500 edges, and 84 warnings.

Coverage is `partial_application_with_extraction_failures` because 47 isolated extraction warnings were recorded. Therefore Neo4j loading and the read-only viewer export were not attempted. The existing UI-only and end-to-end graphs were not changed. No source file was modified.

Next action: review and resolve or explicitly scope the isolated extraction failures, rerun until complete coverage, then load only this project ID and export its viewer projection.
