Implement true, evidence-backed modernization scope boundaries before Neo4j loading.

Read:
- PROJECT_MEMORY.md
- PROGRESS.md
- DECISIONS.md
- AGENTS.md
- docs/prompts/014-step-3c-4-clean-dashboard-profile-graph.md
- docs/validation/healthclinic-dashboard-clean-graph.md

Save this exact request as:
docs/prompts/015-step-3c-5-scope-complete-graph-correctness.md

Important correction:
Never exclude a file merely because it causes a parser failure.
A scoped graph is valid only when it is explicitly identified as a customer-approved modernization scope and all boundary limitations are visible.

Do not modify source/.
Do not load Neo4j yet.
Do not add LangChain, LangGraph, Graphiti, Figma, stories, or Angular generation yet.

Goal:
Make profile-based graph generation correct for both:
1. Full application analysis, and
2. Approved modernization-flow analysis, such as HealthClinic Dashboard.

Implement:

1. Explicit profile scope contract
Extend profile configuration generically with fields such as:
- scope_id
- scope_name
- scope_description
- scope_type: full_application | selected_modernization_flow
- include_paths

The default profile must represent full_application.
The healthclinic-dashboard profile must represent selected_modernization_flow and explain its Dashboard business/UI scope.

Do not hardcode HealthClinic names in reusable engine code.

2. Preserve complete audit inventory
source-inventory.json must still list every discovered source file.

Every file must have one truthful scope/extraction state:
- in_scope_succeeded
- in_scope_failed_isolated
- in_scope_unsupported
- out_of_scope

Do not call an out-of-scope file “skipped because of error.”
Do not remove it from the inventory.

3. Scope the knowledge graph correctly
When scope_type is selected_modernization_flow:
- knowledge-graph.json must contain File nodes only for in-scope files.
- Nonselected files must not appear as normal File nodes in the scoped graph.
- Graph metadata must explicitly state:
  scope_id, scope_name, scope_type, selected_file_count,
  out_of_scope_file_count, extraction_warning_count,
  review_warning_count, and coverage_status.

When scope_type is full_application:
- graph all selected/discovered supported files as today.
- Any failed parser file must remain represented through a structured warning.

4. Preserve cross-scope dependencies honestly
If an in-scope file has proven evidence of dependency on a file, type, controller, API, component, or view outside the selected scope:
- create an `OutOfScopeReference` or equivalent boundary node.
- add an evidence-backed relationship such as DEPENDS_ON_OUT_OF_SCOPE.
- include the source path and reason.
- Never invent its internal implementation or silently omit the dependency.

5. Scope Roslyn correctly
- Roslyn facts declared in out-of-scope C# files must not become normal graph nodes in a selected-flow graph.
- A selected C# file may reference an out-of-scope type through an explicit boundary reference only.
- Default/full profile behavior remains full analysis.

6. Customer-facing status
graph-run-status.json and graph-run-summary.md must clearly distinguish:
- “Scope-complete for approved Dashboard modernization flow”
from
- “Complete application graph”
from
- “Partial graph with extraction failures.”

Do not call a Dashboard graph “clean” merely because unrelated files are out of scope.

7. Tests
Add generic tests proving:
- Full profile graphs all source files.
- Scoped profile inventories all files but graphs only in-scope files.
- Out-of-scope file references are visible when proven.
- A parser failure inside scope prevents scope-complete status.
- A parser failure outside scope does not invalidate the scoped graph, but remains visible in the audit inventory.
- Roslyn facts outside scope are not included as normal graph nodes.
- No source fixture changes.
- All existing tests remain green.

8. Re-run HealthClinic Dashboard scope validation
Run:

python -m polaris_modernization.cli create-knowledge-graph \
  --source-root "source\HealthClinic.biz" \
  --project-id "healthclinic-dashboard-scope-demo-v3" \
  --profile "healthclinic-dashboard" \
  --output "artifacts" \
  --enable-roslyn \
  --skip-neo4j

Show:
- full inventory count
- in-scope graph-file count
- out-of-scope count
- extraction warnings inside scope
- review warnings inside scope
- scope metadata from knowledge-graph.json
- five Dashboard relationships
- any explicit out-of-scope boundary references
- proof source hash is unchanged

Create:
docs/validation/healthclinic-dashboard-scope-complete-v3.md

Only if:
- all selected files are successfully analyzed or honestly unsupported,
- extraction warnings inside scope are zero,
- graph metadata states scope completeness,
- and boundaries are visible,

mark it:
“Ready for Neo4j Dashboard modernization-flow demo.”

Update PROJECT_MEMORY.md, PROGRESS.md, DECISIONS.md, README, and docs/agents/create-knowledge-graph.md.
Commit and push only implementation, tests, documentation, and memory updates.
