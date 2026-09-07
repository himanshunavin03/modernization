POLARIS — REGENERATE AND FREEZE DOCTOR TECHNICAL TASKS

MODEL:
Sol

BASE_COMMIT:
bc49b62a95ca1a6e49efb9f6e974d9d2c654f27d

TARGET_FEATURE:
doctor-directory-management

FROZEN_KG_RUN:
legacy-dashboard-complete-application-demo-v1-2026-09-06-203944

MISSION:

Generate the FINAL Technical Task plan for Doctor Directory Management
from the currently frozen requirements.

The upstream requirements chain is complete.

DO NOT regenerate or modify:

- source analysis
- Tree-sitter
- Roslyn
- Facts
- Knowledge Graph
- Application Understanding
- Feature
- Functional Requirements
- Stories
- Acceptance Criteria
- Feature Specification
- architecture

Use the EXISTING normal Polaris technical-task pipeline.

The final Doctor contract currently contains:

21 Functional Requirements
21 Stories
41 Acceptance Criteria
6 Feature-owned API contracts

Do NOT hardcode those counts into production logic.

Read them from the current approved artifacts.

Generate/reconcile Technical Tasks only.

DO NOT modify Angular in this run.

======================================================================
1. BASELINE
======================================================================

Verify:

HEAD=bc49b62a95ca1a6e49efb9f6e974d9d2c654f27d
WORKTREE_CLEAN=YES

If not:

STOP.

Do not reset/stash/clean/discard user work.

======================================================================
2. RESOLVE CURRENT APPROVED INPUTS
======================================================================

Resolve the CURRENT approved Doctor artifacts from normal lineage/index
mechanisms.

Do not use stale run IDs merely because they exist on disk.

Identify and report:

DOCTOR_FEATURE_RUN=
DOCTOR_STORY_RUN=
DOCTOR_AC_RUN=
FEATURE_SPEC_PATH=

Verify all belong to the current frozen requirements chain.

Required:

FEATURE_LINEAGE=PASS
STORY_LINEAGE=PASS
AC_LINEAGE=PASS
FEATURE_SPEC_LINEAGE=PASS

Verify:

FR_COUNT=
STORY_COUNT=
AC_COUNT=
API_CONTRACT_COUNT=

Expected from current artifacts:

FR_COUNT=21
STORY_COUNT=21
AC_COUNT=41
API_CONTRACT_COUNT=6

If actual approved artifacts disagree:

STOP and report the lineage mismatch.

Do NOT regenerate requirements.

======================================================================
3. ARCHITECTURE INPUT
======================================================================

Use the existing approved architecture selection for:

doctor-directory-management

Do NOT recommend/select a new architecture.

Do NOT regenerate architecture.

Resolve:

ARCHITECTURE_SOURCE=
ARCHITECTURE_SELECTION=
MODERNIZATION_OPERATION=

The generic modernization operation should remain the existing registered
Angular Feature modernization operation where current artifacts select it.

Required:

ARCHITECTURE_STATUS=READY
MODERNIZATION_OPERATION_STATUS=READY

If architecture/operation selection is missing:

STOP.

Do not invent one in Technical Task generation.

======================================================================
4. REGENERATE TECHNICAL TASKS
======================================================================

Run the EXISTING:

/generate-technical-tasks doctor-directory-management

pipeline or its normal underlying implementation.

Generate Technical Tasks from the CURRENT:

Feature
→ FR
→ Stories
→ AC
→ API contracts
→ approved architecture

Do not manually construct the task JSON.

Do not patch old Technical Tasks.

Create a fresh Doctor Technical Task run with correct lineage.

======================================================================
5. TASK COVERAGE
======================================================================

Every implementation-relevant approved behavior must map to one or more
Technical Tasks.

Validate coverage for current requirements including where applicable:

- directory/list UI
- fixed ordering
- empty state
- detail/edit
- create
- successful create continuation
- update
- successful update continuation
- single delete
- selected/bulk delete
- confirmation
- Load More
- result append
- continuation visibility/termination
- form validation
- profile media
- navigation
- automatic tenant context

These are validation targets only.

Do not hardcode them into generic task-generation logic.

Required:

FR_WITHOUT_TECHNICAL_TASK=0
STORY_WITHOUT_TECHNICAL_TASK=0
AC_WITHOUT_TECHNICAL_TASK=0

======================================================================
6. API TASK COVERAGE
======================================================================

Validate task coverage for the six Feature-owned API contracts from the
current Feature artifact.

Expected where current contract confirms them:

GET    /api/doctors
GET    /api/doctors/{id}
POST   /api/doctors
PUT    /api/doctors
DELETE /api/doctors/{id}
GET    /api/users/current/tenant

