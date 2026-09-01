# feature-operational-dashboard-insights — Operational Dashboard Insights

## Stakeholder Summary

| Item | Details |
| --- | --- |
| Feature | Operational Dashboard Insights |
| Business capability | Provide access to dashboard summaries and clinic reporting information in the current tenant context. |
| Stories | 3 |
| Acceptance Criteria | 5 |
| Target Design | Not Yet Analyzed |
| Target Architecture | Pending |
| Modernization | Not Started |
| Stakeholder Review | Pending |

## Feature Overview

Presents clinic-context operational summaries and yearly reporting through the legacy Dashboard experience.

Existing application behavior represented by approved workflows and Stories.

## Business Objective

Provide access to dashboard summaries and clinic reporting information in the current tenant context.

## Business Value

- The Feature appears to support operational visibility by bringing clinic summary and yearly reporting information into one dashboard experience.

## Current Business Behavior

### Open Operational Dashboard

**Trigger:** Dashboard navigation is initiated.

**Interaction:** Resolve the Dashboard route; Present the approved dashboard UI surface.

**Outcome:** The Dashboard experience is available.

### Dashboard summary loads current tenant

**Trigger:** The dashboard summary flow needs clinic context.

**Interaction:** Request current tenant context; Make tenant context available to the summary flow.

**Outcome:** The dashboard summary flow has current tenant context.

### Dashboard expenses load current tenant

**Trigger:** The expense-reporting flow needs clinic context.

**Interaction:** Request current tenant context; Make tenant context available to expense reporting.

**Outcome:** The expense-reporting flow has current tenant context.

### Dashboard patient report loads current tenant

**Trigger:** The patient-reporting flow needs clinic context.

**Interaction:** Request current tenant context; Make tenant context available to patient reporting.

**Outcome:** The patient-reporting flow has current tenant context.

### Dashboard requests clinic summary

**Trigger:** The dashboard requests clinic summary information.

**Interaction:** Initiate the clinic-summary request; Retain the response for dashboard presentation.

**Outcome:** Clinic summary information is requested for the dashboard.

### Dashboard requests yearly expenses

**Trigger:** A year-dependent expense report is requested.

**Interaction:** Use the selected year in a dynamically constructed report address; Request expense information.

**Outcome:** Yearly expense information is requested.

### Dashboard requests yearly patient report

**Trigger:** A year-dependent patient report is requested.

**Interaction:** Use the selected year in a dynamically constructed report address; Request patient-report information.

**Outcome:** Yearly patient-report information is requested.

## Users and Actors

Current evidence establishes a general application user for this Feature. A more specific business persona has not yet been approved.

## Functional Scope

### In Scope

- Dashboard Razor and AngularJS surfaces, seven approved workflows, tenant-context mappings, and reporting contract preservation.

### Out of Scope

- Backend/database redesign, resolution by assumption of unresolved mappings, and modernization of unrelated UI areas.

## Business Rules

No additional Feature-specific business rule has been established from the current application behavior.

## Data and Information

No additional named business-information concept is required for this Feature contract.

## User Experience

### Current Experience

- A server-rendered Razor Dashboard entry surface hosts an AngularJS client-side dashboard experience.

### Target Experience

No target design has been analyzed for this Feature. If a Figma design is supplied, Polaris will map relevant screens and components to the approved Stories and Acceptance Criteria before architecture and implementation. It will not redefine approved business behavior.

## User Stories and Acceptance Criteria

### STORY-OPERATIONAL-DASHBOARD-INSIGHTS-ACCESS-YEARLY-OPERATIONAL-REPORTS — Access Yearly Operational Reports

**Story**

As an application user,  
I want to access year-dependent expense and patient reporting information,  
so that the expense-reporting flow has current tenant context. The patient-reporting flow has current tenant context. Yearly expense information is requested. Yearly patient-report information is requested.

**Business Context**

Represents the approved yearly expense and patient-report interactions while retaining their dynamic URL status.

**Current Behavior**

The existing application supports: The expense-reporting flow has current tenant context. The patient-reporting flow has current tenant context. Yearly expense information is requested. Yearly patient-report information is requested.

#### Acceptance Criteria

##### AC-OPERATIONAL-DASHBOARD-INSIGHTS-ACCESS-YEARLY-OPERATIONAL-REPORTS-001 — Access Yearly Operational Reports Behavior

**Given** The expense-reporting flow needs clinic context.  
**When** Access year-dependent expense and patient reporting information  
**Then** The expense-reporting flow has current tenant context. The patient-reporting flow has current tenant context. Yearly expense information is requested. Yearly patient-report information is requested.

### STORY-OPERATIONAL-DASHBOARD-INSIGHTS-VIEW-TENANT-AWARE-DASHBOARD-SUMMARY — View Tenant-Aware Dashboard Summary

**Story**

