# Operational Dashboard Insights

## 1. Feature Overview

### Objective

Enable users to access the operational dashboard, view yearly expense information, view yearly patient information, and view clinic summary within the applicable organization context.

### Feature Capabilities

- The user must be able to access the operational dashboard.
- The user must be able to view yearly expense information.
- The user must be able to view yearly patient information.
- The user must be able to view clinic summary.
- The application must retrieve the current organization identifier required by organization-specific functionality.

### Business Value

Requires confirmation from Product Owner / Business SME.

### Scope

**In Scope**

- Access Operational Dashboard.
- View Yearly Expense Information.
- View Yearly Patient Information.
- View Clinic Summary.
- Establish Organization Context.

**Out of Scope**

- Backend/database redesign, unspecified integrations, and unrelated user interface areas.

## 2. Functional Requirements

### FR-01 - Access Operational Dashboard

#### Requirement

The user must be able to access the operational dashboard.

#### Functional Flow

1. Dashboard navigation is initiated.
2. The user requests access to the operational dashboard.
3. The operational dashboard becomes available to the user.

#### Clarification Required

- **Q-01:** What business outcome should Open Operational Dashboard support?

### FR-02 - View Yearly Expense Information

#### Requirement

The user must be able to view yearly expense information.

#### Functional Flow

1. The user requests expense summary information.
2. The application supplies the selected reporting year.
3. The application calls `GET /api/reports/expenses/{year}`.
4. Expense summary information is returned and made available to the user.

#### API Integration

- **Method:** `GET`
- **Endpoint:** `/api/reports/expenses/{year}`
- **Input:** `year` - selected reporting year (path parameter)
- **Purpose:** Retrieve expense summary information for the selected reporting year.
- **Response:** Expense summary information.

#### Clarification Required

- **Q-02:** Which expense fields and metrics must be displayed for the selected reporting year?

### FR-03 - View Yearly Patient Information

#### Requirement

The user must be able to view yearly patient information.

#### Functional Flow

1. The user requests patient summary information.
2. The application supplies the selected reporting year.
3. The application calls `GET /api/reports/patients/{year}`.
4. Patient summary information is returned and made available to the user.

#### API Integration

- **Method:** `GET`
- **Endpoint:** `/api/reports/patients/{year}`
- **Input:** `year` - selected reporting year (path parameter)
- **Purpose:** Retrieve patient summary information for the selected reporting year.
- **Response:** Patient summary information.

#### Clarification Required

- **Q-03:** Which patient fields and metrics must be displayed for the selected reporting year?

### FR-04 - View Clinic Summary

#### Requirement

The user must be able to view clinic summary.

#### Functional Flow

1. The user requests clinic summary information.
2. The application calls `GET /api/reports/clinicsummary`.
3. Clinic summary information is returned and made available to the user.

#### API Integration

- **Method:** `GET`
- **Endpoint:** `/api/reports/clinicsummary`
- **Purpose:** Retrieve clinic summary information for the corresponding feature function.
- **Response:** Clinic summary information.

#### Clarification Required

- **Q-04:** Which clinic information must be displayed in the summary?
- **Q-05:** What information must be available when users access the operational dashboard experience?

### FR-05 - Establish Organization Context

#### Requirement

The application must retrieve the current organization identifier required by organization-specific functionality.

#### Functional Flow

1. Current organization identifier is required by the applicable functionality.
2. The application calls `GET /api/users/current/tenant`.
3. Current organization identifier is returned and made available to the applicable functionality.

#### API Integration

- **Method:** `GET`
- **Endpoint:** `/api/users/current/tenant`
- **Purpose:** Retrieve the current organization identifier required by organization-specific functionality.
- **Response:** Current organization identifier.

## 3. User Stories

### US-01 - Access Yearly Operational Reports

#### Story

As an application user,

I want to view expense and patient information for a selected year,

so that I can review information for the required reporting period.

#### Functional Requirements

- **FR-02:** The user must be able to view yearly expense information.
- **FR-03:** The user must be able to view yearly patient information.
- **FR-05:** The application must retrieve the current organization identifier required by organization-specific functionality.

#### API Integration

