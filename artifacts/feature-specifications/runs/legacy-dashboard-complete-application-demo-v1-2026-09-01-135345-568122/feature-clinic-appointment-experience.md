# feature-clinic-appointment-experience — Clinic Appointment Experience

## 1. Feature Summary

**Purpose**

Users can access the existing clinic information views. The application provides tenant context for clinic functionality.

**Business Value**

The Feature appears to provide a focused place to access clinic and appointment information, but its complete business value requires stakeholder validation.

**Current State**

The current implementation uses ClinicsController, clinic, clinics.

**Modernization Objective**

Migrate only approved clinic/appointment surfaces and tenant-context behavior until stakeholders validate the missing appointment operation boundaries.

## 2. Functional Behavior

### Access Clinic Information

Users can access the existing clinic information views.

### Establish Clinic Context

The application provides tenant context for clinic functionality.

The current requirements establish a general application user; a more specific business persona has not yet been approved.

## 3. Scope

### In Scope

- Approved clinic routes, appointment/clinic UI surfaces, appointment concepts, and tenant-context integration.

### Out of Scope

- Appointment creation/update behavior, scheduling rules, backend/database redesign, and any transaction not supported by approved workflows.

## 4. User Stories & Acceptance Criteria

### STORY-CLINIC-APPOINTMENT-EXPERIENCE-ACCESS-CLINIC-INFORMATION — Access Clinic Information

**Story**

As an application user,

I want to access the existing clinic information views,

so that the application can present the supported clinic information.

**Business Context**

Represents the approved clinic list and detail navigation behavior without asserting unsupported appointment transactions.

#### Acceptance Criteria

##### AC-CLINIC-APPOINTMENT-EXPERIENCE-ACCESS-CLINIC-INFORMATION-001 — Access Clinic Information Behavior

**Criterion Type:** Functional Acceptance Criterion

**Given** clinic detail navigation is initiated

**When** the user navigates clinic surfaces

**Then** users can access the existing clinic information views

**Current Backend Contract References**

- `API-CLINIC_APPOINTMENT_EXPERIENCE-DISCOVERED-001`
- `API-CLINIC_APPOINTMENT_EXPERIENCE-DISCOVERED-002`

### STORY-CLINIC-APPOINTMENT-EXPERIENCE-ESTABLISH-CLINIC-CONTEXT — Establish Clinic Context

**Story**

As an application user,

I want to obtain tenant context for clinic functionality,

so that clinic functionality can use tenant context.

**Business Context**

Represents the proven tenant-context interaction that supports the existing clinic area.

#### Acceptance Criteria

##### AC-CLINIC-APPOINTMENT-EXPERIENCE-ESTABLISH-CLINIC-CONTEXT-001 — Establish Clinic Context Behavior

**Criterion Type:** Functional Acceptance Criterion

**Given** clinic functionality needs tenant context

**When** the application resolves clinic tenant context

**Then** the application provides tenant context for clinic functionality

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

**Current Frontend:** `src/MyHealth.Web/content/app/components/clinics/services/clinicsService.js` calls `GET `/api/tenants/${tenantId}``.

**Candidate Existing Backend Contract**

The associated frontend interaction is established, but no deterministic frontend-to-backend mapping proves a contract. The following endpoint is a candidate only and requires confirmation:

- `GET /api/tenants/{tenantId}` — `TenantsController.GetAsync`; response `Task<Tenant>`

**Modernization Requirement:** Confirm the existing integration before implementing this behavior in the target frontend.

#### API-CLINIC_APPOINTMENT_EXPERIENCE-DISCOVERED-002 — /api/tenants/list

**Role in this Feature:** Unresolved Primary Interaction.

**Current Frontend:** `src/MyHealth.Web/content/app/components/clinics/services/clinicsService.js` calls `GET /api/tenants/list`.

**Candidate Existing Backend Contract**

The associated frontend interaction is established, but no deterministic frontend-to-backend mapping proves a contract. The following endpoint is a candidate only and requires confirmation:

- `GET /api/tenants/list` — `TenantsController.GetAsync`; response `Task<IEnumerable<Tenant>>`

**Modernization Requirement:** Confirm the existing integration before implementing this behavior in the target frontend.


## 6. Modernization Considerations

### Current Implementation Context

Relevant legacy surfaces: ClinicsController, clinic, clinics

### Preservation Requirements

- Preserve this approved business behavior during frontend modernization without changing backend contracts.

**Target Design:** Not yet analyzed. If a Figma design is supplied later, it will be mapped to approved Feature behavior, Stories, and Acceptance Criteria.

**Target Architecture:** Pending.

## 7. Decisions Required Before Modernization

| Decision / Question | Why It Matters | Validation Role | Status |
| --- | --- | --- | --- |
| Which appointment operations are part of the current business workflow and must be preserved? | The approved Feature does not contain a complete appointment-operation flow. | Product Owner / Business Analyst / Customer SME | Pending |
| How are the Razor appointment surfaces and AngularJS clinic surfaces intended to work together in the current user journey? | Both are approved surfaces, but their complete composition is not proven. | Product Owner / Business Analyst / Customer SME | Pending |

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
