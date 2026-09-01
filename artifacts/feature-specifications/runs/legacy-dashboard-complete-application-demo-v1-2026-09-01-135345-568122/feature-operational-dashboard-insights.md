# feature-operational-dashboard-insights — Operational Dashboard Insights

## 1. Feature Summary

**Purpose**

Users can access year-dependent expense and patient reporting information. Users can access dashboard summary information in current tenant context. Users can open the existing operational dashboard experience.

**Business Value**

The Feature appears to support operational visibility by bringing clinic summary and yearly reporting information into one dashboard experience.

**Current State**

The current implementation uses DashboardController, dashboard, dashboardService, src/MyHealth.Web/Views/Dashboard/Index.cshtml.

**Modernization Objective**

Preserve the approved dashboard workflows and API contracts while consolidating the Razor-hosted and AngularJS frontend surfaces into the target frontend.

## 2. Functional Behavior

### Access Yearly Operational Reports

Users can access year-dependent expense and patient reporting information.

### View Tenant-Aware Dashboard Summary

Users can access dashboard summary information in current tenant context.

### Open Operational Dashboard

Users can open the existing operational dashboard experience.

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

so that the application can present the supported year-dependent expense and patient reporting information.

**Business Context**

Represents the approved yearly expense and patient-report interactions while retaining their dynamic URL status.

#### Acceptance Criteria

##### AC-OPERATIONAL-DASHBOARD-INSIGHTS-ACCESS-YEARLY-OPERATIONAL-REPORTS-001 — Access Yearly Operational Reports Behavior

**Criterion Type:** Functional Acceptance Criterion

**Given** the expense-reporting flow needs clinic context

**When** the user accesses yearly reporting information

**Then** users can access year-dependent expense and patient reporting information

**Current Backend Contract References**

- `API-OPERATIONAL_DASHBOARD_INSIGHTS-001`
- `API-OPERATIONAL_DASHBOARD_INSIGHTS-002`
- `API-OPERATIONAL_DASHBOARD_INSIGHTS-003`

### STORY-OPERATIONAL-DASHBOARD-INSIGHTS-VIEW-TENANT-AWARE-DASHBOARD-SUMMARY — View Tenant-Aware Dashboard Summary

**Story**

As an application user,

I want to access dashboard summary information in current tenant context,

so that the application can present the supported dashboard summary information in current tenant context.

**Business Context**

Represents tenant-context retrieval and clinic-summary request behavior as one dashboard summary interaction.

#### Acceptance Criteria

##### AC-OPERATIONAL-DASHBOARD-INSIGHTS-VIEW-TENANT-AWARE-DASHBOARD-SUMMARY-001 — View Tenant-Aware Dashboard Summary Behavior

**Criterion Type:** Functional Acceptance Criterion

**Given** the dashboard summary flow needs clinic context

**When** the application loads tenant-aware dashboard summaries

**Then** users can access dashboard summary information in current tenant context

##### AC-OPERATIONAL-DASHBOARD-INSIGHTS-VIEW-TENANT-AWARE-DASHBOARD-SUMMARY-002 — View Tenant-Aware Dashboard Summary Preservation

**Criterion Type:** Modernization Preservation Criterion

**Given** the dashboard summary flow needs clinic context

**When** the application preserves approved behavior independently of legacy implementation technology

**Then** the approved behavior remains available, and unresolved relationships remain unresolved

**Current Backend Contract References**

- `API-OPERATIONAL_DASHBOARD_INSIGHTS-001`
- `API-OPERATIONAL_DASHBOARD_INSIGHTS-004`

### STORY-OPERATIONAL-DASHBOARD-INSIGHTS-OPEN-OPERATIONAL-DASHBOARD — Open Operational Dashboard

**Story**

As an application user,

I want to open the existing operational dashboard experience,

so that I can reach the supported behavior within the operational dashboard experience.

**Business Context**

