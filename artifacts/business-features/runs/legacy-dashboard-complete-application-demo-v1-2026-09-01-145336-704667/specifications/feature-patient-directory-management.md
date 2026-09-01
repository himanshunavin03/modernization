# Patient Directory Management

**Feature ID:** `feature-patient-directory-management`  
**Module:** Patient management  
**Capabilities:** Manage patients  
**Confidence:** `MEDIUM`

## Executive Description

Patient Directory Management represents the current frontend area for navigating patient information. The approved Feature includes a patient route, AngularJS UI/service surfaces, and the Patient domain concept.
The Feature obtains current tenant context through a proven relationship. Other patient operations are acknowledged by the upstream dependency but are not promoted to proven mappings in this specification.

## Business Objectives

**CURRENT_OBJECTIVE:** Provide tenant-aware navigation and access to patient information.

**MODERNIZATION_OBJECTIVE:** Migrate approved patient frontend behavior while preserving the patient and tenant API boundaries.

## Business Value

- **INFERRED_BUSINESS_VALUE:** The Feature appears to support information accessibility by providing a dedicated patient information area.

## Primary Users / Actors

No approved Feature evidence identifies the business role that uses patient management.

## Current Business Functionality

- Provides patient navigation and loads current tenant context for patient functionality.

## Business Workflows

### Route patients

- Trigger: Patient directory navigation is initiated.
- Steps: Resolve the patients route.; Present the patient surface.
- Outcome: The patient directory experience is available.
- Supporting UI: patients, PatientsController
- API status: `NOT_APPLICABLE`

### Patients load current tenant

- Trigger: Patient functionality needs clinic context.
- Steps: Request current tenant context.; Make tenant context available to patient functionality.
- Outcome: Patient functionality has current tenant context.
- Supporting UI: PatientsController, patientsService
- API status: `PROVEN`

## Business Rules

NO_EVIDENCE_BACKED_BUSINESS_RULES_IDENTIFIED

## Domain Concepts and Information

- **Patient:** Information representing a patient in the application domain. Provides the domain information associated with patient behavior.
- The Feature uses patient information and current tenant context.

## Dependencies

- **TECHNICAL:** Patient UI depends on patient API contract - The patient frontend retains an existing patient API boundary.

## API Integration Profile

- PROVEN: 1
- UNRESOLVED: 0
- DYNAMIC: 0
- EXTERNAL: 0
- NO_BACKEND_ROUTE: 0
- `PROVEN`: `src/MyHealth.Web/content/app/components/patients/services/patientsService.js` -> `GET /api/users/current/tenant` -> `GET /api/users/current/tenant`
- Limitation: Tenant context is proven; other patient operations are not represented as proven Feature API relationships.

## Current User Experience

- An AngularJS patient route uses patient controller and service surfaces.

## Current-State Limitations and Concerns

- **BUSINESS_ANALYSIS_LIMITATION:** Only tenant-context integration is proven end to end for this Feature.
- **MODERNIZATION_CONCERN:** Patient behavior depends on a legacy AngularJS frontend and incompletely mapped patient operations.

## Modernization Scope

### In Scope

- Approved patient route, patient UI surfaces, Patient domain concept, and proven tenant-context integration.

### Out of Scope

- Backend rewrite, database migration, and patient operations without approved end-to-end mapping.

## Assumptions

- None identified from approved evidence.

## Open Questions

- **Q-PAT-001:** Which patient operations must be included when this Feature is decomposed into modernization Stories? Reason: The approved Feature proves navigation and tenant context but not every patient operation mapping.

## Risks and Limitations

- **BUSINESS_ANALYSIS_LIMITATION:** Incomplete operation mapping limits detailed behavior decomposition.

## MODERNIZATION_SUCCESS_INDICATORS

- Approved patient navigation, patient information, and tenant-context behavior remain available and traceable in the target frontend.

## STORY_DECOMPOSITION_GUIDANCE

- **Navigate patient directory:** Navigation is a distinct approved workflow. Workflows: Route patients
- **Load tenant-aware patient context:** Separates the proven API-dependent context behavior. Workflows: Patients load current tenant

## Technical Traceability

- `src/MyHealth.Web/content/app/components/patients/controllers/patientsController.js:1` -> `legacy-dashboard-complete-application-demo-v1:AngularController:PatientsController`
- `src/MyHealth.Model/Patient.cs:8` -> `legacy-dashboard-complete-application-demo-v1:Type:Patient`

