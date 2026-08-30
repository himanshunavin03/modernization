# Dashboard Deterministic Extraction Summary

- Inventory files: 24
- Deterministic facts: 87
- Graph nodes: 119
- Graph edges: 163
- Parser: Tree-sitter JavaScript, HTML, and C# only.

## Needs Review

- Razor directives are not modeled beyond file classification because this POC uses the Tree-sitter HTML grammar, not a Razor grammar.
- Dynamic JavaScript URL expressions are emitted as source expressions, not resolved API endpoints.
- Only the configured dashboard source scope was inspected; no behavior outside it is represented.