- **Purpose:** Retrieve the current organization identifier required by organization-specific functionality.
- **Method:** `GET`
- **Endpoint:** `/api/users/current/tenant`
- **Response:** Current organization identifier.
- **Response Model:** `int`

- **Purpose:** Retrieve expense summary information for the selected reporting year.
- **Method:** `GET`
- **Endpoint:** `/api/reports/expenses/{year}`
- **Input:** `year` - selected reporting year (path parameter)
- **Response:** Expense summary information.
- **Response Model:** `ExpensesSummary[]`

- **Purpose:** Retrieve patient summary information for the selected reporting year.
- **Method:** `GET`
- **Endpoint:** `/api/reports/patients/{year}`
- **Input:** `year` - selected reporting year (path parameter)
- **Response:** Patient summary information.
- **Response Model:** `PatientsSummary[]`

#### Acceptance Criteria

##### AC-01 - Access Yearly Operational Reports

**Given** A reporting year has been selected.

**When** The user views expense and patient information for a selected year.

**Then** Expense summary information is retrieved for the selected reporting year.
**And** Patient summary information is retrieved for the selected reporting year.
**And** The retrieved information is associated with the current organization.

#### Clarifications Required

- **Q-02:** Which expense fields and metrics must be displayed for the selected reporting year?
- **Q-03:** Which patient fields and metrics must be displayed for the selected reporting year?

#### Story Readiness

**NEEDS_CLARIFICATION**

Blocking clarifications: Q-02, Q-03.

### US-02 - View Tenant-Aware Dashboard Summary

#### Story

As an application user,

I want to view dashboard summary information for my organization,

so that I can review information relevant to the organization I am working with.

#### Functional Requirements

- **FR-04:** The user must be able to view clinic summary.
- **FR-05:** The application must retrieve the current organization identifier required by organization-specific functionality.

#### API Integration

- **Purpose:** Retrieve the current organization identifier required by organization-specific functionality.
- **Method:** `GET`
- **Endpoint:** `/api/users/current/tenant`
- **Response:** Current organization identifier.
- **Response Model:** `int`

- **Purpose:** Retrieve clinic summary information for the corresponding feature function.
- **Method:** `GET`
- **Endpoint:** `/api/reports/clinicsummary`
- **Response:** Clinic summary information.
- **Response Model:** `ClinicSummary`

#### Acceptance Criteria

##### AC-02 - View Organization-Specific Dashboard Summary

**Given** The application can determine the current organization context.

**When** The user views dashboard summary information for their organization.

**Then** Clinic summary information is retrieved.
**And** The retrieved information is associated with the current organization.

##### AC-03 - View Organization-Specific Dashboard Summary Service Integration

**Given** The application can determine the current organization context.

**When** The application loads dashboard summary information for their organization.

**Then** Clinic summary information is retrieved.
**And** The retrieved information is associated with the current organization.

#### Clarifications Required

- **Q-04:** Which clinic information must be displayed in the summary?
- **Q-05:** What information must be available when users access the operational dashboard experience?

#### Story Readiness

**NEEDS_CLARIFICATION**

Blocking clarifications: Q-04, Q-05.

### US-03 - Open Operational Dashboard

#### Story

As an application user,

I want to open the operational dashboard experience.

**Business Outcome:** Requires confirmation from Product Owner / Business SME.

#### Functional Requirements

- **FR-01:** The user must be able to access the operational dashboard.

#### Acceptance Criteria

##### AC-04 - Open Operational Dashboard

**Given** Dashboard navigation is initiated.

**When** The user requests access to the operational dashboard experience.

**Then** The operational dashboard experience is available to the user.

##### AC-05 - Open Operational Dashboard Availability

**Given** Dashboard navigation is initiated.

**When** The user requests access to the operational dashboard experience.

**Then** The operational dashboard experience is available to the user.

#### Clarifications Required

- **Q-01:** What business outcome should Open Operational Dashboard support?
- **Q-04:** Which clinic information must be displayed in the summary?

#### Story Readiness

**NEEDS_CLARIFICATION**

Blocking clarifications: Q-04.

## 4. Acceptance Criteria

The authoritative Acceptance Criteria are realized in their owning Stories above.

