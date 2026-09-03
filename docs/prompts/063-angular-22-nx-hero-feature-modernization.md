POLARIS MODERNIZATION
PROMPT 063

ANGULAR 22 / NX HERO FEATURE MODERNIZATION
+ EXISTING UI RECONSTRUCTION
+ ARCHITECTURE-DRIVEN CODE GENERATION
+ END-TO-END TRACEABILITY

======================================================================
BASELINE
======================================================================

Work from the approved Polaris baseline:

CURRENT_APPROVED_BASELINE=
eff0cb150e399a5d363519a5f4498f92b36ad5f0

This commit is the APPROVED AND FROZEN planning baseline.

It contains:

- frozen deterministic application understanding
- frozen Knowledge Graph
- approved Business Features
- approved Functional Requirements
- approved Stories
- authoritative Acceptance Criteria
- approved Jira delivery artifacts
- approved Feature Specifications
- locked ArchitectureSelection
- enterprise Angular architecture catalog
- architecture ADRs
- optional Figma provider capability
- approved architecture-driven Technical Tasks

Before changing anything:

1. Verify HEAD and working tree.
2. Verify baseline commit exists in history.
3. Report exact base/parent used.
4. Read:
   - AGENTS.md
   - PROJECT_MEMORY.md
   - PROGRESS.md
   - DECISIONS.md
   - docs/prompts/060*
   - docs/prompts/061*
   - docs/prompts/062*
5. Inspect:
   - artifacts/architecture/latest/
   - artifacts/technical-tasks/latest/
   - approved Feature Specification artifacts
   - approved application-understanding artifacts
   - approved Knowledge Graph / Facts only as needed for traceability
6. Inspect the ACTUAL source implementation for the hero Dashboard.
7. Identify all approved existing Dashboard UI surfaces and supporting
   styles/assets/behavior before generating Angular.

Do not start generation until the actual old UI has been inspected.

======================================================================
FROZEN UPSTREAM CONTRACT
======================================================================

Do NOT redesign or regenerate:

- deterministic analyzers
- Tree-sitter
- Roslyn
- LSP
- Facts
- Knowledge Graph
- API resolver
- Application Understanding
- Business Features
- Functional Requirements
- Stories
- authoritative Acceptance Criteria
- Jira quality
- Feature Specifications
- architecture catalog
- ArchitectureRecommendation
- ArchitectureSelection
- ADR decisions
- Technical Tasks
- Figma provider architecture

Expected business baseline:

FEATURES=5
STORIES=12
AUTHORITATIVE_AC=14

Expected hero Feature:

feature-operational-dashboard-insights

Expected hero requirements:

FR_COUNT=5
HERO_STORY_COUNT=3
HERO_AC_COUNT=5

Expected Technical Tasks:

TECHNICAL_TASK_COUNT=16

Architecture selection MUST remain unchanged.

======================================================================
CRITICAL DESIGN RULE FOR THIS POC
======================================================================

THERE IS NO NEW CUSTOMER FIGMA DESIGN FOR THE CURRENT HEALTHCLINIC
MODERNIZATION.

The Figma fixture created in Prompt 062 is NOT the design source for the
HealthClinic Angular application.

DO NOT generate the Dashboard from:

artifacts/design/latest fixture data

DO NOT treat the Figma fixture as approved visual design.

The fixture exists only to prove that Polaris supports optional Figma input.

For THIS POC:

DESIGN_SOURCE=
EXISTING_APPLICATION_UI

The actual existing Razor / AngularJS / HTML / CSS / assets / visible behavior
are the visual and interaction reference.

The modernization goal is:

PRESERVE / RECONSTRUCT THE EXISTING USER EXPERIENCE
while
MODERNIZING THE TECHNICAL IMPLEMENTATION.

Conceptually:

Existing Razor / AngularJS UI
        ↓
UI Reconstruction Specification
        ↓
Approved Requirements
        +
Locked Architecture
        +
Technical Tasks
        ↓
