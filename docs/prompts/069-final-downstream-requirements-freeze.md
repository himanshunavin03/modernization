POLARIS — FINAL DOWNSTREAM REQUIREMENTS FREEZE

MODEL:
Sol

BASE_COMMIT:
20711a272abbc3da4dc122b43dd8fe33e63b9c6a

FROZEN_CANONICAL_KG_RUN:
legacy-dashboard-complete-application-demo-v1-2026-09-06-203944

TARGET_FEATURE:
doctor-directory-management

FINAL_DEMO_ARTIFACT:
artifacts/feature-specifications/latest/feature-doctor-directory-management.md


======================================================================
MISSION
======================================================================

The deterministic analysis/KG stage is COMPLETE and FROZEN.

Use exactly:

legacy-dashboard-complete-application-demo-v1-2026-09-06-203944

Now finish the downstream Doctor requirements chain:

KG 203944
→ Application Understanding
→ Doctor Feature
→ Doctor Stories
→ Doctor Acceptance Criteria
→ existing consolidated Jira-quality Feature Specification
→ validation
→ ONE commit
→ STOP

There must remain ONE primary human/demo Markdown per Feature:

artifacts/feature-specifications/latest/
feature-doctor-directory-management.md

Do NOT create separate Feature/Story human Markdown documents.

Do NOT reopen extraction/KG work unless load_approved_graph() itself proves
the frozen run cannot be consumed.


======================================================================
0. RESTART / BASELINE SAFETY CHECK
======================================================================

The Codex session may have restarted.

Do NOT rely on previous chat/session state.

Establish state from Git and committed artifacts.

Run:

git rev-parse HEAD
git status --short
git log --oneline -5

Required:

HEAD=
20711a272abbc3da4dc122b43dd8fe33e63b9c6a

WORKTREE_CLEAN_BEFORE=YES

Verify the frozen run exists:

artifacts/knowledge-graph/runs/
legacy-dashboard-complete-application-demo-v1-2026-09-06-203944

Verify its readiness/validation artifacts.

Then load it through the normal approved graph loader.

Required:

KG_RUN_EXISTS=YES
KG_READINESS_ACCEPTABLE=YES
LOAD_APPROVED_GRAPH=PASS

If HEAD/worktree does not match:

STOP.

Do NOT reset, checkout, stash, clean, revert, or discard user work.


======================================================================
1. FROZEN UPSTREAM — HARD RULE
======================================================================

Do NOT modify or regenerate:

- source
- source inventory
- framework detection
- Tree-sitter
- Roslyn
- Facts
- Knowledge Graph
- KG normalization
- KG readiness
- KG validation
- Git LFS configuration
- architecture
- existing Angular
- Playwright

The following are frozen:

SOURCE
EXTRACTION
FACTS
KG 203944
KG READINESS

Required at end:

SOURCE_CHANGED=NO
EXTRACTION_CHANGED=NO
FACTS_CHANGED=NO
KG_CHANGED=NO
KG_READINESS_CHANGED=NO


======================================================================
2. REGENERATE APPLICATION UNDERSTANDING
======================================================================

Run the normal Application Understanding pipeline using ONLY approved KG:

legacy-dashboard-complete-application-demo-v1-2026-09-06-203944

The new KG contains richer deterministic structures including:

- anonymous callback identity
- callback ownership
- PASSES_CALLBACK
- callback-contained invocations
- route/state target linkage
- controller lifecycle
- directive usage/binding
- template binding
- conditional rendering
- state/collection mutation
- navigation
- confirmation
- validation conditions

Application Understanding must consume these GENERICALLY.

Preserve where structurally available:

- interaction identity
- handler/callback lineage
- trigger
- observable result(s)
- state mutation
- collection mutation
- navigation target
- confirmation requirement
- validation gating
- visibility/render condition
- system/user initiation
- API mechanism separately

Do not derive UX from API methods/routes.


======================================================================
3. AU SEMANTIC GATE
======================================================================

Before generating Feature artifacts, verify that the previously blocked
Doctor semantics now survive into AU.

