# Operational Dashboard Technical Delivery Plan

- Status: `TECHNICAL_TASKS_READY`
- Feature: `feature-operational-dashboard-insights`
- Architecture: `LOCKED`
- Design: `AVAILABLE` / `FIXTURE`

## Delivery Sequence

### TT-001 · Establish the Angular 22 Nx delivery workspace

**Category:** `SCAFFOLD`
**Depends on:** None

Create the selected enterprise workspace foundation for the hero Feature.

**Implementation requirements**
- Create the Angular 22 application in the selected Nx workspace.
- Enable standalone bootstrapping and zoneless compatibility checks.
- Apply Nx-aware lint, build, and test boundaries.

**Validation**
- Workspace build and quality commands pass.
- Zoneless dependency compatibility is verified.

**Architecture:** ARCH-001, ARCH-003, ARCH-006, ARCH-017, ARCH-052
**Requirements:** Infrastructure task
**APIs:** None
**Design:** AVAILABLE

### TT-002 · Define Dashboard domain and library boundaries

**Category:** `CONFIGURATION`
**Depends on:** TT-001

Translate the selected modular structure into enforceable project boundaries.

**Implementation requirements**
- Create domain-oriented feature, data-access, and shared UI library boundaries.
- Configure dependency constraints so presentation does not bypass integration boundaries.

**Validation**
- Nx dependency validation passes.
- Boundary rules prevent direct cross-domain imports.

**Architecture:** ARCH-008, ARCH-010, ARCH-034
**Requirements:** Infrastructure task
**APIs:** None
**Design:** AVAILABLE

### TT-003 · Establish the accessible shared design-system boundary

**Category:** `DESIGN_SYSTEM`
**Depends on:** TT-001

Provide reusable presentation primitives for Dashboard delivery.

**Implementation requirements**
- Translate only normalized design tokens and reusable components when design input is available.
- Keep design guidance subordinate to approved requirements.

**Validation**
- Shared primitives meet keyboard, contrast, and responsive validation expectations.
- No design-derived business behavior is introduced.

**Architecture:** ARCH-009, ARCH-046, ARCH-048
**Requirements:** Infrastructure task
**APIs:** None
**Design:** figma://file/FIXTURE_DASHBOARD?node-id=1%3A1, figma://file/FIXTURE_DASHBOARD?node-id=1%3A4, figma://file/FIXTURE_DASHBOARD?node-id=1%3A5, figma://file/FIXTURE_DASHBOARD?node-id=1%3A6, figma://file/FIXTURE_DASHBOARD?node-id=1%3A7

### TT-004 · Model the four existing Dashboard API contracts

**Category:** `API`
**Depends on:** TT-002

Create typed client-side models without changing existing backend semantics.

**Implementation requirements**
- Represent each approved existing method, route, parameter, and response model exactly.
- Keep existing contracts distinct from future target facade design.
- Use the selected typed Angular HTTP strategy.

**Validation**
- Contract tests cover all four approved APIs.
- No replacement or additional existing API is declared.

**Architecture:** ARCH-010, ARCH-037, ARCH-038
**Requirements:** FR-02, FR-03, FR-04, FR-05
**APIs:** API-01, API-02, API-03, API-04
**Design:** AVAILABLE

### TT-005 · Plan provider-neutral Gateway routing and policies

**Category:** `GATEWAY`
**Depends on:** TT-004

Represent the selected target ingress layer without implementing a product or changing business APIs.

**Implementation requirements**
- Configure future routing to preserve the four existing backend contracts.
- Define policy concerns for authentication, correlation propagation, and observability.
- Leave provider selection as a later configuration decision.

**Validation**
- Route mapping review proves all existing contracts are preserved.
- No gateway product is selected by this task.

**Architecture:** ARCH-039, ARCH-044, ARCH-051
**Requirements:** FR-02, FR-03, FR-04, FR-05
**APIs:** API-01, API-02, API-03, API-04
**Design:** AVAILABLE

### TT-006 · Design the future Dashboard BFF boundary

**Category:** `BFF`
**Depends on:** TT-005

Plan the selected frontend-specific integration boundary while preserving backend behavior.

**Implementation requirements**
- Label every future frontend-facing facade as TARGET_CONTRACT_TO_BE_DESIGNED.
- Map justified orchestration to the four existing API contracts without inventing business rules.
- Define tenant context, correlation, and error propagation responsibilities.

