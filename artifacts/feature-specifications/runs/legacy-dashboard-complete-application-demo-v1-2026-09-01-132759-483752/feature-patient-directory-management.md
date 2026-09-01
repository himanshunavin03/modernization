# feature-patient-directory-management — Patient Directory Management

## 1. Feature Summary

Provides tenant-aware navigation and access to patient information.

The Feature appears to support information accessibility by providing a dedicated patient information area.

The Feature provides the business interactions described below through the current application.

Migrate approved patient frontend behavior while preserving the patient and tenant API boundaries.

## 2. Functional Behavior

### Establish Patient Tenant Context

The application provides tenant context for patient functionality.

### Review Patient Directory

Users can access the existing patient directory.

The current requirements establish a general application user; a more specific business persona has not yet been approved.

## 3. Scope

### In Scope

- Approved patient route, patient UI surfaces, Patient domain concept, and proven tenant-context integration.

### Out of Scope

- Backend rewrite, database migration, and patient operations without approved end-to-end mapping.

## 4. User Stories & Acceptance Criteria

### STORY-PATIENT-DIRECTORY-MANAGEMENT-ESTABLISH-PATIENT-TENANT-CONTEXT — Establish Patient Tenant Context

**Story**

As an application user,

I want to obtain tenant context for patient functionality,

so that patient functionality can use tenant context.

**Business Context**

Represents the proven tenant-context interaction supporting the existing patient area.

#### Acceptance Criteria

##### AC-PATIENT-DIRECTORY-MANAGEMENT-ESTABLISH-PATIENT-TENANT-CONTEXT-001 — Establish Patient Tenant Context Behavior

**Given** the related existing application capability is available

**When** the application loads tenant-aware patient context

**Then** the application provides tenant context for patient functionality

**Current Backend Contract References**

- `API-PATIENT_DIRECTORY_MANAGEMENT-001`

### STORY-PATIENT-DIRECTORY-MANAGEMENT-REVIEW-PATIENT-DIRECTORY — Review Patient Directory

**Story**

As an application user,

I want to access the existing patient directory,

so that I can review patient directory.

**Business Context**

Represents the approved patient-directory navigation behavior without asserting unsupported patient operations.

#### Acceptance Criteria

##### AC-PATIENT-DIRECTORY-MANAGEMENT-REVIEW-PATIENT-DIRECTORY-001 — Review Patient Directory Behavior

**Given** the related existing application capability is available

**When** the user navigates patient directory

**Then** users can access the existing patient directory

## 5. Existing Backend API Contract

The existing backend is preserved within the current modernization scope. Confirmed API contracts in this specification are treated as existing integration contracts for the target frontend unless an explicitly approved change modifies them.

### API-PATIENT_DIRECTORY_MANAGEMENT-001 — Patients load current tenant

**Used By**

- Stories: `story-patient-directory-management-establish-patient-tenant-context`
- Acceptance Criteria: `ac-patient-directory-management-establish-patient-tenant-context-001`

**Current Frontend**

| Item | Existing Implementation |
| --- | --- |
| Technology | Legacy AngularJS 1.x |
| Controller / Component | Not established |
| Service | Not established |
| API expression | `GET /api/users/current/tenant` |
| Source | `src/MyHealth.Web/content/app/components/patients/services/patientsService.js` |

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

Relevant legacy surfaces: PatientsController, patients, patientsService

### Preservation Requirements

- Preserve this approved business behavior during frontend modernization without changing backend contracts.

**Target Design:** Not yet analyzed. If a Figma design is supplied later, it will be mapped to approved Feature behavior, Stories, and Acceptance Criteria.

**Target Architecture:** Pending.

## 7. Decisions Required Before Modernization

| Decision / Question | Why It Matters | Validation Role | Status |
| --- | --- | --- | --- |
| Which patient operations must be included when this Feature is decomposed into modernization Stories? | The approved Feature proves navigation and tenant context but not every patient operation mapping. | Product Owner / Business Analyst / Customer SME | Pending |

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

- Story IDs: story-patient-directory-management-establish-patient-tenant-context, story-patient-directory-management-review-patient-directory
- Acceptance Criteria IDs: ac-patient-directory-management-establish-patient-tenant-context-001, ac-patient-directory-management-review-patient-directory-001
- Source references: src/MyHealth.Model/Patient.cs, src/MyHealth.Web/content/app/components/patients/controllers/patientsController.js
