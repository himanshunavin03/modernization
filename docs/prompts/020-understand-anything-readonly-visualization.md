We have approved the hybrid Dashboard POC scope:

Legacy ASP.NET MVC/Razor shell + Legacy AngularJS 1.x UI flow
→ Target Angular 22 application.

Start Step 3C.7: Understand Anything customer visualization integration.

Read first:
PROJECT_MEMORY.md
PROGRESS.md
DECISIONS.md
docs/prompts/019-healthclinic-ui-technology-discovery.md
docs/validation/healthclinic-ui-technology-discovery.md
docs/validation/healthclinic-dashboard-neo4j-visual-demo.md

Create and save this prompt as:
docs/prompts/020-understand-anything-readonly-visualization.md

Goal:
Use Understand Anything only as a customer-friendly, local, read-only graph
viewer for the already validated Polaris knowledge graph.

Critical architecture rules:

- Our Tree-sitter + Roslyn knowledge graph and Neo4j remain the only source
  of truth.
- Do NOT run `$understand`, `/understand`, or any Understand Anything LLM
  analysis against source/HealthClinic.biz.
- Do NOT create `.ua/` or `.understand-anything/` under source/.
- Do not use LLM-generated nodes, summaries, domains, or relationships.
- Do not modify source/, Neo4j data, the existing graph, or Docker configuration.
- Keep all generated visualization data under ignored:
  artifacts/healthclinic-dashboard-scope-demo-v3/visualization/
- Preserve the upstream MIT license and attribution.
- Do not commit automatically.

Step 1 — Install/verify Understand Anything for Codex:
Use its official Windows installer only if it is not already installed:

$installer = Join-Path $env:TEMP "install-understand-anything.ps1"
Invoke-WebRequest "https://raw.githubusercontent.com/Egonex-AI/Understand-Anything/main/install.ps1" -OutFile $installer
& $installer codex

Verify:

- upstream repository URL
- pinned upstream commit/version
- MIT LICENSE exists
- Codex skill link exists
- no project or source files were changed by installation

If VS Code/Codex must restart to discover the skill, report that clearly.
Do not run the new skill yet.

Step 2 — Inspect the Understand Anything viewer schema:

- Inspect its locally installed JSON schema and viewer launch method.
- Do not use its analyzer.
- Define a mapping from our existing knowledge-graph.json to the minimum
  viewer schema required for an interactive graph.

Step 3 — Implement a read-only adapter:

- Read only:
  artifacts/healthclinic-dashboard-scope-demo-v3/knowledge-graph.json
- Reject the input unless:
  - project ID is healthclinic-dashboard-scope-demo-v3
  - scope coverage is scope_complete
  - extraction warnings are zero
- Export only a visualization copy under:
  artifacts/healthclinic-dashboard-scope-demo-v3/visualization/
- Keep project ID, node names, labels, relationship types, evidence metadata,
  and review warnings visible.
- Add a visible dashboard disclaimer:
  “Evidence-backed legacy modernization graph. Tree-sitter/Roslyn source of
  truth. Review warnings remain visible. No LLM inference.”
- Use precise terminology:
  “Legacy AngularJS 1.x” and “Target Angular 22”.
  Never describe AngularJS as modern Angular.
- Do not change the canonical graph labels in this step.

Step 4 — Customer-view requirements:
The local viewer must let a customer:

- see graph nodes and relationships
- search nodes
- click a node and see name, type, source path, evidence, and warnings
- understand Razor → AngularJS → API relationships
- see project-scoped graph counts and disclaimer

Step 5 — Verification:

- verify the visualization input counts match the canonical graph exactly
- verify no source files changed
- verify no LLM/API token usage occurred
- verify no other project ID appears
- provide the local launch command and browser URL
- capture the three best customer-demo interactions/queries

Step 6 — Documentation:
Create:
docs/validation/understand-anything-readonly-visualization.md

Update PROJECT_MEMORY.md, PROGRESS.md, and DECISIONS.md with the actual result.

Run relevant tests for the adapter.

At the end show:

- files changed
- test results
- exact local launch command
- browser URL
- Git status
- files ready to commit

Do not commit automatically. Wait for my approval.