Validate against KG structure, not hardcoded production mappings.

Required:

FR02_AU_SEMANTICS=PASS
FR03_AU_SEMANTICS=PASS
FR04_AU_SEMANTICS=PASS
FR06_AU_SEMANTICS=PASS

Specifically:

FR-02:
detail/edit interaction must retain the route/controller/load/model
observable chain.

FR-03:
Create/Add must retain successful callback → navigateBack → doctors
navigation.

FR-04:
Update/Save must retain successful callback → navigateBack → doctors
navigation.

FR-06:
profile media must retain directive → callback → state/binding →
conditional-render semantics.

Required:

AU_INTERACTION_LINEAGE=PASS
DOCTOR_SEMANTIC_INPUT_STATUS=PASS

If these fail because AU fails to consume evidence already present in
203944:

you MAY repair ONLY the generic KG→AU semantic propagation/model.

You may NOT modify KG/extraction/Facts.

Add neutral regression tests for any AU repair.


======================================================================
4. FEATURE INTERACTION GROUPING — FR-08
======================================================================

The forensic audit established one remaining downstream generic defect:

Feature composition can combine independent navigation handlers into one
requirement.

Repair this GENERICALLY if still present.

Feature composition must preserve distinct interaction groups when AU
contains distinct:

trigger/action
+
handler identity
+
target/effect

For example, generic interactions:

Action A → Handler A → Target A

Action B → Handler B → Target B

must not become one ambiguous interaction merely because they belong to
the same capability.

Do NOT hardcode Doctor navigation actions.

Use stable semantic interaction identity already preserved by AU.


======================================================================
5. FEATURE GROUPING TESTS
======================================================================

Use neutral fixtures.

Prove:

1. two actions in one capability with different handlers/targets remain
   distinguishable;

2. same handler with multiple related effects can remain one logical
   interaction where appropriate;

3. unrelated navigation effects are not borrowed;

4. system prerequisite is not merged into user interaction;

5. grouping does not depend on labels/API routes/source proximity.

Required:

FEATURE_INTERACTION_GROUPING_TESTS=PASS


======================================================================
6. GENERATE DOCTOR FEATURE
======================================================================

Run the EXISTING generic Feature pipeline for ONLY:

doctor-directory-management

Use the new AU.

Do NOT manually patch Feature artifacts.

Do NOT force a specific FR count.

The Feature structure must emerge from current evidence.


======================================================================
7. DOCTOR SOURCE-FIDELITY VALIDATION
======================================================================

Use these as integration validation targets ONLY.

Do not encode them as Doctor-specific production rules.

Where frozen KG/AU proves them, verify the Doctor Feature represents:

- directory presentation
- fixed Name ordering
- empty-directory state
- detail/edit interaction
- create Doctor
- successful create continuation
- update Doctor
- successful update continuation
- single delete
- selected/bulk delete
- deletion confirmation
- Load More / continuation
- appended results
- continuation visibility/termination
- required-field/form validation
- profile-media behavior
- navigation interactions
- automatic tenant context

Do not require behavior explicitly marked unresolved with a legitimate
reason.

Required:

LOST_SOURCE_PROVEN_UI_BEHAVIOR=0
SILENTLY_DROPPED_SOURCE_PROVEN_BEHAVIOR=0
UNSUPPORTED_FEATURE_BEHAVIOR=0


======================================================================
8. LOAD MORE FIDELITY
======================================================================

The source application uses Load More/continuation behavior.

Do NOT transform this into numbered pagination merely because the backend
uses pageSize/pageCount.

If structural evidence proves:

continuation action
→ collection append

and:

condition
→ continuation visibility

preserve that actual UX.

Required:

CONTINUATION_UX_FIDELITY=PASS


======================================================================
9. SYSTEM-INITIATED TENANT CONTEXT
======================================================================

If the application automatically obtains tenant context before Doctor API
operations:

represent it as automatic/system behavior.

Do NOT create a fake user action such as:

"As a user, I establish tenant context."

Required:

SYSTEM_USER_INITIATION_PRESERVATION=PASS


