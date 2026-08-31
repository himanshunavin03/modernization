# Step 3C.8 - Dashboard End-to-End Context Graph

Create the project-scoped, evidence-backed `healthclinic-dashboard-end-to-end-demo-v1` graph for the proven path from the Legacy ASP.NET MVC/Razor UI through Legacy AngularJS 1.x calls to existing API, domain, and data context. Modernize only the UI; backend, API, domain, and data code are read-only context.

## Constraints

- Never modify `source/`.
- Do not modify or delete `healthclinic-dashboard-scope-demo-v3`.
- Do not use an LLM, API key, or inferred relationship.
- Resolve a client API call only when the route/controller evidence is unique and proven. Dynamic or ambiguous paths remain review warnings.
- Never mark backend context as eligible for Angular generation.
- Do not commit automatically.

## Required Outcome

1. Add a reusable end-to-end context-flow profile type with file roles: `transform_ui`, `preserve_backend`, `preserve_domain_data`, and `review_required`.
2. Preserve the existing UI selection and add only Dashboard-relevant API controllers/actions, DTOs/domain models, and repositories/data dependencies proven reachable by Roslyn semantics.
3. Emit evidence-bearing `CALLS_API`, `RESOLVES_TO_ENDPOINT`, `RETURNS_TYPE`, `INVOKES` or `DEPENDS_ON`, and `PRESERVES_CONTRACT` relationships only when proven. Record unresolved or ambiguous links as review warnings.
4. Add `modernization_scope: end_to_end_context`, the UI-only transform boundary, backend preservation boundary, and coverage/warning metadata.
5. Add tests for unique route resolution, dynamic/ambiguous warnings, role isolation, project isolation, source integrity, and exclusion of unrelated API files.
6. Run the Roslyn-enabled workflow and load only this new project into Neo4j after `scope_complete` coverage and zero extraction warnings.
7. Create `docs/validation/healthclinic-dashboard-end-to-end-context-graph.md`, update recovery documents truthfully, and generalize the read-only visualization adapter to accept a safe specified project ID. Do not create a viewer export until the new graph passes its gates.
