# feature-patient-directory-management — Patient Directory Management

## Stakeholder Summary

| Item | Details |
| --- | --- |
| Feature | Patient Directory Management |
| Business capability | Provide tenant-aware navigation and access to patient information. |
| Stories | 2 |
| Acceptance Criteria | 2 |
| Target Design | Not Yet Analyzed |
| Target Architecture | Pending |
| Modernization | Not Started |
| Stakeholder Review | Pending |

## Feature Overview

Provides tenant-aware navigation and access to patient information.

Existing application behavior represented by approved workflows and Stories.

## Business Objective

Provide tenant-aware navigation and access to patient information.

## Business Value

- The Feature appears to support information accessibility by providing a dedicated patient information area.

## Current Business Behavior

### View Patient Directory

**Trigger:** Patient directory navigation is initiated.

**Interaction:** Resolve the patients route; Present the patient surface.

**Outcome:** The patient directory experience is available.

### Patients load current tenant

**Trigger:** Patient functionality needs clinic context.

**Interaction:** Request current tenant context; Make tenant context available to patient functionality.

**Outcome:** Patient functionality has current tenant context.

## Users and Actors

Current evidence establishes a general application user for this Feature. A more specific business persona has not yet been approved.

## Functional Scope

### In Scope

- Approved patient route, patient UI surfaces, Patient domain concept, and proven tenant-context integration.

### Out of Scope

- Backend rewrite, database migration, and patient operations without approved end-to-end mapping.

## Business Rules

No additional Feature-specific business rule has been established from the current application behavior.

## Data and Information

- **Patient:** Information representing a patient in the application domain.

## User Experience

### Current Experience

- An AngularJS patient route uses patient controller and service surfaces.

### Target Experience

No target design has been analyzed for this Feature. If a Figma design is supplied, Polaris will map relevant screens and components to the approved Stories and Acceptance Criteria before architecture and implementation. It will not redefine approved business behavior.

## User Stories and Acceptance Criteria

### STORY-PATIENT-DIRECTORY-MANAGEMENT-ESTABLISH-PATIENT-TENANT-CONTEXT — Establish Patient Tenant Context

**Story**

As an application user,  
I want to obtain tenant context for patient functionality,  
so that patient functionality has current tenant context.

**Business Context**

Represents the proven tenant-context interaction supporting the existing patient area.

**Current Behavior**

The existing application supports: Patient functionality has current tenant context.

#### Acceptance Criteria

##### AC-PATIENT-DIRECTORY-MANAGEMENT-ESTABLISH-PATIENT-TENANT-CONTEXT-001 — Establish Patient Tenant Context Behavior

**Given** Patient functionality needs clinic context.  
**When** Obtain tenant context for patient functionality  
**Then** Patient functionality has current tenant context.

### STORY-PATIENT-DIRECTORY-MANAGEMENT-REVIEW-PATIENT-DIRECTORY — Review Patient Directory

**Story**

As an application user,  
I want to access the existing patient directory,  
so that the patient directory experience is available.

**Business Context**

Represents the approved patient-directory navigation behavior without asserting unsupported patient operations.

**Current Behavior**

The existing application supports: The patient directory experience is available.

#### Acceptance Criteria

##### AC-PATIENT-DIRECTORY-MANAGEMENT-REVIEW-PATIENT-DIRECTORY-001 — Review Patient Directory Behavior

**Given** Patient directory navigation is initiated.  
**When** Access the existing patient directory  
**Then** The patient directory experience is available.

## Integration and Data Context

- **Patients load current tenant:** Established relationship must be preserved.

## Architecture Inputs

- Patient behavior depends on a legacy AngularJS frontend and incompletely mapped patient operations.
- Only tenant-context integration is proven end to end for this Feature.

Target Architecture is pending. These facts are inputs for that decision and do not prescribe an implementation approach.

## Open Decisions

### Which patient operations must be included when this Feature is decomposed into modernization Stories?

The approved Feature proves navigation and tenant context but not every patient operation mapping.

**Validation role:** Product Owner / Business Analyst / Customer SME

## Risks and Constraints

- Incomplete operation mapping limits detailed behavior decomposition.

## Modernization Requirements

- Preserve this approved business behavior during frontend modernization without changing backend contracts.

## Definition of Ready

- [ ] Business Feature reviewed
- [ ] Stories reviewed
- [ ] Acceptance Criteria reviewed
- [ ] Open decisions resolved or explicitly accepted
- [ ] Target-design path selected
- [ ] Target Architecture approved
- [ ] Required integration contracts confirmed

## Review and Sign-Off

| Role | Review Focus | Status |
| --- | --- | --- |
| Product Owner | Objective, value, scope, and Stories | Pending |
| Business Analyst | Workflows, rules, requirements, and criteria | Pending |
| Solution Architect | Integrations, data, constraints, and architecture inputs | Pending |
| QA Lead | Criterion testability and requirement clarity | Pending |
| Modernization Lead | Implementation readiness | Pending |
| Customer SME | Current behavior and open business decisions | Pending |

## Technical Traceability Appendix

- Story IDs: story-patient-directory-management-establish-patient-tenant-context, story-patient-directory-management-review-patient-directory
- Acceptance Criteria IDs: ac-patient-directory-management-establish-patient-tenant-context-001, ac-patient-directory-management-review-patient-directory-001
- Legacy surfaces: PatientsController, patients, patientsService
