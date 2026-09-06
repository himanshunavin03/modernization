# Dashboard Deterministic Extraction Summary

- Inventory files: 2384
- Deterministic facts: 30685
- Graph nodes: 16888
- Graph edges: 38876
- Extraction warnings: 0
- Total graph warnings: 4453
- Scope: Full application analysis
- Coverage status: complete_with_opaque_dependencies
- Parser: Tree-sitter JavaScript, HTML, and C# only.

## Needs Review

- Razor directives are not modeled beyond file classification because this POC uses the Tree-sitter HTML grammar, not a Razor grammar.
- Dynamic JavaScript API expressions are normalized when structure is deterministic; runtime-dependent URL composition remains unresolved.
- Only the configured dashboard source scope was inspected; no behavior outside it is represented.