======================================================================
10. API / UX SEPARATION
======================================================================

Feature-owned API contracts should be determined from current evidence.

Expected where still supported:

GET    /api/doctors
GET    /api/doctors/{id}
POST   /api/doctors
PUT    /api/doctors
DELETE /api/doctors/{id}
GET    /api/users/current/tenant

Do not add speciality/availability/etc. merely because those APIs exist
elsewhere.

Required:

UNSUPPORTED_FEATURE_API=0
API_UX_SEPARATION=PASS

HTTP methods/routes are technical dependencies, not UX definitions.


======================================================================
11. GENERATE TARGETED DOCTOR STORIES
======================================================================

Run the existing targeted Story pipeline ONLY for:

doctor-directory-management

Use the generated Feature contract.

Preserve the existing Jira-quality behavior already built into Polaris.

Do NOT redesign Story formatting.

Do NOT generate generic filler such as:

"As a user, I want to use <FR>"

or:

"so that I can complete the supported interaction"

Do not invent unsupported business motivation.

System-initiated prerequisites must not become artificial user actions.


======================================================================
12. GENERATE TARGETED ACCEPTANCE CRITERIA
======================================================================

Generate targeted AC ONLY for:

doctor-directory-management

Use the now-preserved interaction/effect lineage.

Required conceptual chain:

FR
→ interaction
→ handler/callback lineage
→ structural effect
→ observable result
→ AC

Never use:

first interaction
first non-null interaction
any non-null effect in Feature

Association must be deterministic.

One interaction may generate multiple independently testable AC.


======================================================================
13. AC QUALITY
======================================================================

Every AC must contain:

real context
+
real trigger/system event
+
observable result

Reject:

"interaction responds"
"behavior is available"
"supported behavior occurs"
"requirement is satisfied"
control label used as the result
NOT_PROVEN

Required:

NOT_PROVEN_AC_COUNT=0
TAUTOLOGICAL_AC_COUNT=0
PLACEHOLDER_PRECONDITION_COUNT=0
NON_OBSERVABLE_OUTCOME_COUNT=0
REQUIREMENT_RESTATEMENT_COUNT=0
CONTROL_NAME_AS_OUTCOME_COUNT=0
GENERIC_INTERACTION_OUTCOME_COUNT=0


======================================================================
14. ONE CONSOLIDATED FEATURE MD
======================================================================

Use the EXISTING generic Jira-quality Feature Specification renderer.

Do NOT create:

separate Doctor Feature MD
separate Doctor Stories MD
one-off demo documents

The primary human/demo artifact must be:

artifacts/feature-specifications/latest/
feature-doctor-directory-management.md

ONE_FEATURE_MD_PER_FEATURE=PASS

This single file must automatically consolidate the current:

- Feature
- scope
- Functional Requirements
- Stories
- Acceptance Criteria
- API contracts
- behavioral/business rules
- dependencies
- open questions/exclusions where applicable
- Definition of Ready
- Definition of Done
- human-readable traceability

Do NOT manually construct the file.

If the established generic renderer fails to include information it is
supposed to include, repair the generic renderer only.


======================================================================
15. DEMO QUALITY REVIEW
======================================================================

Actually open and read the final:

artifacts/feature-specifications/latest/
feature-doctor-directory-management.md

Do not rely only on JSON validators.

This is the file that will be shown in the demo.

Verify:

- PO/BA can understand complete Feature scope;
- developer can understand what to implement;
- QA can derive tests directly from AC;
- create/edit/delete behavior is concrete;
- Load More is concrete;
- empty state is represented where proven;
- bulk/selected delete is represented where proven;
- confirmation is represented where proven;
- media behavior is represented where proven;
- navigation interactions are clear;
- tenant context is automatic where proven;
- APIs are dependencies, not substitutes for UX;
- Stories are Jira-quality;
- AC are testable;
- no stale references exist.

Required:

FEATURE_SPEC_SYNCHRONIZED=YES
FEATURE_SPEC_HUMAN_QUALITY=PASS
JIRA_QUALITY=PASS