Do NOT invent new backend APIs.

Do NOT add speciality/availability/appointment APIs unless the current
approved Feature explicitly owns them.

Required:

API_WITHOUT_IMPLEMENTATION_TASK=0
UNSUPPORTED_API_TASK=0

======================================================================
7. ANGULAR 22 ARCHITECTURE QUALITY
======================================================================

Technical Tasks must follow the EXISTING approved Angular architecture.

Where the architecture calls for them, tasks should correctly plan use of
modern Angular patterns such as:

- standalone components
- Signals
- computed/derived state
- signal-compatible state management
- typed reactive HTTP/service contracts
- modern template control flow
- lazy-loaded feature routes
- OnPush / zoneless-compatible design where architecture specifies it
- accessible UI behavior
- typed forms / Signal Forms only where the approved architecture and
  current Angular version/project configuration support them

IMPORTANT:

Do NOT add technology merely because it is fashionable.

Do NOT force Signal Forms if the current project/toolchain does not support
the intended implementation safely.

Technical choices must come from approved architecture + target stack.

======================================================================
8. PRESERVE LEGACY UX FIDELITY
======================================================================

Technical Tasks must implement the approved Feature behavior.

Do NOT convert:

Load More
→ numbered pagination

Do NOT invent:

search
filter
sorting controls
new navigation
new workflows

unless current requirements explicitly contain them.

Modernize the implementation architecture while preserving the approved UX
contract.

Required:

UX_FIDELITY=PASS
UNSUPPORTED_TECHNICAL_BEHAVIOR=0

======================================================================
9. TASK QUALITY
======================================================================

Each Technical Task must be implementation-ready.

Use the existing generic Technical Task artifact structure.

Tasks should contain the information already supported by the pipeline,
such as:

- Task ID
- title
- implementation objective
- linked FR/Story/AC
- affected layer/component
- implementation guidance
- API dependency where applicable
- validation/test expectation
- dependencies
- completion criteria

Do NOT create a new Doctor-specific task format.

Do not expose unnecessary KG/Roslyn internals in human-facing task
descriptions.

Required:

TECHNICAL_TASK_QUALITY=PASS

======================================================================
10. TASK GRANULARITY
======================================================================

Do not create:

one giant "Implement Doctor Feature" task.

Also do not create hundreds of trivial line-level tasks.

Tasks should be meaningful implementation units that can be assigned,
implemented, and validated.

Related AC may share a Technical Task where implementation is naturally
shared.

Do NOT force:

1 FR = 1 task
1 Story = 1 task
1 AC = 1 task

Report:

TECHNICAL_TASK_COUNT=

The count is an output, not a target.

======================================================================
11. EXISTING ANGULAR IMPLEMENTATION — READ ONLY
======================================================================

The Doctor Angular implementation already exists partially.

Inspect it READ-ONLY to determine implementation status against the new
Technical Task plan.

Do NOT modify Angular.

Classify each Technical Task:

IMPLEMENTED
PARTIALLY_IMPLEMENTED
NOT_IMPLEMENTED
BLOCKED

Use actual Angular code, not previous task status.

Report:

IMPLEMENTED_TASKS=
PARTIALLY_IMPLEMENTED_TASKS=
NOT_IMPLEMENTED_TASKS=
BLOCKED_TASKS=

This classification will be used by the NEXT modernization run.

======================================================================
12. DO NOT DELETE WORKING ANGULAR
======================================================================

When inspecting existing Angular, recognize valid existing implementation.

The next implementation stage should reconcile and extend it, not blindly
regenerate everything.

For this run:

ANGULAR_CHANGED=NO

======================================================================
13. TEST PLANNING
======================================================================

Technical Tasks should identify appropriate validation layers where
applicable:

- component/unit tests
- service/API tests
- form validation tests
- interaction tests
- Playwright E2E coverage

Do NOT write Playwright tests yet.

Do NOT run Playwright.

The task plan should make later test generation traceable to AC.

Required:

AC_TO_TEST_PLAN_COVERAGE=PASS

======================================================================
14. TRACEABILITY
======================================================================

Validate:

Feature
→ FR
→ Story
→ AC
→ Technical Task
→ API where applicable
→ planned validation

Required:

FR_WITHOUT_TECHNICAL_TASK=0
STORY_WITHOUT_TECHNICAL_TASK=0
AC_WITHOUT_TECHNICAL_TASK=0

ORPHAN_TECHNICAL_TASKS=0
UNSUPPORTED_TECHNICAL_TASKS=0

TECHNICAL_TASK_TRACEABILITY=PASS

