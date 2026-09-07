# Active Agent Reasoning Instructions

Read only `evidence-packages.json` and produce `agent-reasoning.json` matching `agent-reasoning-schema.json`.
Every agent-derived item must set `origin` to `AGENT_REASONING` and reuse exact evidence references from the packages.
Copy the exact KG run ID and evidence-package manifest hash into the submission. Do not scan source or invent source relationships.
A PROVEN backend mapping requires package evidence for an existing IMPLEMENTED_BY relationship. Preserve unresolved, dynamic, and external states.
Use only existing Dashboard candidates when present. The deterministic validator rejects malformed, unsupported, or out-of-package claims.