As an application user,  
I want to access dashboard summary information in current tenant context,  
so that the dashboard summary flow has current tenant context. Clinic summary information is requested for the dashboard.

**Business Context**

Represents tenant-context retrieval and clinic-summary request behavior as one dashboard summary interaction.

**Current Behavior**

The existing application supports: The dashboard summary flow has current tenant context. Clinic summary information is requested for the dashboard.

#### Acceptance Criteria

##### AC-OPERATIONAL-DASHBOARD-INSIGHTS-VIEW-TENANT-AWARE-DASHBOARD-SUMMARY-001 — View Tenant-Aware Dashboard Summary Behavior

**Given** The dashboard summary flow needs clinic context.  
**When** Access dashboard summary information in current tenant context  
**Then** The dashboard summary flow has current tenant context. Clinic summary information is requested for the dashboard.

##### AC-OPERATIONAL-DASHBOARD-INSIGHTS-VIEW-TENANT-AWARE-DASHBOARD-SUMMARY-002 — View Tenant-Aware Dashboard Summary Preservation

**Given** The dashboard summary flow needs clinic context.  
**When** Access dashboard summary information in current tenant context  
**Then** The evidenced behavior remains available and unresolved relationships remain unresolved.

### STORY-OPERATIONAL-DASHBOARD-INSIGHTS-OPEN-OPERATIONAL-DASHBOARD — Open Operational Dashboard

**Story**

As an application user,  
I want to open the existing operational dashboard experience,  
so that the Dashboard experience is available.

**Business Context**

Represents entry into the operational Dashboard across its Razor host and AngularJS client surface.

**Current Behavior**

The existing application supports: The Dashboard experience is available.

#### Acceptance Criteria

##### AC-OPERATIONAL-DASHBOARD-INSIGHTS-OPEN-OPERATIONAL-DASHBOARD-001 — Open Operational Dashboard Behavior

**Given** Dashboard navigation is initiated.  
**When** Open the existing operational dashboard experience  
**Then** The Dashboard experience is available.

##### AC-OPERATIONAL-DASHBOARD-INSIGHTS-OPEN-OPERATIONAL-DASHBOARD-002 — Open Operational Dashboard Preservation

**Given** Dashboard navigation is initiated.  
**When** Open the existing operational dashboard experience  
**Then** The evidenced behavior remains available and unresolved relationships remain unresolved.

## Integration and Data Context

- **Dashboard expenses load current tenant:** Established relationship must be preserved.
- **Dashboard patient report loads current tenant:** Established relationship must be preserved.
- **Dashboard requests yearly expenses:** The responsible backend service must be confirmed before this interaction is implemented.
- **Dashboard requests yearly patient report:** The responsible backend service must be confirmed before this interaction is implemented.
- **Dashboard summary loads current tenant:** Established relationship must be preserved.
- **Dashboard requests clinic summary:** The responsible backend service must be confirmed before this interaction is implemented.

## Architecture Inputs

- The same Feature spans Razor and AngularJS frontend technologies, so migration must preserve one business outcome across both legacy surfaces.
- Clinic-summary frontend-to-backend resolution is not proven, and two yearly report relationships are dynamic.

Target Architecture is pending. These facts are inputs for that decision and do not prescribe an implementation approach.

## Open Decisions

### Which dashboard summaries and yearly reports are most important for the initial modernization workshop?

Evidence identifies available flows but not stakeholder priority.

**Validation role:** Product Owner / Business Analyst / Customer SME
### Should the target frontend preserve the current year-dependent report navigation behavior or present those reports inside the new dashboard experience?

The current dynamic URL construction proves behavior but not desired future presentation.

**Validation role:** Product Owner / Business Analyst / Customer SME
### What contract detail is required to validate the unresolved clinic-summary frontend-to-backend relationship before implementation?

The approved Feature retains this relationship as unresolved.

**Validation role:** Product Owner / Business Analyst / Customer SME

## Risks and Constraints

- Unresolved and dynamic reporting relationships limit complete end-to-end story detail.
- Consolidating two legacy frontend technologies can introduce behavior-parity risk if their shared responsibilities are not traced during implementation.

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

- Story IDs: story-operational-dashboard-insights-access-yearly-operational-reports, story-operational-dashboard-insights-view-tenant-aware-dashboard-summary, story-operational-dashboard-insights-open-operational-dashboard
- Acceptance Criteria IDs: ac-operational-dashboard-insights-access-yearly-operational-reports-001, ac-operational-dashboard-insights-open-operational-dashboard-001, ac-operational-dashboard-insights-open-operational-dashboard-002, ac-operational-dashboard-insights-view-tenant-aware-dashboard-summary-001, ac-operational-dashboard-insights-view-tenant-aware-dashboard-summary-002
- Legacy surfaces: DashboardController, dashboard, dashboardService, src/MyHealth.Web/Views/Dashboard/Index.cshtml