======================================================================
15. REUSABILITY
======================================================================

Search changed generic production code if any.

Required:

APPLICATION_SPECIFIC_PRODUCTION_BRANCHES=0

No generic production branching based on:

HealthClinic
MyHealth
Doctor
doctor-directory-management
/api/doctors
LOAD MORE

Application-specific generated Technical Task artifacts naturally contain
Doctor details and are allowed.

======================================================================
16. FOCUSED TESTS
======================================================================

Run focused tests for:

- Technical Task generation
- Feature/Story/AC lineage resolution
- Technical Task traceability
- API task coverage
- task-quality validation
- generic modernization-operation resolution
- existing Angular implementation-status classification

Do NOT run:

- KG generation
- AU generation
- Feature generation
- Story generation
- AC generation
- architecture generation
- Angular build
- Playwright
- full repository suite unless a directly changed shared module genuinely
  requires it.

======================================================================
17. FROZEN-UPSTREAM CHECK
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
ANGULAR_CHANGED=NO
PLAYWRIGHT_CHANGED=NO
DASHBOARD_CHANGED=NO

Only Technical Task artifacts and generic Technical Task pipeline
code/tests, if genuinely required, may change.

======================================================================
18. FINAL REPORT
======================================================================

Return:

BASE_COMMIT=

DOCTOR_FEATURE_RUN=
DOCTOR_STORY_RUN=
DOCTOR_AC_RUN=
FEATURE_SPEC_PATH=

FR_COUNT=
STORY_COUNT=
AC_COUNT=
API_CONTRACT_COUNT=

FEATURE_LINEAGE=
STORY_LINEAGE=
AC_LINEAGE=
FEATURE_SPEC_LINEAGE=

ARCHITECTURE_SOURCE=
ARCHITECTURE_SELECTION=
ARCHITECTURE_STATUS=

MODERNIZATION_OPERATION=
MODERNIZATION_OPERATION_STATUS=

TECHNICAL_TASK_RUN=
TECHNICAL_TASK_COUNT=

FR_WITHOUT_TECHNICAL_TASK=
STORY_WITHOUT_TECHNICAL_TASK=
AC_WITHOUT_TECHNICAL_TASK=

API_WITHOUT_IMPLEMENTATION_TASK=
UNSUPPORTED_API_TASK=

ORPHAN_TECHNICAL_TASKS=
UNSUPPORTED_TECHNICAL_TASKS=

UX_FIDELITY=
TECHNICAL_TASK_QUALITY=
TECHNICAL_TASK_TRACEABILITY=
AC_TO_TEST_PLAN_COVERAGE=

IMPLEMENTED_TASKS=
PARTIALLY_IMPLEMENTED_TASKS=
NOT_IMPLEMENTED_TASKS=
BLOCKED_TASKS=

APPLICATION_SPECIFIC_PRODUCTION_BRANCHES=
FOCUSED_TESTS=

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
TECHNICAL_TASKS_CHANGED=
ANGULAR_CHANGED=
PLAYWRIGHT_CHANGED=
DASHBOARD_CHANGED=

======================================================================
19. HARD GATE
======================================================================

Do not commit unless:

FR_COUNT=21
STORY_COUNT=21
AC_COUNT=41
API_CONTRACT_COUNT=6

FEATURE_LINEAGE=PASS
STORY_LINEAGE=PASS
AC_LINEAGE=PASS
FEATURE_SPEC_LINEAGE=PASS

ARCHITECTURE_STATUS=READY
MODERNIZATION_OPERATION_STATUS=READY

FR_WITHOUT_TECHNICAL_TASK=0
STORY_WITHOUT_TECHNICAL_TASK=0
AC_WITHOUT_TECHNICAL_TASK=0

API_WITHOUT_IMPLEMENTATION_TASK=0
UNSUPPORTED_API_TASK=0

ORPHAN_TECHNICAL_TASKS=0
UNSUPPORTED_TECHNICAL_TASKS=0

UX_FIDELITY=PASS
TECHNICAL_TASK_QUALITY=PASS
TECHNICAL_TASK_TRACEABILITY=PASS
AC_TO_TEST_PLAN_COVERAGE=PASS

APPLICATION_SPECIFIC_PRODUCTION_BRANCHES=0

and all frozen-upstream checks are NO.

======================================================================
20. COMMIT
======================================================================

If all gates pass, create exactly ONE commit:

Freeze Doctor technical task plan

Return:

COMMIT_SHA=
WORKTREE_STATUS=

Then STOP.

DO NOT RUN /modernize-feature YET.
DO NOT MODIFY ANGULAR.
DO NOT RUN PLAYWRIGHT.
