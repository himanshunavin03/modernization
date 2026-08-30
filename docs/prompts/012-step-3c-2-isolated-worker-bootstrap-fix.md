Repair Step 3C.1 isolated extraction worker startup.

Read:

- PROJECT_MEMORY.md
- PROGRESS.md
- DECISIONS.md
- AGENTS.md
- docs/prompts/011-step-3c-1-tree-sitter-fault-isolation.md

Save this exact request as:
docs/prompts/012-step-3c-2-isolated-worker-bootstrap-fix.md

Problem:
In a clean repository checkout, the child process started by
python -m polaris_modernization.isolated_extraction
cannot reliably import the package. This makes normal fixture files return failed_isolated and breaks existing tests.

Goal:
Keep native parser isolation, but ensure the child worker can always import the local source package when running from an uninstalled source checkout, editable install, or normal installed package.

Implement:

1. Safe worker bootstrap

- In isolated_extraction.py, derive the repository-local Python source directory from the module location.
- Create a child environment copy.
- Prepend the local `src` directory to PYTHONPATH using os.pathsep while preserving any existing PYTHONPATH.
- Use an explicit safe working directory if needed.
- Continue using argument arrays, structured JSON input, timeout, and no shell interpolation.

2. Error classification

- Distinguish worker startup/import failure from a native abnormal parser exit where possible.
- Keep diagnostics safe: no source content, credentials, or full traceback in artifacts.
- A normal supported fixture file must return succeeded and facts.
- A native worker termination must still become failed_isolated without stopping the parent process.

3. Tests
   Add or correct tests proving:

- extract_file() successfully extracts a normal fixture file from a clean source checkout, without depending on an editable pip installation.
- One simulated abnormal worker exit produces only one failed_isolated warning.
- Existing generic extraction tests pass again.
- Partial-success and all-files-failed behavior still work.
- Run python -m pytest -q from the repository root.

4. HealthClinic retry
   Only after all tests pass:

- Rerun Create Knowledge Graph graph-only mode against source\HealthClinic.biz.
- Confirm the expected result is either succeeded or succeeded_with_warnings.
- If MobileServices.Web.js still crashes, it must appear as one structured skipped warning while other files produce artifacts.
- Show graph-run-summary.md, counts, warning details, five relationships, and source hash proof.

5. Durable history

- Do not mark Step 3C.1 complete until tests and the HealthClinic retry pass.
- Update PROJECT_MEMORY.md, PROGRESS.md, DECISIONS.md, and docs/agents/create-knowledge-graph.md with the corrected behavior.
- Commit and push only code, tests, and documentation—not generated artifacts or source code.