**Validation**
- Review confirms no future facade is represented as an existing API.
- Backend method, path, and response semantics remain unchanged.

**Architecture:** ARCH-041, ARCH-044, ARCH-051
**Requirements:** FR-02, FR-03, FR-04, FR-05
**APIs:** API-01, API-02, API-03, API-04
**Design:** AVAILABLE

### TT-007 · Implement the Angular-to-BFF client boundary

**Category:** `INTEGRATION`
**Depends on:** TT-006

Keep the browser integration aligned to the selected target topology.

**Implementation requirements**
- Create a typed integration port for the future BFF contract.
- Mark the port contract TARGET_CONTRACT_TO_BE_DESIGNED until approved.
- Keep the existing API contracts traceable behind the target boundary.

**Validation**
- The Dashboard feature depends on the integration port rather than backend-specific transport.
- Contract status remains explicit.

**Architecture:** ARCH-037, ARCH-038, ARCH-041
**Requirements:** FR-02, FR-03, FR-04, FR-05
**APIs:** API-01, API-02, API-03, API-04
**Design:** AVAILABLE

### TT-008 · Configure the lazy Operational Dashboard route

**Category:** `ROUTING`
**Depends on:** TT-002

Expose the approved Dashboard experience through the selected routing strategy.

**Implementation requirements**
- Register a lazy feature route for the standalone Dashboard shell.
- Use functional route APIs and a functional guard boundary without defining an identity provider.

**Validation**
- Route loading is lazy and resolves to the standalone shell.
- Approved Dashboard access criteria are covered.

**Architecture:** ARCH-024, ARCH-025, ARCH-026, ARCH-028
**Requirements:** FR-01
**APIs:** None
**Design:** figma://file/FIXTURE_DASHBOARD?node-id=1%3A1

### TT-009 · Implement the standalone Operational Dashboard shell

**Category:** `UI`
**Depends on:** TT-003, TT-008

Create the feature container and presentation regions without changing functional scope.

**Implementation requirements**
- Build a standalone shell within the Dashboard feature boundary.
- Expose year selection and approved expense, patient, and clinic summary regions.

**Validation**
- Shell renders all approved presentation regions.
- No unsupported field, metric, or business rule is added.

**Architecture:** ARCH-003, ARCH-034, ARCH-046
**Requirements:** FR-01, FR-02, FR-03, FR-04
**APIs:** None
**Design:** figma://file/FIXTURE_DASHBOARD?node-id=1%3A1, figma://file/FIXTURE_DASHBOARD?node-id=1%3A4, figma://file/FIXTURE_DASHBOARD?node-id=1%3A5, figma://file/FIXTURE_DASHBOARD?node-id=1%3A6, figma://file/FIXTURE_DASHBOARD?node-id=1%3A7

### TT-010 · Implement Dashboard Signals and RxJS data flow

**Category:** `STATE`
**Depends on:** TT-004, TT-007, TT-009

Separate synchronous UI state from asynchronous report retrieval.

**Implementation requirements**
- Use Signals for selected-year, loading, error, and derived presentation state.
- Use RxJS for HTTP cancellation and composition across approved contracts.
- Do not embed transport calls in presentation components.

**Validation**
- Year changes cancel stale asynchronous work.
- Derived UI state remains deterministic and independently tested.

**Architecture:** ARCH-012, ARCH-013, ARCH-015, ARCH-016, ARCH-021
**Requirements:** FR-02, FR-03, FR-04
**APIs:** API-02, API-03, API-04
**Design:** figma://file/FIXTURE_DASHBOARD?node-id=1%3A3, figma://file/FIXTURE_DASHBOARD?node-id=1%3A4, figma://file/FIXTURE_DASHBOARD?node-id=1%3A5, figma://file/FIXTURE_DASHBOARD?node-id=1%3A6, figma://file/FIXTURE_DASHBOARD?node-id=1%3A7

### TT-011 · Propagate tenant context through the target integration path

**Category:** `SECURITY_CONTEXT`
**Depends on:** TT-005, TT-006, TT-010

Preserve organization-aware behavior without selecting an identity provider.

**Implementation requirements**
- Retrieve the approved current-tenant contract through the integration boundary.
- Propagate tenant and correlation context through Angular, Gateway, and BFF responsibilities.
- Keep authentication provider and browser session implementation as explicit clarifications.

**Validation**
- Tenant context uses only the approved contract.
- Tests prove context propagation and no provider assumption.

