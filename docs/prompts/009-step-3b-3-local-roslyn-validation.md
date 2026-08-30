Validate Step 3B.2 on this local machine before any new implementation.

Read:

- PROJECT_MEMORY.md
- PROGRESS.md
- DECISIONS.md
- AGENTS.md
- docs/prompts/008-step-3b-2-return-type-label-correction.md

Save this exact request as:
docs/prompts/009-step-3b-3-local-roslyn-validation.md

Do not modify source/.
Do not start Step 4, LangChain, LangGraph, Graphiti, UI, or Angular generation.

Validation steps:

1. Check whether the .NET SDK is available:
   dotnet --info

2. If dotnet is unavailable:

- Do not change the implementation.
- Clearly report that .NET 8 SDK installation or PATH configuration is required.
- Keep PROGRESS.md status as pending real Roslyn validation.
- Show me the exact Windows command/link guidance needed to install .NET 8 SDK.

3. If dotnet is available:

- Run:
  dotnet restore tools\Polaris.RoslynAnalyzer\Polaris.RoslynAnalyzer.csproj
  dotnet build tools\Polaris.RoslynAnalyzer\Polaris.RoslynAnalyzer.csproj --no-restore
  python -m pytest -q

- Run this real semantic analysis:
  python -m polaris_modernization.cli analyze `  --source-root "tests\fixtures\roslyn-semantic"
  \--project-id "semantic-fixture" `  --profile "default"
  \--output "artifacts" \
  \--enable-roslyn

- Verify:
  artifacts\semantic-fixture\roslyn-semantic.json exists.
  artifacts\semantic-fixture\knowledge-graph.json exists.
  The graph contains:
  DECLARES, EXPOSES, RETURNS_TYPE, HAS_PROPERTY, INVOKES, and PROTECTED_BY.
  Fetch returns ShipmentSummary as DTO.
  Status returns System.String as Type.
  No files under tests\fixtures\roslyn-semantic changed.

4. Only if every validation passes:

- Update PROJECT_MEMORY.md, PROGRESS.md, and DECISIONS.md to mark Step 3B complete.
- Set the next stage to:
  Step 3C — Create Knowledge Graph agent command and customer-facing graph run status.
- Save exact commands and results in docs/validation/step-3b-local-validation.md.

Do not commit or push unless I explicitly ask.
