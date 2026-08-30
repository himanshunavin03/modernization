Roslyn Step 3B needs a correctness repair. Do not begin Step 4.

Read:

- PROJECT_MEMORY.md
- PROGRESS.md
- DECISIONS.md
- AGENTS.md
- docs/prompts/006-step-3b-roslyn-semantic-enrichment.md

Save this exact request as:
docs/prompts/007-step-3b-1-roslyn-correctness-repair.md

Do not modify source/ and do not add LLM, LangChain, LangGraph, Graphiti, Figma, Agile stories, or Angular generation.

Correct these issues:

1. Use Roslyn semantic APIs genuinely

- Use SemanticModel, GetDeclaredSymbol, GetSymbolInfo, and type-symbol information where available.
- Do not label a fact as resolution_status=proven unless Roslyn actually resolved it.
- For unresolved symbols, emit resolution_status=unresolved with an honest diagnostic.

2. Correct fact types

- Do not map every C# class/type to DTO.
- Emit distinct kinds such as:
  namespace, controller, action, type, dto, property, method,
  endpoint, authorization_policy, invocation, type_reference.
- Classify a DTO/model only from deterministic evidence, such as a type used as an action return type or parameter, or a configured/model namespace rule. Otherwise keep it as a generic type.

3. Add missing semantic extraction

- Extract namespaces.
- Extract properties and typed properties from model/DTO classes.
- Extract controller and action route attributes.
- Extract HTTP verb attributes.
- Combine controller-level and action-level route templates only when both are static literals.
- Extract action return types and parameter types.
- Extract resolved invocation targets when Roslyn can resolve them.
- Preserve source path, line range, source hash, project_id, extractor, confidence, resolution status, and diagnostics for every result.

4. Correct graph integration
   Add only evidence-backed relationships:

- Controller -> DECLARES -> Action
- Action -> EXPOSES -> Endpoint
- Action -> RETURNS_TYPE -> Type/DTO
- Type/DTO -> HAS_PROPERTY -> Property
- Method/Action -> INVOKES -> Method
- Controller/Action -> PROTECTED_BY -> AuthorizationPolicy

Do not create duplicate nodes when Tree-sitter and Roslyn find the same controller/action.
Do not use a type name alone as a global identity if two namespaces can contain the same name. Include namespace or fully qualified identity.

5. Add a real semantic fixture and tests
   Create a generic fixture with arbitrary names containing:

- Controller-level route
- Action-level HTTP route
- Authorize policy or role
- Typed action return value
- DTO with two typed properties
- One local/service method invocation that Roslyn can resolve

Tests must verify the generated roslyn-semantic.json and normalized graph contain:

- endpoint route
- authorization evidence
- return-type relation
- DTO property relation
- resolved invocation relation when available
- correct project_id isolation
- no source fixture changes

Keep the no-dotnet fallback test, but it must not be the only Roslyn test.
If dotnet exists, build and run the helper during validation. If it does not exist, clearly mark the real Roslyn integration test as skipped.

6. Documentation and memory

- Correct README, PROJECT_MEMORY.md, PROGRESS.md, and DECISIONS.md so they do not claim Step 3B is complete until the real semantic tests pass.
- Keep LSP documented only as a future interactive boundary.
- Do not commit or push unless I ask.

Validation required:

- python -m pytest -q
- dotnet build tools/Polaris.RoslynAnalyzer/Polaris.RoslynAnalyzer.csproj
- Run analyze with --enable-roslyn against the semantic fixture
- Show the resulting roslyn-semantic.json and the relevant graph relationships.
