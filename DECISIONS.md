# Decisions

| Decision | Reason |
| --- | --- |
| The solution is customized for Polaris-style enterprise applications, not a generic conversion tool. | The POC is intended to preserve enterprise-specific architecture and modernization policy. |
| HealthClinic.biz is only a public reference application for the POC. | It provides an inspectable legacy flow without representing the Polaris product itself. |
| The POC will support one selected legacy ASP.NET MVC Dashboard flow first. | A bounded flow permits evidence-led discovery and later validation before broader scope. |
| Neo4j is the source-of-truth code/UI knowledge graph. | Code and UI relationships require a durable, queryable authoritative representation. |
| Graphiti is shared team/agent working memory, not the source-of-truth code graph. | Agent context is operational memory and must not replace evidence-backed code knowledge. |
| LangGraph orchestrates the workflow; LangChain manages LLM schemas, retrieval, and structured outputs. | This separates workflow control from model-facing integration concerns. |
| The first runnable target will be Angular 22 Nx modular monolith. | It is the stated target architecture for the initial modernization POC. |
| Step 1 discovery is limited to the requested Dashboard, Shared, Controllers, and Models paths. | The source boundary prevents unsupported conclusions from client-side code outside the approved scope. |
| The Dashboard Razor page is treated as a protected shell, not as proof of its detailed feature UI. | The inspected server views delegate navigation/content to client-side elements outside the selected scope. |
| The current Git repository root is the solution root. | Step 2 explicitly eliminates the nested `solution/` folder so recovery files, implementation, and Git history have one canonical root. |
| Step 2 uses Tree-sitter JavaScript, HTML, and C# grammars without a regular-expression source-parser fallback. | Deterministic, reproducible source facts require syntax-tree evidence and a clear failure mode if a grammar is unavailable. |
| Step 2 writes source inventory, facts, graph, and summary artifacts as versionable JSON/Markdown. | Later graph loading and review require durable evidence with source path, lines, hashes, extraction method, and confidence. |
| The knowledge graph will be transformed into PRDs, epics, features, user stories, acceptance criteria, and traceability links before code generation. | Business approval must be based on traceable discovered behavior. |
| Customer Figma designs are optional target-design input. | Figma defines target look and design tokens; the knowledge graph remains the evidence source for existing behavior and APIs. |
| Existing approved Angular shared components/design systems must be discovered before generation. | Reuse avoids duplicate components and preserves approved design standards. |
| A target architecture assessment, diagram, ADR, Nx boundaries, and migration plan precede Angular generation. | Architecture must be reviewable before code changes are generated. |
| Target architecture is evidence-based and rule-driven, not LLM-only. | Standard Angular, Nx modular monolith, microfrontend, SSR/hydration, BFF, Signals, typed forms, security, and testing need deterministic decision inputs. |
| Angular 22 Nx modular monolith remains the likely POC default but architecture assessment is configurable. | The default supports the POC while allowing evidence to justify a different target architecture. |
| Source projects are local runtime inputs and are not committed. | The customized solution must support multiple read-only customer/reference repositories without embedding them in its Git history. |
| Scanner outputs and graph namespace are isolated by project ID. | Project-specific artifacts, future Neo4j nodes, Graphiti memory, decisions, backlog, Figma mappings, and generated output must not mix. |
| HealthClinic Dashboard is a YAML sample profile, not hardcoded application logic. | The deterministic scanner must remain reusable for arbitrary future source roots. |
| Project-to-file edges use `CONTAINS`; `CONTAINS_CONTROL` is reserved for file-hosted controls and components. | Graph edge semantics must distinguish repository structure from UI composition. |
| MVC view relationships require a static explicit view name and matching discovered Razor view. | Implicit MVC conventions cannot be connected deterministically without project-specific guessing. |
| API calls are owned only by a unique Angular owner in the same source file. | File-local ownership prevents incorrect cross-service API relationships. |
| Neo4j persists generic graph records keyed by project ID and graph ID. | Project-scoped idempotency prevents duplicate loads and cross-project collisions. |
| Neo4j relationships use the stable `GRAPH_REL` type with a queryable `type` property. | Relationship semantics remain preserved without dynamically constructing Cypher relationship types. |
| Project clearing requires matching repeated confirmation and label-scoped deletes. | A project operation must never become a database-wide delete. |
| Roslyn is an opt-in semantic provider; Tree-sitter remains the default syntax provider. | C# semantic analysis should enrich deterministic facts without requiring a legacy project build. |
| LSP is a future interactive boundary, not a batch-analysis dependency. | Batch analysis must not require an IDE or language server. |
| Roslyn semantic facts require an actual resolved Roslyn symbol before they are marked proven. | Syntax evidence alone must not be presented as semantic resolution. |
| Roslyn identities use fully qualified symbols, while matching Tree-sitter controller/action nodes requires same-file evidence. | This prevents namespace collisions without duplicating equivalent syntax and semantic findings. |
| A type becomes a DTO only when an action return or parameter references it. | The scanner must not misclassify every C# type as a model. |
