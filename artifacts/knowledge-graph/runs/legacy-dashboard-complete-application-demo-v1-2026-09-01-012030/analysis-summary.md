# Dashboard Deterministic Extraction Summary

- Inventory files: 2384
- Deterministic facts: 1474
- Graph nodes: 4868
- Graph edges: 5124
- Extraction warnings: 0
- Total graph warnings: 4453
- Scope: Full application analysis
- Coverage status: complete_with_opaque_dependencies
- Parser: Tree-sitter JavaScript, HTML, and C# only.

## Needs Review

- Razor directives are not modeled beyond file classification because this POC uses the Tree-sitter HTML grammar, not a Razor grammar.
- Dynamic JavaScript URL expressions are emitted as source expressions, not resolved API endpoints.
- Only the configured dashboard source scope was inspected; no behavior outside it is represented.
