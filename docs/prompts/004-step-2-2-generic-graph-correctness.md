We are continuing the Polaris Modernization POC.

First read completely:
\- PROJECT\_MEMORY.md
\- PROGRESS.md
\- DECISIONS.md
\- AGENTS.md
\- .github/copilot-instructions.md
\- docs/prompts/003-step-2-1-reusable-scanner-correction.md

Create and save this exact request as:
docs/prompts/004-step-2-2-generic-graph-correctness.md

Goal:
Make the normalized knowledge graph fully project-agnostic and correct before we add Neo4j persistence.

Important boundaries:
\- Do not modify anything under source/.
\- Do not add Neo4j, LangGraph, LangChain, Graphiti, LSP, Roslyn, Figma, or Angular generation yet.
\- Keep the CLI reusable:
&#x20; python -m polaris\_modernization.cli analyze --source-root "\<path>" --project-id "\<id>" --profile "\<profile>" --output "artifacts"
\- Do not hardcode HealthClinic, DashboardController, Index, or any source-project-specific name.

Implement these corrections:

1\. Graph relationship semantics
\- Change the Project/Application to File relationship from CONTAINS\_CONTROL to CONTAINS.
\- Keep CONTAINS\_CONTROL only for File to UI-control/component relationships where appropriate.

2\. Remove the Dashboard-specific MVC rule
\- Remove any logic that specifically checks DashboardController and Index.
\- Implement only deterministic generic Razor/MVC relationships.
\- If an action returns View("ExplicitName"), connect it to a matching Razor view when evidence exists.
\- If an action uses return View() without an explicit view name, do not guess using a project-specific rule. Record a review warning or unresolved relationship candidate instead.
\- The graph must work with arbitrary controller and view names.

3\. Correct API-call ownership
\- Ensure each API\_CALL relationship starts from the Angular service, controller, or UI owner declared in the same source file.
\- Never attach API calls to the first Angular service found in the whole project.
\- If no owning Angular service/controller can be proven, attach the API call to its File node and mark the ownership as unresolved in metadata.

4\. Add or improve evidence metadata
\- Graph nodes and edges must retain project\_id, source path, line/column or range when available, parser/extractor, and confidence.
\- Keep output deterministic; do not require an LLM to create relationships.

5\. Tests
Add tests proving:
\- Two separate JavaScript/AngularJS service files with different API calls generate edges owned by their correct service.
\- Arbitrary controller/view names work without DashboardController or HealthClinic-specific logic.
\- Project/Application -> File uses CONTAINS.
\- Running the analyzer does not change any input source fixture files. Use before/after hashes in the test.

6\. Repository hygiene
\- Inspect the accidentally named root file:
&#x20; "Read solutionPROJECT\_MEMORY.md, sol.txt"
&#x20; If it is accidental and contains no required project material, remove it.
\- Do not remove any required documentation or source files.

7\. Documentation and recovery memory
\- Update PROJECT\_MEMORY.md, PROGRESS.md, and DECISIONS.md with what was corrected and how to resume.
\- Update README only if the behavior/output contract changes.
\- Add the exact commands to install and run tests.

Validation:
\- Run python -m pytest -q
\- Run a sample analysis against test fixtures or an available local source path.
\- Show the output folder and a short summary of the corrected graph behavior.
\- Do not commit or push unless I explicitly ask.
