POLARIS MODERNIZATION
PROMPT 062

MINIMAL FIGMA DESIGN ADAPTER
+ ARCHITECTURE-DRIVEN TECHNICAL TASK GENERATION
+ CUSTOMER TECHNICAL DELIVERY SHOWCASE

======================================================================
BASELINE
======================================================================

Work from the approved Polaris baseline:

CURRENT_APPROVED_BASELINE=
5b80ecdeba804edcba7a8eff1953808679b1b991

This commit is the APPROVED AND FROZEN architecture baseline.

Before modifying anything:

1. Verify HEAD and working tree.
2. Verify this baseline is present in history.
3. Report the exact parent/base used.
4. Read:
   - AGENTS.md
   - PROJECT_MEMORY.md
   - PROGRESS.md
   - DECISIONS.md
   - docs/prompts/060*
   - docs/prompts/061*
5. Inspect:
   - src/polaris_modernization/architecture/
   - artifacts/architecture/latest/architecture.json
   - artifacts/architecture/latest/architecture-selection.json
   - artifacts/architecture/latest/architecture-recommendation.json
   - artifacts/architecture/latest/architecture.html
   - artifacts/architecture/latest/adrs/
6. Inspect approved Feature Specification/Jira artifacts.
7. Identify the approved hero Feature:

feature-operational-dashboard-insights

Do not proceed from assumptions when approved artifacts already contain the
answer.

======================================================================
FROZEN UPSTREAM CONTRACT
======================================================================

The following are frozen and MUST NOT be redesigned:

- deterministic source analysis
- framework detection
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
- Jira quality layer
- Feature Specifications
- Architecture Recommendation
- Architecture Selection
- architecture decision catalog
- architecture ADRs

Expected business baseline:

FEATURES=5
STORIES=12
AUTHORITATIVE_AC=14

Expected architecture baseline includes:

- Angular 22
- Nx
- standalone components
- domain/feature-oriented structure
- Signals
- RxJS async boundaries
- zoneless target
- lazy routing
- typed HttpClient/API clients
- API Gateway target topology
- BFF target topology
- accessibility
- observability
- Playwright
- CSR selected
- SSR/hydration evaluated but not selected
- NgRx evaluated but not selected
- microfrontends evaluated but not selected

DO NOT make new architecture decisions in this prompt.

Technical tasks MUST obey architecture-selection.json.

======================================================================
PURPOSE
======================================================================

Implement the next PLAN-stage capability:

Approved Requirements
       +
Locked Architecture Selection
       +
Optional Design Input
       ↓
Technical Task Generator
       ↓
TechnicalTaskModel[]
       ↓
technical-tasks.json
technical-tasks.md
technical-tasks.html
       ↓
Future Angular 22 Generation

At the same time, add a small reusable optional design-provider abstraction
with a real Figma adapter.

Figma must remain OPTIONAL.

If Figma is unavailable, unconfigured, unauthorized, or not supplied:

THE TECHNICAL TASK PIPELINE MUST STILL SUCCEED.

Do not let Figma block the POC.

======================================================================
PART 1 — DESIGN PROVIDER ABSTRACTION
======================================================================

Create or extend a generic design provider boundary.

Do not couple future Angular generation directly to Figma JSON.

Conceptually:

DesignProvider
      ↓
DesignSpecification
      ↓
Technical Tasks
      ↓
Future Angular Generator

Support provider status such as:

NO_DESIGN
FIGMA
FIXTURE
UNAVAILABLE
UNAUTHORIZED
INVALID
PARTIAL

Use clean typed models/enums.

DesignSpecification should normalize useful implementation-oriented design
information.

Suggested model:

DesignSpecification
- provider
- status
- source_reference
- document_name
- pages[]
- screens[]
- components[]
- component_instances[]
- layouts[]
- controls[]
- typography[]
- colors[]
- design_tokens[]
- spacing[]
- assets[]
- responsive_hints[]
- interactions[]
- navigation_hints[]
- unresolved_items[]
- requirement_links[]
- traceability[]

Do not blindly mirror the complete Figma API response.

Normalize only information useful to implementation.

======================================================================
PART 2 — FIGMA DESIGN PROVIDER
======================================================================

Implement a real:

FigmaDesignProvider

The implementation must be provider-isolated.

Prefer structure conceptually similar to:

src/polaris_modernization/design/
    __init__.py
    models.py
    providers/
        base.py
        figma.py
    normalizer.py
    fixtures/
    renderers.py

