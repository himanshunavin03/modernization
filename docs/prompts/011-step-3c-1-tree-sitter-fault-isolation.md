Repair Create Knowledge Graph resilience after a native Tree-sitter JavaScript parser termination.

Read:

- PROJECT_MEMORY.md
- PROGRESS.md
- DECISIONS.md
- AGENTS.md
- docs/prompts/010-step-3c-create-knowledge-graph-agent.md
- docs/agents/create-knowledge-graph.md

Save this exact request as:
docs/prompts/011-step-3c-1-tree-sitter-fault-isolation.md

Observed real source failure:
Tree-sitter extraction terminates the Python process while parsing:
source\HealthClinic.biz\src\MyHealth.Client.Cordova\content\js\MobileServices.Web.js

The source tree hash was unchanged. Do not modify source/.

Goal:
A parser failure in one file must never crash the full Create Knowledge Graph workflow.

Implement:

1. Fault isolation

- Run each native Tree-sitter extraction in an isolated child Python process.
- Use argument arrays or structured JSON input; never use shell string concatenation.
- The parent workflow must detect abnormal child exit codes, timeouts, invalid JSON output, and normal Python extraction errors.
- Continue analyzing all other files.

2. Honest evidence and warnings
   For a failed file:

- Add a structured extraction warning with:
  source_path, language/extractor, failure category, safe diagnostic, and status = skipped.
- Do not include source content in logs or artifacts.
- Do not invent facts for that file.
- Include extraction warning counts in analysis-summary.md, graph-run-status.json, and graph-run-summary.md.

3. Partial-success behavior

- If at least one file is successfully analyzed and only some files fail:
  overall workflow status should be `succeeded_with_warnings`, not failed.
- If every selected extractable file fails, overall status should be `failed`.
- Graph JSON, source inventory, framework detection, run status, and summary must still be written for partial success.
- Neo4j load must be blocked by default for `succeeded_with_warnings` unless an explicit future approval option exists. Do not add that option now.

4. Source inventory
   Add per-file extraction status, for example:

- succeeded
- skipped
- unsupported
- failed_isolated

Keep the input source read-only.

5. Tests
   Add tests that simulate:

- a worker process abnormal exit for one file while another file succeeds;
- timeout or invalid worker output;
- a partial graph run that creates artifacts and warnings;
- all-files-failed behavior;
- no source fixture changes.

Do not create a real crashing fixture. Mock the worker/process boundary safely.

6. HealthClinic retry
   After tests pass, rerun graph-only analysis on:
   source\HealthClinic.biz
   with project ID:
   healthclinic-demo

Show:

- graph-run-summary.md
- file/fact/node/edge/warning counts
- the failed/skipped file warning for MobileServices.Web.js, if it still crashes
- five strongest UI/controller/API relationships from the successfully analyzed files
- proof source files remain unchanged

Do not load Neo4j, do not begin Step 4, and do not commit generated artifacts.
Update durable project memory and progress with this resilience behavior.
Commit and push only source, tests, docs, and memory changes.
