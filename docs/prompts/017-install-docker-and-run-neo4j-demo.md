We are continuing the Polaris Modernization POC.

First read:
PROJECT_MEMORY.md
PROGRESS.md
DECISIONS.md
docs/prompts/016-step-3c-6-neo4j-visual-demo.md
docs/validation/healthclinic-dashboard-neo4j-visual-demo.md

Save this prompt as:
docs/prompts/017-install-docker-and-run-neo4j-demo.md

Goal:
Install and start Docker Desktop on this Windows machine, then run the approved Step 3C.6 Neo4j visual-demo workflow.

Rules:

- Do not modify anything under source/.
- Do not overwrite .env.
- Do not print or commit passwords, tokens, Docker volumes, generated artifacts, bin/, or obj/.
- Do not claim Neo4j is loaded unless verification succeeds.
- Do not enable WSL, change Windows features, reboot the computer, or bypass an administrator/UAC prompt automatically. Stop and tell me if any of those actions are required.
- Do not commit automatically.

Step 1 — Check Docker:
Run:
docker version
docker compose version

If both work, skip installation and go directly to Step 4.

Step 2 — Install Docker Desktop only if Docker is unavailable:
Run this command in PowerShell:

winget install --id Docker.DockerDesktop -e --accept-source-agreements --accept-package-agreements

If installation requires admin rights, user interaction, WSL installation, restart, or reboot:

- Stop safely.
- Tell me the exact action required.
- Update only the project recovery documents with the true status.
- Do not run any graph or source operation.

Step 3 — Start Docker Desktop:
After successful installation, start Docker Desktop if it is not already running.

Wait until these commands succeed:
docker version
docker compose version

If Docker is installed but the current VS Code terminal cannot find it, tell me to close and reopen the VS Code terminal, then stop safely.

Step 4 — Run the approved Neo4j demo:
Continue every step in:
docs/prompts/016-step-3c-6-neo4j-visual-demo.md

This includes:

- start Neo4j with Docker Compose
- run the scope-complete Dashboard graph workflow with Neo4j loading enabled
- verify Neo4j data matches the generated graph
- verify no source files changed
- create the actual Neo4j evidence report
- update PROJECT_MEMORY.md, PROGRESS.md, and DECISIONS.md with true results only

At the end, show:

1. Docker version and Docker Compose version
2. Docker Compose status
3. Neo4j load status
4. graph counts from Neo4j
5. evidence report path
6. Git status
7. exact files ready to commit

Do not commit. Wait for my approval.