Exact structure can follow repository conventions.

======================================================================
PART 3 — FIGMA URL PARSER
======================================================================

Support common Figma design URLs.

Extract where available:

- file key
- node-id
- provider
- normalized document reference

Do not assume every URL has a node-id.

Validate malformed URLs.

Do not hardcode a specific customer Figma URL.

======================================================================
PART 4 — FIGMA AUTHENTICATION
======================================================================

Support configuration through:

FIGMA_ACCESS_TOKEN

Never:

- hardcode token
- commit token
- print token
- log token
- write token into artifacts

Provide explicit statuses/errors:

FIGMA_AUTH_NOT_CONFIGURED
FIGMA_ACCESS_DENIED
FIGMA_DOCUMENT_UNAVAILABLE
FIGMA_INVALID_URL
FIGMA_NETWORK_ERROR
FIGMA_RESPONSE_INVALID

Do not collapse all failures into "Figma failed."

======================================================================
PART 5 — LIVE AND FIXTURE MODES
======================================================================

Because this POC has a deadline, implement two explicit modes:

LIVE
FIXTURE

LIVE:
Uses configured Figma access and real provider response.

FIXTURE:
Uses deterministic local sample Figma-like data to validate the complete
normalization pipeline without network/auth dependency.

IMPORTANT:

Never claim FIXTURE is LIVE.

Artifacts must clearly record:

DESIGN_MODE=LIVE

or

DESIGN_MODE=FIXTURE

or

DESIGN_MODE=NONE

If live Figma authentication/network is unavailable during implementation:

DO NOT BLOCK THIS PROMPT.

Complete:

- provider
- URL parser
- auth/config handling
- fixture
- normalization
- tests
- technical tasks
- artifacts

and report the exact live limitation.

======================================================================
PART 6 — FIGMA NORMALIZATION
======================================================================

Normalize only deterministic design information.

Examples:

PAGE
FRAME / SCREEN
COMPONENT
INSTANCE
TEXT
CONTROL
LAYOUT
COLOR
TYPOGRAPHY
SPACING
ASSET
RESPONSIVE_HINT
DETERMINISTIC_INTERACTION

Where safely derivable, normalize:

- screen/frame names
- hierarchy
- component names
- component reuse
- auto-layout direction
- spacing values
- dimensions
- text styles
- color values
- typography
- button/input-like controls when explicit
- assets/images/icons references
- layout relationships
- explicit prototype navigation relationships
- responsive/layout hints supported by source data

DO NOT infer:

- business rules from colors
- business requirements from visual appearance
- API behavior from screen labels
- hidden validation rules
- authorization rules
- backend behavior
- business meaning not represented in requirements

Design does NOT override approved requirements.

======================================================================
PART 7 — DESIGN / REQUIREMENT CONFLICTS
======================================================================

If design appears inconsistent with approved Feature requirements:

DO NOT silently choose Figma.

Create:

DESIGN_REQUIREMENT_CONFLICT

Include:

- design reference
- requirement reference
- conflict description
- required clarification

Priority remains:

APPROVED REQUIREMENTS
        ↓
LOCKED ARCHITECTURE
        ↓
DESIGN INPUT
        ↓
IMPLEMENTATION

Design controls presentation.

Requirements control functionality.

Architecture controls technical structure.

======================================================================
PART 8 — NO-DESIGN PATH
======================================================================

This path is mandatory.

The following must work:

Feature
+
Requirements
+
Architecture Selection
+
NO FIGMA
       ↓
Technical Tasks

No fake design must be invented.

Record:

DESIGN_STATUS=NOT_PROVIDED

Technical tasks may say:

"Implement using approved design system / implementation defaults pending
design input"

only where appropriate.

Do not manufacture pixel values/colors/layouts.

======================================================================
PART 9 — TECHNICAL TASK MODEL
======================================================================

Implement:

TechnicalTaskModel

Each technical task should support fields conceptually like:

- task_id
- feature_id
- title
- objective
- category
- description
- implementation_requirements[]
- architecture_decision_refs[]
- adr_refs[]
- functional_requirement_refs[]
- story_refs[]
- acceptance_criteria_refs[]
- api_refs[]
- design_refs[]
- dependencies[]
- validation_requirements[]
- deliverables[]
- status
- implementation_order
- blocking
- open_questions[]
- traceability[]

Categories should be controlled.

At minimum support:

