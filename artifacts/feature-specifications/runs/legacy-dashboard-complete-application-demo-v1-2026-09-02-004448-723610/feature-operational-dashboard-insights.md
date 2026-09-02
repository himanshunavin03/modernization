# Operational Dashboard Insights

## 1. Feature Overview

### Objective

Provide access to dashboard summaries and clinic reporting information in the current tenant context.

### Feature Capabilities

- The application requests expense and patient reporting information for a selected year.
- The dashboard summary flow has current tenant context. Clinic summary information is requested for the dashboard.
- Users can open the operational dashboard experience.

### Business Value

Makes the year-dependent reporting capability available to users. Preserves tenant-aware access to the dashboard summary information. Additional business value requires confirmation from Product Owner / Business SME.

### Scope

**In Scope**

- User-facing experience, seven workflows, tenant context, and reporting API contracts.

**Out of Scope**

- Backend/database redesign, unspecified integrations, and delivery of unrelated UI areas.

## 2. Functional Requirements

### FR-01 - Access Yearly Operational Reports

#### Requirement

The application requests expense and patient reporting information for a selected year.

#### Functional Flow

1. The expense-reporting flow needs clinic context.
2. The user accesses year-dependent expense and patient reporting information.
3. The expense-reporting flow has current tenant context.
4. The patient-reporting flow has current tenant context.
5. Yearly expense information is requested.
6. Yearly patient-report information is requested.

#### API Integration

- **API-01:** `GET /api/users/current/tenant` - Provides shared context for Access Yearly Operational Reports, View Tenant-Aware Dashboard Summary.
- **API-02:** `GET /api/reports/expenses/{year}` - Supports Access Yearly Operational Reports.
- **API-03:** `GET /api/reports/patients/{year}` - Supports Access Yearly Operational Reports.

#### Clarification Required

- **Q-02:** Which information must be considered mandatory when validating Access Yearly Operational Reports?

### FR-02 - View Tenant-Aware Dashboard Summary

#### Requirement

The dashboard summary flow has current tenant context. Clinic summary information is requested for the dashboard.

#### Functional Flow

1. The dashboard summary flow needs clinic context.
2. The user accesses dashboard summary information in current tenant context.
3. The dashboard summary flow has current tenant context.
4. Clinic summary information is requested for the dashboard.

#### API Integration

- **API-01:** `GET /api/users/current/tenant` - Provides shared context for Access Yearly Operational Reports, View Tenant-Aware Dashboard Summary.
- **API-04:** `GET /api/reports/clinicsummary` - Supports View Tenant-Aware Dashboard Summary.

#### Clarification Required

- **Q-04:** Which information must be considered mandatory when validating View Tenant-Aware Dashboard Summary?

### FR-03 - Open Operational Dashboard

#### Requirement

Users can open the operational dashboard experience.

#### Functional Flow

1. Dashboard navigation is initiated.
2. The user opens the operational dashboard experience.
3. The user can access the operational dashboard experience.

#### Clarification Required

- **Q-01:** What business outcome should users achieve through Open Operational Dashboard?
- **Q-03:** Which information must be considered mandatory when validating Open Operational Dashboard?

## 3. User Stories

### US-01 - Access Yearly Operational Reports

As an application user,

I want to access year-dependent expense and patient reporting information,

so that the reporting information remains available for the selected year.

### US-02 - View Tenant-Aware Dashboard Summary

As an application user,

I want to access dashboard summary information in current tenant context,

so that the dashboard summary information remains associated with current tenant context.

### US-03 - Open Operational Dashboard

As an application user,

I want to open the operational dashboard experience,

so that I can use the information and functions provided by this feature.

## 4. Acceptance Criteria

### AC-01 - Access Yearly Operational Reports

**Given** The expense-reporting flow needs clinic context.

**When** The user accesses year-dependent expense and patient reporting information.

**Then** The expense-reporting flow has current tenant context; and the patient-reporting flow has current tenant context; and yearly expense information is requested; and yearly patient-report information is requested.

### AC-02 - View Tenant-Aware Dashboard Summary

**Given** The dashboard summary flow needs clinic context.

