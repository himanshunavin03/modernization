# Polaris - Final PO/BA Semantic Quality and Feature Specification Refinement

Continue from approved baseline `ce9dbbb5dc4b804f659936882a733099445d8e9c`. This is a narrow final refinement of the five existing Modernization Feature Specifications. Preserve the Knowledge Graph, deterministic analyzers, API association architecture, primary/supporting/candidate classifications, coverage matrix, provenance, and authoritative Feature/Story/AC lineage. Preserve `FEATURES=5`, `STORIES=12`, and `AUTHORITATIVE_AC=14`.

## Objective

Make the specifications useful in a customer workshop without inventing missing requirements. Correct circular and system-centric Stories, weak outcomes, vague Functional Behavior, weak Acceptance Criteria, unclear Feature purpose/name alignment, stakeholder-enrichment handling, inflated quality scoring, and customer readability. Distinguish evidence-proven behavior, supported business interpretation, and stakeholder-enriched business intent.

## Semantic Models

Build `StorySemanticModel` before Story prose with actor, business action/object, observable capability, supported outcome, outcome evidence status, business value/status, and stakeholder-enrichment requirement. Use `PROVEN`, `SUPPORTED_INTERPRETATION`, `NOT_ESTABLISHED`, or `REQUIRES_STAKEHOLDER_ENRICHMENT`. Prefer proven outcomes, then supported interpretation, then capability-oriented outcomes; if none is non-circular, explicitly request stakeholder enrichment. Keep `application user` unless an authoritative persona exists.

Reject circular or semantically circular patterns such as access/view/open/get of X followed by present/review/use/make-available of the same X without a meaningful consequence. Detect `CIRCULAR_STORY`, `SEMANTICALLY_CIRCULAR_STORY`, `SYSTEM_CENTRIC_STORY`, `UNSUPPORTED_BUSINESS_VALUE`, and `STAKEHOLDER_ENRICHMENT_REQUIRED`. Do not manufacture business value merely to satisfy a User Story template. Separate Observed Capability, Business Value, and Business Value Status.

Build `AcceptanceCriterionSemanticModel` with precondition, trigger, observable behavior/object, known data characteristics, navigation result, tenant/API preservation requirements, evidence status, and limitations. Statuses are `FULLY_TESTABLE_FROM_EVIDENCE`, `TESTABLE_WITH_EVIDENCE_LIMITATION`, `MODERNIZATION_PRESERVATION`, and `REQUIRES_STAKEHOLDER_CLARIFICATION`. Improve observability only from evidence; never invent UI controls, fields, validations, rules, or presentation details. Render preservation AC separately while retaining its authoritative ID and meaning.

## Customer Documents

Use this structure without empty subsections: Feature Summary with Purpose, Current Business Capability, Business Value, and Modernization Objective; Functional Behavior; Scope with In Scope and Not Established by Current Evidence; User Stories and AC; Existing Backend Integration with Primary Business APIs, Supporting/Shared APIs, and Unresolved/Dynamic Integrations; Modernization Considerations; Decisions Required with separate Business and Technical clarifications; Review and Approval; Technical Traceability appendix.

Keep business behavior free of controller/service/API/framework terminology. Keep established API details and improve customer wording without promoting candidates. Preserve Doctor and Patient business integrations as unresolved/dynamic/candidate where established and Tenant as supporting. Preserve Dashboard yearly reports as dynamic primary, clinic summary as unresolved primary, and tenant context as supporting. Preserve User Access/Tenant Feature-relative primary classifications.

Validate Feature-name-to-behavior alignment as `ALIGNED`, `PARTIALLY_ALIGNED`, or `REQUIRES_PO_BA_REVIEW`; never infer behavior from a Feature name. Explicitly review Clinic Appointment Experience because appointment creation, update, and scheduling are not established. Add actionable `StakeholderEnrichmentItem` records with IDs, references, category, question, reason, evidence, impact, owner, and status. Separate blocking from non-blocking and business from technical questions.

## Quality and Readiness

Score evidence integrity; Feature purpose/name/business value/behavior clarity; Story business/outcome/readability/evidence safety; AC precondition/action/outcome/testability/evidence safety; API coverage/classification/contract/evidence safety; PO, BA, customer SME, QA, architect, and modernization-engineer usability; Markdown readability; audience separation; and overall readiness. Apply explicit penalties for circular semantics, action/outcome repetition, system-centric or generic/unsupported value, vague/non-observable AC, Feature-name mismatch, and boilerplate. Use 10 exceptional, 9 strong, 8 usable with meaningful refinement remaining, 7 visibly analyst/generated, and 6 or below not customer-ready. Do not award 9+ merely for evidence safety.

For every Feature report business, technical, QA, and modernization readiness plus blocking/non-blocking items. Detect cross-Feature template similarity, especially Doctor versus Patient, but do not reject legitimate structural similarity automatically. Preserve authoritative statements separately from customer presentation and record semantic equivalence; use the authoritative text if equivalence fails.

## Validation and Limits

Maintain zero invented Features, behaviors, Stories, AC, personas, business value/rules, UI requirements, data/API fields, endpoints, security requirements, NFRs, Figma details, and architecture decisions. Keep JSON as machine/provenance contract and Markdown as human contract. Do not analyze Figma, recommend architecture, create ADRs/tasks, generate Angular, modify backend/database/source, use an LLM, or start modernization. Keep target design `NOT_YET_ANALYZED`, target architecture `PENDING`, and modernization `NOT_STARTED`.

Add focused tests for semantic circularity, supported interpretation, enrichment fallback, system-centric outcomes, observable/limitation-aware/preservation AC, no invented fields, Feature alignment, Clinic Appointment mismatch, cross-Feature similarity, and API classification regressions. Run the full suite. Open and manually review all five Markdown documents for customer comprehension, meaningful Story outcomes, observable QA behavior, API role separation, and actionable gaps.

Update `PROJECT_MEMORY.md`, `PROGRESS.md`, and `DECISIONS.md` with the evidence/business-intent distinction, rejection of circular Stories, limitation-aware AC, explicit Feature-name alignment, and independence of API completeness from PO/BA quality. Regenerate all five Feature specifications and supporting artifacts. Return the complete requested metrics, readiness values, test results, files changed, and commit. Stop before target design or architecture work.