Angular 22 / Nx Implementation

======================================================================
PART 1 — IDENTIFY THE REAL HERO UI
======================================================================

Before generating Angular, deterministically inspect the actual existing
Dashboard implementation.

Use the approved application-understanding/KG artifacts to locate the relevant
surfaces, then inspect the real source.

Known approved candidates include:

Razor:
src/MyHealth.Web/Views/Dashboard/Index.cshtml

AngularJS:
the approved DashboardController / Dashboard AngularJS implementation and
associated templates/routes/scripts.

Do NOT assume these are the only relevant files.

Follow deterministic references to find relevant:

- Razor views
- AngularJS templates
- AngularJS controllers
- route configuration
- CSS
- layout files
- partials
- JavaScript
- assets
- images/icons
- shared UI elements
- navigation
- existing controls
- visible labels
- reporting-year behavior
- Dashboard API usage

Only include files actually relevant to the hero Feature.

Do not broadly copy the entire old frontend.

======================================================================
PART 2 — UI RECONSTRUCTION SPECIFICATION
======================================================================

Create a deterministic:

ExistingUiSpecification
or
UiReconstructionSpecification

Use whichever name best fits repository conventions.

This is NOT an LLM-generated redesign.

It is a normalized implementation reference extracted from the existing
application.

Suggested fields:

- feature_id
- source_mode
- surfaces[]
- regions[]
- controls[]
- visible_text[]
- navigation[]
- interactions[]
- layouts[]
- styles[]
- css_classes[]
- assets[]
- data_bindings[]
- api_relationships[]
- responsive_behavior[]
- shared_elements[]
- unresolved_visual_details[]
- source_traceability[]

SOURCE_MODE must be:

EXISTING_APPLICATION_UI

NOT:

FIGMA

======================================================================
PART 3 — UI PRESERVATION PRINCIPLES
======================================================================

Preserve where deterministically observable:

- information hierarchy
- page structure
- major regions
- headings
- labels
- controls
- reporting-year selection behavior
- expense presentation
- patient presentation
- clinic summary presentation
- navigation behavior
- visible business information
- relevant colors
- typography hierarchy
- spacing/layout relationships
- reusable visual patterns
- relevant assets/icons
- responsive behavior where actually established

Do NOT require pixel-perfect copying.

Do NOT copy obsolete implementation mechanics merely because they existed.

The goal is:

FUNCTIONALLY RECOGNIZABLE
+
VISUALLY FAITHFUL
+
TECHNICALLY MODERN

Do not redesign the Dashboard into an unrelated modern template.

======================================================================
PART 4 — LEGACY IMPLEMENTATION MUST NOT LEAK INTO NEW ARCHITECTURE
======================================================================

Preserve UI/behavior.

Do NOT preserve obsolete implementation patterns.

Examples:

Razor rendering
    →
Angular 22 components

AngularJS controllers
    →
Angular 22 standalone components/services/state

$scope
    →
Signals / appropriate state

AngularJS routing
    →
Angular Router

legacy AJAX/API wrappers
    →
selected typed integration architecture

manual DOM manipulation
    →
Angular declarative templates

Zone-dependent architecture
    →
locked zoneless target where compatible

Do not copy AngularJS architecture into Angular 22.

======================================================================
PART 5 — GENERATION SOURCE-OF-TRUTH ORDER
======================================================================

When generating code, use this precedence:

1. Approved Functional Requirements
2. Authoritative Acceptance Criteria
3. Locked ArchitectureSelection
4. Approved Technical Tasks
5. Existing API Contracts
6. Existing UI Reconstruction Specification
7. Existing UI assets/styles where safe and relevant
8. Optional implementation defaults

Figma fixture has NO authority for current generation.

If existing UI conflicts with approved business requirements:

REQUIREMENTS WIN.

If existing UI conflicts with locked architecture:

ARCHITECTURE WINS for technical implementation.

If visual behavior is unclear:

