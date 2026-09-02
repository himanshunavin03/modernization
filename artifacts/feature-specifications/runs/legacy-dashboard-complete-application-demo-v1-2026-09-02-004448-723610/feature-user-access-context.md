# User Access and Tenant Context

## 1. Feature Overview

### Objective

Provide current user, claims, and tenant context to shared and user-management frontend flows.

### Feature Capabilities

- The application makes the user list and detail views available to users.
- The header has current user identity. The header has current claims. Initial-page behavior has current claims.
- User functionality has tenant context.

### Business Value

Maintains the current user identity and claims used by shared application behavior. Maintains the current tenant context used by user functionality. Additional business value requires confirmation from Product Owner / Business SME.

### Scope

**In Scope**

- user routes, user surfaces, identity/claims/tenant workflows, one tenant-context rule, and four API integrations.

**Out of Scope**

- Backend identity redesign, authorization policy redesign, and unspecified meaning for individual claims.

## 2. Functional Requirements

### FR-01 - Access User Management Views

#### Requirement

The application makes the user list and detail views available to users.

#### Functional Flow

1. User detail navigation is initiated.
2. The user accesses user list and detail views.
3. The user list and detail views are available.

#### API Integration

- **API-04:** `GET /api/users/{username}` - Supports Access User Management Views.
- **API-05:** `GET /api/users` - Supports Access User Management Views.

#### Clarification Required

- **Q-01:** What business outcome should users achieve through Access User Management Views?
- **Q-02:** Which information must be considered mandatory when validating Access User Management Views?

### FR-02 - Resolve Current User and Claims

#### Requirement

The header has current user identity. The header has current claims. Initial-page behavior has current claims.

#### Functional Flow

1. Shared header initialization needs current user identity.
2. The application makes current user identity and claims available to shared application behavior.
3. The header has current user identity.
4. The header has current claims.
5. Initial-page behavior has current claims.

#### API Integration

- **API-01:** `GET /api/users/current/user` - Supports Resolve Current User and Claims.
- **API-02:** `GET /api/users/current/claims` - Supports Resolve Current User and Claims.

### FR-03 - Resolve Tenant Context for User Functions

#### Requirement

User functionality has tenant context.

#### Functional Flow

1. User functionality needs tenant context.
2. The application makes current tenant context available to user functionality.
3. User functionality has tenant context.

#### API Integration

- **API-03:** `GET /api/users/current/tenant` - Supports Resolve Tenant Context for User Functions.

## 3. User Stories

### US-01 - Access User Management Views

As an application user,

I want to access user list and detail views,

so that I can use the information and functions provided by this feature.

### US-02 - Resolve Current User and Claims

As an application user,

I want to make current user identity and claims available to shared application behavior,

so that shared application behavior retains its identity and claims context.

### US-03 - Resolve Tenant Context for User Functions

As an application user,

I want to make current tenant context available to user functionality,

so that user functionality retains its tenant-aware behavior.

## 4. Acceptance Criteria

### AC-01 - Access User Management Views

**Given** User detail navigation is initiated.

**When** The user accesses user list and detail views.

**Then** The user list and detail views are available.

### AC-02 - Resolve Current User and Claims

**Given** Shared header initialization needs current user identity.

**When** The application makes current user identity and claims available to shared application behavior.

**Then** The header has current user identity; and the header has current claims; and initial-page behavior has current claims.

### AC-03 - Resolve Tenant Context for User Functions

**Given** User functionality needs tenant context.

**When** The application makes current tenant context available to user functionality.

**Then** User functionality has tenant context.

## 5. API Requirements

### API-01 - Resolve Current User and Claims

**Method:** `GET`

**Endpoint:** `/api/users/current/user`

**Purpose:** Supports Resolve Current User and Claims.

**Expected Result:** `Task<string>`

**Used By:** Resolve Current User and Claims

### API-02 - Resolve Current User and Claims

**Method:** `GET`

**Endpoint:** `/api/users/current/claims`

**Purpose:** Supports Resolve Current User and Claims.

**Expected Result:** `JsonResult`

**Used By:** Resolve Current User and Claims

### API-03 - Resolve Tenant Context for User Functions

**Method:** `GET`

**Endpoint:** `/api/users/current/tenant`

**Purpose:** Supports Resolve Tenant Context for User Functions.

**Expected Result:** `Task<int?>`

**Used By:** Resolve Tenant Context for User Functions

### API-04 - Access User Management Views

**Method:** `GET`

**Endpoint:** `/api/users/{username}`

**Purpose:** Supports Access User Management Views.

**Required Input**

- `username` - path parameter

**Expected Result:** `Task<ApplicationUser>`

**Response Fields**

- `FirstName (string)`
- `LastName (string)`
- `TenantId (int?)`
- `Tenant (MyHealth.Model.Tenant)`

**Used By:** Access User Management Views

### API-05 - Access User Management Views

**Method:** `GET`

**Endpoint:** `/api/users`

**Purpose:** Supports Access User Management Views.

**Required Input**

- `pageSize (int)` - query parameter
- `pageCount (int)` - query parameter

**Expected Result:** `Task<IEnumerable<ApplicationUser>>`

**Response Fields**

- `FirstName (string)`
- `LastName (string)`
- `TenantId (int?)`
- `Tenant (MyHealth.Model.Tenant)`

**Used By:** Access User Management Views

## 6. Business Rules

### BR-01

Tenant-scoped frontend flows obtain current tenant context before continuing.

## 7. Development Requirements

- Implement the functional requirements defined in this specification.
- Integrate with the listed backend APIs and supply each documented input.
- Make the returned information available to the applicable feature behavior.
- Maintain the documented user and tenant context.
- Satisfy every acceptance criterion.

## 8. Clarifications Required

| ID | Question | Owner | Required Before |
| --- | --- | --- | --- |
| Q-01 | What business outcome should users achieve through Access User Management Views? | Product Owner / Business Analyst / Customer SME | Final stakeholder approval |
| Q-02 | Which information must be considered mandatory when validating Access User Management Views? | Product Owner / Business Analyst / Customer SME / QA Lead | Development and QA completion |

## 9. Definition of Done

- [ ] All functional requirements in this specification are implemented.
- [ ] All listed APIs are integrated with their documented inputs.
- [ ] All documented business rules are satisfied.
- [ ] All acceptance criteria pass.
- [ ] Blocking clarifications are resolved.
- [ ] QA validation is complete.

## 10. Review and Approval

| Role | Review Responsibility | Status |
| --- | --- | --- |
| Product Owner | Objective, business value, scope, and priorities | Pending |
| Business Analyst | Functional requirements, rules, Stories, and clarifications | Pending |
| Solution Architect | API contracts, inputs, and integration boundaries | Pending |
| Development Lead | Implementation clarity and delivery feasibility | Pending |
| QA Lead | Acceptance Criteria and validation coverage | Pending |
| Customer SME | Business terminology and unresolved decisions | Pending |
