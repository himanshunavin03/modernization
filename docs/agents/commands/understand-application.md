# understand-application

Use the shared Phase-2 CLI only after an approved KG exists. In Codex or Copilot Chat, the active agent performs the interpretation; Polaris performs only deterministic preparation and validation. No API key is required.

```powershell
python -m polaris_modernization.cli understand-application --kg-root artifacts/knowledge-graph/latest --output artifacts/application-understanding
```

Read the resulting `evidence-packages.json`, `agent-reasoning-schema.json`, and `agent-instructions.md` only. Do not scan source or the full KG. Create `agent-reasoning.json` with `AGENT_REASONING` origin and exact package evidence references, then validate it:

```powershell
python -m polaris_modernization.cli understand-application --kg-root artifacts/knowledge-graph/latest --output artifacts/application-understanding --agent-result <prepared-path>/agent-reasoning.json
```

The validator rejects nonexistent evidence, invented relationships/API mappings, malformed claims, missing confidence/provenance, and non-approved demo candidates. Backend mappings remain `UNRESOLVED`.
