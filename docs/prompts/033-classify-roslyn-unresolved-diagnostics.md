# Prompt 033: Classify Roslyn Unresolved Diagnostics

Extend the existing project-aware Roslyn helper with stable unresolved-diagnostic IDs, source evidence, project ownership, analysis mode, candidate-symbol evidence, and explicit classifications. Preserve project-load diagnostics and lower-confidence synthetic fallback provenance; do not regenerate the complete graph until unknown or analyzer-defect categories are understood.