SCAFFOLD
ROUTING
UI
STATE
API
INTEGRATION
BFF
GATEWAY
SECURITY_CONTEXT
SHARED_COMPONENT
DESIGN_SYSTEM
ACCESSIBILITY
OBSERVABILITY
TEST
CONFIGURATION

Do not force every category to have a task.

======================================================================
PART 10 — TECHNICAL TASK GENERATOR
======================================================================

Generate technical tasks from:

Feature
+
Functional Requirements
+
Stories
+
Acceptance Criteria
+
Existing API Contracts
+
LOCKED ArchitectureSelection
+
ADRs
+
Optional DesignSpecification

ArchitectureSelection is the technical architecture source of truth.

The generator MUST NOT independently choose:

- Angular CLI instead of Nx
- NgRx
- SSR
- hydration
- microfrontend
- Module Federation
- direct API bypassing selected integration architecture

unless architecture-selection.json is explicitly changed upstream.

======================================================================
PART 11 — HERO FEATURE
======================================================================

Generate tasks for:

feature-operational-dashboard-insights

Do NOT generate implementation tasks for all five Features yet.

POC scope remains one representative hero Feature.

The Feature includes the approved Dashboard behavior and must preserve the
approved Functional Requirements, Stories and Acceptance Criteria.

======================================================================
PART 12 — EXISTING API CONTRACTS
======================================================================

The following four existing backend business API contracts MUST remain
traceable:

GET /api/reports/expenses/{year}

GET /api/reports/patients/{year}

GET /api/reports/clinicsummary

GET /api/users/current/tenant

These are existing backend contracts.

Do not modify them.

Do not invent replacements.

======================================================================
PART 13 — GATEWAY + BFF TASK STRATEGY
======================================================================

Architecture Selection currently chooses target:

Angular
   ↓
API Gateway
   ↓
BFF
   ↓
Existing APIs

Technical tasks should represent this architecture.

BUT:

This is still a POC.

Do not build the Gateway or BFF in this prompt.

Generate appropriate future implementation tasks.

For example:

GATEWAY task:
- configure target gateway routing/policies
- preserve backend contract routing
- auth/policy concerns
- correlation propagation
- observability
- provider remains architecture/config choice unless selected

BFF task:
- create Angular-specific backend integration boundary
- orchestrate existing Dashboard API calls where justified
- preserve backend API semantics
- establish frontend-facing contract design
- tenant/context propagation
- error/correlation strategy

CRITICAL:

Do not invent BFF endpoints as proven business requirements.

If future BFF facade endpoints need to be designed, explicitly label them:

TARGET_CONTRACT_TO_BE_DESIGNED

not:

EXISTING_API

Existing APIs remain:

/api/reports/expenses/{year}
/api/reports/patients/{year}
/api/reports/clinicsummary
/api/users/current/tenant

======================================================================
PART 14 — ANGULAR / NX TASK STRATEGY
======================================================================

Tasks should reflect the locked architecture.

Expected areas may include:

1. Nx workspace/application scaffold

2. Domain/feature library structure

3. Shared design-system/UI library

4. Dashboard feature route

5. Standalone Dashboard shell/components

6. Signals-based Dashboard UI state

7. RxJS HTTP/data-flow boundaries

8. Typed Dashboard API contracts

9. BFF integration client boundary

10. Tenant/context handling

11. yearly report state / selected year behavior

12. expense summary UI

13. patient summary UI

14. clinic summary UI

15. lazy routing

16. @defer where justified

17. zoneless compatibility

18. accessibility

19. error/loading/empty-state behavior where supported by requirements or
    clearly identified as implementation quality behavior

20. observability/correlation

21. unit/component tests

22. Playwright Acceptance-Criteria tests

Do not create one tiny task for every line above.

Produce meaningful engineering tasks.

Target roughly:

10–18 tasks

if that naturally represents the implementation.

Quality is more important than task count.

======================================================================
PART 15 — TASK DEPENDENCIES / IMPLEMENTATION ORDER
======================================================================

Tasks should form a sensible implementation sequence.

Example conceptual dependency graph:

Workspace Scaffold
      ↓
Shared Architecture / Libraries
      ↓
API Models / Integration Boundary
      ↓
Routing
      ↓
Dashboard Shell
      ↓
State + API Integration
      ↓
Dashboard UI
      ↓
Accessibility / Observability
      ↓
Tests

Gateway/BFF tasks may have their own dependency chain.

Represent dependencies explicitly.

Validate:

- no missing task dependency
- no circular task dependencies
- implementation order consistent with dependencies

======================================================================
PART 16 — TASK TRACEABILITY
======================================================================

