# POLARIS — RESOLVE DOCTOR PATIENTS NAVIGATION AND FREEZE ANGULAR

MODEL:
Sol

BASE_COMMIT:
05f7d14

FROZEN_KG_RUN:
legacy-dashboard-complete-application-demo-v1-2026-09-06-203944

TARGET_FEATURE:
doctor-directory-management

MISSION:

Resolve ONLY the remaining Doctor Angular functional blocker:

FR-10 Patients navigation.

Current status:

41 AC total
39 functionally implemented
2 blocked by Patients navigation

15 non-Playwright Technical Tasks:
11 complete
4 partial

TT-016:
DEFERRED_TO_PLAYWRIGHT_STAGE

The current Angular implementation must be preserved.

Do NOT regenerate the Doctor feature.
Do NOT modify frozen upstream artifacts.
Do NOT run Playwright.

======================================================================
1. BASELINE
======================================================================

Verify:

HEAD starts with 05f7d14
WORKTREE_CLEAN=YES

If not, STOP.

Do not reset/stash/clean/discard work.

======================================================================
2. RESOLVE PATIENTS TARGET FROM FROZEN EVIDENCE
======================================================================

Do NOT ask the user to invent a Patients URL.

Trace FR-10 using ONLY frozen evidence:

KG 203944
→ Application Understanding
→ Doctor Feature
→ Story
→ AC
→ Technical Task

Determine the exact legacy Patients interaction:

Doctor UI action
→ frontend handler
→ navigation/state target
→ parameters/context passed

Report:

PATIENTS_ACTION=
PATIENTS_HANDLER=
LEGACY_NAVIGATION_TARGET=
LEGACY_NAVIGATION_PARAMETERS=
DOCTOR_CONTEXT_PASSED=
PATIENTS_NAVIGATION_EVIDENCE=PASS/FAIL

Do not infer from labels alone.

======================================================================
3. INSPECT MODERN ANGULAR ROUTES
======================================================================

Search the existing modern Angular application READ-ONLY first.

Determine whether a Patient destination already exists.

Inspect:

- app routes
- lazy routes
- feature routes
- patient feature libraries/components
- navigation configuration

Report:

MODERN_PATIENT_FEATURE_EXISTS=YES/NO
MODERN_PATIENT_ROUTE_EXISTS=YES/NO
MODERN_PATIENT_ROUTE=
MODERN_PATIENT_ROUTE_PARAMETERS=

Do not create anything yet.

======================================================================
4. RESOLVE CROSS-FEATURE DEPENDENCY
======================================================================

The project already has a separate Feature:

patient-directory-management

Determine whether FR-10 is actually a cross-feature navigation dependency
from Doctor Directory Management to Patient Directory Management.

Report:

PATIENT_DIRECTORY_FEATURE_EXISTS=YES/NO
FR10_CROSS_FEATURE_DEPENDENCY=YES/NO

If Patient Directory Management is the evidence-backed destination, preserve
that relationship.

Do NOT duplicate the Patient feature inside Doctor.

======================================================================
5. IMPLEMENTATION DECISION
======================================================================

Use this deterministic decision:

CASE A:
Modern Patient route already exists.

→ Wire the Doctor Patients action to that route using the evidence-backed
context/parameters.

CASE B:
Patient feature exists as an approved Feature but its Angular destination
has not yet been implemented.

→ Do NOT build the entire Patient feature.

→ Implement the smallest architecture-valid cross-feature navigation
contract supported by the existing application architecture, ONLY if a
real routable destination/feature-shell contract already exists.

If no routable destination exists, classify:

PATIENT_FEATURE_IMPLEMENTATION_DEPENDENCY

Do NOT invent a fake Patient screen or arbitrary URL.

CASE C:
Frozen evidence points to a destination unrelated to Patient Directory
Management.

→ Follow the actual frozen evidence.

======================================================================
6. NO INVENTED ROUTES
======================================================================

Forbidden:

inventing /patients
inventing /patients/:doctorId
inventing /doctor/patients
creating placeholder Patient UI merely to satisfy AC
hardcoding an unsupported external URL

The route must come from:

existing modern Angular architecture

or

a legitimate existing cross-feature route contract.

======================================================================
7. FINISH OTHER PARTIAL TASKS
======================================================================

Inspect the four currently PARTIAL non-Playwright Technical Tasks.

Some may be partial solely because FR-10 is unresolved.

Complete every remaining implementation gap that does NOT require building
the separate Patient Directory Feature.

