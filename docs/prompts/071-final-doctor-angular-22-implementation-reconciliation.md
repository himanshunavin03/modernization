POLARIS — FINAL DOCTOR ANGULAR 22 IMPLEMENTATION RECONCILIATION

MODEL:
Sol

BASE_COMMIT:
480c17fa4d5b9b29ad8c5a8ccada0e2279552d29

TARGET_FEATURE:
doctor-directory-management

FROZEN_KG_RUN:
legacy-dashboard-complete-application-demo-v1-2026-09-06-203944

FROZEN_TECHNICAL_TASK_RUN:
legacy-dashboard-complete-application-demo-v1-2026-09-07-054315-967074

TECHNICAL_TASK_PLAN:
artifacts/technical-tasks/features/
feature-doctor-directory-management/latest/technical-tasks.md

FINAL_FEATURE_SPEC:
artifacts/feature-specifications/latest/
feature-doctor-directory-management.md


======================================================================
MISSION
======================================================================

Complete the Doctor Directory Management Angular implementation against the
FROZEN Technical Task plan and requirements.

Current Technical Task status:

TOTAL_TASKS=16
IMPLEMENTED=4
PARTIALLY_IMPLEMENTED=10
NOT_IMPLEMENTED=2
BLOCKED=0

DO NOT regenerate the Angular Feature from scratch.

Inspect the existing Doctor Angular implementation first.

Preserve correct working code.

Then:

1. map existing Angular implementation to all 16 Technical Tasks;
2. identify concrete implementation gaps;
3. implement only missing/partial behavior;
4. preserve the frozen legacy UX contract;
5. use the approved Angular 22 architecture;
6. validate all 16 tasks;
7. build the Angular application;
8. run focused Angular tests if present/applicable;
9. produce an implementation reconciliation report;
10. commit exactly once;
11. STOP.

DO NOT run Playwright yet.

======================================================================
1. BASELINE
======================================================================

Verify:

git rev-parse HEAD
git status --short

Required:

HEAD=480c17fa4d5b9b29ad8c5a8ccada0e2279552d29
WORKTREE_CLEAN_BEFORE=YES

If not:

STOP.

Do not reset, stash, clean, checkout, revert, or discard user work.

======================================================================
2. FROZEN UPSTREAM
======================================================================

The following layers are FROZEN:

- source analysis
- source inventory
- Tree-sitter
- Roslyn
- Facts
- KG
- KG readiness
- Application Understanding
- Feature
- Functional Requirements
- Stories
- Acceptance Criteria
- Feature Specification
- architecture
- Technical Task plan

Do NOT modify/regenerate them.

Required at end:

SOURCE_CHANGED=NO
EXTRACTION_CHANGED=NO
FACTS_CHANGED=NO
KG_CHANGED=NO
APPLICATION_UNDERSTANDING_CHANGED=NO
FEATURE_CHANGED=NO
STORIES_CHANGED=NO
AC_CHANGED=NO
FEATURE_SPEC_CHANGED=NO
ARCHITECTURE_CHANGED=NO
TECHNICAL_TASK_PLAN_CHANGED=NO

======================================================================
3. RESOLVE FROZEN IMPLEMENTATION CONTRACT
======================================================================

Load the current Doctor Technical Task plan and current Feature
Specification.

Verify:

TECHNICAL_TASK_COUNT=16
FR_COUNT=21
STORY_COUNT=21
AC_COUNT=41
API_CONTRACT_COUNT=6

Verify the Technical Task lineage still points to the frozen requirements.

Required:

TECHNICAL_TASK_LINEAGE=PASS

Do NOT proceed if stale artifacts are selected.

======================================================================
4. INSPECT EXISTING DOCTOR ANGULAR FIRST
======================================================================

Before writing code, inspect the complete existing Doctor Angular feature.

Identify:

- routes
- components
- templates
- services
- models/interfaces
- state/signals
- forms
- HTTP integration
- loading/error state
- list behavior
- detail/edit behavior
- create/update behavior
- delete behavior
- bulk/selected delete
- confirmation
- Load More
- profile media
- validation
- navigation
- tenant-context handling
- tests

Do not assume previous task classifications are still correct.