Every task must be traceable where relevant.

Target traceability:

Feature
  ↓
Functional Requirement
  ↓
Story
  ↓
Acceptance Criteria
  ↓
Architecture Decision
  ↓
ADR
  ↓
Technical Task
  ↓
Future Angular Component
  ↓
Future Test

For API tasks:

Technical Task
  ↓
API Contract

For design:

Figma Node
  ↓
Design Component
  ↓
Technical Task
  ↓
Future Angular Component

Do not fabricate future component/test IDs yet if they do not exist.

Use placeholders/statuses only where model explicitly supports future
traceability.

======================================================================
PART 17 — TASK QUALITY
======================================================================

Technical tasks should read like useful Jira engineering tasks.

BAD:

"Implement Angular."

BAD:

"Create component."

GOOD:

"Implement the standalone Operational Dashboard feature shell within the
selected Nx feature boundary, configure lazy route activation, and expose the
approved Dashboard child presentation areas without introducing backend
contract changes."

GOOD:

"Implement typed Dashboard data-access services for expense, patient,
clinic-summary and tenant contracts using the selected Angular HTTP integration
strategy and RxJS asynchronous boundaries."

Each task should tell a developer:

- what to build
- why
- architecture constraints
- requirement/API/design inputs
- expected output
- how to validate it

======================================================================
PART 18 — TECHNICAL TASK ARTIFACTS
======================================================================

Generate:

artifacts/technical-tasks/latest/technical-tasks.json

artifacts/technical-tasks/latest/technical-tasks.md

Also generate:

artifacts/technical-tasks/latest/technical-tasks.html

The HTML is useful for the customer/demo.

Like architecture.html, it should be data-driven.

Do not manually maintain separate semantics.

======================================================================
PART 19 — TECHNICAL TASK HTML
======================================================================

Generate a polished standalone HTML file.

Suggested sections:

1. Hero Feature
2. Delivery Summary
3. Selected Architecture
4. Implementation Roadmap
5. Technical Tasks
6. Task Dependency Flow
7. Angular/Nx Delivery Areas
8. Gateway/BFF Delivery Areas
9. API Contracts
10. Design Input Status
11. Testing Strategy
12. Traceability
13. Readiness

Each task card should show:

TASK ID
CATEGORY
TITLE
OBJECTIVE
DEPENDENCIES
ARCHITECTURE
REQUIREMENTS
APIs
DESIGN
VALIDATION

Do not expose:

- source hashes
- Roslyn
- Tree-sitter
- KG internals
- analyzer warnings

This is an engineering/customer artifact.

======================================================================
PART 20 — OPTIONAL DESIGN SHOWCASE
======================================================================

If FIXTURE mode is used, optionally generate:

artifacts/design/latest/design.json
artifacts/design/latest/design.md

and, if useful:

artifacts/design/latest/design.html

But keep this lightweight.

Do not spend excessive effort on a standalone design UI.

Architecture HTML and Technical Tasks HTML are higher priority.

======================================================================
PART 21 — LANGGRAPH INTEGRATION
======================================================================

Do not create a disconnected script.

Extend the existing workflow/orchestration architecture appropriately.

The broader future modernization graph should conceptually support:

Requirements
    ↓
Architecture
    ↓
Optional Design
    ↓
Technical Tasks
    ↓
Future Generate
    ↓
Future Build
    ↓
Future Test
    ↓
Future PEP

For this prompt, actual execution ends at:

TECHNICAL_TASKS_READY

Do not generate Angular.

Do not implement PEP yet.

Record workflow execution.

If a separate task-generation subgraph is cleaner, implement it without
unnecessary complexity.

======================================================================
PART 22 — LANGCHAIN
======================================================================

Use LangChain only where it provides a meaningful structured transformation
boundary.

Do not introduce an external LLM dependency.

EXTERNAL_LLM_CALLS must remain 0 for deterministic POC execution unless the
existing project explicitly supports an optional configured provider.

Do not require API credentials.

Technical task generation should remain reproducible.

======================================================================
PART 23 — CLI
======================================================================

Provide minimal usable CLI integration.

Conceptually support something like:

python -m polaris_modernization.cli generate-technical-tasks \
  --project-id legacy-dashboard-complete-application-demo-v1 \
  --feature-id feature-operational-dashboard-insights \
  --output artifacts

Optional design:

--design-provider figma
--figma-url "<url>"

Fixture:

--design-provider figma
--design-mode fixture

No design:

--design-provider none