**When** The user accesses dashboard summary information in current tenant context.

**Then** The dashboard summary flow has current tenant context; and clinic summary information is requested for the dashboard.

### AC-03 - View Tenant-Aware Dashboard Summary Delivery

**Given** The feature behavior is ready for delivery.

**When** The feature is implemented.

**Then** The behavior and backend integrations defined in this specification remain available.

### AC-04 - Open Operational Dashboard

**Given** Dashboard navigation is initiated.

**When** The user opens the operational dashboard experience.

**Then** The user can access the operational dashboard experience.

### AC-05 - Open Operational Dashboard Delivery

**Given** The feature behavior is ready for delivery.

**When** The feature is implemented.

**Then** The behavior and backend integrations defined in this specification remain available.

## 5. API Requirements

### API-01 - Access Yearly Operational Reports, View Tenant-Aware Dashboard Summary

**Method:** `GET`

**Endpoint:** `/api/users/current/tenant`

**Purpose:** Provides shared context for Access Yearly Operational Reports, View Tenant-Aware Dashboard Summary.

**Expected Result:** `Task<int?>`

**Used By:** Access Yearly Operational Reports, View Tenant-Aware Dashboard Summary

### API-02 - Access Yearly Operational Reports

**Method:** `GET`

**Endpoint:** `/api/reports/expenses/{year}`

**Purpose:** Supports Access Yearly Operational Reports.

**Required Input**

- `year` - path parameter

**Expected Result:** `Task<IEnumerable<ExpensesSummary>>`

**Used By:** Access Yearly Operational Reports

### API-03 - Access Yearly Operational Reports

**Method:** `GET`

**Endpoint:** `/api/reports/patients/{year}`

**Purpose:** Supports Access Yearly Operational Reports.

**Required Input**

- `year` - path parameter

**Expected Result:** `Task<IEnumerable<PatientsSummary>>`

**Used By:** Access Yearly Operational Reports

### API-04 - View Tenant-Aware Dashboard Summary

**Method:** `GET`

**Endpoint:** `/api/reports/clinicsummary`

**Purpose:** Supports View Tenant-Aware Dashboard Summary.

**Expected Result:** `Task<ClinicSummary>`

**Used By:** View Tenant-Aware Dashboard Summary

## 6. Development Requirements

- Implement the functional requirements defined in this specification.
- Integrate with the listed backend APIs and supply each documented input.
- Make the returned information available to the applicable feature behavior.
- Maintain the documented user and tenant context.
- Satisfy every acceptance criterion.

## 7. Clarifications Required

| ID | Question | Owner | Required Before |
| --- | --- | --- | --- |
| Q-01 | What business outcome should users achieve through Open Operational Dashboard? | Product Owner / Business Analyst / Customer SME | Final stakeholder approval |
| Q-02 | Which information must be considered mandatory when validating Access Yearly Operational Reports? | Product Owner / Business Analyst / Customer SME / QA Lead | Development and QA completion |
| Q-03 | Which information must be considered mandatory when validating Open Operational Dashboard? | Product Owner / Business Analyst / Customer SME / QA Lead | Development and QA completion |
| Q-04 | Which information must be considered mandatory when validating View Tenant-Aware Dashboard Summary? | Product Owner / Business Analyst / Customer SME / QA Lead | Development and QA completion |

## 8. Definition of Done

- [ ] All functional requirements in this specification are implemented.
- [ ] All listed APIs are integrated with their documented inputs.
- [ ] The behavior stays within the documented scope.
- [ ] All acceptance criteria pass.
- [ ] Blocking clarifications are resolved.
- [ ] QA validation is complete.

## 9. Review and Approval

| Role | Review Responsibility | Status |
| --- | --- | --- |
| Product Owner | Objective, business value, scope, and priorities | Pending |
| Business Analyst | Functional requirements, rules, Stories, and clarifications | Pending |
| Solution Architect | API contracts, inputs, and integration boundaries | Pending |
| Development Lead | Implementation clarity and delivery feasibility | Pending |
| QA Lead | Acceptance Criteria and validation coverage | Pending |
| Customer SME | Business terminology and unresolved decisions | Pending |
