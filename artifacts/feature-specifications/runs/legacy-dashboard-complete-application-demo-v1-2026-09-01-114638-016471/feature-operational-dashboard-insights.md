# feature-operational-dashboard-insights — Operational Dashboard Insights

## 1. Feature Overview

Presents clinic-context operational summaries and yearly reporting through the legacy Dashboard experience.

**Purpose:** Provide access to dashboard summaries and clinic reporting information in the current tenant context.

**Modernization relevance:** Preserve the approved dashboard workflows and API contracts while consolidating the Razor-hosted and AngularJS frontend surfaces into the target frontend.

## 2. Business Objective

Provide access to dashboard summaries and clinic reporting information in the current tenant context.

## 3. Business Value

- The Feature appears to support operational visibility by bringing clinic summary and yearly reporting information into one dashboard experience.

## 4. Current Business Behavior

- The Dashboard experience is available.
- The dashboard summary flow has current tenant context.
- The expense-reporting flow has current tenant context.
- The patient-reporting flow has current tenant context.
- Clinic summary information is requested for the dashboard.
- Yearly expense information is requested.
- Yearly patient-report information is requested.

## 5. Users / Actors

The existing evidence identifies a general application user but does not establish a more specific business persona for this Feature.

## 6. Functional Scope

### In Scope

- Dashboard Razor and AngularJS surfaces, seven approved workflows, tenant-context mappings, and reporting contract preservation.

### Out of Scope

- Backend/database redesign, resolution by assumption of unresolved mappings, and modernization of unrelated UI areas.

## 7. Business Workflows

### Route dashboard

**Trigger:** Dashboard navigation is initiated.

**Interaction:** Resolve the Dashboard route.; Present the approved dashboard UI surface.

**Observable outcome:** The Dashboard experience is available.

### Dashboard summary loads current tenant

**Trigger:** The dashboard summary flow needs clinic context.

**Interaction:** Request current tenant context.; Make tenant context available to the summary flow.

**Observable outcome:** The dashboard summary flow has current tenant context.

### Dashboard expenses load current tenant

**Trigger:** The expense-reporting flow needs clinic context.

**Interaction:** Request current tenant context.; Make tenant context available to expense reporting.

**Observable outcome:** The expense-reporting flow has current tenant context.

### Dashboard patient report loads current tenant

**Trigger:** The patient-reporting flow needs clinic context.

**Interaction:** Request current tenant context.; Make tenant context available to patient reporting.

**Observable outcome:** The patient-reporting flow has current tenant context.

### Dashboard requests clinic summary

**Trigger:** The dashboard requests clinic summary information.

**Interaction:** Initiate the clinic-summary request.; Retain the response for dashboard presentation.

**Observable outcome:** Clinic summary information is requested for the dashboard.

### Dashboard requests yearly expenses

**Trigger:** A year-dependent expense report is requested.

**Interaction:** Use the selected year in a dynamically constructed report address.; Request expense information.

**Observable outcome:** Yearly expense information is requested.

### Dashboard requests yearly patient report

**Trigger:** A year-dependent patient report is requested.

**Interaction:** Use the selected year in a dynamically constructed report address.; Request patient-report information.

**Observable outcome:** Yearly patient-report information is requested.

## 8. Business Rules

No additional Feature-specific Business Rule has been established from the current approved application evidence.

## 9. Data / Information Requirements

No additional named domain information concept has been established for this Feature.

## 10. User Experience

### Current Experience

- A server-rendered Razor Dashboard entry surface hosts an AngularJS client-side dashboard experience.

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

### story-operational-dashboard-insights-access-yearly-operational-reports — Access Yearly Operational Reports

**Story**

As a user of the existing application, I want access year-dependent expense and patient reporting information, so that I can access the supported behavior in the existing experience.

#### Description

Represents the approved yearly expense and patient-report interactions while retaining their dynamic URL status.

#### Business Context

This Story implements the approved workflow boundary: Access yearly reporting information.

#### Current Behavior

The existing application supports: The expense-reporting flow has current tenant context. The patient-reporting flow has current tenant context. Yearly expense information is requested. Yearly patient-report information is requested.

## 13. Acceptance Criteria

### ac-operational-dashboard-insights-access-yearly-operational-reports-001 — Access Yearly Operational Reports Behavior

**Given** the approved current-state context for access yearly reporting information is available

**When** access year-dependent expense and patient reporting information

**Then** The existing application supports: The expense-reporting flow has current tenant context. The patient-reporting flow has current tenant context. Yearly expense information is requested. Yearly patient-report information is requested.

### story-operational-dashboard-insights-view-tenant-aware-dashboard-summary — View Tenant-Aware Dashboard Summary

**Story**

As a user of the existing application, I want access dashboard summary information in current tenant context, so that I can access the supported behavior in the existing experience.

#### Description

Represents tenant-context retrieval and clinic-summary request behavior as one dashboard summary interaction.

#### Business Context

This Story implements the approved workflow boundary: Load tenant-aware dashboard summaries.

#### Current Behavior

The existing application supports: The dashboard summary flow has current tenant context. Clinic summary information is requested for the dashboard.

## 13. Acceptance Criteria

### ac-operational-dashboard-insights-view-tenant-aware-dashboard-summary-001 — View Tenant-Aware Dashboard Summary Behavior

**Given** the approved current-state context for load tenant-aware dashboard summaries is available

**When** access dashboard summary information in current tenant context

**Then** The existing application supports: The dashboard summary flow has current tenant context. Clinic summary information is requested for the dashboard.

### ac-operational-dashboard-insights-view-tenant-aware-dashboard-summary-002 — View Tenant-Aware Dashboard Summary Preservation