Reclassify all 16 Technical Tasks against actual current Angular code:

IMPLEMENTED
PARTIALLY_IMPLEMENTED
NOT_IMPLEMENTED
BLOCKED

Return internally before editing:

PRE_IMPLEMENTED_TASKS=
PRE_PARTIALLY_IMPLEMENTED_TASKS=
PRE_NOT_IMPLEMENTED_TASKS=
PRE_BLOCKED_TASKS=

Expected baseline is approximately:

4 / 10 / 2 / 0

but actual code is authoritative.

======================================================================
5. CREATE GAP PLAN BEFORE EDITING
======================================================================

For every PARTIALLY_IMPLEMENTED or NOT_IMPLEMENTED task identify:

TASK_ID=
CURRENT_IMPLEMENTATION=
MISSING_BEHAVIOR=
FILES_TO_CHANGE=
LINKED_FR=
LINKED_STORIES=
LINKED_AC=
API_DEPENDENCY=
VALIDATION_REQUIRED=

Do NOT change code for tasks already correctly implemented unless a shared
change is genuinely necessary.

Required:

UNNECESSARY_REIMPLEMENTATION=0

======================================================================
6. PRESERVE WORKING ANGULAR
======================================================================

This is a reconciliation operation, NOT a greenfield generation.

Do NOT:

- delete the existing Doctor feature and recreate it;
- replace correct components merely for style;
- rename everything unnecessarily;
- rewrite working services without reason;
- change unrelated Dashboard Angular;
- introduce a new architecture;
- add unrelated features.

Prefer minimal, maintainable changes.

Required:

EXISTING_WORKING_BEHAVIOR_PRESERVED=PASS
DASHBOARD_CHANGED=NO

======================================================================
7. APPROVED ANGULAR 22 ARCHITECTURE
======================================================================

Follow the EXISTING approved architecture selection.

Use modern Angular patterns where appropriate and supported by the current
project.

Prefer/reuse:

- standalone Angular architecture
- Signals for local synchronous UI state
- computed state where useful
- typed models
- typed HTTP services
- modern template control flow
- lazy-loaded feature routing where architecture specifies it
- OnPush / zoneless-compatible patterns where architecture specifies them
- accessible controls and state
- strict TypeScript

Do NOT introduce technology merely to demonstrate it.

Architecture fidelity is more important than feature-showcase code.

Required:

ANGULAR_ARCHITECTURE_FIDELITY=PASS

======================================================================
8. SIGNALS
======================================================================

Use Signals where they naturally improve Doctor UI state.

Examples may include:

- Doctor collection
- loading state
- selected records
- continuation/load-more state
- derived button/visibility state
- current detail state

Do not convert HTTP Observables into Signals merely for appearance if the
service boundary is cleaner as RxJS.

A reasonable architecture is:

HTTP/RxJS at service boundary
→ component/feature state
→ Signals/computed for synchronous UI state

Follow the existing architecture.

Required:

SIGNAL_USAGE=APPROPRIATE

======================================================================
9. FORMS / SIGNAL FORMS
======================================================================

Inspect the current Angular 22 project/toolchain before changing forms.

If Signal Forms are already supported by the project's approved Angular
version/configuration and can be introduced without destabilizing the POC,
it is acceptable to use them for the Doctor form where the architecture
supports it.

However:

DO NOT force Signal Forms merely for demonstration.

If current typed Reactive Forms are already correct and architecture-
compliant, preserve them.

Report:

DOCTOR_FORM_TECHNOLOGY=

Required:

FORM_ARCHITECTURE_FIDELITY=PASS

======================================================================
10. DOCTOR DIRECTORY
======================================================================

Implement/preserve the frozen Feature behavior for the Doctor directory.

Where required by the Feature contract:

- render the Doctor collection;
- preserve required displayed fields;
- preserve fixed ordering;
- represent the empty state;
- preserve correct loading state;
- preserve selected-record state;
- preserve actions/navigation.

Do not invent new UI functionality.

======================================================================
11. LOAD MORE — CRITICAL FIDELITY
======================================================================

The frozen contract preserves the source application's Load More behavior.

Do NOT replace it with:

- numbered pagination
- paginator component
- previous/next pages

unless the frozen Feature explicitly says so.

Implement/preserve:

initial result retrieval
→ Load More interaction
→ additional results appended to existing collection
→ continuation visibility/termination according to the frozen AC

The backend may use pageSize/pageCount internally.

That is NOT the visible UX.

Required:

CONTINUATION_UX_FIDELITY=PASS

======================================================================
12. DETAIL / EDIT
======================================================================

Implement/preserve the frozen detail/edit behavior.

Where required:

Doctor interaction
→ detail/edit route
→ selected Doctor load
→ populated form/state

Preserve route semantics from the approved contract.

Do not invent additional detail screens.

======================================================================
13. CREATE
======================================================================

Implement/preserve Create Doctor behavior according to frozen AC.

Where required:

New Doctor
→ form
→ validation
→ POST
→ successful completion behavior
→ approved navigation/state result

Do not infer success UX from POST itself.

Use the frozen AC.

======================================================================
14. UPDATE
======================================================================

Implement/preserve Update Doctor behavior according to frozen AC.

Where required:

existing Doctor
→ populated form
→ validation
→ PUT
→ successful completion behavior
→ approved navigation/state result

Use the frozen AC.

======================================================================
15. DELETE / SELECTED DELETE
======================================================================

Implement/preserve:

- single-record deletion
- selected/bulk deletion where frozen requirements require it
- confirmation behavior
- collection/UI update after successful operation

Do not invent a backend bulk-delete API if none exists.

If frozen behavior proves per-ID DELETE operations for selected records,
implement using the approved API contract.

Required:

DELETE_UX_FIDELITY=PASS

======================================================================
16. PROFILE MEDIA
======================================================================

Implement/preserve the frozen profile-media behavior.

Where required:

file selection
→ client-side processing/state
→ Doctor picture value
→ preview/render state

Do not invent a new upload endpoint if the Feature does not own one.

Use the approved contract.

Required:

PROFILE_MEDIA_FIDELITY=PASS

======================================================================
17. VALIDATION
======================================================================

Implement all frozen Doctor validation AC.

Validation must affect actual submission availability/behavior.

Do not add arbitrary validation rules.

Use only current requirements.

Required:

FORM_VALIDATION_COVERAGE=PASS

======================================================================
18. TENANT CONTEXT
======================================================================

Preserve automatic tenant-context behavior.

Expected Feature-owned contract includes:

GET /api/users/current/tenant

Tenant context is a system prerequisite.

Do NOT make the user manually establish tenant context.

Use existing architecture/service patterns.

Required:

TENANT_CONTEXT_FIDELITY=PASS

======================================================================
19. API CONTRACTS
======================================================================

Implement/reconcile against exactly the current Feature-owned API contracts.

Expected where frozen contract confirms:

GET    /api/doctors
GET    /api/doctors/{id}
POST   /api/doctors
PUT    /api/doctors
DELETE /api/doctors/{id}
GET    /api/users/current/tenant

Do not invent endpoints.

Required:

API_CONTRACT_IMPLEMENTATION=PASS
UNSUPPORTED_API_USAGE=0

======================================================================
20. ERROR / LOADING BEHAVIOR
======================================================================

Preserve existing correct error/loading behavior where present.

Implement missing behavior only where required by Technical Tasks/AC.

Do not invent elaborate new UX outside the frozen contract.

No silent failures.

======================================================================
21. ACCESSIBILITY / ANGULAR QUALITY
======================================================================

For changed Doctor UI:

- use semantic controls;
- buttons must be actual buttons where appropriate;
- form labels must remain associated;
- disabled state must be meaningful;
- interactive controls should be keyboard usable;
- avoid inaccessible click-only containers;
- preserve useful loading/empty/error feedback.

Required:

ACCESSIBILITY_CHECK=PASS

======================================================================
22. SECURITY / CODE QUALITY
======================================================================

Do not introduce:

- unsafe HTML injection
- hardcoded secrets
- API credentials
- unsafe bypassSecurityTrust usage without approved reason
- direct DOM manipulation where Angular APIs suffice
- `any` merely to silence typing
- duplicated API logic across components