Preserve all working implementation from 05f7d14.

Do not reimplement completed functionality.

======================================================================
8. ANGULAR ARCHITECTURE AUDIT
======================================================================

Before freezing Angular, validate the Doctor implementation against the
approved Angular architecture.

Report explicitly:

ANGULAR_VERSION=
STANDALONE_COMPONENTS=
LAZY_FEATURE_ROUTING=
SIGNALS_USED=
COMPUTED_USED=
RXJS_HTTP_BOUNDARY=
FORM_TECHNOLOGY=
ONPUSH_OR_APPROVED_CHANGE_DETECTION=
STRICT_TYPING=
MODERN_TEMPLATE_CONTROL_FLOW=

Do not change working architecture merely to make a technology flag YES.

======================================================================
9. SIGNALS
======================================================================

Verify Signals are being used appropriately for synchronous Doctor UI
state.

Check where applicable:

- collection state
- selected Doctor
- selected-record IDs
- loading state
- continuation state
- derived ordering
- derived button/visibility state

Required:

SIGNAL_ARCHITECTURE=PASS

Do not convert every Observable into a Signal.

======================================================================
10. SIGNAL FORMS — AUDIT ONLY
======================================================================

Determine whether the current approved Angular version/project setup
supports Signal Forms appropriately.

Report:

SIGNAL_FORMS_AVAILABLE=
SIGNAL_FORMS_CURRENTLY_USED=
SIGNAL_FORMS_MIGRATION_RECOMMENDED_FOR_POC=YES/NO

IMPORTANT:

Do NOT migrate the Doctor form to Signal Forms in this run.

Current typed Reactive Forms may remain if architecture-compliant.

Required:

CURRENT_FORM_ARCHITECTURE=PASS

We will decide separately whether Signal Forms are worth demonstrating
after functional/E2E freeze.

======================================================================
11. UX FIDELITY
======================================================================

Revalidate:

CONTINUATION_UX_FIDELITY=PASS
DELETE_UX_FIDELITY=PASS
PROFILE_MEDIA_FIDELITY=PASS
FORM_VALIDATION_COVERAGE=PASS
TENANT_CONTEXT_FIDELITY=PASS

Load More must remain Load More.

Do not introduce numbered pagination.

======================================================================
12. API CONTRACT
======================================================================

Required:

API_CONTRACT_IMPLEMENTATION=PASS
UNSUPPORTED_API_USAGE=0
PRODUCTION_MOCK_DATA=0

Do not create a Patient backend API merely to resolve navigation.

======================================================================
13. FUNCTIONAL AC STATUS
======================================================================

Re-evaluate all 41 AC.

Separate:

FUNCTIONALLY_IMPLEMENTED

from:

PLAYWRIGHT_COVERED

Required if the Patient route can legitimately be resolved:

AC_FUNCTIONALLY_IMPLEMENTED=41
AC_FUNCTIONALLY_PARTIAL=0
AC_FUNCTIONALLY_MISSING=0

If Patient destination genuinely depends on the not-yet-modernized Patient
Feature and cannot be routed yet, report:

AC_FUNCTIONALLY_IMPLEMENTED=39
AC_BLOCKED_BY_CROSS_FEATURE_DEPENDENCY=2

and identify the exact AC IDs.

Do NOT falsely mark them implemented.

======================================================================
14. TECHNICAL TASK STATUS
======================================================================

Re-evaluate all 16 frozen Technical Tasks.

TT-016 remains:

DEFERRED_TO_PLAYWRIGHT_STAGE

For the other 15:

NON_PLAYWRIGHT_IMPLEMENTED_TASKS=
NON_PLAYWRIGHT_PARTIAL_TASKS=
NON_PLAYWRIGHT_NOT_IMPLEMENTED_TASKS=
NON_PLAYWRIGHT_BLOCKED_TASKS=

Target:

15 / 0 / 0 / 0

But do not fake completion if the Patient cross-feature dependency
legitimately blocks one task.

======================================================================
15. BUILD + FOCUSED TESTS
======================================================================

Run:

Angular build
focused Doctor Angular tests

Required:

ANGULAR_BUILD=PASS
ANGULAR_FOCUSED_TESTS=PASS

Do NOT run Playwright.

======================================================================
16. FROZEN BOUNDARY
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

Only Doctor Angular code/tests and an implementation validation record may
change.

======================================================================
17. FINAL REPORT
======================================================================

Return:

BASE_COMMIT=

