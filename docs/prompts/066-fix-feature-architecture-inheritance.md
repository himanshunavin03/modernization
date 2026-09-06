# Prompt 066: Fix Feature Architecture Inheritance

## Objective

Repair command prerequisite semantics so Feature technical planning inherits the canonical locked application architecture instead of requiring a Feature-ID match.

## Constraints

- Prefer an explicit valid Feature override when one exists.
- Otherwise reference the one canonical application selection.
- Validate selection equality, lock status, post-validation state, and selection hash.
- Do not regenerate architecture or technical tasks.
- Do not change application source, approved requirements, API contracts, or generated Angular code.

## Validation

Cover explicit, inherited, missing, unlocked, unknown, Doctor Directory, and synthetic application cases. Run prerequisite-only Doctor validation, the full Polaris suite, the existing Angular build, protected-artifact comparison, and the application-specific branch audit.
