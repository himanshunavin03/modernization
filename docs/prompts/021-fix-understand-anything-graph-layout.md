Fix the blank Understand Anything customer graph canvas.

Read:
tools/export_understand_anything_visualization.py
tests/test_understand_anything_visualization.py
docs/validation/understand-anything-readonly-visualization.md
PROJECT_MEMORY.md
PROGRESS.md

Create and save this prompt as:
docs/prompts/021-fix-understand-anything-graph-layout.md

Problem:
The viewer loads the exported graph and shows 24 files in its side panel, but the
main canvas is blank. Inspect the installed Understand Anything v2.9.0 viewer
schema and rendering code. The current adapter exports `"layers": []`, which
prevents the structural graph from rendering correctly.

Rules:

- Do not modify source/.
- Do not modify canonical knowledge-graph.json, Neo4j, Docker, or profiles.
- Do not invoke `$understand`, `/understand`, any LLM, or any source analyzer.
- Keep the viewer export read-only under artifacts/.../visualization/.
- Do not change canonical graph labels in this step.
- Do not commit automatically.

Implement a deterministic layout fix:

1. Update the adapter to generate non-empty viewer `layers`.

2. Every exported node must belong to exactly one deterministic visualization layer.

3. Use only canonical node label, source path, and proven relationships—not LLM inference.

4. Create customer-friendly layers such as:

   - Legacy ASP.NET MVC/Razor shell
   - Legacy AngularJS 1.x client-side flow
   - API and integration flow
   - C# domain and semantic model
   - Project/supporting graph records

   Use actual graph evidence to assign them.

5. Preserve:

   - all 123 nodes
   - all 169 edges
   - all 27 review warnings
   - project isolation
   - disclaimer and source evidence

6. If the viewer schema supports it safely, add a deterministic three-step customer
   tour using only proven existing nodes:

   - Razor/MVC Dashboard shell
   - Legacy AngularJS Dashboard route/ui-view
   - Dashboard API service flow

   Do not invent business meaning.

7. Add tests proving:

   - layers are non-empty
   - every node is assigned exactly once
   - layer node IDs all exist
   - canonical counts remain unchanged
   - incomplete or cross-project input is rejected

8. Regenerate the local read-only export from:
   artifacts/healthclinic-dashboard-scope-demo-v3/knowledge-graph.json

9. Start the standalone viewer on unused port 5175 and verify the browser can
   load the exported graph. If visual rendering cannot be verified automatically,
   state that honestly and tell me exactly what to refresh/check manually.

10. Update:
    docs/validation/understand-anything-readonly-visualization.md
    PROJECT_MEMORY.md
    PROGRESS.md
    DECISIONS.md

Show me changed files, test results, launch command, browser URL, Git status,
and files ready to commit. Do not commit automatically.
