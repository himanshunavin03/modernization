# feature-doctor-directory-management — Doctor Directory Management

## 1. Feature Summary

### Purpose

Provide tenant-aware navigation and access to doctor information.

### Current Business Capability

A doctor detail experience is available. Doctor functionality has current tenant context. The current application provides a dedicated doctor directory through which users can access the information supported by that experience.

### Business Value

Preserves tenant-aware access to the established doctor detail information. Specific stakeholder outcomes for one or more access capabilities are not established and require confirmation.

**Business Value Status:** Requires Stakeholder Enrichment.

### Modernization Objective

Migrate approved doctor list/detail frontend behavior while preserving the existing doctor and tenant API boundaries.

## 2. Functional Behavior

### View Doctor Details in Tenant Context

A doctor detail experience is available. Doctor functionality has current tenant context.

### Review Doctor Directory

The current application provides a dedicated doctor directory through which users can access the information supported by that experience.

The available requirements establish a general application user; no more specific business persona is authoritative.

**Feature Name / Behavior Alignment:** Aligned.

## 3. Scope

### In Scope

- Approved doctor routes, doctor UI surfaces, Doctor domain concept, and proven tenant-context integration.

### Not Established by Current Evidence

- Backend rewrite, database migration, and doctor operations without approved end-to-end mapping.

## 4. User Stories & Acceptance Criteria

### STORY-DOCTOR-DIRECTORY-MANAGEMENT-VIEW-DOCTOR-DETAILS-IN-TENANT-CONTEXT — View Doctor Details in Tenant Context

**Story**

As an application user,

I want to access doctor detail information with current tenant context,

so that the established doctor detail information remains associated with current tenant context.

**Business Context**

Combines the approved doctor detail navigation and its proven tenant-context dependency as one coherent interaction.

**Business Value Status:** Supported Interpretation.

#### Acceptance Criteria

##### AC-DOCTOR-DIRECTORY-MANAGEMENT-VIEW-DOCTOR-DETAILS-IN-TENANT-CONTEXT-001 — View Doctor Details in Tenant Context Behavior

**Quality Status:** Testable With Evidence Limitation.

**Given** Doctor detail navigation is initiated

**When** the user accesses doctor detail information with current tenant context

**Then** a doctor detail experience is available; and doctor functionality has current tenant context.

**Evidence Limitation**

Current evidence does not establish a complete customer-approved definition of the information or presentation details that must be retained.

**Current Backend Contract References**

- `API-DOCTOR_DIRECTORY_MANAGEMENT-001`
- `API-DOCTOR_DIRECTORY_MANAGEMENT-DISCOVERED-001`
- `API-DOCTOR_DIRECTORY_MANAGEMENT-DISCOVERED-002`

### STORY-DOCTOR-DIRECTORY-MANAGEMENT-REVIEW-DOCTOR-DIRECTORY — Review Doctor Directory

**Story**

As an application user,

I want to access the existing doctor directory.

Business outcome: Requires stakeholder confirmation; current evidence establishes the capability but not its specific business purpose.

**Business Context**

Represents the approved doctor-directory navigation behavior.

**Business Value Status:** Not Established.

#### Acceptance Criteria

##### AC-DOCTOR-DIRECTORY-MANAGEMENT-REVIEW-DOCTOR-DIRECTORY-001 — Review Doctor Directory Behavior

**Quality Status:** Testable With Evidence Limitation.

**Given** Doctor list navigation is initiated

**When** the user accesses the existing doctor directory

**Then** the doctor directory information supported by the current application is made available.

**Evidence Limitation**

Current evidence does not establish a complete customer-approved definition of the information or presentation details that must be retained.

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

**Current Frontend:** `src/MyHealth.Web/content/app/components/doctors/services/doctorsService.js` calls `GET `/api/doctors/${doctorId}`.

**Candidate Existing Backend Contract**

A matching backend endpoint exists, but the current frontend-to-backend relationship has not been conclusively established:

- `GET /api/doctors/{id}` — `DoctorsController.GetAsync`; response `Task<Doctor>`

**Modernization Requirement:** Confirm the existing integration before implementing this behavior in the target frontend.

#### API-DOCTOR_DIRECTORY_MANAGEMENT-DISCOVERED-002 — /api/doctors

**Role in this Feature:** Unresolved Primary Interaction.

**Current Frontend:** `src/MyHealth.Web/content/app/components/doctors/services/doctorsService.js` calls `GET /api/doctors`.

**Candidate Existing Backend Contract**

A matching backend endpoint exists, but the current frontend-to-backend relationship has not been conclusively established:

- `GET /api/doctors` — `DoctorsController.GetAsync`; response `Task<IEnumerable<Doctor>>`

**Modernization Requirement:** Confirm the existing integration before implementing this behavior in the target frontend.

## 6. Modernization Considerations

### Current Implementation Context

Relevant legacy surfaces: DoctorsController, doctor, doctors, doctorsService

### Preservation Requirements

- Preserve this approved business behavior during frontend modernization without changing backend contracts.

**Target Design:** Not yet analyzed.

**Target Architecture:** Pending.

## 7. Decisions Required Before Modernization

### Business Clarifications

| Question | Why It Matters | Impact | Owner |
| --- | --- | --- | --- |
| What business outcome should users achieve through Review Doctor Directory beyond access to the currently established capability? | Current evidence establishes the behavior but not the stakeholder's intended business outcome. | NON_BLOCKING | Product Owner / Business Analyst / Customer SME |
| Which information must be considered mandatory when validating Review Doctor Directory in the modernized experience? | Current evidence does not establish a complete customer-approved definition of the information or presentation details that must be retained. | BLOCKING | Product Owner / Business Analyst / Customer SME / QA Lead |
| Which information must be considered mandatory when validating View Doctor Details in Tenant Context in the modernized experience? | Current evidence does not establish a complete customer-approved definition of the information or presentation details that must be retained. | BLOCKING | Product Owner / Business Analyst / Customer SME / QA Lead |

### Technical Integration Clarifications

| Question | Why It Matters | Impact | Owner |
| --- | --- | --- | --- |
| Which existing backend contract conclusively supports `/api/doctors/${doctorId}`? | The frontend interaction is established, but its backend relationship is dynamic or unresolved. | BLOCKING | Solution Architect / Modernization Engineer |
| Which existing backend contract conclusively supports `/api/doctors`? | The frontend interaction is established, but its backend relationship is dynamic or unresolved. | BLOCKING | Solution Architect / Modernization Engineer |

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
