# feature-clinic-appointment-experience — Clinic Appointment Experience

## 1. Feature Summary

Provides clinic/appointment navigation and appointment information with proven tenant context but incomplete transaction flow evidence.

The Feature appears to provide a focused place to access clinic and appointment information, but its complete business value requires stakeholder validation.

The Feature provides the business interactions described below through the current application.

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

so that I can review clinic information.

**Business Context**

Represents the approved clinic list and detail navigation behavior without asserting unsupported appointment transactions.

#### Acceptance Criteria

##### AC-CLINIC-APPOINTMENT-EXPERIENCE-ACCESS-CLINIC-INFORMATION-001 — Access Clinic Information Behavior

**Given** the related existing application capability is available

**When** the user navigates clinic surfaces

**Then** users can access the existing clinic information views

### STORY-CLINIC-APPOINTMENT-EXPERIENCE-ESTABLISH-CLINIC-CONTEXT — Establish Clinic Context

**Story**

As an application user,

I want to obtain tenant context for clinic functionality,

so that clinic functionality can use tenant context.

**Business Context**

Represents the proven tenant-context interaction that supports the existing clinic area.

#### Acceptance Criteria

##### AC-CLINIC-APPOINTMENT-EXPERIENCE-ESTABLISH-CLINIC-CONTEXT-001 — Establish Clinic Context Behavior

**Given** the related existing application capability is available

**When** the application resolves clinic tenant context

**Then** the application provides tenant context for clinic functionality

**Current Backend Contract References**

- `API-CLINIC_APPOINTMENT_EXPERIENCE-001`

## 5. Existing Backend API Contract

The existing backend is preserved within the current modernization scope. Confirmed API contracts in this specification are treated as existing integration contracts for the target frontend unless an explicitly approved change modifies them.

### API-CLINIC_APPOINTMENT_EXPERIENCE-001 — Clinics load current tenant

**Used By**

- Stories: `story-clinic-appointment-experience-establish-clinic-context`
- Acceptance Criteria: `ac-clinic-appointment-experience-establish-clinic-context-001`

**Current Frontend**

| Item | Existing Implementation |
| --- | --- |
| Technology | Legacy AngularJS 1.x |
| Controller / Component | Not established |
| Service | Not established |
| API expression | `GET /api/users/current/tenant` |
| Source | `src/MyHealth.Web/content/app/components/clinics/services/clinicsService.js` |

**Backend Endpoint**

| Item | Contract |
| --- | --- |
| HTTP Method | `GET` |
| Route | `/api/users/current/tenant` |
| Route Template | `api/[controller]/current/tenant` |
| Controller | `UsersController` |
| Action | `GetCurrentTenantAsync` |
| Source | `src/MyHealth.API/Controllers/UsersController.cs` |

**Request**

No path, query, header, or body contract is established for this endpoint.

**Response**

Response type: `Task<int?>`

Field-level contract: Not established from current deterministic evidence.

**Contract Status**

Contract confirmed from existing application evidence.

**Modernization Requirement**

Preserve this backend contract when implementing the target frontend unless an approved change explicitly modifies the integration contract.


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
