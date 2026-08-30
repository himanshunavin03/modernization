We are continuing the Polaris Modernization POC. First read and follow:
PROJECT_MEMORY.md
PROGRESS.md
DECISIONS.md
AGENTS.md
.github/copilot-instructions.md
docs/prompts/010-step-3c-1.md through docs/prompts/015-step-3c-5.md
docs/validation/healthclinic-dashboard-scope-complete-v3.md

Create and save this exact prompt as:
docs/prompts/016-step-3c-6-neo4j-visual-demo.md

Goal:
Load the already validated scope-complete HealthClinic Dashboard knowledge graph into local Neo4j and produce evidence that a customer can see in Neo4j Browser.

Rules:
- Do not modify anything under source/.
- Do not commit generated artifacts, .env, passwords, Docker volumes, bin/, or obj/.
- Do not overwrite an existing .env.
- Do not claim Neo4j was loaded unless it is actually verified.
- The graph must remain project-scoped using project ID:
  healthclinic-dashboard-scope-demo-v3
- Do not hide warnings or exclude customer files. Preserve the existing scope contract.

Steps:

1. Preflight:
  Run:
  docker version
  docker compose version

  If Docker Desktop is unavailable or not running:
  - Stop safely.
  - Report the exact issue and the one action I need to take.
  - Do not change graph code or source code.

2. If .env does not exist, create it from .env.example without committing it. Ask me to provide the local Neo4j password if it is required and not documented locally.

3. Start Neo4j:
  docker compose up -d
  docker compose ps

4. Wait until Neo4j is healthy and reachable.

5. In the current PowerShell session, set the Neo4j environment variables from the local .env values. Do not print the password:
  NEO4J_URI=bolt://localhost:7687
  NEO4J_USERNAME=neo4j
  NEO4J_PASSWORD=<local value>

6. Rerun the Create Knowledge Graph workflow with Neo4j loading enabled, using:
  - source root: source\HealthClinic.biz
  - project ID: healthclinic-dashboard-scope-demo-v3
  - profile: healthclinic-dashboard
  - Roslyn enabled
  - Neo4j loading enabled

7. Verify all of the following:
  - workflow status succeeded or succeeded_with_warnings
  - Neo4j stage succeeded
  - scope coverage remains scope_complete
  - selected File node count is 24
  - audit file count is 2,384
  - no source files changed
  - Neo4j contains nodes only for this project ID
  - Neo4j node and edge counts match the generated knowledge-graph.json

8. Provide three safe Cypher queries for the customer demo:
  - project overview and graph counts
  - UI flow / component relationships
  - dependency or API-flow relationships

9. Create a concise evidence report under docs/validation/ with:
  - commands run, excluding passwords
  - actual Neo4j verification result
  - final counts
  - Neo4j Browser URL: [http://localhost:7474](http://localhost:7474)
  - the three demo Cypher queries
  - known review warnings, if any
  - confirmation that source was unchanged

10. Update PROJECT_MEMORY.md, PROGRESS.md, and DECISIONS.md with the true outcome only.

11. Run relevant tests or validation checks available in the repository.

12. Show me:
  - files changed
  - commands executed
  - verification output
  - Git status
  - exactly what should be committed

Do not commit automatically. Wait for my approval after verification.