DO NOT INVENT IMPORTANT BUSINESS BEHAVIOR.

Record:

UI_RECONSTRUCTION_CLARIFICATION

======================================================================
PART 6 — GENERATION OUTPUT LOCATION
======================================================================

Do NOT modify source/.

Create the modernized target application in a clearly separate location.

Prefer repository-consistent location such as:

modernized/
or
generated/

Use the existing project convention if one already exists.

Conceptually:

modernized/
    apps/
    libs/

Do not mix generated Angular code with:

src/polaris_modernization/

Polaris engine code and generated application code must remain clearly
separated.

======================================================================
PART 7 — NX WORKSPACE
======================================================================

The locked architecture selects Nx.

Create the actual target Nx workspace/application structure.

Do NOT silently substitute Angular CLI single-app architecture.

Use a practical POC structure.

Conceptually:

modernized/
├── apps/
│   └── healthclinic-web/
│
├── libs/
│   ├── dashboard/
│   │   ├── feature/
│   │   ├── ui/
│   │   ├── data-access/
│   │   └── state/
│   │
│   ├── shared/
│   │   ├── ui/
│   │   ├── data-access/
│   │   └── util/
│   │
│   └── core/
│       ├── auth/
│       ├── tenant/
│       └── observability/
│
├── nx.json
├── package.json
└── ...

Do not create excessive libraries for a small POC.

The actual structure should demonstrate Nx/domain boundaries without becoming
architecture theater.

======================================================================
PART 8 — ANGULAR 22
======================================================================

The generated application must target Angular 22.

Use modern Angular patterns supported by the actual installed/selected Angular
version.

Use:

- standalone components
- modern template syntax/control flow
- Signals
- computed() where derived state exists
- effect() only where a real side effect justifies it
- RxJS at async/HTTP/event boundaries
- Signals/RxJS interoperability where useful
- Angular Router
- lazy feature routing
- typed HttpClient
- functional interceptors where appropriate
- functional guards where appropriate
- zoneless configuration if valid for the selected Angular version/runtime
- @defer only where it provides a real loading/performance boundary

Do not use technology merely to satisfy a checklist.

======================================================================
PART 9 — STATE STRATEGY
======================================================================

Architecture selection does NOT select NgRx.

Do NOT introduce:

- NgRx Store
- NgRx Effects
- NgRx Entity
- global Redux-style architecture

Use Signals for appropriate Dashboard UI/feature state.

Use RxJS for asynchronous API boundaries.

Example conceptual state:

selectedYear = signal(...)
expenses = signal(...)
patients = signal(...)
clinicSummary = signal(...)
tenant = signal(...)

loading/error may be represented appropriately.

Use computed() for real derived state only.

Do not artificially create signals for constants.

======================================================================
PART 10 — FORMS / YEAR SELECTION
======================================================================

Do not invent a large form architecture if Dashboard only contains a reporting
year selector.

Preserve the actual year-selection interaction.

If the existing UI uses a selector/dropdown/input, reproduce the appropriate
behavior.

Signal Forms support exists in the architecture catalog, but do not force a
form framework where unnecessary.

Use the simplest Angular 22 implementation consistent with the actual UI and
locked architecture.

======================================================================
PART 11 — ROUTING
======================================================================

Create a proper Dashboard feature route.

Use lazy loading as selected by architecture.

Preserve existing navigation intent.

Do not replicate obsolete URL structures unless required by approved
requirements.

Where route equivalence matters, record mapping:

OLD_ROUTE
→
NEW_ROUTE

in generation traceability.

======================================================================
PART 12 — API CONTRACT PRESERVATION
======================================================================

These four existing backend business contracts remain authoritative:

GET /api/reports/expenses/{year}

GET /api/reports/patients/{year}

GET /api/reports/clinicsummary

GET /api/users/current/tenant

Do NOT change:

- HTTP method
- path semantics
- year parameter semantics
- known response-model semantics

Create typed target models based only on approved/proven contract information.

Do not invent backend fields merely to make UI prettier.

