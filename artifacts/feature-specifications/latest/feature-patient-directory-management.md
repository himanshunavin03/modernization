# feature-patient-directory-management — Patient Directory Management

## 1. Feature Overview

Provides tenant-aware navigation and access to patient information.

**Purpose:** Provide tenant-aware navigation and access to patient information.

**Modernization relevance:** Migrate approved patient frontend behavior while preserving the patient and tenant API boundaries.

## 2. Business Objective

Provide tenant-aware navigation and access to patient information.

## 3. Business Value

- The Feature appears to support information accessibility by providing a dedicated patient information area.

## 4. Current Business Behavior

- The patient directory experience is available.
- Patient functionality has current tenant context.

## 5. Users / Actors

The existing evidence identifies a general application user but does not establish a more specific business persona for this Feature.

## 6. Functional Scope

### In Scope

- Approved patient route, patient UI surfaces, Patient domain concept, and proven tenant-context integration.

### Out of Scope

- Backend rewrite, database migration, and patient operations without approved end-to-end mapping.

## 7. Business Workflows

### Route patients

**Trigger:** Patient directory navigation is initiated.

**Interaction:** Resolve the patients route.; Present the patient surface.

**Observable outcome:** The patient directory experience is available.

### Patients load current tenant

**Trigger:** Patient functionality needs clinic context.

**Interaction:** Request current tenant context.; Make tenant context available to patient functionality.

**Observable outcome:** Patient functionality has current tenant context.

## 8. Business Rules

No additional Feature-specific Business Rule has been established from the current approved application evidence.

## 9. Data / Information Requirements

- **Patient:** Information representing a patient in the application domain.

## 10. User Experience

### Current Experience

- An AngularJS patient route uses patient controller and service surfaces.

### Target Experience

The target user experience will be defined during the optional target-design/Figma and Target Architecture stages.

## 11. Target Design / Figma

Status: **Not provided / not analyzed in this stage**

Polaris supports an optional target-design source such as Figma. When supplied, the target design will be mapped to this Feature and its Stories without silently redefining approved business behavior.

- Design source: Not provided
- Figma URL: Not provided
- Relevant page/frame: Not mapped
- Design status: Not Yet Analyzed
- Mapped Stories: None

## 12. User Stories

### story-patient-directory-management-establish-patient-tenant-context — Establish Patient Tenant Context

**Story**

As a user of the existing application, I want obtain tenant context for patient functionality, so that I can access the supported behavior in the existing experience.

#### Description

Represents the proven tenant-context interaction supporting the existing patient area.

#### Business Context

This Story implements the approved workflow boundary: Load tenant-aware patient context.

#### Current Behavior

The existing application supports: Patient functionality has current tenant context.

## 13. Acceptance Criteria

### ac-patient-directory-management-establish-patient-tenant-context-001 — Establish Patient Tenant Context Behavior

**Given** the approved current-state context for load tenant-aware patient context is available

**When** obtain tenant context for patient functionality

**Then** The existing application supports: Patient functionality has current tenant context.

### story-patient-directory-management-review-patient-directory — Review Patient Directory

**Story**

As a user of the existing application, I want access the existing patient directory, so that I can access the supported behavior in the existing experience.

#### Description

Represents the approved patient-directory navigation behavior without asserting unsupported patient operations.

#### Business Context

This Story implements the approved workflow boundary: Navigate patient directory.

#### Current Behavior

The existing application supports: The patient directory experience is available.

## 13. Acceptance Criteria

### ac-patient-directory-management-review-patient-directory-001 — Review Patient Directory Behavior

**Given** the approved current-state context for navigate patient directory is available

**When** access the existing patient directory

**Then** The existing application supports: The patient directory experience is available.

## 14. Functional Requirements Summary

- `ac-patient-directory-management-establish-patient-tenant-context-001`: The existing application supports: Patient functionality has current tenant context.
- `ac-patient-directory-management-review-patient-directory-001`: The existing application supports: The patient directory experience is available.

## 15. Integration / API Requirements

- Patients load current tenant: Established relationship must be preserved.

## 16. Data Dependencies

- **Patient UI depends on patient API contract:** The patient frontend retains an existing patient API boundary.

## 17. Security and Access

Feature-specific access and authorization requirements will be confirmed during architecture and stakeholder validation.

## 18. Modernization Requirements

- Preserve this approved business behavior during frontend modernization without changing backend contracts.

## 19. Legacy-to-Target Mapping

### Legacy Side

- PatientsController
- patients
- patientsService

### Target Side

Target implementation mapping will be completed after Target Design and Target Architecture are approved.

## 20. Architecture Considerations

- Patient behavior depends on a legacy AngularJS frontend and incompletely mapped patient operations.
- Only tenant-context integration is proven end to end for this Feature.

These are architecture inputs, not architecture decisions.

## 21. Non-Functional Requirements

Feature-specific non-functional requirements have not yet been approved. Performance, accessibility, security, observability and related quality attributes will be addressed during Target Architecture and stakeholder review.

## 22. Open Business / Architecture Decisions

- **Question:** Which patient operations must be included when this Feature is decomposed into modernization Stories? **Why it matters:** The approved Feature proves navigation and tenant context but not every patient operation mapping. **Validation:** Product Owner / Business Analyst / Customer SME

## 23. Risks and Constraints

- Incomplete operation mapping limits detailed behavior decomposition.

## 24. Dependencies

- Patient UI depends on patient API contract

## 25. Definition of Ready for Modernization

- [ ] Business Feature reviewed
- [ ] Stories reviewed
- [ ] Acceptance Criteria reviewed
- [ ] Open decisions resolved or explicitly accepted
- [ ] Target-design path selected
- [ ] Target Architecture approved
- [ ] Required integration contracts confirmed

## 26. Validation and Sign-Off

| Role | Review Focus | Status |
| --- | --- | --- |
| Product Owner | Business objective, value, scope, Stories | Pending |
| Business Analyst | Workflows, rules, requirements, AC | Pending |
| Solution Architect | Integrations, data, constraints, architecture inputs | Pending |
| QA Lead | AC testability and requirement clarity | Pending |
| Modernization Lead | Implementation readiness | Pending |

## Technical Traceability Appendix

- Story IDs: story-patient-directory-management-establish-patient-tenant-context, story-patient-directory-management-review-patient-directory
- Acceptance Criteria IDs: ac-patient-directory-management-establish-patient-tenant-context-001, ac-patient-directory-management-review-patient-directory-001
- Legacy surfaces: PatientsController, patients, patientsService
