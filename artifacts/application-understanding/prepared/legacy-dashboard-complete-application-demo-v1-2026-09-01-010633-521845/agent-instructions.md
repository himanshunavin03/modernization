# Active Agent Reasoning Instructions

Read only `evidence-packages.json` and produce `agent-reasoning.json` matching `agent-reasoning-schema.json`.
Every agent-derived item must set `origin` to `AGENT_REASONING` and reuse exact evidence references from the packages.
Do not scan source, invent source relationships, or map frontend API calls to backend endpoints. Every workflow with an API dependency must retain `backend_mapping: UNRESOLVED`.
Use only existing Dashboard candidates when present. The deterministic validator rejects malformed, unsupported, or out-of-package claims.