======================================================================
16. HUMAN DOCUMENT CLEANLINESS
======================================================================

The consolidated human MD must describe WHAT TO BUILD.

Do NOT expose internal analysis terminology such as:

Polaris
Knowledge Graph / KG
Facts
Roslyn
Tree-sitter
LSP
analyzer metadata
source paths
source line numbers
confidence internals
source-proven
evidence-backed
modernization-analysis terminology

Machine artifacts retain provenance.


======================================================================
17. TRACEABILITY
======================================================================

Validate:

KG 203944
→ new AU
→ Doctor Feature
→ FR
→ Story
→ AC
→ API where applicable

Required:

FR_WITHOUT_STORY=0
STORIES_WITHOUT_AC=0
ORPHAN_STORIES=0
ORPHAN_AC=0

UNSUPPORTED_STORY_BEHAVIOR=0
UNSUPPORTED_AC_BEHAVIOR=0

STALE_FEATURE_SPEC_REFERENCES=0

FR_STORY_AC_TRACEABILITY=PASS


======================================================================
18. REUSABILITY
======================================================================

Search any changed GENERIC production code.

Required:

APPLICATION_SPECIFIC_PRODUCTION_BRANCHES=0

No production branching based on:

HealthClinic
MyHealth
Doctor
Patient
Appointment
doctor-directory-management
/api/doctors
navigateBack
nagivateToDetail
file-base64
doctor.Picture
LOAD MORE
NO DATA

Application-specific generated artifacts/integration assertions are allowed.


======================================================================
19. FOCUSED TESTS
======================================================================

Run focused tests for changed downstream components:

- KG→AU semantic propagation
- interaction lineage
- Feature interaction grouping
- Feature generation
- targeted Story generation
- targeted AC generation
- AC semantic validation
- Feature Specification synchronization
- Jira-quality validation
- Doctor fidelity integration validation

Do NOT run:

- source extraction
- Tree-sitter
- Roslyn
- Facts generation
- KG generation
- KG readiness regeneration
- architecture
- Technical Tasks
- Angular build
- Playwright
- full repository suite unless a directly changed shared module genuinely
  requires one additional test.


======================================================================
20. CHANGE BOUNDARY
======================================================================

Expected/allowed:

APPLICATION_UNDERSTANDING_CHANGED=YES
DOCTOR_FEATURE_CHANGED=YES
DOCTOR_STORIES_CHANGED=YES
DOCTOR_AC_CHANGED=YES
FEATURE_SPEC_CHANGED=YES

Possible:

FEATURE_COMPOSITION_CODE_CHANGED=YES/NO
AU_PROPAGATION_CODE_CHANGED=YES/NO

Required frozen:

SOURCE_CHANGED=NO
EXTRACTION_CHANGED=NO
FACTS_CHANGED=NO
KG_CHANGED=NO
KG_READINESS_CHANGED=NO
ARCHITECTURE_CHANGED=NO
TECHNICAL_TASKS_CHANGED=NO
ANGULAR_CHANGED=NO
PLAYWRIGHT_CHANGED=NO
DASHBOARD_CHANGED=NO


======================================================================
21. FINAL REPORT
======================================================================

Return:

BASE_COMMIT=

KG_RUN_USED=
KG_RUN_EXISTS=
KG_READINESS_ACCEPTABLE=
LOAD_APPROVED_GRAPH=

NEW_APPLICATION_UNDERSTANDING_RUN=
APPLICATION_UNDERSTANDING_KG_RUN=

AU_PROPAGATION_REPAIR_REQUIRED=
AU_INTERACTION_LINEAGE=
DOCTOR_SEMANTIC_INPUT_STATUS=

FR02_AU_SEMANTICS=
FR03_AU_SEMANTICS=
FR04_AU_SEMANTICS=
FR06_AU_SEMANTICS=

FEATURE_GROUPING_REPAIR_REQUIRED=
FEATURE_INTERACTION_GROUPING_TESTS=

DOCTOR_FEATURE_RUN=
DOCTOR_FR_COUNT=
DOCTOR_FRS=

