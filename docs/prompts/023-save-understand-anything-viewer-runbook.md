# Save Understand Anything Viewer Runbook

Create a reusable local read-only viewer runbook and PowerShell launcher for approved Polaris graph artifacts. Do not run `$understand`, `/understand`, or an LLM analyzer. Do not modify source, Neo4j, Docker, or canonical graph data; do not commit tokens or passwords. The launcher must require `ProjectId`, `Port`, and `AccessToken`, validate the canonical artifact, run the deterministic exporter, start the official standalone viewer, print only the intended token-bearing localhost URL, and never write under `source/`.

Document the validated UI-only graph `healthclinic-dashboard-scope-demo-v3`. Include the end-to-end graph only after its Step 3C.8 Roslyn and Neo4j gates complete successfully.