Required:

ANGULAR_CODE_QUALITY=PASS

======================================================================
23. NO MOCK IMPLEMENTATION AS FINAL BEHAVIOR
======================================================================

Inspect whether the existing Doctor implementation uses temporary/mock data.

The final implementation must use the approved service/API architecture.

Mocks may remain only in tests.

Required:

PRODUCTION_MOCK_DATA=0

======================================================================
24. TASK-BY-TASK RECONCILIATION
======================================================================

After implementation, reevaluate all 16 frozen Technical Tasks.

Required final status:

IMPLEMENTED_TASKS=16
PARTIALLY_IMPLEMENTED_TASKS=0
NOT_IMPLEMENTED_TASKS=0
BLOCKED_TASKS=0

For every task provide:

TASK_ID
STATUS
IMPLEMENTATION_PATHS
LINKED_AC
VALIDATION

Do not modify the frozen Technical Task plan to make implementation appear
complete.

The CODE must satisfy the plan.

======================================================================
25. AC IMPLEMENTATION COVERAGE
======================================================================

Map all 41 frozen AC to implementation paths.

Required:

AC_IMPLEMENTED=41
AC_PARTIALLY_IMPLEMENTED=0
AC_NOT_IMPLEMENTED=0

Every AC must point to actual implementation behavior.

Do not claim coverage from comments or placeholder methods.

Required:

AC_IMPLEMENTATION_COVERAGE=PASS

======================================================================
26. BUILD
======================================================================

Run the normal Angular build.

Required:

ANGULAR_BUILD=PASS

Do not suppress compiler errors.

Do not weaken TypeScript configuration.

======================================================================
27. FOCUSED TESTS
======================================================================

Run existing relevant Doctor Angular/unit/component/service tests.

Add focused tests only where necessary for changed behavior.

Validate at minimum where test infrastructure supports it:

- list state
- Load More append behavior
- continuation visibility
- create validation
- update validation
- delete confirmation
- selected deletion
- media preview state
- tenant-context service behavior
- navigation state

Do NOT run Playwright yet.

Required:

ANGULAR_FOCUSED_TESTS=PASS

======================================================================
28. PLAYWRIGHT READINESS — DO NOT GENERATE YET
======================================================================

Use the 41 frozen AC to assess whether the implementation is ready for E2E
generation.

Required:

PLAYWRIGHT_READINESS=READY

Report any AC that cannot yet be exercised through the UI/backend.

Required:

AC_NOT_E2E_READY=0

Do NOT create Playwright tests in this run.

======================================================================
29. REUSABILITY
======================================================================

If generic modernization code must change, inspect it carefully.

Required:

APPLICATION_SPECIFIC_PRODUCTION_BRANCHES=0

Do not add generic engine branches based on:

HealthClinic
MyHealth
Doctor
doctor-directory-management
/api/doctors
LOAD MORE

Application-specific Angular code naturally contains Doctor semantics.

That is allowed.

======================================================================
30. FROZEN BOUNDARY
======================================================================

Required:

SOURCE_CHANGED=NO
EXTRACTION_CHANGED=NO
FACTS_CHANGED=NO
KG_CHANGED=NO
APPLICATION_UNDERSTANDING_CHANGED=NO
FEATURE_CHANGED=NO
STORIES_CHANGED=NO
AC_CHANGED=NO
FEATURE_SPEC_CHANGED=NO
ARCHITECTURE_CHANGED=NO
TECHNICAL_TASK_PLAN_CHANGED=NO
DASHBOARD_CHANGED=NO
PLAYWRIGHT_CHANGED=NO

Expected:

DOCTOR_ANGULAR_CHANGED=YES

======================================================================
31. FINAL REPORT
======================================================================

Return:

BASE_COMMIT=

TECHNICAL_TASK_RUN_USED=
TECHNICAL_TASK_COUNT=

FR_COUNT=
STORY_COUNT=
AC_COUNT=
API_CONTRACT_COUNT=

PRE_IMPLEMENTED_TASKS=
PRE_PARTIALLY_IMPLEMENTED_TASKS=
PRE_NOT_IMPLEMENTED_TASKS=
PRE_BLOCKED_TASKS=

