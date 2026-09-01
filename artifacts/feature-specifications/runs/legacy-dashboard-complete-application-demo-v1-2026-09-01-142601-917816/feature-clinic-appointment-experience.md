# feature-clinic-appointment-experience — Clinic Appointment Experience

## 1. Feature Summary

### Purpose

Provide access to clinic/appointment navigation and appointment information within current tenant context.

### Current Business Capability

The current application makes the established clinic information views available to users. Clinic functionality has current tenant context.

### Business Value

Maintains the established tenant context used by clinic functionality. Specific stakeholder outcomes for one or more access capabilities are not established and require confirmation.

**Business Value Status:** Requires Stakeholder Enrichment.

### Modernization Objective

Migrate only approved clinic/appointment surfaces and tenant-context behavior until stakeholders validate the missing appointment operation boundaries.

## 2. Functional Behavior

### Access Clinic Information

The current application makes the established clinic information views available to users.

### Establish Clinic Context

Clinic functionality has current tenant context.

The available requirements establish a general application user; no more specific business persona is authoritative.

**Feature Name / Behavior Alignment:** Partially Aligned.

The current primary behaviors do not establish: appointment. The Feature name does not create additional scope.

## 3. Scope

### In Scope

- Approved clinic routes, appointment/clinic UI surfaces, appointment concepts, and tenant-context integration.

### Not Established by Current Evidence

- Appointment creation/update behavior, scheduling rules, backend/database redesign, and any transaction not supported by approved workflows.

## 4. User Stories & Acceptance Criteria

### STORY-CLINIC-APPOINTMENT-EXPERIENCE-ACCESS-CLINIC-INFORMATION — Access Clinic Information

**Story**

As an application user,

I want to access the existing clinic information views.

Business outcome: Requires stakeholder confirmation; current evidence establishes the capability but not its specific business purpose.

**Business Context**

Represents the approved clinic list and detail navigation behavior without asserting unsupported appointment transactions.

**Business Value Status:** Not Established.

#### Acceptance Criteria

##### AC-CLINIC-APPOINTMENT-EXPERIENCE-ACCESS-CLINIC-INFORMATION-001 — Access Clinic Information Behavior

**Quality Status:** Testable With Evidence Limitation.

**Given** Clinic detail navigation is initiated

**When** the user accesses the existing clinic information views

**Then** the established clinic information views are available.

**Evidence Limitation**

Current evidence does not establish a complete customer-approved definition of the information or presentation details that must be retained.

**Current Backend Contract References**

- `API-CLINIC_APPOINTMENT_EXPERIENCE-DISCOVERED-001`
- `API-CLINIC_APPOINTMENT_EXPERIENCE-DISCOVERED-002`

### STORY-CLINIC-APPOINTMENT-EXPERIENCE-ESTABLISH-CLINIC-CONTEXT — Establish Clinic Context

**Story**

As an application user,

I want to obtain tenant context for clinic functionality,

so that clinic functionality retains its established tenant-aware behavior.

**Business Context**

Represents the proven tenant-context interaction that supports the existing clinic area.

**Business Value Status:** Supported Interpretation.

#### Acceptance Criteria

##### AC-CLINIC-APPOINTMENT-EXPERIENCE-ESTABLISH-CLINIC-CONTEXT-001 — Establish Clinic Context Behavior

**Quality Status:** Fully Testable From Evidence.

**Given** Clinic functionality needs tenant context

**When** the application obtains tenant context for clinic functionality

**Then** clinic functionality has current tenant context.

**Current Backend Contract References**

- `API-CLINIC_APPOINTMENT_EXPERIENCE-001`

## 5. Existing Backend Integration

Confirmed existing backend API contracts are preserved integration boundaries for the target frontend unless an explicitly approved change modifies them.

### Supporting / Shared APIs

#### API-CLINIC_APPOINTMENT_EXPERIENCE-001 — GET /api/users/current/tenant

**Role in this Feature:** Supporting Shared Api.

**Current Frontend:** `src/MyHealth.Web/content/app/components/clinics/services/clinicsService.js` calls `GET /api/users/current/tenant`.

**Confirmed Backend:** `GET /api/users/current/tenant` implemented by `UsersController.GetCurrentTenantAsync`.

