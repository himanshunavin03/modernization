# feature-doctor-directory-management — Doctor Directory Management

## 1. Feature Summary

**Purpose**

Users can access doctor detail information with current tenant context. Users can access the existing doctor directory.

**Business Value**

The Feature appears to support information accessibility by organizing doctor navigation and doctor information in one functional area.

**Current State**

The current implementation uses DoctorsController, doctor, doctors, doctorsService.

**Modernization Objective**

Migrate approved doctor list/detail frontend behavior while preserving the existing doctor and tenant API boundaries.

## 2. Functional Behavior

### View Doctor Details in Tenant Context

Users can access doctor detail information with current tenant context.

### Review Doctor Directory

Users can access the existing doctor directory.

The current requirements establish a general application user; a more specific business persona has not yet been approved.

## 3. Scope

### In Scope

- Approved doctor routes, doctor UI surfaces, Doctor domain concept, and proven tenant-context integration.

### Out of Scope

- Backend rewrite, database migration, and doctor operations without approved end-to-end mapping.

## 4. User Stories & Acceptance Criteria

### STORY-DOCTOR-DIRECTORY-MANAGEMENT-VIEW-DOCTOR-DETAILS-IN-TENANT-CONTEXT — View Doctor Details in Tenant Context

**Story**

As an application user,

I want to access doctor detail information with current tenant context,

so that the application can present the supported doctor detail information with current tenant context.

**Business Context**

Combines the approved doctor detail navigation and its proven tenant-context dependency as one coherent interaction.

#### Acceptance Criteria

##### AC-DOCTOR-DIRECTORY-MANAGEMENT-VIEW-DOCTOR-DETAILS-IN-TENANT-CONTEXT-001 — View Doctor Details in Tenant Context Behavior

**Criterion Type:** Functional Acceptance Criterion

**Given** doctor detail navigation is initiated

**When** the user accesses doctor detail with tenant context

**Then** users can access doctor detail information with current tenant context

**Current Backend Contract References**

- `API-DOCTOR_DIRECTORY_MANAGEMENT-001`
- `API-DOCTOR_DIRECTORY_MANAGEMENT-DISCOVERED-001`
- `API-DOCTOR_DIRECTORY_MANAGEMENT-DISCOVERED-002`

### STORY-DOCTOR-DIRECTORY-MANAGEMENT-REVIEW-DOCTOR-DIRECTORY — Review Doctor Directory

**Story**

As an application user,

I want to access the existing doctor directory,

so that the application can present the supported doctor directory.

**Business Context**

Represents the approved doctor-directory navigation behavior.

#### Acceptance Criteria

##### AC-DOCTOR-DIRECTORY-MANAGEMENT-REVIEW-DOCTOR-DIRECTORY-001 — Review Doctor Directory Behavior

**Criterion Type:** Functional Acceptance Criterion

**Given** doctor list navigation is initiated

**When** the user navigates doctor directory

**Then** users can access the existing doctor directory

**Current Backend Contract References**

- `API-DOCTOR_DIRECTORY_MANAGEMENT-DISCOVERED-001`
- `API-DOCTOR_DIRECTORY_MANAGEMENT-DISCOVERED-002`

## 5. Existing Backend Integration

Confirmed existing backend API contracts are preserved integration boundaries for the target frontend unless an explicitly approved change modifies them.

### Supporting / Shared APIs

#### API-DOCTOR_DIRECTORY_MANAGEMENT-001 — GET /api/users/current/tenant

**Role in this Feature:** Supporting Shared Api.

**Current Frontend:** `src/MyHealth.Web/content/app/components/doctors/services/doctorsService.js` calls `GET /api/users/current/tenant`.

**Confirmed Backend:** `GET /api/users/current/tenant` implemented by `UsersController.GetCurrentTenantAsync`.

This contract supplies shared context only; it does not provide the Feature's primary business data.

### Unresolved or Dynamic Integrations

#### API-DOCTOR_DIRECTORY_MANAGEMENT-DISCOVERED-001 — `/api/doctors/${doctorId}`

**Role in this Feature:** Dynamic Primary Interaction.

**Current Frontend:** `src/MyHealth.Web/content/app/components/doctors/services/doctorsService.js` calls `GET `/api/doctors/${doctorId}``.

**Candidate Existing Backend Contract**

The associated frontend interaction is established, but no deterministic frontend-to-backend mapping proves a contract. The following endpoint is a candidate only and requires confirmation:

- `GET /api/doctors/{id}` — `DoctorsController.GetAsync`; response `Task<Doctor>`

**Modernization Requirement:** Confirm the existing integration before implementing this behavior in the target frontend.

#### API-DOCTOR_DIRECTORY_MANAGEMENT-DISCOVERED-002 — /api/doctors

**Role in this Feature:** Unresolved Primary Interaction.

**Current Frontend:** `src/MyHealth.Web/content/app/components/doctors/services/doctorsService.js` calls `GET /api/doctors`.

**Candidate Existing Backend Contract**

The associated frontend interaction is established, but no deterministic frontend-to-backend mapping proves a contract. The following endpoint is a candidate only and requires confirmation:

- `GET /api/doctors` — `DoctorsController.GetAsync`; response `Task<IEnumerable<Doctor>>`

**Modernization Requirement:** Confirm the existing integration before implementing this behavior in the target frontend.


## 6. Modernization Considerations

### Current Implementation Context

Relevant legacy surfaces: DoctorsController, doctor, doctors, doctorsService

### Preservation Requirements

- Preserve this approved business behavior during frontend modernization without changing backend contracts.

**Target Design:** Not yet analyzed. If a Figma design is supplied later, it will be mapped to approved Feature behavior, Stories, and Acceptance Criteria.

**Target Architecture:** Pending.

## 7. Decisions Required Before Modernization

| Decision / Question | Why It Matters | Validation Role | Status |
| --- | --- | --- | --- |
| Which doctor list and detail operations must be included when this Feature is decomposed into modernization Stories? | The approved Feature proves navigation and tenant context but not every doctor operation mapping. | Product Owner / Business Analyst / Customer SME | Pending |

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

- Story IDs: story-doctor-directory-management-view-doctor-details-in-tenant-context, story-doctor-directory-management-review-doctor-directory
- Acceptance Criteria IDs: ac-doctor-directory-management-view-doctor-details-in-tenant-context-001, ac-doctor-directory-management-review-doctor-directory-001
- Source references: src/MyHealth.Model/Doctor.cs, src/MyHealth.Web/content/app/components/doctors/controllers/doctorsController.js