Represents entry into the operational Dashboard across its Razor host and AngularJS client surface.

#### Acceptance Criteria

##### AC-OPERATIONAL-DASHBOARD-INSIGHTS-OPEN-OPERATIONAL-DASHBOARD-001 — Open Operational Dashboard Behavior

**Criterion Type:** Functional Acceptance Criterion

**Given** dashboard navigation is initiated

**When** the user opens the operational dashboard

**Then** users can open the existing operational dashboard experience

##### AC-OPERATIONAL-DASHBOARD-INSIGHTS-OPEN-OPERATIONAL-DASHBOARD-002 — Open Operational Dashboard Preservation

**Criterion Type:** Modernization Preservation Criterion

**Given** dashboard navigation is initiated

**When** the application preserves approved behavior independently of legacy implementation technology

**Then** the approved behavior remains available, and unresolved relationships remain unresolved

## 5. Existing Backend Integration

Confirmed existing backend API contracts are preserved integration boundaries for the target frontend unless an explicitly approved change modifies them.

### Supporting / Shared APIs

#### API-OPERATIONAL_DASHBOARD_INSIGHTS-001 — GET /api/users/current/tenant

**Role in this Feature:** Supporting Shared Api.

**Current Frontend:** `src/MyHealth.Web/content/app/components/dashboard/services/dashboardService.js` calls `GET /api/users/current/tenant`.

**Confirmed Backend:** `GET /api/users/current/tenant` implemented by `UsersController.GetCurrentTenantAsync`.

This contract supplies shared context only; it does not provide the Feature's primary business data.

### Unresolved or Dynamic Integrations

#### API-OPERATIONAL_DASHBOARD_INSIGHTS-002 — '/api/reports/expenses/' + year

**Role in this Feature:** Dynamic Primary Interaction.

**Current Frontend:** `src/MyHealth.Web/content/app/components/dashboard/services/dashboardService.js` calls `'/api/reports/expenses/' + year`.

**Candidate Existing Backend Contract**

The associated frontend interaction is established, but no deterministic frontend-to-backend mapping proves a contract. The following endpoint is a candidate only and requires confirmation:

- `GET /api/reports/expenses/{year}` — `ReportsController.GetExpensesSummaryAsync`; response `Task<IEnumerable<ExpensesSummary>>`

**Modernization Requirement:** Confirm the existing integration before implementing this behavior in the target frontend.

#### API-OPERATIONAL_DASHBOARD_INSIGHTS-003 — '/api/reports/patients/' + year

**Role in this Feature:** Dynamic Primary Interaction.

**Current Frontend:** `src/MyHealth.Web/content/app/components/dashboard/services/dashboardService.js` calls `'/api/reports/patients/' + year`.

**Candidate Existing Backend Contract**

The associated frontend interaction is established, but no deterministic frontend-to-backend mapping proves a contract. The following endpoint is a candidate only and requires confirmation:

- `GET /api/reports/patients/{year}` — `ReportsController.GetPatientsSummaryAsync`; response `Task<IEnumerable<PatientsSummary>>`

**Modernization Requirement:** Confirm the existing integration before implementing this behavior in the target frontend.

#### API-OPERATIONAL_DASHBOARD_INSIGHTS-004 — /api/reports/clinicsummary

**Role in this Feature:** Unresolved Primary Interaction.

**Current Frontend:** `src/MyHealth.Web/content/app/components/dashboard/services/dashboardService.js` calls `/api/reports/clinicsummary`.

**Candidate Existing Backend Contract**

The associated frontend interaction is established, but no deterministic frontend-to-backend mapping proves a contract. The following endpoint is a candidate only and requires confirmation:

- `GET /api/reports/clinicsummary` — `ReportsController.GetClinicSummaryAsync`; response `Task<ClinicSummary>`

**Modernization Requirement:** Confirm the existing integration before implementing this behavior in the target frontend.


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