PATIENTS_ACTION=
PATIENTS_HANDLER=
LEGACY_NAVIGATION_TARGET=
LEGACY_NAVIGATION_PARAMETERS=
DOCTOR_CONTEXT_PASSED=
PATIENTS_NAVIGATION_EVIDENCE=

MODERN_PATIENT_FEATURE_EXISTS=
MODERN_PATIENT_ROUTE_EXISTS=
MODERN_PATIENT_ROUTE=
MODERN_PATIENT_ROUTE_PARAMETERS=

PATIENT_DIRECTORY_FEATURE_EXISTS=
FR10_CROSS_FEATURE_DEPENDENCY=
PATIENT_NAVIGATION_RESOLUTION=

NON_PLAYWRIGHT_IMPLEMENTED_TASKS=
NON_PLAYWRIGHT_PARTIAL_TASKS=
NON_PLAYWRIGHT_NOT_IMPLEMENTED_TASKS=
NON_PLAYWRIGHT_BLOCKED_TASKS=

TT016_STATUS=

AC_FUNCTIONALLY_IMPLEMENTED=
AC_FUNCTIONALLY_PARTIAL=
AC_FUNCTIONALLY_MISSING=
AC_BLOCKED_BY_CROSS_FEATURE_DEPENDENCY=

ANGULAR_VERSION=
STANDALONE_COMPONENTS=
LAZY_FEATURE_ROUTING=
SIGNALS_USED=
COMPUTED_USED=
RXJS_HTTP_BOUNDARY=
FORM_TECHNOLOGY=
ONPUSH_OR_APPROVED_CHANGE_DETECTION=
STRICT_TYPING=
MODERN_TEMPLATE_CONTROL_FLOW=

SIGNAL_ARCHITECTURE=
SIGNAL_FORMS_AVAILABLE=
SIGNAL_FORMS_CURRENTLY_USED=
SIGNAL_FORMS_MIGRATION_RECOMMENDED_FOR_POC=
CURRENT_FORM_ARCHITECTURE=

CONTINUATION_UX_FIDELITY=
DELETE_UX_FIDELITY=
PROFILE_MEDIA_FIDELITY=
FORM_VALIDATION_COVERAGE=
TENANT_CONTEXT_FIDELITY=

API_CONTRACT_IMPLEMENTATION=
UNSUPPORTED_API_USAGE=
PRODUCTION_MOCK_DATA=

ANGULAR_BUILD=
ANGULAR_FOCUSED_TESTS=

PLAYWRIGHT_GENERATION_READINESS=

CHANGED_ANGULAR_FILES=

SOURCE_CHANGED=
FACTS_CHANGED=
KG_CHANGED=
APPLICATION_UNDERSTANDING_CHANGED=
FEATURE_CHANGED=
STORIES_CHANGED=
AC_CHANGED=
FEATURE_SPEC_CHANGED=
ARCHITECTURE_CHANGED=
TECHNICAL_TASK_PLAN_CHANGED=
DASHBOARD_CHANGED=
PLAYWRIGHT_CHANGED=

======================================================================
18. COMMIT GATE
======================================================================

If the Patient navigation can be legitimately resolved and:

NON_PLAYWRIGHT_IMPLEMENTED_TASKS=15
NON_PLAYWRIGHT_PARTIAL_TASKS=0
NON_PLAYWRIGHT_NOT_IMPLEMENTED_TASKS=0
NON_PLAYWRIGHT_BLOCKED_TASKS=0

AC_FUNCTIONALLY_IMPLEMENTED=41
AC_FUNCTIONALLY_PARTIAL=0
AC_FUNCTIONALLY_MISSING=0

SIGNAL_ARCHITECTURE=PASS
CURRENT_FORM_ARCHITECTURE=PASS

ANGULAR_BUILD=PASS
ANGULAR_FOCUSED_TESTS=PASS

PLAYWRIGHT_GENERATION_READINESS=READY

and all frozen-boundary gates pass:

create exactly ONE commit:

Freeze Doctor Angular implementation

Return:

COMMIT_SHA=
WORKTREE_STATUS=

If the Patient destination genuinely cannot exist until the separate Patient
Feature is modernized:

DO NOT invent it.

Commit the valid Doctor Angular implementation only if repository policy
permits an explicit cross-feature dependency checkpoint, with:

FR10_STATUS=BLOCKED_BY_PATIENT_FEATURE

and clearly preserve the two blocked AC for later integration.

Then STOP.

DO NOT RUN PLAYWRIGHT.
