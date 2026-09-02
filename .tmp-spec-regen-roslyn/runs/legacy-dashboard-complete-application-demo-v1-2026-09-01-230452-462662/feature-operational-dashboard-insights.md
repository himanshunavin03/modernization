# feature-operational-dashboard-insights — Operational Dashboard Insights

## 1. Feature Summary

### Purpose

Provide access to dashboard summaries and clinic reporting information in the current tenant context.

### Current Business Capability

The current application requests expense and patient reporting information for a selected year. The dashboard summary flow has current tenant context. Clinic summary information is requested for the dashboard. Users can open the established operational dashboard experience.

### Business Value

Makes the established year-dependent reporting capability available to users. Preserves tenant-aware access to the established dashboard summary information. Specific stakeholder outcomes for one or more access capabilities are not established and require confirmation.

**Business Value Status:** Requires Stakeholder Enrichment.

### Modernization Objective

Preserve the approved dashboard workflows and API contracts while consolidating the Razor-hosted and AngularJS frontend surfaces into the target frontend.

## 2. Functional Behavior

### Access Yearly Operational Reports

The current application requests expense and patient reporting information for a selected year.

### View Tenant-Aware Dashboard Summary

The dashboard summary flow has current tenant context. Clinic summary information is requested for the dashboard.

### Open Operational Dashboard

Users can open the established operational dashboard experience.

The available requirements establish a general application user; no more specific business persona is authoritative.

**Feature Name / Behavior Alignment:** Aligned.

## 3. Scope

### In Scope

- Dashboard Razor and AngularJS surfaces, seven approved workflows, tenant-context mappings, and reporting contract preservation.

### Not Established by Current Evidence

- Backend/database redesign, resolution by assumption of unresolved mappings, and modernization of unrelated UI areas.

## 4. User Stories & Acceptance Criteria

### STORY-OPERATIONAL-DASHBOARD-INSIGHTS-ACCESS-YEARLY-OPERATIONAL-REPORTS — Access Yearly Operational Reports

**Story**

As an application user,

I want to access year-dependent expense and patient reporting information,

so that the established reporting information remains available for the selected year.

**Business Context**

Represents the approved yearly expense and patient-report interactions while retaining their dynamic URL status.

**Business Value Status:** Supported Interpretation.

#### Acceptance Criteria

##### AC-OPERATIONAL-DASHBOARD-INSIGHTS-ACCESS-YEARLY-OPERATIONAL-REPORTS-001 — Access Yearly Operational Reports Behavior

**Quality Status:** Testable With Evidence Limitation.

**Given** The expense-reporting flow needs clinic context

**When** the user accesses year-dependent expense and patient reporting information

**Then** the expense-reporting flow has current tenant context; and the patient-reporting flow has current tenant context; and yearly expense information is requested; and yearly patient-report information is requested.

**Evidence Limitation**

Current evidence does not establish a complete customer-approved definition of the information or presentation details that must be retained.

**Current Backend Contract References**

- `API-OPERATIONAL_DASHBOARD_INSIGHTS-001`
- `API-OPERATIONAL_DASHBOARD_INSIGHTS-002`
- `API-OPERATIONAL_DASHBOARD_INSIGHTS-003`

### STORY-OPERATIONAL-DASHBOARD-INSIGHTS-VIEW-TENANT-AWARE-DASHBOARD-SUMMARY — View Tenant-Aware Dashboard Summary

**Story**

As an application user,

I want to access dashboard summary information in current tenant context,

so that the established dashboard summary information remains associated with current tenant context.

**Business Context**

Represents tenant-context retrieval and clinic-summary request behavior as one dashboard summary interaction.

**Business Value Status:** Supported Interpretation.

#### Acceptance Criteria

##### AC-OPERATIONAL-DASHBOARD-INSIGHTS-VIEW-TENANT-AWARE-DASHBOARD-SUMMARY-001 — View Tenant-Aware Dashboard Summary Behavior

**Quality Status:** Testable With Evidence Limitation.

**Given** The dashboard summary flow needs clinic context

**When** the user accesses dashboard summary information in current tenant context

**Then** the dashboard summary flow has current tenant context; and clinic summary information is requested for the dashboard.

**Evidence Limitation**

Current evidence does not establish a complete customer-approved definition of the information or presentation details that must be retained.

#### Modernization Preservation Requirement

**AC-OPERATIONAL-DASHBOARD-INSIGHTS-VIEW-TENANT-AWARE-DASHBOARD-SUMMARY-002 — View Tenant-Aware Dashboard Summary Preservation**

the approved current-state behavior remains available without changing the evidenced backend relationship status.

**Current Backend Contract References**

- `API-OPERATIONAL_DASHBOARD_INSIGHTS-001`
- `API-OPERATIONAL_DASHBOARD_INSIGHTS-004`

