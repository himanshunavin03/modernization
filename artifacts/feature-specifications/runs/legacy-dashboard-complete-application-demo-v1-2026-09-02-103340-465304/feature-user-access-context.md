# User Access and Tenant Context

## 1. Feature Overview

### Objective

Enable users to view application user details and review the application user directory while the application provides current user identity and claims within the applicable organization context.

### Feature Capabilities

- The user must be able to view application user details.
- The user must be able to review the application user directory.
- The application must retrieve current user identifier for shared application functions.
- The application must retrieve current user claims for shared application functions.
- The application must retrieve the current organization identifier required by organization-specific functionality.

### Business Value

Requires confirmation from Product Owner / Business SME.

### Scope

**In Scope**

- View Application User Details.
- Review Application User Directory.
- Resolve Current User Identity.
- Resolve Current User Claims.
- Establish Organization Context.

**Out of Scope**

- Backend identity redesign, authorization policy redesign, and unspecified meaning for individual claims.

## 2. Functional Requirements

### FR-01 - View Application User Details

#### Requirement

The user must be able to view application user details.

#### Functional Flow

1. The user requests application user information.
2. The application supplies the username.
3. The application calls `GET /api/users/{username}`.
4. Application user information is returned and made available to the user.

#### API Integration

- **Method:** `GET`
- **Endpoint:** `/api/users/{username}`
- **Input:** `username` - username (path parameter)
- **Purpose:** Retrieve application user information using the username.
- **Response:** Application user information.

#### Clarification Required

- **Q-01:** What business outcome should Access User Management Views support?
- **Q-02:** Which application user fields must be displayed in the detail view?

### FR-02 - Review Application User Directory

#### Requirement

The user must be able to review the application user directory.

#### Functional Flow

1. The user requests collection of application user records.
2. The application supplies the number of records per page and page count.
3. The application calls `GET /api/users`.
4. Collection of application user records is returned and made available to the user.

#### API Integration

- **Method:** `GET`
- **Endpoint:** `/api/users`
- **Input:** `pageSize (int)` - number of records per page (query parameter)
- **Input:** `pageCount (int)` - page count (query parameter)
- **Purpose:** Retrieve collection of application user records using the number of records per page and page count.
- **Response:** Collection of application user records.

#### Clarification Required

- **Q-03:** Which application user fields must be displayed in the directory?

### FR-03 - Resolve Current User Identity

#### Requirement

The application must retrieve current user identifier for shared application functions.

#### Functional Flow

1. Current user identifier is required by the applicable functionality.
2. The application calls `GET /api/users/current/user`.
3. Current user identifier is returned and made available to the applicable functionality.

#### API Integration

- **Method:** `GET`
- **Endpoint:** `/api/users/current/user`
- **Purpose:** Retrieve current user identifier for shared application functions.
- **Response:** Current user identifier.

### FR-04 - Resolve Current User Claims

#### Requirement

The application must retrieve current user claims for shared application functions.

#### Functional Flow

1. Current user claims are required by the applicable functionality.
2. The application calls `GET /api/users/current/claims`.
3. Current user claims are returned and made available to the applicable functionality.

#### API Integration

- **Method:** `GET`
- **Endpoint:** `/api/users/current/claims`
- **Purpose:** Retrieve current user claims for shared application functions.
- **Response:** Current user claims.

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

### US-01 - Access User Management Views

#### Story

As an application user,

I want to view user list and details.

**Business Outcome:** Requires confirmation from Product Owner / Business SME.

#### Functional Requirements

- **FR-01:** The user must be able to view application user details.
- **FR-02:** The user must be able to review the application user directory.

#### API Integration

- **Purpose:** Retrieve application user information using the username.
- **Method:** `GET`
- **Endpoint:** `/api/users/{username}`
- **Input:** `username` - username (path parameter)
- **Response:** Application user information.
- **Response Model:** `ApplicationUser`

- **Purpose:** Retrieve collection of application user records using the number of records per page and page count.
- **Method:** `GET`
- **Endpoint:** `/api/users`
- **Input:** `pageSize (int)` - number of records per page (query parameter)
- **Input:** `pageCount (int)` - page count (query parameter)
- **Response:** Collection of application user records.
- **Response Model:** `ApplicationUser[]`

#### Acceptance Criteria

##### AC-01 - Access User Management Views

**Given** The required username, number of records per page, and page count are available.

**When** The user views user list and details.

**Then** Application user information is retrieved.
**And** Collection of application user records is retrieved.

#### Clarifications Required

- **Q-01:** What business outcome should Access User Management Views support?
- **Q-02:** Which application user fields must be displayed in the detail view?
- **Q-03:** Which application user fields must be displayed in the directory?

#### Story Readiness

**NEEDS_CLARIFICATION**

Blocking clarifications: Q-02, Q-03.

### US-02 - Resolve Current User and Claims

#### Story

As an application user,

I want to make current user identity and claims available to shared application behavior,

so that shared application functions receive the required identity and claims context.

#### Functional Requirements

- **FR-03:** The application must retrieve current user identifier for shared application functions.
- **FR-04:** The application must retrieve current user claims for shared application functions.

#### API Integration

- **Purpose:** Retrieve current user identifier for shared application functions.
- **Method:** `GET`
- **Endpoint:** `/api/users/current/user`
- **Response:** Current user identifier.
- **Response Model:** `string`

- **Purpose:** Retrieve current user claims for shared application functions.
- **Method:** `GET`
- **Endpoint:** `/api/users/current/claims`
- **Response:** Current user claims.
- **Response Model:** `JsonResult`

#### Acceptance Criteria

##### AC-02 - Resolve Current User and Claims

