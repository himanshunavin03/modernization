# Operational Dashboard Insights

**Feature ID:** `feature-operational-dashboard-insights`  
**Module:** Dashboard and reporting  
**Capabilities:** Dashboard visualization, Clinic summary reporting  
**Confidence:** `HIGH`

## Executive Description

Operational Dashboard Insights represents the application's dashboard and clinic-reporting experience. It brings together an entry page, an interactive dashboard surface, tenant-context lookup, and requests for clinic summary, expense, and patient reporting information.
The Feature belongs to the broader Dashboard and reporting module. Current evidence shows that the Razor page and AngularJS controller are two implementation surfaces of the same business Feature rather than separate business outcomes.
The existing experience uses proven tenant-context integrations, while clinic-summary resolution is unresolved and yearly report addresses are constructed dynamically. These distinctions constrain what can be stated about current behavior and what later modernization work may safely preserve.

## Business Objectives

**CURRENT_OBJECTIVE:** Provide access to dashboard summaries and clinic reporting information in the current tenant context.

**MODERNIZATION_OBJECTIVE:** Preserve the approved dashboard workflows and API contracts while consolidating the Razor-hosted and AngularJS frontend surfaces into the target frontend.

## Business Value

- **INFERRED_BUSINESS_VALUE:** The Feature appears to support operational visibility by bringing clinic summary and yearly reporting information into one dashboard experience.

## Primary Users / Actors

No approved Feature evidence identifies a named business actor or persona; the specification therefore uses application-trigger language rather than assuming a healthcare role.

## Current Business Functionality

- Makes the Dashboard route and its Razor-hosted AngularJS experience available.
- Obtains tenant context and requests clinic-summary, expense, and patient-report information.

## Business Workflows

### Route dashboard

- Trigger: Dashboard navigation is initiated.
- Steps: Resolve the Dashboard route.; Present the approved dashboard UI surface.
- Outcome: The Dashboard experience is available.
- Supporting UI: dashboard, DashboardController, src/MyHealth.Web/Views/Dashboard/Index.cshtml
- API status: `NOT_APPLICABLE`

### Dashboard summary loads current tenant

- Trigger: The dashboard summary flow needs clinic context.
- Steps: Request current tenant context.; Make tenant context available to the summary flow.
- Outcome: The dashboard summary flow has current tenant context.
- Supporting UI: DashboardController, dashboardService
- API status: `PROVEN`

### Dashboard expenses load current tenant

- Trigger: The expense-reporting flow needs clinic context.
- Steps: Request current tenant context.; Make tenant context available to expense reporting.
- Outcome: The expense-reporting flow has current tenant context.
- Supporting UI: DashboardController, dashboardService
- API status: `PROVEN`

### Dashboard patient report loads current tenant

- Trigger: The patient-reporting flow needs clinic context.
- Steps: Request current tenant context.; Make tenant context available to patient reporting.
- Outcome: The patient-reporting flow has current tenant context.
- Supporting UI: DashboardController, dashboardService
- API status: `PROVEN`

### Dashboard requests clinic summary

- Trigger: The dashboard requests clinic summary information.
- Steps: Initiate the clinic-summary request.; Retain the response for dashboard presentation.
- Outcome: Clinic summary information is requested for the dashboard.
- Supporting UI: DashboardController, dashboardService
- API status: `UNRESOLVED`

### Dashboard requests yearly expenses

- Trigger: A year-dependent expense report is requested.
- Steps: Use the selected year in a dynamically constructed report address.; Request expense information.
- Outcome: Yearly expense information is requested.
- Supporting UI: DashboardController, dashboardService
- API status: `DYNAMIC`

### Dashboard requests yearly patient report

- Trigger: A year-dependent patient report is requested.
- Steps: Use the selected year in a dynamically constructed report address.; Request patient-report information.
- Outcome: Yearly patient-report information is requested.
- Supporting UI: DashboardController, dashboardService
- API status: `DYNAMIC`

## Business Rules

NO_EVIDENCE_BACKED_BUSINESS_RULES_IDENTIFIED

## Domain Concepts and Information

- The Feature exchanges current tenant context, clinic summary information, yearly expense information, and yearly patient-report information.

## Dependencies

- **TECHNICAL:** Dashboard depends on tenant context API - Dashboard reporting flows require preserved current-tenant integration.
- **TECHNICAL:** Dashboard depends on reports API contract - Dashboard summaries and yearly reports depend on existing reporting contracts.

## API Integration Profile

