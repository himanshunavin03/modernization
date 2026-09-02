# feature-patient-directory-management — Patient Directory Management

## 1. Feature Summary

### Purpose

Provide tenant-aware navigation and access to patient information.

### Current Business Capability

Patient functionality has current tenant context. The current application provides a dedicated patient directory through which users can access the information supported by that experience.

### Business Value

Maintains the established tenant context used by patient functionality. Specific stakeholder outcomes for one or more access capabilities are not established and require confirmation.

**Business Value Status:** Requires Stakeholder Enrichment.

### Modernization Objective

Migrate approved patient frontend behavior while preserving the patient and tenant API boundaries.

## 2. Functional Behavior

### Establish Patient Tenant Context

Patient functionality has current tenant context.

### Review Patient Directory

The current application provides a dedicated patient directory through which users can access the information supported by that experience.

The available requirements establish a general application user; no more specific business persona is authoritative.

**Feature Name / Behavior Alignment:** Aligned.

## 3. Scope

### In Scope

- Approved patient route, patient UI surfaces, Patient domain concept, and proven tenant-context integration.

### Not Established by Current Evidence

- Backend rewrite, database migration, and patient operations without approved end-to-end mapping.

## 4. User Stories & Acceptance Criteria

### STORY-PATIENT-DIRECTORY-MANAGEMENT-ESTABLISH-PATIENT-TENANT-CONTEXT — Establish Patient Tenant Context

**Story**

As an application user,

I want to obtain tenant context for patient functionality,

so that patient functionality retains its established tenant-aware behavior.

**Business Context**

Represents the proven tenant-context interaction supporting the existing patient area.

**Business Value Status:** Supported Interpretation.

#### Acceptance Criteria

##### AC-PATIENT-DIRECTORY-MANAGEMENT-ESTABLISH-PATIENT-TENANT-CONTEXT-001 — Establish Patient Tenant Context Behavior

**Quality Status:** Fully Testable From Evidence.

**Given** Patient functionality needs clinic context

**When** the application obtains tenant context for patient functionality

**Then** patient functionality has current tenant context.

**Current Backend Contract References**

- `API-PATIENT_DIRECTORY_MANAGEMENT-001`

### STORY-PATIENT-DIRECTORY-MANAGEMENT-REVIEW-PATIENT-DIRECTORY — Review Patient Directory

**Story**

As an application user,

I want to access the existing patient directory.

Business outcome: Requires stakeholder confirmation; current evidence establishes the capability but not its specific business purpose.

**Business Context**

Represents the approved patient-directory navigation behavior without asserting unsupported patient operations.

**Business Value Status:** Not Established.

#### Acceptance Criteria

##### AC-PATIENT-DIRECTORY-MANAGEMENT-REVIEW-PATIENT-DIRECTORY-001 — Review Patient Directory Behavior

**Quality Status:** Testable With Evidence Limitation.

**Given** Patient directory navigation is initiated

**When** the user accesses the existing patient directory

**Then** the patient directory information supported by the current application is made available.

**Evidence Limitation**

Current evidence does not establish a complete customer-approved definition of the information or presentation details that must be retained.

**Current Backend Contract References**

- `API-PATIENT_DIRECTORY_MANAGEMENT-DISCOVERED-001`

## 5. Existing Backend Integration

Confirmed existing backend API contracts are preserved integration boundaries for the target frontend unless an explicitly approved change modifies them.

### Primary Business APIs

#### API-PATIENT_DIRECTORY_MANAGEMENT-DISCOVERED-001 — /api/patients

**Role in this Feature:** Primary Business Api.

**Current Frontend:** `src/MyHealth.Web/content/app/components/patients/services/patientsService.js` calls `GET /api/patients`.

**Confirmed Backend:** `GET /api/patients` implemented by `PatientsController.Get`.

### Supporting / Shared APIs

#### API-PATIENT_DIRECTORY_MANAGEMENT-001 — /api/users/current/tenant

**Role in this Feature:** Supporting Shared Api.

**Current Frontend:** `src/MyHealth.Web/content/app/components/patients/services/patientsService.js` calls `GET /api/users/current/tenant`.

**Confirmed Backend:** `GET /api/users/current/tenant` implemented by `UsersController.GetCurrentTenantAsync`.

This contract supplies shared context only; it does not provide the Feature's primary business data.

## 6. Modernization Considerations

### Current Implementation Context

Relevant legacy surfaces: PatientsController, patients, patientsService

### Preservation Requirements

- Preserve this approved business behavior during frontend modernization without changing backend contracts.

**Target Design:** Not yet analyzed.

**Target Architecture:** Pending.

## 7. Decisions Required Before Modernization

### Business Clarifications

| Question | Why It Matters | Impact | Owner |
| --- | --- | --- | --- |
| What business outcome should users achieve through Review Patient Directory beyond access to the currently established capability? | Current evidence establishes the behavior but not the stakeholder's intended business outcome. | NON_BLOCKING | Product Owner / Business Analyst / Customer SME |
| Which information must be considered mandatory when validating Review Patient Directory in the modernized experience? | Current evidence does not establish a complete customer-approved definition of the information or presentation details that must be retained. | BLOCKING | Product Owner / Business Analyst / Customer SME / QA Lead |

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
