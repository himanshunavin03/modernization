# feature-operational-dashboard-insights — Operational Dashboard Insights

## 1. Feature Summary

Presents clinic-context operational summaries and yearly reporting through the legacy Dashboard experience.

The Feature appears to support operational visibility by bringing clinic summary and yearly reporting information into one dashboard experience.

The Feature provides the business interactions described below through the current application.

Preserve the approved dashboard workflows and API contracts while consolidating the Razor-hosted and AngularJS frontend surfaces into the target frontend.

## 2. Functional Behavior

### Access Yearly Operational Reports

The expense-reporting flow has current tenant context. The patient-reporting flow has current tenant context. Yearly expense information is requested. Yearly patient-report information is requested.

### View Tenant-Aware Dashboard Summary

The dashboard summary flow has current tenant context. Clinic summary information is requested for the dashboard.

### Open Operational Dashboard

The Dashboard experience is available.

The current requirements establish a general application user; a more specific business persona has not yet been approved.

## 3. Scope

### In Scope

- Dashboard Razor and AngularJS surfaces, seven approved workflows, tenant-context mappings, and reporting contract preservation.

### Out of Scope

- Backend/database redesign, resolution by assumption of unresolved mappings, and modernization of unrelated UI areas.

## 4. User Stories & Acceptance Criteria

### STORY-OPERATIONAL-DASHBOARD-INSIGHTS-ACCESS-YEARLY-OPERATIONAL-REPORTS — Access Yearly Operational Reports

**Story**

As an application user,  
I want to access year-dependent expense and patient reporting information,  
so that the expense-reporting flow has current tenant context. The patient-reporting flow has current tenant context. Yearly expense information is requested. Yearly patient-report information is requested.

**Business Context**

Represents the approved yearly expense and patient-report interactions while retaining their dynamic URL status.

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
so that I can use open operational dashboard.

**Business Context**

Represents entry into the operational Dashboard across its Razor host and AngularJS client surface.

#### Acceptance Criteria

##### AC-OPERATIONAL-DASHBOARD-INSIGHTS-OPEN-OPERATIONAL-DASHBOARD-001 — Open Operational Dashboard Behavior

**Given** Dashboard navigation is initiated.  
**When** Open the existing operational dashboard experience  
**Then** The Dashboard experience is available.

##### AC-OPERATIONAL-DASHBOARD-INSIGHTS-OPEN-OPERATIONAL-DASHBOARD-002 — Open Operational Dashboard Preservation

**Given** Dashboard navigation is initiated.  
**When** Open the existing operational dashboard experience  
**Then** The evidenced behavior remains available and unresolved relationships remain unresolved.

## 5. Integration & Data Context

### Dashboard expenses load current tenant

Established relationship must be preserved.

### Dashboard patient report loads current tenant

Established relationship must be preserved.

### Dashboard requests yearly expenses

The existing backend service for this interaction must be confirmed before modernization.

### Dashboard requests yearly patient report

The existing backend service for this interaction must be confirmed before modernization.

### Dashboard summary loads current tenant

Established relationship must be preserved.

### Dashboard requests clinic summary

The existing backend service for this interaction must be confirmed before modernization.


## 6. Modernization Considerations

### Current Implementation Context

Relevant legacy surfaces: DashboardController, dashboard, dashboardService, src/MyHealth.Web/Views/Dashboard/Index.cshtml

### Preservation Requirements

- Preserve this approved business behavior during frontend modernization without changing backend contracts.

**Target Design:** Not yet analyzed. If a Figma design is supplied later, it will be mapped to approved Feature behavior, Stories, and Acceptance Criteria.

**Target Architecture:** Pending.

## 7. Decisions Required Before Modernization

| Decision / Question | Why It Matters | Validation Role | Status |
| --- | --- | --- | --- |
| Which dashboard summaries and yearly reports are most important for the initial modernization workshop? | Evidence identifies available flows but not stakeholder priority. | Product Owner / Business Analyst / Customer SME | Pending |
| Should the target frontend preserve the current year-dependent report navigation behavior or present those reports inside the new dashboard experience? | The current dynamic URL construction proves behavior but not desired future presentation. | Product Owner / Business Analyst / Customer SME | Pending |
| What contract detail is required to validate the unresolved clinic-summary frontend-to-backend relationship before implementation? | The approved Feature retains this relationship as unresolved. | Product Owner / Business Analyst / Customer SME | Pending |

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

- Story IDs: story-operational-dashboard-insights-access-yearly-operational-reports, story-operational-dashboard-insights-view-tenant-aware-dashboard-summary, story-operational-dashboard-insights-open-operational-dashboard
- Acceptance Criteria IDs: ac-operational-dashboard-insights-access-yearly-operational-reports-001, ac-operational-dashboard-insights-view-tenant-aware-dashboard-summary-001, ac-operational-dashboard-insights-view-tenant-aware-dashboard-summary-002, ac-operational-dashboard-insights-open-operational-dashboard-001, ac-operational-dashboard-insights-open-operational-dashboard-002
- Source references: src/MyHealth.API/Controllers/ReportsController.cs, src/MyHealth.Web/Views/Dashboard/Index.cshtml, src/MyHealth.Web/content/app/components/dashboard/controllers/dashboardController.js
