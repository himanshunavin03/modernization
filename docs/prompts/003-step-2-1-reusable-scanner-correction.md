We are performing Step 2.1 — reusable-scanner and repository-hygiene correction.

Do not start Neo4j, Roslyn/LSP, LangGraph, LangChain, Graphiti, Figma, backlog generation, architecture assessment, or Angular generation yet.

Before work:
1\. Read PROJECT\_MEMORY.md, PROGRESS.md, DECISIONS.md, AGENTS.md, and docs/prompts/002-deterministic-tree-sitter-extractor.md.
2\. Create docs/prompts/003-step-2-1-reusable-scanner-correction.md.
3\. Copy this complete prompt unchanged into that file.
4\. Never modify source/HealthClinic.biz source code.

GOAL

The customized solution must support any future project placed under source/ or provided through --source-root.

HealthClinic Dashboard is only the first sample profile. Do not hardcode:
\- HealthClinic.biz
\- Dashboard
\- MyHealth.Web
\- fixed source paths
\- fixed output file names

PART 1 — FIX REPOSITORY HYGIENE

1\. Inspect whether source/HealthClinic.biz is a Git submodule pointer.
2\. If it is a Git submodule pointer and there is no valid .gitmodules configuration:
&#x20;  \- Remove only the Git index entry for source/HealthClinic.biz.
&#x20;  \- Do not delete the local source folder or modify any source file.
&#x20;  \- Add source/ to .gitignore, while keeping source/.gitkeep and source/README.md tracked.
&#x20;  \- Create source/README.md explaining that customer/reference repositories are local runtime inputs and must not be committed to this customized solution repository.
3\. Remove tracked generated files from Git:
&#x20;  \- all \_\_pycache\_\_/ files
&#x20;  \- all \*.pyc files
&#x20;  \- all \*.egg-info/ files
&#x20;  Do not delete source code.
4\. Strengthen .gitignore for Python caches, virtual environments, egg-info, test cache, and local output.

PART 2 — MAKE THE EXTRACTOR REUSABLE

Refactor the CLI so it requires:

python -m polaris\_modernization.cli analyze ^
&#x20; \--source-root "\<any project path>" ^
&#x20; \--project-id "\<unique project id>" ^
&#x20; \--profile "\<profile name or profile path>" ^
&#x20; \--output "artifacts"

Requirements:

1\. project-id is required and becomes the graph namespace.
2\. Output must be written under:

artifacts/\<project-id>/

3\. Rename generic output artifacts to:

source-inventory.json
facts.json
knowledge-graph.json
analysis-summary.md

4\. The Application graph node must use project-id, not “HealthClinic.biz”.
5\. Source inventory must recursively discover files under any supplied source root.
6\. Detect file type/language by extension and report unsupported files in inventory metadata.
7\. Profiles may define relative source paths for focused extraction, but must not be embedded in Python code.
8\. Move the current Dashboard paths into a named profile such as:

config/profiles/healthclinic-dashboard.yaml

9\. Keep the HealthClinic Dashboard profile as the first POC example only.
10\. The scanner must continue safely if a configured path is absent and report the missing path as a warning.

PART 3 — TESTS MUST WORK AFTER A FRESH CLONE

1\. Add pytest as a development dependency in pyproject.toml.
2\. Add small committed test fixtures under:

tests/fixtures/healthclinic-dashboard/

Use only the minimal copied/synthetic files required to test:
\- C# controller/action/Authorize extraction
\- AngularJS module/controller/service/directive extraction
\- Razor/HTML host controls
\- route and API-call extraction

3\. Unit tests must use fixtures, not source/HealthClinic.biz.
4\. Add an optional integration test that runs only when environment variable:

HEALTHCLINIC\_SOURCE\_ROOT

is supplied.

5\. Add a test proving the graph has a project namespace and source evidence.
6\. Add a test proving source files are not modified by the analyzer.

PART 4 — UPDATE DOCUMENTATION AND MEMORY

Update README.md with:
\- setup command:
&#x20; python -m pip install -e ".[dev]"
\- generic analyze command
\- HealthClinic Dashboard example command
\- explanation that any future project can be analyzed with a new source-root and profile
\- deterministic analysis versus future LLM work

Update PROJECT\_MEMORY.md, PROGRESS.md, and DECISIONS.md.

Record:
\- source projects are local runtime inputs and are not committed
\- graph data, artifacts, Graphiti memory, and future Neo4j nodes must be isolated by project-id
\- HealthClinic Dashboard is a sample profile, not a hardcoded application

Set status to:

“Step 2.1 complete — reusable deterministic scanner and repository hygiene validated.”

Set the next step to:

“Step 3 — load project-scoped knowledge graph JSON into Neo4j and add a Roslyn/LSP semantic enrichment adapter.”

FINISHING REQUIREMENTS

Run:

python -m pip install -e ".[dev]"
python -m pytest -q

Then run the analyzer against the local HealthClinic source only if it exists locally.

Do not claim success unless tests pass.

Return:
1\. exact commands run
2\. test results
3\. output artifact paths
4\. node and edge counts
5\. source path used, if integration run
6\. any limitations