Exact CLI syntax should follow existing Polaris conventions.

Do not proliferate commands unnecessarily.

======================================================================
PART 24 — VALIDATORS
======================================================================

Add validators for:

TECHNICAL_TASK_HAS_FEATURE
TECHNICAL_TASK_HAS_CATEGORY
TECHNICAL_TASK_HAS_OBJECTIVE
TECHNICAL_TASK_HAS_DELIVERABLE
TECHNICAL_TASK_HAS_VALIDATION
TECHNICAL_TASK_ARCHITECTURE_ALIGNED
TECHNICAL_TASK_API_CONTRACT_PRESERVED
TECHNICAL_TASK_NO_UNSELECTED_ARCHITECTURE
TECHNICAL_TASK_DEPENDENCIES_VALID
TECHNICAL_TASK_NO_CYCLE
TECHNICAL_TASK_TRACEABILITY_VALID
TECHNICAL_TASK_NO_INVENTED_BUSINESS_BEHAVIOR
TECHNICAL_TASK_NO_INVENTED_EXISTING_API
DESIGN_DOES_NOT_OVERRIDE_REQUIREMENTS
FIGMA_SECRET_NOT_EXPOSED
FIGMA_FIXTURE_NOT_REPORTED_AS_LIVE

Specifically validate that tasks do NOT introduce:

NgRx
SSR
Hydration
Microfrontend
Module Federation

as selected implementation requirements while they remain unselected in the
locked architecture.

======================================================================
PART 25 — TESTS
======================================================================

Add focused tests.

At minimum:

1. DesignProvider interface works
2. no-design provider/path works
3. Figma URL parser valid URL
4. Figma URL parser malformed URL
5. Figma node-id optional
6. missing Figma auth handled safely
7. denied Figma access handled
8. fixture mode works
9. fixture clearly labeled fixture
10. token never serialized
11. DesignSpecification normalization works
12. design does not invent business requirements
13. design conflict detection works
14. task generator loads locked ArchitectureSelection
15. task generator does not choose architecture independently
16. hero Feature only
17. task IDs unique
18. dependencies valid
19. no cycles
20. implementation order valid
21. all four Dashboard APIs preserved
22. no invented existing API
23. Gateway task represented
24. BFF task represented
25. Gateway/BFF preserve backend contracts
26. Nx alignment
27. standalone alignment
28. Signals alignment
29. RxJS alignment
30. zoneless alignment
31. no NgRx implementation task
32. no SSR implementation task
33. no MFE implementation task
34. Playwright task represented
35. AC traceability represented
36. technical-tasks.json valid
37. technical-tasks.md generated
38. technical-tasks.html generated
39. HTML data-driven
40. HTML has architecture summary
41. HTML has dependency roadmap
42. HTML has Gateway/BFF section
43. HTML has existing APIs
44. HTML has design status
45. no internal analyzer leakage
46. Features remain 5
47. Stories remain 12
48. authoritative AC remains 14
49. architecture selection unchanged
50. source/ unchanged
51. full regression passes

======================================================================
PART 26 — DESIGN FIXTURE
======================================================================

Create a small GENERIC fixture if needed for deterministic tests.

It may represent an Operational Dashboard-like layout containing:

- dashboard frame
- reporting-year selector
- expense summary region
- patient summary region
- clinic summary region
- reusable cards
- heading/text styles
- spacing/layout data

IMPORTANT:

Fixture data is test/demo design input.

Do not claim it came from the real HealthClinic source or a real customer
Figma document.

Label:

FIXTURE

clearly in machine artifacts.

======================================================================
PART 27 — POC DELIVERY DISCIPLINE
======================================================================

This is a deadline-sensitive POC.

Prioritize:

1. trustworthy model
2. real optional Figma adapter
3. no-design path
4. architecture-driven technical tasks
5. traceability
6. good HTML
7. tests

Do NOT over-engineer:

- full design platform
- Figma plugin
- design editor
- pixel-perfect code generation
- full Jira integration
- cloud infrastructure
- BFF implementation
- gateway implementation

Those come later if needed.

======================================================================
PART 28 — DOCUMENTATION
======================================================================

Update:

PROJECT_MEMORY.md
PROGRESS.md
DECISIONS.md

Record:

- architecture baseline remains frozen
- Figma provider abstraction added
- Figma is optional
- LIVE/FIXTURE/NONE distinction
- technical task model added
- hero Feature technical tasks generated
- tasks consume locked ArchitectureSelection
- Gateway/BFF represented as target implementation work
- existing APIs preserved
- Angular generation not started
- next stage is Angular 22 hero Feature generation