======================================================================
PART 13 — GATEWAY / BFF REALITY
======================================================================

The locked TARGET architecture selects:

Angular
    ↓
API Gateway
    ↓
BFF
    ↓
Existing APIs

However:

Prompt 063 is primarily the Angular hero-feature generation stage.

Do NOT falsely claim a production Gateway or BFF exists unless this prompt
actually implements the required POC boundary.

Do NOT rewrite existing backend contracts.

Implement the frontend integration so it is compatible with the selected
Gateway/BFF topology.

Prefer an abstraction such as:

Angular Dashboard
       ↓
DashboardDataAccess / Client Boundary
       ↓
configurable frontend integration base URL
       ↓
future/target BFF
       ↓
existing backend APIs

If a minimal local POC BFF is genuinely required to make the generated
application architecture coherent, keep it extremely small and clearly mark
its target contracts as GENERATED_TARGET_CONTRACT, never EXISTING_API.

BUT DO NOT spend this prompt building enterprise gateway infrastructure.

Gateway remains a target deployment/integration concern.

The existing backend APIs remain the source business contracts.

======================================================================
PART 14 — CONFIGURATION
======================================================================

Do not hardcode production URLs.

Use environment/runtime configuration for API integration.

Support a clean future topology:

local development
→ direct/configurable integration

enterprise deployment
→ Gateway/BFF endpoint

Do not expose secrets.

======================================================================
PART 15 — DASHBOARD UI
======================================================================

Generate the actual hero Dashboard UI.

It must visibly represent the existing application's Dashboard behavior.

Expected functional areas, where supported by existing UI/requirements:

- operational Dashboard entry
- organization/tenant-aware context
- reporting-year selection
- yearly expense information
- yearly patient information
- clinic summary
- relevant headings/labels
- existing recognizable card/panel/summary structure
- loading/empty/error behavior only where requirements or implementation
  quality justify it

Do not invent unrelated:

- charts
- KPIs
- metrics
- workflows
- buttons
- business actions

unless the existing UI or approved requirements support them.

======================================================================
PART 16 — VISUAL FIDELITY
======================================================================

Reuse or recreate relevant visual styling safely.

Prefer modern CSS while preserving visual identity.

If old CSS is reusable and legally/repository appropriate, selectively adapt
the relevant styles.

Do NOT dump the entire old CSS bundle into the Angular app.

Normalize:

- layout
- spacing
- card/panel presentation
- typography hierarchy
- relevant colors
- responsive behavior

Create shared styles/tokens only where actual reuse justifies them.

======================================================================
PART 17 — ASSETS
======================================================================

Reuse existing local assets only when:

- they belong to the application
- they are relevant to the hero Feature
- they are safe to copy into generated target
- references can be preserved

Record asset traceability.

Do not copy unrelated application assets.

======================================================================
PART 18 — ACCESSIBILITY
======================================================================

Implement baseline accessibility:

- semantic HTML
- labels for controls
- keyboard operability
- visible focus behavior
- sensible heading hierarchy
- accessible status/loading communication where applicable
- sufficient structure for later automated accessibility testing

Do not claim formal WCAG compliance yet.

======================================================================
PART 19 — OBSERVABILITY / ERROR BOUNDARY
======================================================================

Implement architecture-aligned foundations for:

- centralized HTTP error handling
- correlation identifier propagation where appropriate
- frontend error boundary/service
- structured logging abstraction

Do not select a telemetry vendor.

Do not build a full observability platform.

======================================================================
PART 20 — SECURITY / TENANT CONTEXT
======================================================================

Preserve approved tenant context behavior.

Use:

GET /api/users/current/tenant

where required by the approved Dashboard requirements.

Do not invent an identity provider.

Do not invent roles/permissions that are not approved.

Provide architecture-ready auth/tenant boundaries without fabricating security
requirements.

======================================================================
PART 21 — TEST GENERATION
======================================================================

Generate tests with the Angular code.