IMPLEMENTED_TASKS=
PARTIALLY_IMPLEMENTED_TASKS=
NOT_IMPLEMENTED_TASKS=
BLOCKED_TASKS=

TASKS_IMPLEMENTED_THIS_RUN=
TASKS_COMPLETED_FROM_PARTIAL=
TASKS_PRESERVED_WITHOUT_CHANGE=

UNNECESSARY_REIMPLEMENTATION=

DOCTOR_FORM_TECHNOLOGY=
SIGNAL_USAGE=
ANGULAR_ARCHITECTURE_FIDELITY=
FORM_ARCHITECTURE_FIDELITY=

CONTINUATION_UX_FIDELITY=
DELETE_UX_FIDELITY=
PROFILE_MEDIA_FIDELITY=
FORM_VALIDATION_COVERAGE=
TENANT_CONTEXT_FIDELITY=

API_CONTRACT_IMPLEMENTATION=
UNSUPPORTED_API_USAGE=
PRODUCTION_MOCK_DATA=

AC_IMPLEMENTED=
AC_PARTIALLY_IMPLEMENTED=
AC_NOT_IMPLEMENTED=
AC_IMPLEMENTATION_COVERAGE=

ACCESSIBILITY_CHECK=
ANGULAR_CODE_QUALITY=

ANGULAR_BUILD=
ANGULAR_FOCUSED_TESTS=

PLAYWRIGHT_READINESS=
AC_NOT_E2E_READY=

APPLICATION_SPECIFIC_PRODUCTION_BRANCHES=

SOURCE_CHANGED=
EXTRACTION_CHANGED=
FACTS_CHANGED=
KG_CHANGED=
APPLICATION_UNDERSTANDING_CHANGED=
FEATURE_CHANGED=
STORIES_CHANGED=
AC_CHANGED=
FEATURE_SPEC_CHANGED=
ARCHITECTURE_CHANGED=
TECHNICAL_TASK_PLAN_CHANGED=
DOCTOR_ANGULAR_CHANGED=
DASHBOARD_CHANGED=
PLAYWRIGHT_CHANGED=

CHANGED_ANGULAR_FILES=

======================================================================
32. HARD GATE
======================================================================

Do not commit unless:

TECHNICAL_TASK_COUNT=16

IMPLEMENTED_TASKS=16
PARTIALLY_IMPLEMENTED_TASKS=0
NOT_IMPLEMENTED_TASKS=0
BLOCKED_TASKS=0

UNNECESSARY_REIMPLEMENTATION=0

ANGULAR_ARCHITECTURE_FIDELITY=PASS
FORM_ARCHITECTURE_FIDELITY=PASS

CONTINUATION_UX_FIDELITY=PASS
DELETE_UX_FIDELITY=PASS
PROFILE_MEDIA_FIDELITY=PASS
FORM_VALIDATION_COVERAGE=PASS
TENANT_CONTEXT_FIDELITY=PASS

API_CONTRACT_IMPLEMENTATION=PASS
UNSUPPORTED_API_USAGE=0
PRODUCTION_MOCK_DATA=0

AC_IMPLEMENTED=41
AC_PARTIALLY_IMPLEMENTED=0
AC_NOT_IMPLEMENTED=0
AC_IMPLEMENTATION_COVERAGE=PASS

ACCESSIBILITY_CHECK=PASS
ANGULAR_CODE_QUALITY=PASS

ANGULAR_BUILD=PASS
ANGULAR_FOCUSED_TESTS=PASS

PLAYWRIGHT_READINESS=READY
AC_NOT_E2E_READY=0

APPLICATION_SPECIFIC_PRODUCTION_BRANCHES=0

and all frozen-boundary checks pass.

======================================================================
33. COMMIT
======================================================================

If and ONLY if every hard gate passes, create exactly ONE commit:

Complete Doctor Angular implementation

Return:

COMMIT_SHA=
WORKTREE_STATUS=

Then STOP.

DO NOT RUN PLAYWRIGHT.
DO NOT REGENERATE REQUIREMENTS.
DO NOT TOUCH THE KNOWLEDGE GRAPH.
