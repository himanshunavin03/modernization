# Clinic Appointment Experience

**Feature ID:** `feature-clinic-appointment-experience`  
**Module:** Appointment management  
**Capabilities:** Manage clinic appointments  
**Confidence:** `LOW`

## Executive Description

Clinic Appointment Experience represents the approved clinic and appointment frontend surfaces associated with appointment management. It includes appointment views, clinic navigation, tenant-context loading, and Clinic appointment and Home appointment domain concepts.
The evidence does not establish a complete appointment transaction from user action through an appointment API. The only proven API relationship in this Feature is current tenant context, so this specification does not claim appointment creation, update, or scheduling behavior.

## Business Objectives

**CURRENT_OBJECTIVE:** Provide access to clinic/appointment navigation and appointment information within current tenant context.

**MODERNIZATION_OBJECTIVE:** Migrate only approved clinic/appointment surfaces and tenant-context behavior until stakeholders validate the missing appointment operation boundaries.

## Business Value

- **INFERRED_BUSINESS_VALUE:** The Feature appears to provide a focused place to access clinic and appointment information, but its complete business value requires stakeholder validation.

## Primary Users / Actors

No approved Feature evidence identifies who uses clinic appointment functionality.

## Current Business Functionality

- Provides clinic navigation, appointment-related UI surfaces, and current tenant context.

## Business Workflows

### Route clinic

- Trigger: Clinic detail navigation is initiated.
- Steps: Resolve the clinic route.; Present the clinic surface.
- Outcome: A clinic detail experience is available.
- Supporting UI: clinic, ClinicsController
- API status: `NOT_APPLICABLE`

### Route clinics

- Trigger: Clinic list navigation is initiated.
- Steps: Resolve the clinics route.; Present the clinics surface.
- Outcome: A clinic list experience is available.
- Supporting UI: clinics, ClinicsController
- API status: `NOT_APPLICABLE`

### Clinics load current tenant

- Trigger: Clinic functionality needs tenant context.
- Steps: Request current tenant context.; Make tenant context available to clinic functionality.
- Outcome: Clinic functionality has current tenant context.
- Supporting UI: ClinicsController
- API status: `PROVEN`

## Business Rules

NO_EVIDENCE_BACKED_BUSINESS_RULES_IDENTIFIED

## Domain Concepts and Information

- **Clinic appointment:** Information representing an appointment associated with a clinic. Provides approved appointment-domain context.
- **Home appointment:** Information representing a home appointment. Identifies another approved appointment concept; its behavior is not elaborated by this Feature evidence.
- The Feature involves clinic appointment information, home appointment information, and current tenant context.

## Dependencies


## API Integration Profile

- PROVEN: 1
- UNRESOLVED: 0
- DYNAMIC: 0
- EXTERNAL: 0
- NO_BACKEND_ROUTE: 0
- `PROVEN`: `src/MyHealth.Web/content/app/components/clinics/services/clinicsService.js` -> `/api/users/current/tenant` -> `GET /api/users/current/tenant`
- Limitation: The proven relationship supplies tenant context; it does not prove an appointment transaction endpoint.

## Current User Experience

- Razor appointment views and AngularJS clinic routes coexist in the approved Feature scope.

## Current-State Limitations and Concerns

- **BUSINESS_ANALYSIS_LIMITATION:** No complete appointment operation workflow or proven appointment transaction API relationship is present.
- **MODERNIZATION_CONCERN:** Generating appointment transaction behavior from the current Feature would exceed approved evidence.

## Modernization Scope

### In Scope

- Approved clinic routes, appointment/clinic UI surfaces, appointment concepts, and tenant-context integration.

### Out of Scope

- Appointment creation/update behavior, scheduling rules, backend/database redesign, and any transaction not supported by approved workflows.

## Assumptions

- None identified from approved evidence.

## Open Questions

- **Q-APT-001:** Which appointment operations are part of the current business workflow and must be preserved? Reason: The approved Feature does not contain a complete appointment-operation flow.
- **Q-APT-002:** How are the Razor appointment surfaces and AngularJS clinic surfaces intended to work together in the current user journey? Reason: Both are approved surfaces, but their complete composition is not proven.

## Risks and Limitations

- **BUSINESS_ANALYSIS_LIMITATION:** Low-confidence workflow interpretation prevents detailed Story generation without clarification.
- **TECHNICAL_MODERNIZATION_RISK:** Treating tenant-context integration as an appointment transaction would create unsupported behavior.

## MODERNIZATION_SUCCESS_INDICATORS

- Only approved clinic/appointment surfaces and tenant behavior are migrated until open workflow questions are resolved.

## STORY_DECOMPOSITION_GUIDANCE

- **Navigate clinic surfaces:** Approved navigation boundary; appointment transaction behavior must not be added. Workflows: Route clinic, Route clinics
- **Resolve clinic tenant context:** Only proven API-dependent workflow in this Feature. Workflows: Clinics load current tenant

## Technical Traceability

- `src/MyHealth.Model/ClinicAppointment.cs:4` -> `legacy-dashboard-complete-application-demo-v1:DTO:global::MyHealth.Model.ClinicAppointment`
- `src/MyHealth.API/Controllers/UsersController.cs:146` -> `legacy-dashboard-complete-application-demo-v1:Endpoint:GET /api/users/current/tenant`