At minimum:

- component/unit tests for meaningful Dashboard behavior
- state/data-access tests
- API client tests/mocks
- routing test where useful
- Playwright E2E specification mapped to hero Acceptance Criteria

The Playwright tests should be traceable to:

AC IDs

Do not claim they passed until Prompt 064 actually executes them.

This prompt GENERATES tests.

Prompt 064 EXECUTES/REPAIRS them.

======================================================================
PART 22 — ACCEPTANCE CRITERIA TRACEABILITY
======================================================================

Every hero AC must map to at least one:

- Angular implementation element
or
- generated test

Target:

HERO_AC=5
AC_WITH_IMPLEMENTATION_TRACEABILITY=5
AC_WITH_TEST_TRACEABILITY=5

If a genuine limitation prevents test implementation, record it explicitly.

Do not fabricate coverage.

======================================================================
PART 23 — TECHNICAL TASK EXECUTION TRACEABILITY
======================================================================

Consume the 16 approved Technical Tasks.

For every task, classify:

IMPLEMENTED
PARTIALLY_IMPLEMENTED
DEFERRED
NOT_APPLICABLE

Do not silently drop tasks.

Gateway infrastructure tasks may legitimately be:

DEFERRED_TO_DEPLOYMENT

if implementation is outside the Angular hero POC.

BFF tasks may be:

IMPLEMENTED_POC_BOUNDARY
or
DEFERRED

depending on actual implementation.

Explain honestly.

======================================================================
PART 24 — GENERATION TRACEABILITY MODEL
======================================================================

Create a machine-readable generation traceability artifact.

Conceptually:

Source UI
   ↓
UI Reconstruction Element
   ↓
Feature
   ↓
FR
   ↓
Story
   ↓
AC
   ↓
Architecture Decision
   ↓
ADR
   ↓
Technical Task
   ↓
Generated File
   ↓
Angular Component/Service/Route
   ↓
Generated Test

Suggested artifact:

artifacts/modernization/latest/traceability.json

Also generate a human-readable summary:

artifacts/modernization/latest/traceability.md

Do not manually duplicate inconsistent traceability.

======================================================================
PART 25 — UI RECONSTRUCTION ARTIFACTS
======================================================================

Generate:

artifacts/modernization/latest/ui-reconstruction.json

artifacts/modernization/latest/ui-reconstruction.md

Optionally generate:

artifacts/modernization/latest/ui-reconstruction.html

if it can be produced cheaply and is useful for the demo.

The HTML, if generated, should show:

OLD UI ELEMENT
→
NEW ANGULAR ELEMENT

without exposing internal analyzer noise.

Example:

Operational Dashboard
→
DashboardFeatureComponent

Reporting year selector
→
Angular year selector control

Expense summary
→
ExpenseSummaryComponent

Only use mappings actually created.

======================================================================
PART 26 — MODERNIZATION SUMMARY HTML
======================================================================

Generate a polished:

artifacts/modernization/latest/modernization.html

This will be valuable for the final customer demo.

Suggested sections:

1. Modernization Summary
2. Existing UI → Angular 22
3. Selected Architecture
4. Hero Feature
5. UI Reconstruction
6. Generated Angular Components
7. API Contract Preservation
8. Technical Task Progress
9. Acceptance Criteria Coverage
10. Test Generation
11. Traceability
12. Build/Test Status
13. Next Step

IMPORTANT:

At this stage Build/Test Status should say:

NOT YET EXECUTED

unless generation requires a minimal syntax check.

Do not claim Prompt 064 results before Prompt 064.

======================================================================
PART 27 — GENERATION MANIFEST
======================================================================

Generate:

artifacts/modernization/latest/generation-manifest.json

Include:

- project_id
- feature_id
- source_ui_mode
- architecture_selection_ref
- technical_task_ref
- generated_workspace
- generated_files[]
- generated_components[]
- generated_services[]
- generated_routes[]
- generated_models[]
- generated_tests[]
- preserved_api_contracts[]
- reused_assets[]
- task_statuses[]
- unresolved_items[]
- generation_timestamp
- generator/version metadata where available

