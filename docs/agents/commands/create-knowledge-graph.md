# /create-knowledge-graph

Use this command only to orchestrate the existing deterministic Knowledge Graph workflow. Never use an LLM to create nodes, edges, summaries, or source facts.

If the user supplies a source root, pass it as the positional argument. Otherwise use the current workspace root. Run:

```powershell
python -m polaris_modernization.cli agent-create-knowledge-graph [<source-root>] --project-id <optional-id> --profile default --output artifacts
```

Add `--load-neo4j` only when the user explicitly requests it and local Neo4j configuration is available. The adapter discovers `.sln`/`.csproj` and enables the existing project-aware Roslyn path only when applicable. It delegates to `create_knowledge_graph`, which performs graph validation and review-artifact publishing. Report status and limitations exactly; generation success is not readiness.