**Given** Shared header initialization requires current user identity.

**When** The application resolves current user identity and claims for shared application behavior.

**Then** Current user identifier is available to the applicable application functions.
**And** Current user claims are available to the applicable application functions.

#### Story Readiness

**READY**

### US-03 - Resolve Tenant Context for User Functions

#### Story

As an application user,

I want to make organization context available to user functionality,

so that the applicable functions use the required organization context.

#### Functional Requirements

- **FR-05:** The application must retrieve the current organization identifier required by organization-specific functionality.

#### Business Rules

- **BR-01:** Functionality that requires organization context must obtain it before continuing.

#### API Integration

- **Purpose:** Retrieve the current organization identifier required by organization-specific functionality.
- **Method:** `GET`
- **Endpoint:** `/api/users/current/tenant`
- **Response:** Current organization identifier.
- **Response Model:** `int`

#### Acceptance Criteria

##### AC-03 - Resolve Organization Context for User Functions

**Given** The applicable functionality requires the current organization context.

**When** The application resolves organization context for user functionality.

**Then** The current organization identifier is available to the applicable functionality.

#### Story Readiness

**READY**

## 4. Acceptance Criteria

The authoritative Acceptance Criteria are realized in their owning Stories above.

| ID | Story | Criterion |
| --- | --- | --- |
| AC-01 | US-01 | Access User Management Views |
| AC-02 | US-02 | Resolve Current User and Claims |
| AC-03 | US-03 | Resolve Organization Context for User Functions |

## 5. API Requirements

### API-01 - Resolve Current User Identity

| Property | Details |
| --- | --- |
| Method | `GET` |
| Endpoint | `/api/users/current/user` |
| Input | None |
| Purpose | Retrieve current user identifier for shared application functions. |
| Response | Current user identifier |
| Response Model | `string` |
| Used By | Resolve Current User and Claims |

### API-02 - Resolve Current User Claims

| Property | Details |
| --- | --- |
| Method | `GET` |
| Endpoint | `/api/users/current/claims` |
| Input | None |
| Purpose | Retrieve current user claims for shared application functions. |
| Response | Current user claims |
| Response Model | `JsonResult` |
| Used By | Resolve Current User and Claims |

### API-03 - Establish Organization Context

| Property | Details |
| --- | --- |
| Method | `GET` |
| Endpoint | `/api/users/current/tenant` |
| Input | None |
| Purpose | Retrieve the current organization identifier required by organization-specific functionality. |
| Response | Current organization identifier |
| Response Model | `int` |
| Used By | Resolve Tenant Context for User Functions |

### API-04 - View Application User Details

| Property | Details |
| --- | --- |
| Method | `GET` |
| Endpoint | `/api/users/{username}` |
| Input | `username` - username (path) |
| Purpose | Retrieve application user information using the username. |
| Response | Application user information |
| Response Model | `ApplicationUser` |
| Used By | Access User Management Views |

**Response Fields**

- `FirstName (string)`
- `LastName (string)`
- `TenantId (int?)`
- `Tenant (MyHealth.Model.Tenant)`

### API-05 - Review Application User Directory

| Property | Details |
| --- | --- |
| Method | `GET` |
| Endpoint | `/api/users` |
| Input | `pageSize (int)` - number of records per page (query); `pageCount (int)` - page count (query) |
| Purpose | Retrieve collection of application user records using the number of records per page and page count. |
| Response | Collection of application user records |
| Response Model | `ApplicationUser` |
| Used By | Access User Management Views |

**Response Fields**

- `FirstName (string)`
- `LastName (string)`
- `TenantId (int?)`
- `Tenant (MyHealth.Model.Tenant)`

## 6. Business Rules

### BR-01

Functionality that requires organization context must obtain it before continuing.

## 7. Development Requirements

- Implement the functionality defined by this Feature.
- Integrate with the specified backend APIs.
- Supply every documented API parameter.
- Use each API result for the corresponding functionality.
- Maintain required user and organization context.
- Satisfy all authoritative Acceptance Criteria.

## 8. Clarifications Required

| ID | Question | Owner | Required Before |
| --- | --- | --- | --- |
| Q-01 | What business outcome should Access User Management Views support? | Product Owner / Business Analyst / Customer SME | Final stakeholder approval |
| Q-02 | Which application user fields must be displayed in the detail view? | Product Owner / Business Analyst / Customer SME / QA Lead | Development and QA completion |
| Q-03 | Which application user fields must be displayed in the directory? | Product Owner / Business Analyst / Customer SME / QA Lead | Development and QA completion |

## 9. Definition of Done

- [ ] Implementation is complete for View Application User Details.
- [ ] Implementation is complete for Review Application User Directory.
- [ ] Implementation is complete for Resolve Current User Identity.
- [ ] Implementation is complete for Resolve Current User Claims.
- [ ] Implementation is complete for Establish Organization Context.
- [ ] All specified backend APIs are integrated.
- [ ] Required API parameters are supplied as documented.
- [ ] All documented business rules are satisfied.
- [ ] All authoritative Acceptance Criteria pass.
- [ ] Blocking business clarifications are resolved.
- [ ] QA validation is complete.

## 10. Review and Approval

| Role | Review Responsibility | Status |
| --- | --- | --- |
| Product Owner | Objective, business value, scope, and priorities | Pending |
| Business Analyst | Functional requirements, rules, Stories, and clarifications | Pending |
| Solution Architect | API contracts, inputs, responses, and integration boundaries | Pending |
| Development Lead | Implementation clarity and delivery feasibility | Pending |
| QA Lead | Acceptance Criteria and validation coverage | Pending |
| Customer SME | Business terminology and unresolved decisions | Pending |