- PROVEN: 3
- UNRESOLVED: 1
- DYNAMIC: 2
- EXTERNAL: 0
- NO_BACKEND_ROUTE: 0
- `PROVEN`: `src/MyHealth.Web/content/app/components/dashboard/services/dashboardService.js` -> `GET /api/users/current/tenant` -> `GET /api/users/current/tenant`
- `PROVEN`: `src/MyHealth.Web/content/app/components/dashboard/services/dashboardService.js` -> `GET /api/users/current/tenant` -> `GET /api/users/current/tenant`
- `PROVEN`: `src/MyHealth.Web/content/app/components/dashboard/services/dashboardService.js` -> `GET /api/users/current/tenant` -> `GET /api/users/current/tenant`
- `UNRESOLVED`: `src/MyHealth.Web/content/app/components/dashboard/services/dashboardService.js` -> `/api/reports/clinicsummary` -> `GET /api/reports/clinicsummary`
- `DYNAMIC`: `src/MyHealth.Web/content/app/components/dashboard/services/dashboardService.js` -> `'/api/reports/expenses/' + year` -> `GET /api/reports/expenses/{year}`
- `DYNAMIC`: `src/MyHealth.Web/content/app/components/dashboard/services/dashboardService.js` -> `'/api/reports/patients/' + year` -> `GET /api/reports/patients/{year}`
- Limitation: Tenant context is proven, but the clinic-summary link is unresolved and yearly report addresses are dynamic; no endpoint is guessed for those limitations.

## Current User Experience

- A server-rendered Razor Dashboard entry surface hosts an AngularJS client-side dashboard experience.

## Current-State Limitations and Concerns

- **BUSINESS_ANALYSIS_LIMITATION:** Clinic-summary frontend-to-backend resolution is not proven, and two yearly report relationships are dynamic.
- **MODERNIZATION_CONCERN:** The same Feature spans Razor and AngularJS frontend technologies, so migration must preserve one business outcome across both legacy surfaces.

## Modernization Scope

### In Scope

- Dashboard Razor and AngularJS surfaces, seven approved workflows, tenant-context mappings, and reporting contract preservation.

### Out of Scope

- Backend/database redesign, resolution by assumption of unresolved mappings, and modernization of unrelated UI areas.

## Assumptions

- None identified from approved evidence.

## Open Questions

- **Q-DASH-001:** Which dashboard summaries and yearly reports are most important for the initial modernization workshop? Reason: Evidence identifies available flows but not stakeholder priority.
- **Q-DASH-002:** Should the target frontend preserve the current year-dependent report navigation behavior or present those reports inside the new dashboard experience? Reason: The current dynamic URL construction proves behavior but not desired future presentation.
- **Q-DASH-003:** What contract detail is required to validate the unresolved clinic-summary frontend-to-backend relationship before implementation? Reason: The approved Feature retains this relationship as unresolved.

## Risks and Limitations

- **BUSINESS_ANALYSIS_LIMITATION:** Unresolved and dynamic reporting relationships limit complete end-to-end story detail.
- **TECHNICAL_MODERNIZATION_RISK:** Consolidating two legacy frontend technologies can introduce behavior-parity risk if their shared responsibilities are not traced during implementation.

## MODERNIZATION_SUCCESS_INDICATORS

- All seven approved Dashboard workflows remain traceable and available in the target frontend without changing proven API statuses.
- The target Dashboard builds and tests successfully without introducing behavior unsupported by approved evidence.

## STORY_DECOMPOSITION_GUIDANCE

- **Open the operational dashboard:** Separates entry/navigation from data retrieval. Workflows: Route dashboard
- **Load tenant-aware dashboard summaries:** Groups summary behavior and its unresolved report mapping. Workflows: Dashboard summary loads current tenant, Dashboard requests clinic summary
- **Access yearly reporting information:** Groups the year-dependent report behaviors while preserving dynamic status. Workflows: Dashboard expenses load current tenant, Dashboard patient report loads current tenant, Dashboard requests yearly expenses, Dashboard requests yearly patient report

## Technical Traceability

- `src/MyHealth.Web/Views/Dashboard/Index.cshtml:1` -> `legacy-dashboard-complete-application-demo-v1:RazorView:src/MyHealth.Web/Views/Dashboard/Index.cshtml`
- `src/MyHealth.Web/content/app/components/dashboard/controllers/dashboardController.js:1` -> `legacy-dashboard-complete-application-demo-v1:AngularController:DashboardController`
- `src/MyHealth.API/Controllers/ReportsController.cs:23` -> `legacy-dashboard-complete-application-demo-v1:Endpoint:GET /api/reports/clinicsummary`