This contract supplies shared context only; it does not provide the Feature's primary business data.

### Unresolved or Dynamic Integrations

#### API-CLINIC_APPOINTMENT_EXPERIENCE-DISCOVERED-001 — `/api/tenants/${tenantId}`

**Role in this Feature:** Dynamic Primary Interaction.

**Current Frontend:** `src/MyHealth.Web/content/app/components/clinics/services/clinicsService.js` calls `GET `/api/tenants/${tenantId}`.

**Candidate Existing Backend Contract**

A matching backend endpoint exists, but the current frontend-to-backend relationship has not been conclusively established:

- `GET /api/tenants/{tenantId}` — `TenantsController.GetAsync`; response `Task<Tenant>`

**Modernization Requirement:** Confirm the existing integration before implementing this behavior in the target frontend.

#### API-CLINIC_APPOINTMENT_EXPERIENCE-DISCOVERED-002 — /api/tenants/list

**Role in this Feature:** Unresolved Primary Interaction.

**Current Frontend:** `src/MyHealth.Web/content/app/components/clinics/services/clinicsService.js` calls `GET /api/tenants/list`.

**Candidate Existing Backend Contract**

A matching backend endpoint exists, but the current frontend-to-backend relationship has not been conclusively established:

- `GET /api/tenants/list` — `TenantsController.GetAsync`; response `Task<IEnumerable<Tenant>>`

**Modernization Requirement:** Confirm the existing integration before implementing this behavior in the target frontend.

## 6. Modernization Considerations

### Current Implementation Context

Relevant legacy surfaces: ClinicsController, clinic, clinics

### Preservation Requirements

- Preserve this approved business behavior during frontend modernization without changing backend contracts.

**Target Design:** Not yet analyzed.

**Target Architecture:** Pending.

## 7. Decisions Required Before Modernization

### Business Clarifications

| Question | Why It Matters | Impact | Owner |
| --- | --- | --- | --- |
| What business outcome should users achieve through Access Clinic Information beyond access to the currently established capability? | Current evidence establishes the behavior but not the stakeholder's intended business outcome. | NON_BLOCKING | Product Owner / Business Analyst / Customer SME |
| Which information must be considered mandatory when validating Access Clinic Information in the modernized experience? | Current evidence does not establish a complete customer-approved definition of the information or presentation details that must be retained. | BLOCKING | Product Owner / Business Analyst / Customer SME / QA Lead |
| Does 'Clinic Appointment Experience' include behavior related to appointment, or should the approved scope/name remain limited to the currently established behaviors? | One or more meaningful Feature-name terms are not established by the primary behaviors. | NON_BLOCKING | Product Owner / Business Analyst |

### Technical Integration Clarifications

| Question | Why It Matters | Impact | Owner |
| --- | --- | --- | --- |
| Which existing backend contract conclusively supports `/api/tenants/${tenantId}`? | The frontend interaction is established, but its backend relationship is dynamic or unresolved. | BLOCKING | Solution Architect / Modernization Engineer |
| Which existing backend contract conclusively supports `/api/tenants/list`? | The frontend interaction is established, but its backend relationship is dynamic or unresolved. | BLOCKING | Solution Architect / Modernization Engineer |

## 8. Review & Approval

| Role | Review Focus | Status |
| --- | --- | --- |
| Business Analyst | Review this Feature contract for the role's area of responsibility | Pending |
| Modernization Lead | Review this Feature contract for the role's area of responsibility | Pending |
| Product Owner | Review this Feature contract for the role's area of responsibility | Pending |
| QA Lead | Review this Feature contract for the role's area of responsibility | Pending |
| Solution Architect | Review this Feature contract for the role's area of responsibility | Pending |
| Customer SME | Current behavior and unresolved business decisions | Pending |

## Appendix — Technical Traceability

- Story IDs: story-clinic-appointment-experience-access-clinic-information, story-clinic-appointment-experience-establish-clinic-context
- Acceptance Criteria IDs: ac-clinic-appointment-experience-access-clinic-information-001, ac-clinic-appointment-experience-establish-clinic-context-001
- Source references: src/MyHealth.API/Controllers/UsersController.cs, src/MyHealth.Model/ClinicAppointment.cs