### STORY-OPERATIONAL-DASHBOARD-INSIGHTS-OPEN-OPERATIONAL-DASHBOARD — Open Operational Dashboard

**Story**

As an application user,

I want to open the existing operational dashboard experience.

Business outcome: Requires stakeholder confirmation; current evidence establishes the capability but not its specific business purpose.

**Business Context**

Represents entry into the operational Dashboard across its Razor host and AngularJS client surface.

**Business Value Status:** Not Established.

#### Acceptance Criteria

##### AC-OPERATIONAL-DASHBOARD-INSIGHTS-OPEN-OPERATIONAL-DASHBOARD-001 — Open Operational Dashboard Behavior

**Quality Status:** Testable With Evidence Limitation.

**Given** Dashboard navigation is initiated

**When** the user opens the existing operational dashboard experience

**Then** the user can access the established operational dashboard experience.

**Evidence Limitation**

Current evidence does not establish a complete customer-approved definition of the information or presentation details that must be retained.

#### Modernization Preservation Requirement

**AC-OPERATIONAL-DASHBOARD-INSIGHTS-OPEN-OPERATIONAL-DASHBOARD-002 — Open Operational Dashboard Preservation**

the approved current-state behavior remains available without changing the evidenced backend relationship status.

## 5. Existing Backend Integration

Confirmed existing backend API contracts are preserved integration boundaries for the target frontend unless an explicitly approved change modifies them.

### Primary Business APIs

#### API-OPERATIONAL_DASHBOARD_INSIGHTS-002 — '/api/reports/expenses/' + year

**Role in this Feature:** Primary Business Api.

**Current Frontend:** `src/MyHealth.Web/content/app/components/dashboard/services/dashboardService.js` calls `GET '/api/reports/expenses/' + year`.

**Confirmed Backend:** `GET /api/reports/expenses/{year}` implemented by `ReportsController.GetExpensesSummaryAsync`.

#### API-OPERATIONAL_DASHBOARD_INSIGHTS-003 — '/api/reports/patients/' + year

**Role in this Feature:** Primary Business Api.

**Current Frontend:** `src/MyHealth.Web/content/app/components/dashboard/services/dashboardService.js` calls `GET '/api/reports/patients/' + year`.

**Confirmed Backend:** `GET /api/reports/patients/{year}` implemented by `ReportsController.GetPatientsSummaryAsync`.

#### API-OPERATIONAL_DASHBOARD_INSIGHTS-004 — /api/reports/clinicsummary

**Role in this Feature:** Primary Business Api.

**Current Frontend:** `src/MyHealth.Web/content/app/components/dashboard/services/dashboardService.js` calls `GET /api/reports/clinicsummary`.

**Confirmed Backend:** `GET /api/reports/clinicsummary` implemented by `ReportsController.GetClinicSummaryAsync`.

### Supporting / Shared APIs

#### API-OPERATIONAL_DASHBOARD_INSIGHTS-001 — /api/users/current/tenant

**Role in this Feature:** Supporting Shared Api.

**Current Frontend:** `src/MyHealth.Web/content/app/components/dashboard/services/dashboardService.js` calls `GET /api/users/current/tenant`.

**Confirmed Backend:** `GET /api/users/current/tenant` implemented by `UsersController.GetCurrentTenantAsync`.

This contract supplies shared context only; it does not provide the Feature's primary business data.

## 6. Modernization Considerations

### Current Implementation Context

Relevant legacy surfaces: DashboardController, dashboard, dashboardService, src/MyHealth.Web/Views/Dashboard/Index.cshtml

### Preservation Requirements

- Preserve this approved business behavior during frontend modernization without changing backend contracts.

**Target Design:** Not yet analyzed.

**Target Architecture:** Pending.

## 7. Decisions Required Before Modernization

### Business Clarifications

| Question | Why It Matters | Impact | Owner |
| --- | --- | --- | --- |
| What business outcome should users achieve through Open Operational Dashboard beyond access to the currently established capability? | Current evidence establishes the behavior but not the stakeholder's intended business outcome. | NON_BLOCKING | Product Owner / Business Analyst / Customer SME |
| Which information must be considered mandatory when validating Access Yearly Operational Reports in the modernized experience? | Current evidence does not establish a complete customer-approved definition of the information or presentation details that must be retained. | BLOCKING | Product Owner / Business Analyst / Customer SME / QA Lead |
| Which information must be considered mandatory when validating Open Operational Dashboard in the modernized experience? | Current evidence does not establish a complete customer-approved definition of the information or presentation details that must be retained. | BLOCKING | Product Owner / Business Analyst / Customer SME / QA Lead |
| Which information must be considered mandatory when validating View Tenant-Aware Dashboard Summary in the modernized experience? | Current evidence does not establish a complete customer-approved definition of the information or presentation details that must be retained. | BLOCKING | Product Owner / Business Analyst / Customer SME / QA Lead |

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