**Architecture:** ARCH-026, ARCH-038, ARCH-044
**Requirements:** FR-05
**APIs:** API-01
**Design:** AVAILABLE

### TT-012 · Implement yearly report and clinic summary presentation

**Category:** `UI`
**Depends on:** TT-010, TT-011

Present approved operational information while preserving unresolved field-level questions.

**Implementation requirements**
- Connect expense and patient regions to selected-year state.
- Connect clinic summary presentation to current organization context.
- Do not invent report fields or metrics pending approved clarifications.

**Validation**
- Each region is driven by approved state and API references.
- Unknown fields remain documented rather than fabricated.

**Architecture:** ARCH-003, ARCH-034, ARCH-046
**Requirements:** FR-02, FR-03, FR-04, FR-05
**APIs:** API-01, API-02, API-03, API-04
**Design:** figma://file/FIXTURE_DASHBOARD?node-id=1%3A4, figma://file/FIXTURE_DASHBOARD?node-id=1%3A5, figma://file/FIXTURE_DASHBOARD?node-id=1%3A6, figma://file/FIXTURE_DASHBOARD?node-id=1%3A7

### TT-013 · Validate responsive and accessible Dashboard behavior

**Category:** `ACCESSIBILITY`
**Depends on:** TT-012

Apply the selected accessibility strategy across the implemented experience.

**Implementation requirements**
- Verify semantic structure, keyboard operation, focus behavior, labels, and responsive reflow.
- Use normalized responsive hints only when present and retain implementation defaults otherwise.

**Validation**
- Automated accessibility checks pass.
- Manual keyboard and responsive review is recorded without unsupported compliance claims.

**Architecture:** ARCH-046, ARCH-048
**Requirements:** FR-01, FR-02, FR-03, FR-04
**APIs:** None
**Design:** figma://file/FIXTURE_DASHBOARD?node-id=1%3A1, figma://file/FIXTURE_DASHBOARD?node-id=1%3A3, figma://file/FIXTURE_DASHBOARD?node-id=1%3A4, figma://file/FIXTURE_DASHBOARD?node-id=1%3A5, figma://file/FIXTURE_DASHBOARD?node-id=1%3A6, figma://file/FIXTURE_DASHBOARD?node-id=1%3A7

### TT-014 · Add correlated Dashboard telemetry and failure handling

**Category:** `OBSERVABILITY`
**Depends on:** TT-007, TT-010, TT-011

Make target integration failures diagnosable without selecting a telemetry vendor.

**Implementation requirements**
- Propagate correlation context across browser, Gateway, BFF, and existing API boundaries.
- Instrument report loading and technical failures without recording sensitive tenant data.
- Keep vendor configuration external to feature code.

**Validation**
- Correlation propagation is covered by integration tests.
- Telemetry contains no sensitive context values.

**Architecture:** ARCH-038, ARCH-039, ARCH-041, ARCH-051
**Requirements:** FR-02, FR-03, FR-04, FR-05
**APIs:** API-01, API-02, API-03, API-04
**Design:** AVAILABLE

### TT-015 · Implement unit and component coverage

**Category:** `TEST`
**Depends on:** TT-012, TT-013, TT-014

Verify state, UI, routing, contract, and accessibility behavior at component boundaries.

**Implementation requirements**
- Cover Signals-derived state and RxJS cancellation.
- Cover standalone shell and summary regions against approved requirements.
- Cover typed contract and tenant-context boundaries.

**Validation**
- Unit and component suites pass in affected Nx targets.
- Tests retain exact approved API references.

**Architecture:** ARCH-049, ARCH-052
**Requirements:** FR-01, FR-02, FR-03, FR-04, FR-05
**APIs:** API-01, API-02, API-03, API-04
**Design:** AVAILABLE

### TT-016 · Automate approved Dashboard acceptance flows with Playwright

**Category:** `TEST`
**Depends on:** TT-015

Provide end-to-end evidence for the five hero Feature acceptance criteria.

**Implementation requirements**
- Automate Dashboard route access, yearly reporting, and tenant-aware summary behavior.
- Map each scenario to an authoritative acceptance-criteria reference.
- Use controlled test data without redefining unresolved report fields.

**Validation**
- All five approved criteria have executable scenario traceability.
- End-to-end suite passes against the target integration boundary.

**Architecture:** ARCH-050, ARCH-052
**Requirements:** FR-01, FR-02, FR-03, FR-04, FR-05
**APIs:** API-01, API-02, API-03, API-04
**Design:** AVAILABLE
