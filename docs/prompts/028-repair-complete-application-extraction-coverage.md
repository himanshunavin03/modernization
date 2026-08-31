# Repair Complete Application Extraction Coverage

Repair generic isolated Tree-sitter extraction so the full-application graph can reach complete coverage without excluding failed supported files or hiding failures. Inventory every failure by parser/language/signature, add generic regression fixtures, preserve worker isolation, rerun the complete graph, and load/export only after zero supported-file extraction failures.
