# Patient Directory Management

## 1. Feature Overview

### Objective

Enable users to review the patient directory within the applicable organization context.

### Feature Capabilities

- The user must be able to review the patient directory.
- The application must retrieve the current organization identifier required by organization-specific functionality.

### Business Value

Requires confirmation from Product Owner / Business SME.

### Scope

**In Scope**

- Review Patient Directory.
- Establish Organization Context.

**Out of Scope**

- Backend rewrite, database redesign, and patient operations without specified integration.

## 2. Functional Requirements

### FR-01 - Review Patient Directory

#### Requirement

The user must be able to review the patient directory.

#### Functional Flow

1. The user requests collection of patient records.
2. The application supplies the number of records per page and page count.
3. The application calls `GET /api/patients`.
4. Collection of patient records is returned and made available to the user.

#### API Integration

- **Method:** `GET`
- **Endpoint:** `/api/patients`
- **Input:** `pageSize (int)` - number of records per page (query parameter)
- **Input:** `pageCount (int)` - page count (query parameter)
- **Purpose:** Retrieve collection of patient records using the number of records per page and page count.
- **Response:** Collection of patient records.

#### Clarification Required

- **Q-01:** What business outcome should Review Patient Directory support?
- **Q-02:** Which patient fields must be displayed in the directory?

### FR-02 - Establish Organization Context

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

### US-01 - Establish Patient Tenant Context

#### Story

As an application user,

I want to make organization context available to patient functionality,

so that the applicable functions use the required organization context.

#### Functional Requirements

- **FR-02:** The application must retrieve the current organization identifier required by organization-specific functionality.

#### API Integration

- **Purpose:** Retrieve the current organization identifier required by organization-specific functionality.
- **Method:** `GET`
- **Endpoint:** `/api/users/current/tenant`
- **Response:** Current organization identifier.
- **Response Model:** `int`

#### Acceptance Criteria

##### AC-01 - Establish Patient Organization Context

**Given** The applicable functionality requires the current organization context.

**When** The application resolves organization context for patient functionality.

**Then** The current organization identifier is available to the applicable functionality.

#### Story Readiness

**READY**

### US-02 - Review Patient Directory

#### Story

As an application user,

I want to review the patient directory.

**Business Outcome:** Requires confirmation from Product Owner / Business SME.

#### Functional Requirements

- **FR-01:** The user must be able to review the patient directory.

#### API Integration

- **Purpose:** Retrieve collection of patient records using the number of records per page and page count.
- **Method:** `GET`
- **Endpoint:** `/api/patients`
- **Input:** `pageSize (int)` - number of records per page (query parameter)
- **Input:** `pageCount (int)` - page count (query parameter)
- **Response:** Collection of patient records.
- **Response Model:** `Patient[]`

#### Acceptance Criteria

##### AC-02 - Review Patient Directory

**Given** The required number of records per page and page count are available.

**When** The user reviews the patient directory.

**Then** Collection of patient records is retrieved.

#### Clarifications Required

- **Q-01:** What business outcome should Review Patient Directory support?
- **Q-02:** Which patient fields must be displayed in the directory?

#### Story Readiness

**NEEDS_CLARIFICATION**

Blocking clarifications: Q-02.

## 4. Acceptance Criteria

The authoritative Acceptance Criteria are realized in their owning Stories above.

| ID | Story | Criterion |
| --- | --- | --- |
| AC-01 | US-01 | Establish Patient Organization Context |
| AC-02 | US-02 | Review Patient Directory |

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
| Used By | Establish Patient Tenant Context |

### API-02 - Review Patient Directory

| Property | Details |
| --- | --- |
| Method | `GET` |
| Endpoint | `/api/patients` |
| Input | `pageSize (int)` - number of records per page (query); `pageCount (int)` - page count (query) |
| Purpose | Retrieve collection of patient records using the number of records per page and page count. |
| Response | Collection of patient records |
| Response Model | `Patient` |
| Used By | Review Patient Directory |

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
| Q-01 | What business outcome should Review Patient Directory support? | Product Owner / Business Analyst / Customer SME | Final stakeholder approval |
| Q-02 | Which patient fields must be displayed in the directory? | Product Owner / Business Analyst / Customer SME / QA Lead | Development and QA completion |

## 8. Definition of Done

- [ ] Implementation is complete for Review Patient Directory.
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