======================================================================
PART 29 — DO NOT DO
======================================================================

DO NOT:

- modify source/
- change KG
- change API resolver
- change Application Understanding
- change Features
- change Stories
- change authoritative AC
- change architecture selection
- regenerate architecture with different choices
- scaffold Angular/Nx application
- implement Angular components
- implement Gateway
- implement BFF
- invent backend APIs
- implement PEP
- integrate Jira/Rovo
- implement full Polaris UI
- require an external LLM
- expose Figma token
- block the task because live Figma credentials are absent

======================================================================
PART 30 — CANONICAL RUN
======================================================================

Run for:

PROJECT_ID=
legacy-dashboard-complete-application-demo-v1

FEATURE_ID=
feature-operational-dashboard-insights

First validate:

DESIGN_MODE=NONE

Technical task generation MUST succeed.

Then validate FIXTURE mode.

If FIGMA_ACCESS_TOKEN and a usable Figma URL are already safely available in
the environment, LIVE mode may also be tested.

Do NOT require live mode for POC completion.

Do not invent credentials or URLs.

======================================================================
PART 31 — REQUIRED FINAL REPORT
======================================================================

Report exactly:

BASE_COMMIT=
NEW_COMMIT=
COMMIT_TITLE=

FILES_CHANGED=

FEATURES=
STORIES=
AUTHORITATIVE_AC=

ARCHITECTURE_BASELINE=
ARCHITECTURE_SELECTION_CHANGED=

DESIGN_PROVIDER_IMPLEMENTED=
FIGMA_PROVIDER_IMPLEMENTED=
FIGMA_URL_PARSER=
FIGMA_LIVE_MODE=
FIGMA_FIXTURE_MODE=
NO_DESIGN_MODE=
FIGMA_AUTH_STATUS=
FIGMA_SECRET_EXPOSURE=

DESIGN_SPECIFICATION_MODEL=
DESIGN_CONFLICT_VALIDATION=

HERO_FEATURE=
TECHNICAL_TASK_COUNT=
TECHNICAL_TASK_CATEGORIES=
TASK_DEPENDENCY_VALIDATION=
TASK_CYCLE_COUNT=

NX_ALIGNED=
ANGULAR_22_ALIGNED=
STANDALONE_ALIGNED=
SIGNALS_ALIGNED=
RXJS_ALIGNED=
ZONELESS_ALIGNED=
GATEWAY_ALIGNED=
BFF_ALIGNED=
PLAYWRIGHT_ALIGNED=

UNSELECTED_NGRX_INTRODUCED=
UNSELECTED_SSR_INTRODUCED=
UNSELECTED_HYDRATION_INTRODUCED=
UNSELECTED_MFE_INTRODUCED=
UNSELECTED_MODULE_FEDERATION_INTRODUCED=

DASHBOARD_API_CONTRACTS_PRESERVED=
DASHBOARD_API_CONTRACT_COUNT=
INVENTED_EXISTING_API_COUNT=

FEATURE_TRACEABILITY=
FR_TRACEABILITY=
STORY_TRACEABILITY=
AC_TRACEABILITY=
API_TRACEABILITY=
ARCHITECTURE_TRACEABILITY=
ADR_TRACEABILITY=
DESIGN_TRACEABILITY=

TECHNICAL_TASKS_JSON=
TECHNICAL_TASKS_MD=
TECHNICAL_TASKS_HTML=
TECHNICAL_TASK_HTML_DATA_DRIVEN=

DESIGN_JSON=
DESIGN_MD=
DESIGN_HTML=

LANGGRAPH_INTEGRATION=
LANGCHAIN_USAGE=
EXTERNAL_LLM_CALLS=

FOCUSED_TEST_RESULT=
FULL_TEST_RESULT=
SOURCE_CHANGED=

TECHNICAL_TASK_READINESS=

READY_FOR_ANGULAR_GENERATION=

NEXT_POC_STAGE=
ANGULAR_22_HERO_FEATURE_GENERATION

======================================================================
PART 32 — COMMIT AND STOP
======================================================================

Create ONE focused commit.

Suggested commit title:

Add optional Figma design and technical task planning

After committing:

STOP.

DO NOT generate Angular.

DO NOT scaffold Nx.

DO NOT implement Gateway/BFF.

Return the exact commit SHA and required report.

The commit will be independently validated before Prompt 063.
