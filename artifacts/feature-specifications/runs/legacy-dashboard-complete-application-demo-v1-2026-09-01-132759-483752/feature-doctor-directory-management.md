# feature-doctor-directory-management — Doctor Directory Management

## 1. Feature Summary

Provides navigation and tenant-aware access to doctor information.

The Feature appears to support information accessibility by organizing doctor navigation and doctor information in one functional area.

The Feature provides the business interactions described below through the current application.

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

so that I can review doctor detail information with current tenant context.

**Business Context**

Combines the approved doctor detail navigation and its proven tenant-context dependency as one coherent interaction.

#### Acceptance Criteria

##### AC-DOCTOR-DIRECTORY-MANAGEMENT-VIEW-DOCTOR-DETAILS-IN-TENANT-CONTEXT-001 — View Doctor Details in Tenant Context Behavior

**Given** the related existing application capability is available

**When** the user accesses doctor detail with tenant context

**Then** users can access doctor detail information with current tenant context

**Current Backend Contract References**

- `API-DOCTOR_DIRECTORY_MANAGEMENT-001`

### STORY-DOCTOR-DIRECTORY-MANAGEMENT-REVIEW-DOCTOR-DIRECTORY — Review Doctor Directory

**Story**

As an application user,

I want to access the existing doctor directory,

so that I can review doctor directory.

**Business Context**

Represents the approved doctor-directory navigation behavior.

#### Acceptance Criteria

##### AC-DOCTOR-DIRECTORY-MANAGEMENT-REVIEW-DOCTOR-DIRECTORY-001 — Review Doctor Directory Behavior

**Given** the related existing application capability is available

**When** the user navigates doctor directory

**Then** users can access the existing doctor directory

## 5. Existing Backend API Contract

The existing backend is preserved within the current modernization scope. Confirmed API contracts in this specification are treated as existing integration contracts for the target frontend unless an explicitly approved change modifies them.

### API-DOCTOR_DIRECTORY_MANAGEMENT-001 — Doctors load current tenant

**Used By**

- Stories: `story-doctor-directory-management-view-doctor-details-in-tenant-context`
- Acceptance Criteria: `ac-doctor-directory-management-view-doctor-details-in-tenant-context-001`

**Current Frontend**

| Item | Existing Implementation |
| --- | --- |
| Technology | Legacy AngularJS 1.x |
| Controller / Component | Not established |
| Service | Not established |
| API expression | `GET /api/users/current/tenant` |
| Source | `src/MyHealth.Web/content/app/components/doctors/services/doctorsService.js` |

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