**Given** the approved current-state behavior and evidence limitations are used as the modernization baseline

**When** the frontend experience is modernized

**Then** the approved current-state behavior remains available without changing the evidenced backend relationship status

### story-operational-dashboard-insights-open-operational-dashboard — Open Operational Dashboard

**Story**

As a user of the existing application, I want open the existing operational dashboard experience, so that I can access the supported behavior in the existing experience.

#### Description

Represents entry into the operational Dashboard across its Razor host and AngularJS client surface.

#### Business Context

This Story implements the approved workflow boundary: Open the operational dashboard.

#### Current Behavior

The existing application supports: The Dashboard experience is available.

## 13. Acceptance Criteria

### ac-operational-dashboard-insights-open-operational-dashboard-001 — Open Operational Dashboard Behavior

**Given** the approved current-state context for open the operational dashboard is available

**When** open the existing operational dashboard experience

**Then** The existing application supports: The Dashboard experience is available.

### ac-operational-dashboard-insights-open-operational-dashboard-002 — Open Operational Dashboard Preservation

**Given** the approved current-state behavior and evidence limitations are used as the modernization baseline

**When** the frontend experience is modernized

**Then** the approved current-state behavior remains available without changing the evidenced backend relationship status

## 14. Functional Requirements Summary

- `ac-operational-dashboard-insights-access-yearly-operational-reports-001`: The existing application supports: The expense-reporting flow has current tenant context. The patient-reporting flow has current tenant context. Yearly expense information is requested. Yearly patient-report information is requested.
- `ac-operational-dashboard-insights-open-operational-dashboard-001`: The existing application supports: The Dashboard experience is available.
- `ac-operational-dashboard-insights-open-operational-dashboard-002`: The evidenced behavior remains available and unresolved relationships remain unresolved.
- `ac-operational-dashboard-insights-view-tenant-aware-dashboard-summary-001`: The existing application supports: The dashboard summary flow has current tenant context. Clinic summary information is requested for the dashboard.
- `ac-operational-dashboard-insights-view-tenant-aware-dashboard-summary-002`: The evidenced behavior remains available and unresolved relationships remain unresolved.

## 15. Integration / API Requirements

- Dashboard expenses load current tenant: Established relationship must be preserved.
- Dashboard patient report loads current tenant: Established relationship must be preserved.
- Dashboard requests yearly expenses: Backend integration details require confirmation before implementation.
- Dashboard requests yearly patient report: Backend integration details require confirmation before implementation.
- Dashboard summary loads current tenant: Established relationship must be preserved.
- Dashboard requests clinic summary: Backend integration details require confirmation before implementation.

## 16. Data Dependencies

- **Dashboard depends on tenant context API:** Dashboard reporting flows require preserved current-tenant integration.
- **Dashboard depends on reports API contract:** Dashboard summaries and yearly reports depend on existing reporting contracts.

## 17. Security and Access

Feature-specific access and authorization requirements will be confirmed during architecture and stakeholder validation.

## 18. Modernization Requirements

- Preserve this approved business behavior during frontend modernization without changing backend contracts.

## 19. Legacy-to-Target Mapping

### Legacy Side

- DashboardController
- dashboard
- dashboardService
- src/MyHealth.Web/Views/Dashboard/Index.cshtml

### Target Side

Target implementation mapping will be completed after Target Design and Target Architecture are approved.

## 20. Architecture Considerations

- The same Feature spans Razor and AngularJS frontend technologies, so migration must preserve one business outcome across both legacy surfaces.
- Clinic-summary frontend-to-backend resolution is not proven, and two yearly report relationships are dynamic.

These are architecture inputs, not architecture decisions.

## 21. Non-Functional Requirements

Feature-specific non-functional requirements have not yet been approved. Performance, accessibility, security, observability and related quality attributes will be addressed during Target Architecture and stakeholder review.

## 22. Open Business / Architecture Decisions

- **Question:** Which dashboard summaries and yearly reports are most important for the initial modernization workshop? **Why it matters:** Evidence identifies available flows but not stakeholder priority. **Validation:** Product Owner / Business Analyst / Customer SME
- **Question:** Should the target frontend preserve the current year-dependent report navigation behavior or present those reports inside the new dashboard experience? **Why it matters:** The current dynamic URL construction proves behavior but not desired future presentation. **Validation:** Product Owner / Business Analyst / Customer SME
- **Question:** What contract detail is required to validate the unresolved clinic-summary frontend-to-backend relationship before implementation? **Why it matters:** The approved Feature retains this relationship as unresolved. **Validation:** Product Owner / Business Analyst / Customer SME

## 23. Risks and Constraints

- Unresolved and dynamic reporting relationships limit complete end-to-end story detail.
- Consolidating two legacy frontend technologies can introduce behavior-parity risk if their shared responsibilities are not traced during implementation.

## 24. Dependencies

- Dashboard depends on tenant context API
- Dashboard depends on reports API contract

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

- Story IDs: story-operational-dashboard-insights-access-yearly-operational-reports, story-operational-dashboard-insights-view-tenant-aware-dashboard-summary, story-operational-dashboard-insights-open-operational-dashboard
- Acceptance Criteria IDs: ac-operational-dashboard-insights-access-yearly-operational-reports-001, ac-operational-dashboard-insights-open-operational-dashboard-001, ac-operational-dashboard-insights-open-operational-dashboard-002, ac-operational-dashboard-insights-view-tenant-aware-dashboard-summary-001, ac-operational-dashboard-insights-view-tenant-aware-dashboard-summary-002
- Legacy surfaces: DashboardController, dashboard, dashboardService, src/MyHealth.Web/Views/Dashboard/Index.cshtml
