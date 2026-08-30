# Runtime Analysis Boundary

The scanner uses deterministic Tree-sitter adapters and profile configuration only. It does not call LLMs, AI APIs, Neo4j, Graphiti, Roslyn/LSP, Figma, or code generation during Step 2.1. Unsupported parser types remain inventory metadata and never become inferred facts.