| ID | Story | Criterion |
| --- | --- | --- |
| AC-01 | US-01 | Access Yearly Operational Reports |
| AC-02 | US-02 | View Organization-Specific Dashboard Summary |
| AC-03 | US-02 | View Organization-Specific Dashboard Summary Service Integration |
| AC-04 | US-03 | Open Operational Dashboard |
| AC-05 | US-03 | Open Operational Dashboard Availability |

## 5. API Requirements

### API-01 - Establish Organization Context

| Property | Details |
| --- | --- |
| Method | `GET` |
| Endpoint | `/api/users/current/tenant` |
| Input | None |
| Purpose | Retrieve the current organization identifier required by organization-specific functionality. |
| Response | Current organization identifier |
| Response Model | `int` |
| Used By | Access Yearly Operational Reports, View Tenant-Aware Dashboard Summary |

### API-02 - View Yearly Expense Information

| Property | Details |
| --- | --- |
| Method | `GET` |
| Endpoint | `/api/reports/expenses/{year}` |
| Input | `year` - selected reporting year (path) |
| Purpose | Retrieve expense summary information for the selected reporting year. |
| Response | Expense summary information |
| Response Model | `ExpensesSummary` |
| Used By | Access Yearly Operational Reports |

### API-03 - View Yearly Patient Information

| Property | Details |
| --- | --- |
| Method | `GET` |
| Endpoint | `/api/reports/patients/{year}` |
| Input | `year` - selected reporting year (path) |
| Purpose | Retrieve patient summary information for the selected reporting year. |
| Response | Patient summary information |
| Response Model | `PatientsSummary` |
| Used By | Access Yearly Operational Reports |

### API-04 - View Clinic Summary

| Property | Details |
| --- | --- |
| Method | `GET` |
| Endpoint | `/api/reports/clinicsummary` |
| Input | None |
| Purpose | Retrieve clinic summary information for the corresponding feature function. |
| Response | Clinic summary information |
| Response Model | `ClinicSummary` |
| Used By | View Tenant-Aware Dashboard Summary |

## 6. Development Requirements

- Implement the functionality defined by this Feature.
- Integrate with the specified backend APIs.
- Supply every documented API parameter.
- Use each API result for the corresponding functionality.
- Maintain required user and organization context.
- Satisfy all authoritative Acceptance Criteria.

## 7. Clarifications Required

| ID | Question | Owner | Required Before |
| --- | --- | --- | --- |
| Q-01 | What business outcome should Open Operational Dashboard support? | Product Owner / Business Analyst / Customer SME | Final stakeholder approval |
| Q-02 | Which expense fields and metrics must be displayed for the selected reporting year? | Product Owner / Business Analyst / Customer SME / QA Lead | Development and QA completion |
| Q-03 | Which patient fields and metrics must be displayed for the selected reporting year? | Product Owner / Business Analyst / Customer SME / QA Lead | Development and QA completion |
| Q-04 | Which clinic information must be displayed in the summary? | Product Owner / Business Analyst / Customer SME / QA Lead | Development and QA completion |
| Q-05 | What information must be available when users access the operational dashboard experience? | Product Owner / Business Analyst / Customer SME / QA Lead | Development and QA completion |

## 8. Definition of Done

- [ ] Implementation is complete for Access Operational Dashboard.
- [ ] Implementation is complete for View Yearly Expense Information.
- [ ] Implementation is complete for View Yearly Patient Information.
- [ ] Implementation is complete for View Clinic Summary.
- [ ] Implementation is complete for Establish Organization Context.
- [ ] All specified backend APIs are integrated.
- [ ] Required API parameters are supplied as documented.
- [ ] All authoritative Acceptance Criteria pass.
- [ ] Blocking business clarifications are resolved.
- [ ] QA validation is complete.

## 9. Review and Approval

| Role | Review Responsibility | Status |
| --- | --- | --- |
| Product Owner | Objective, business value, scope, and priorities | Pending |
| Business Analyst | Functional requirements, rules, Stories, and clarifications | Pending |
| Solution Architect | API contracts, inputs, responses, and integration boundaries | Pending |
| Development Lead | Implementation clarity and delivery feasibility | Pending |
| QA Lead | Acceptance Criteria and validation coverage | Pending |
| Customer SME | Business terminology and unresolved decisions | Pending |
