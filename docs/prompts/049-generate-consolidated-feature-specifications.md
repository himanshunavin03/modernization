# Prompt 049: Generate Consolidated Feature Specifications

Create exactly one professional Markdown Feature Specification and one machine-readable JSON companion for each of the five approved Business Features, bound to immutable KG `034128`, Application Understanding `054440-719694`, Feature `141302-518966`, Business Feature `145336-704667`, Story `105453-078418`, and Acceptance Criteria `112024-635713` runs.

This is consolidation, translation, and structure only. Preserve all five Feature IDs and names, all 12 Stories, all 14 Acceptance Criteria, parent relationships, evidence classifications, open questions, and uncertainty. Do not create, delete, split, merge, rewrite, or upgrade upstream requirements.

Markdown is the primary human review and modernization contract for Product Owner, Business Analyst, Solution Architect, QA Lead, and Modernization Engineer. It must explain objective, value, current behavior, users, scope, workflows, rules, information, experience, Stories, approved AC, integrations, dependencies, security uncertainty, preservation requirements, legacy/target mapping, architecture inputs, NFR status, open decisions, risks, readiness, sign-off, and concise technical traceability without analyzer noise. JSON is the machine trust and downstream automation contract and retains exact lineage and evidence references.

Classify output as customer-reviewable, architect-reviewable, or internal-only. Never leak parser/Roslyn/KG diagnostics, package hashes, internal confidence mechanics, or opaque-dependency noise into primary Markdown. Do not invent personas, rules, requirements, NFRs, security requirements, target UX, Figma links, architecture decisions, tasks, tests, or implementation.

Every Feature includes an unpopulated optional target-design/Figma section. Target design remains not analyzed, Target Architecture remains pending, and modernization remains not started. Figma may later enrich design mapping but cannot redefine approved behavior.

Persist an immutable `artifacts/feature-specifications` run plus a byte-identical `latest`, index, validation, quality review, provenance, and zero-external-call metadata. If valid, return `FEATURE_SPECIFICATIONS_READY_WITH_LIMITATIONS` and `NEXT_ACTION=ANALYZE_OPTIONAL_TARGET_DESIGN_OR_RECOMMEND_TARGET_ARCHITECTURE`, then stop.