DOCTOR_FEATURE_API_COUNT=
DOCTOR_FEATURE_APIS=
UNSUPPORTED_FEATURE_API=

DOCTOR_STORY_RUN=
DOCTOR_STORY_COUNT=

DOCTOR_AC_RUN=
DOCTOR_AC_COUNT=

NOT_PROVEN_AC_COUNT=
TAUTOLOGICAL_AC_COUNT=
PLACEHOLDER_PRECONDITION_COUNT=
NON_OBSERVABLE_OUTCOME_COUNT=
REQUIREMENT_RESTATEMENT_COUNT=
CONTROL_NAME_AS_OUTCOME_COUNT=
GENERIC_INTERACTION_OUTCOME_COUNT=

LOST_SOURCE_PROVEN_UI_BEHAVIOR=
SILENTLY_DROPPED_SOURCE_PROVEN_BEHAVIOR=
UNSUPPORTED_FEATURE_BEHAVIOR=
UNSUPPORTED_STORY_BEHAVIOR=
UNSUPPORTED_AC_BEHAVIOR=

API_UX_SEPARATION=
CONTINUATION_UX_FIDELITY=
SYSTEM_USER_INITIATION_PRESERVATION=

FR_WITHOUT_STORY=
STORIES_WITHOUT_AC=
ORPHAN_STORIES=
ORPHAN_AC=
FR_STORY_AC_TRACEABILITY=

FEATURE_SPEC_PATH=
ONE_FEATURE_MD_PER_FEATURE=
FEATURE_SPEC_SYNCHRONIZED=
FEATURE_SPEC_HUMAN_QUALITY=
JIRA_QUALITY=
STALE_FEATURE_SPEC_REFERENCES=

APPLICATION_SPECIFIC_PRODUCTION_BRANCHES=
FOCUSED_TESTS=

SOURCE_CHANGED=
EXTRACTION_CHANGED=
FACTS_CHANGED=
KG_CHANGED=
KG_READINESS_CHANGED=
APPLICATION_UNDERSTANDING_CHANGED=
FEATURE_COMPOSITION_CODE_CHANGED=
DOCTOR_FEATURE_CHANGED=
DOCTOR_STORIES_CHANGED=
DOCTOR_AC_CHANGED=
FEATURE_SPEC_CHANGED=
ARCHITECTURE_CHANGED=
TECHNICAL_TASKS_CHANGED=
ANGULAR_CHANGED=
PLAYWRIGHT_CHANGED=
DASHBOARD_CHANGED=


======================================================================
22. HARD GATE
======================================================================

Do not commit unless:

KG_RUN_USED=
legacy-dashboard-complete-application-demo-v1-2026-09-06-203944

LOAD_APPROVED_GRAPH=PASS

AU_INTERACTION_LINEAGE=PASS
DOCTOR_SEMANTIC_INPUT_STATUS=PASS

FR02_AU_SEMANTICS=PASS
FR03_AU_SEMANTICS=PASS
FR04_AU_SEMANTICS=PASS
FR06_AU_SEMANTICS=PASS

FEATURE_INTERACTION_GROUPING_TESTS=PASS

UNSUPPORTED_FEATURE_API=0

NOT_PROVEN_AC_COUNT=0
TAUTOLOGICAL_AC_COUNT=0
PLACEHOLDER_PRECONDITION_COUNT=0
NON_OBSERVABLE_OUTCOME_COUNT=0
REQUIREMENT_RESTATEMENT_COUNT=0
CONTROL_NAME_AS_OUTCOME_COUNT=0
GENERIC_INTERACTION_OUTCOME_COUNT=0

LOST_SOURCE_PROVEN_UI_BEHAVIOR=0
SILENTLY_DROPPED_SOURCE_PROVEN_BEHAVIOR=0
UNSUPPORTED_FEATURE_BEHAVIOR=0
UNSUPPORTED_STORY_BEHAVIOR=0
UNSUPPORTED_AC_BEHAVIOR=0

API_UX_SEPAR