======================================================================
PART 28 — NO FIGMA CONTAMINATION
======================================================================

Add an explicit validator:

CURRENT_GENERATION_DESIGN_SOURCE_IS_EXISTING_UI

Validate:

FIGMA_FIXTURE_USED_FOR_GENERATION=NO

The generated Angular UI must not contain design values that exist only in the
Prompt 062 fixture unless independently present in the real existing UI.

This is critical.

The final report must explicitly state whether fixture design influenced
generation.

Expected:

FIGMA_FIXTURE_USED_FOR_GENERATION=NO

======================================================================
PART 29 — GENERATION VALIDATORS
======================================================================

Add validators for:

GENERATED_WORKSPACE_EXISTS
NX_ARCHITECTURE_ALIGNED
ANGULAR_22_TARGETED
STANDALONE_COMPONENTS_USED
SIGNALS_STRATEGY_ALIGNED
RXJS_ASYNC_BOUNDARY_ALIGNED
ZONELESS_TARGET_ALIGNED
NO_UNSELECTED_NGRX
NO_UNSELECTED_SSR
NO_UNSELECTED_HYDRATION
NO_UNSELECTED_MICROFRONTEND
NO_UNSELECTED_MODULE_FEDERATION
HERO_FEATURE_ONLY
EXISTING_API_CONTRACTS_PRESERVED
NO_INVENTED_EXISTING_API
UI_RECONSTRUCTION_TRACEABLE
NO_FIGMA_FIXTURE_CONTAMINATION
TECHNICAL_TASKS_ACCOUNTED_FOR
HERO_FR_TRACEABILITY_COMPLETE
HERO_STORY_TRACEABILITY_COMPLETE
HERO_AC_TRACEABILITY_COMPLETE
GENERATED_TEST_TRACEABILITY_COMPLETE
SOURCE_UNCHANGED

Do not equate static validation with successful build/runtime.

======================================================================
PART 30 — BUILD DISCIPLINE
======================================================================

Prompt 063 is GENERATION.

Prompt 064 will be:

BUILD
→ TEST
→ PEP DIAGNOSIS
→ REPAIR
→ REBUILD
→ RETEST

Therefore:

Do not spend unlimited time repairing dependency/environment/build issues in
this prompt.

However, perform cheap generation-level validation such as:

- JSON validation
- file existence
- package manifest consistency
- TypeScript/Angular structural checks if immediately available
- obvious import/reference validation

If a simple build can be executed quickly without repair work, it may be
recorded as informational.

But do not turn Prompt 063 into Prompt 064.

======================================================================
PART 31 — LANGGRAPH
======================================================================

Integrate generation into the existing orchestration architecture.

Do not create an unrelated script.

Conceptually extend the modernization flow:

Requirements
    ↓
Architecture
    ↓
Optional Design
    ↓
Technical Tasks
    ↓
Load Existing UI
    ↓
Reconstruct UI
    ↓
Generate Angular Hero Feature
    ↓
Validate Generation
    ↓
Finalize Generation

The exact graph may be a dedicated modernization subgraph.

Keep it simple and real.

Record actual transitions.

======================================================================
PART 32 — LANGCHAIN
======================================================================

Preserve the existing structured LangChain integration boundary.

Do not require an external LLM API.

EXTERNAL_LLM_CALLS=0 remains acceptable for this deterministic POC stage.

If code generation is implemented deterministically/templates/models, report
that honestly.

Do not claim an LLM generated code if it did not.

Keep future Codex/Copilot/Azure/Bedrock integration possible.

======================================================================
PART 33 — PEP PREPARATION
======================================================================

Do NOT implement full PEP repair yet.

But generation artifacts should be ready for Prompt 064 to consume.

Prepare a simple validation/result contract capable of later representing:

ATTEMPT
FAILURE
CONTEXT
DIAGNOSIS
REPAIR
REVALIDATION

Do not over-engineer it now.

======================================================================
PART 34 — CUSTOMER DEMO STORY
======================================================================

The generated artifacts should support this truthful demonstration:

"We analyzed the complete application and identified a representative
business Feature spanning the existing Dashboard implementation.

Because no new target design was supplied, Polaris reconstructed the existing
user experience rather than inventing a new interface.

The Feature was then generated using the selected Angular 22 enterprise
architecture while preserving the existing backend business contracts.

If a customer supplies Figma, Polaris can consume it as an optional target
design input through the same modernization pipeline."

Do not use this statement unless implementation supports it.

======================================================================
PART 35 — TESTS FOR POLARIS GENERATOR
======================================================================

Add focused Polaris tests for:

1. existing UI source mode selected
2. Figma fixture excluded
3. Dashboard Razor surface discovered
4. Dashboard AngularJS surface discovered where applicable
5. UI reconstruction model generated
6. relevant UI regions normalized
7. relevant controls normalized
8. source traceability present
9. Nx target generated
10. Angular 22 target present
11. standalone components generated
12. Signals used
13. RxJS async boundary present
14. no NgRx
15. no SSR
16. no hydration
17. no MFE
18. no Module Federation
19. lazy Dashboard route generated
20. typed API integration generated
21. all four existing APIs preserved
22. no invented existing APIs
23. tenant context represented
24. year behavior represented
25. expense behavior represented
26. patient behavior represented
27. clinic-summary behavior represented
28. relevant UI fidelity mapping exists
29. all 16 technical tasks accounted for
30. hero 5 FR traceability
31. hero 3 Story traceability
32. hero 5 AC traceability
33. generated tests map to AC
34. generation manifest valid
35. traceability JSON valid
36. modernization HTML generated
37. modernization HTML data-driven
38. no internal analyzer leakage in customer HTML
39. Figma fixture contamination count zero
40. Features remain 5
41. Stories remain 12
42. authoritative AC remains 14
43. architecture selection unchanged
44. technical tasks unchanged
45. source/ unchanged
46. full Polaris regression passes

======================================================================
PART 36 — DOCUMENTATION
======================================================================

Update:

PROJECT_MEMORY.md
PROGRESS.md
DECISIONS.md

Record clearly:

- Prompt 062 baseline frozen
- current POC has no real Figma target design
- existing application UI is current design source
- Figma remains optional future/customer design capability
- hero Dashboard UI reconstructed from existing application
- Angular 22/Nx generation completed
- existing APIs preserved
- architecture selection unchanged
- technical tasks consumed
- Build/Test/PEP not yet completed
- next stage is Build/Test/PEP validation and repair

======================================================================
PART 37 — DO NOT DO
======================================================================

DO NOT:

- modify source/
- redesign KG
- change Features
- change FRs
- change Stories
- change authoritative AC
- change architecture selection
- change approved Technical Tasks
- use Prompt 062 Figma fixture as HealthClinic design
- invent a new Dashboard design
- invent business metrics
- invent APIs
- introduce NgRx
- introduce SSR
- introduce hydration
- introduce microfrontends
- introduce Module Federation
- implement full API Gateway infrastructure
- implement production cloud infrastructure
- perform full PEP repair loop
- integrate Jira/Rovo
- implement full Polaris UI
- require external LLM credentials
- claim tests passed without executing them

======================================================================
PART 38 — CANONICAL GENERATION RUN
======================================================================

Run for:

PROJECT_ID=
legacy-dashboard-complete-application-demo-v1

FEATURE_ID=
feature-operational-dashboard-insights

DESIGN_SOURCE=
EXISTING_APPLICATION_UI

FIGMA_FOR_GENERATION=
DISABLED

Generate the canonical Angular hero output.

======================================================================
PART 39 — REQUIRED FINAL REPORT
======================================================================

Report exactly:

BASE_COMMIT=
NEW_COMMIT=
COMMIT_TITLE=

