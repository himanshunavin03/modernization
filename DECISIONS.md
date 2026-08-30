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
