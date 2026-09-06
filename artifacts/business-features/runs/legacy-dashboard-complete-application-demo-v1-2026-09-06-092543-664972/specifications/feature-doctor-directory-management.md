# Doctor Directory Management

**Feature ID:** `feature-doctor-directory-management`  
**Module:** Doctor management  
**Capabilities:** Manage doctors  
**Confidence:** `MEDIUM`

## Executive Description

Doctor Directory Management represents the current frontend area for navigating doctor list and detail experiences. The approved Feature includes doctor routes, AngularJS UI/service surfaces, and the Doctor domain concept.
The Feature obtains current tenant context through a proven relationship. Other doctor operations are visible as a dependency on the doctor API contract, but their end-to-end mappings are not proven in the approved Feature evidence.

## Business Objectives

**CURRENT_OBJECTIVE:** Provide tenant-aware navigation and access to doctor information.

**MODERNIZATION_OBJECTIVE:** Migrate approved doctor list/detail frontend behavior while preserving the existing doctor and tenant API boundaries.

## Business Value

- **INFERRED_BUSINESS_VALUE:** The Feature appears to support information accessibility by organizing doctor navigation and doctor information in one functional area.

## Primary Users / Actors

No approved Feature evidence identifies the business role that uses doctor management.

## Current Business Functionality

- Provides doctor list/detail navigation and loads current tenant context for doctor operations.

## Business Workflows

### Route doctor

- Trigger: Doctor detail navigation is initiated.
- Steps: Resolve the doctor route.; Present the doctor detail surface.
- Outcome: A doctor detail experience is available.
- Supporting UI: doctor, DoctorsController
- API status: `NOT_APPLICABLE`

### Route doctors

- Trigger: Doctor list navigation is initiated.
- Steps: Resolve the doctors route.; Present the doctor list surface.
- Outcome: A doctor list experience is available.
- Supporting UI: doctors, DoctorsController
- API status: `NOT_APPLICABLE`

### Doctors load current tenant

- Trigger: Doctor functionality needs clinic context.
- Steps: Request current tenant context.; Make tenant context available to doctor functionality.
- Outcome: Doctor functionality has current tenant context.
- Supporting UI: DoctorsController, doctorsService
- API status: `PROVEN`

## Business Rules

NO_EVIDENCE_BACKED_BUSINESS_RULES_IDENTIFIED

## Domain Concepts and Information

- **Doctor:** Information representing a doctor in the application domain. Provides the domain information associated with doctor list/detail behavior.
- The Feature uses doctor information and current tenant context.

## Dependencies

- **TECHNICAL:** Doctor UI depends on doctor API contract - The doctor frontend retains an existing doctor API boundary.

## API Integration Profile

- PROVEN: 1
- UNRESOLVED: 0
- DYNAMIC: 0
- EXTERNAL: 0
- NO_BACKEND_ROUTE: 0
- `PROVEN`: `src/MyHealth.Web/content/app/components/doctors/services/doctorsService.js` -> `/api/users/current/tenant` -> `GET /api/users/current/tenant`
- Limitation: The tenant-context mapping is proven; other doctor operations mentioned by the upstream dependency are not represented as proven Feature API relationships.

## Current User Experience

- AngularJS doctor list/detail routes use doctor controller and service surfaces.

## Current-State Limitations and Concerns

- **BUSINESS_ANALYSIS_LIMITATION:** Only tenant-context integration is proven end to end for this Feature.
- **MODERNIZATION_CONCERN:** Doctor list/detail behavior depends on a legacy AngularJS frontend and incompletely mapped doctor operations.

## Modernization Scope

### In Scope

- Approved doctor routes, doctor UI surfaces, Doctor domain concept, and proven tenant-context integration.

### Out of Scope

- Backend rewrite, database migration, and doctor operations without approved end-to-end mapping.

## Assumptions

- None identified from approved evidence.

## Open Questions

- **Q-DOC-001:** Which doctor list and detail operations must be included when this Feature is decomposed into modernization Stories? Reason: The approved Feature proves navigation and tenant context but not every doctor operation mapping.

## Risks and Limitations

- **BUSINESS_ANALYSIS_LIMITATION:** Incomplete operation mapping limits detailed behavior decomposition.

## MODERNIZATION_SUCCESS_INDICATORS

- Approved doctor navigation, doctor information, and tenant-context behavior remain available and traceable in the target frontend.

## STORY_DECOMPOSITION_GUIDANCE

- **Navigate doctor directory:** List navigation is a distinct approved workflow. Workflows: Route doctors
- **Access doctor detail with tenant context:** Groups detail navigation with its proven context dependency. Workflows: Route doctor, Doctors load current tenant

## Technical Traceability

- `src/MyHealth.Web/content/app/components/doctors/controllers/doctorsController.js:1` -> `legacy-dashboard-complete-application-demo-v1:AngularController:DoctorsController`
- `src/MyHealth.Model/Doctor.cs:10` -> `legacy-dashboard-complete-application-demo-v1:DTO:global::MyHealth.Model.Doctor`