FILES_CHANGED=

FEATURES=
STORIES=
AUTHORITATIVE_AC=

ARCHITECTURE_SELECTION_CHANGED=
TECHNICAL_TASKS_CHANGED=

HERO_FEATURE=
HERO_FR_COUNT=
HERO_STORY_COUNT=
HERO_AC_COUNT=
TECHNICAL_TASK_COUNT=

DESIGN_SOURCE=
FIGMA_CAPABILITY_STILL_SUPPORTED=
FIGMA_FIXTURE_USED_FOR_GENERATION=

EXISTING_UI_SPECIFICATION=
RAZOR_UI_SURFACES=
ANGULARJS_UI_SURFACES=
UI_REGIONS=
UI_CONTROLS=
UI_ASSETS_REUSED=
UI_RECONSTRUCTION_CLARIFICATIONS=

GENERATED_WORKSPACE=
NX_STATUS=
ANGULAR_VERSION=
STANDALONE_STATUS=
SIGNALS_STATUS=
RXJS_STATUS=
ZONELESS_STATUS=
LAZY_ROUTING_STATUS=
DEFER_STATUS=

NGRX_INTRODUCED=
SSR_INTRODUCED=
HYDRATION_INTRODUCED=
MICROFRONTEND_INTRODUCED=
MODULE_FEDERATION_INTRODUCED=

GENERATED_COMPONENT_COUNT=
GENERATED_SERVICE_COUNT=
GENERATED_MODEL_COUNT=
GENERATED_ROUTE_COUNT=
GENERATED_TEST_COUNT=

GATEWAY_IMPLEMENTATION_STATUS=
BFF_IMPLEMENTATION_STATUS=
BFF_TARGET_CONTRACT_STATUS=

DASHBOARD_API_CONTRACTS_PRESERVED=
DASHBOARD_API_CONTRACT_COUNT=
INVENTED_EXISTING_API_COUNT=

FEATURE_TRACEABILITY=
FR_TRACEABILITY=
STORY_TRACEABILITY=
AC_IMPLEMENTATION_TRACEABILITY=
AC_TEST_TRACEABILITY=
ARCHITECTURE_TRACEABILITY=
ADR_TRACEABILITY=
TECHNICAL_TASK_TRACEABILITY=
SOURCE_UI_TRACEABILITY=

TECHNICAL_TASK_IMPLEMENTED=
TECHNICAL_TASK_PARTIAL=
TECHNICAL_TASK_DEFERRED=
TECHNICAL_TASK_NOT_APPLICABLE=

GENERATION_MANIFEST=
UI_RECONSTRUCTION_JSON=
UI_RECONSTRUCTION_MD=
UI_RECONSTRUCTION_HTML=
TRACEABILITY_JSON=
TRACEABILITY_MD=
MODERNIZATION_HTML=

LANGGRAPH_GENERATION_INTEGRATION=
LANGGRAPH_GENERATION_NODE_COUNT=
LANGCHAIN_USAGE=
EXTERNAL_LLM_CALLS=

GENERATION_VALIDATION=
ANGULAR_BUILD_EXECUTED=
ANGULAR_BUILD_RESULT=
GENERATED_TESTS_EXECUTED=
GENERATED_TEST_RESULT=

POLARIS_FOCUSED_TEST_RESULT=
POLARIS_FULL_TEST_RESULT=

SOURCE_CHANGED=

MODERNIZATION_GENERATION_READINESS=

READY_FOR_BUILD_TEST_PEP=

NEXT_POC_STAGE=
BUILD_TEST_PEP_AND_FINAL_TRACEABILITY

======================================================================
PART 40 — COMMIT AND STOP
======================================================================

Create ONE focused commit.

Suggested commit title:

Generate Angular 22 hero feature from existing UI

After committing:

STOP.

DO NOT begin Prompt 064 repair work.

Return the exact commit SHA and required report so the generation can be
independently validated before Build/Test/PEP.
