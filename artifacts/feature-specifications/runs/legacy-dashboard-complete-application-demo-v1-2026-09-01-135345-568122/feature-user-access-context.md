# feature-user-access-context — User Access and Tenant Context

## 1. Feature Summary

**Purpose**

Users can access existing user list and detail views. The application can make current user identity and claims available to shared application behavior. The application can make current tenant context available to user functionality.

**Business Value**

The Feature appears to support consistent access to user and tenant context across frontend areas.

**Current State**

The current implementation uses UsersController, user, users, usersService.

**Modernization Objective**

Preserve proven identity, claims, and tenant contracts as reusable target-frontend context behavior without redesigning backend authorization.

## 2. Functional Behavior

### Access User Management Views

Users can access existing user list and detail views.

### Resolve Current User and Claims

The application can make current user identity and claims available to shared application behavior.

### Resolve Tenant Context for User Functions

The application can make current tenant context available to user functionality.

The current requirements establish a general application user; a more specific business persona has not yet been approved.

## 3. Scope

### In Scope

- Approved user routes, user surfaces, identity/claims/tenant workflows, one tenant-context rule, and four proven API relationships.

### Out of Scope

- Backend identity redesign, authorization policy redesign, and inferred meaning for individual claims.

## 4. User Stories & Acceptance Criteria

### STORY-USER-ACCESS-CONTEXT-ACCESS-USER-MANAGEMENT-VIEWS — Access User Management Views

**Story**

As an application user,

I want to access existing user list and detail views,

so that the application can present the supported user list and detail views.

**Business Context**

Represents the approved user-management navigation behavior.

#### Acceptance Criteria

##### AC-USER-ACCESS-CONTEXT-ACCESS-USER-MANAGEMENT-VIEWS-001 — Access User Management Views Behavior

**Criterion Type:** Functional Acceptance Criterion

**Given** user detail navigation is initiated

**When** the user navigates user management surfaces

**Then** users can access existing user list and detail views

**Current Backend Contract References**

- `API-USER_ACCESS_CONTEXT-DISCOVERED-001`
- `API-USER_ACCESS_CONTEXT-DISCOVERED-002`

### STORY-USER-ACCESS-CONTEXT-RESOLVE-CURRENT-USER-AND-CLAIMS — Resolve Current User and Claims

**Story**

As an application user,

I want to make current user identity and claims available to shared application behavior,

so that shared application behavior can use current user identity and claims.

**Business Context**

Combines the approved identity and claims retrieval workflows used by shared header and initial-page behavior.

#### Acceptance Criteria

##### AC-USER-ACCESS-CONTEXT-RESOLVE-CURRENT-USER-AND-CLAIMS-001 — Resolve Current User and Claims Behavior

**Criterion Type:** Functional Acceptance Criterion

**Given** shared header initialization needs current user identity

**When** the application resolves current user and claims for shared UI

**Then** the application can make current user identity and claims available to shared application behavior

**Current Backend Contract References**

- `API-USER_ACCESS_CONTEXT-001`
- `API-USER_ACCESS_CONTEXT-002`
- `API-USER_ACCESS_CONTEXT-003`

### STORY-USER-ACCESS-CONTEXT-RESOLVE-TENANT-CONTEXT-FOR-USER-FUNCTIONS — Resolve Tenant Context for User Functions

**Story**

As an application user,

I want to make current tenant context available to user functionality,

so that user functionality can use current tenant context.

**Business Context**

Represents the proven tenant-context interaction and its approved tenant-scoped behavior rule.

#### Acceptance Criteria

##### AC-USER-ACCESS-CONTEXT-RESOLVE-TENANT-CONTEXT-FOR-USER-FUNCTIONS-001 — Resolve Tenant Context for User Functions Behavior

**Criterion Type:** Functional Acceptance Criterion

**Given** user functionality needs tenant context

**When** the application resolves tenant context for user functionality

**Then** the application can make current tenant context available to user functionality

**Current Backend Contract References**

- `API-USER_ACCESS_CONTEXT-004`

## 5. Existing Backend Integration

Confirmed existing backend API contracts are preserved integration boundaries for the target frontend unless an explicitly approved change modifies them.

### Primary Business APIs

#### API-USER_ACCESS_CONTEXT-001 — GET /api/users/current/user

**Role in this Feature:** Primary Business Api.

**Current Frontend:** `src/MyHealth.Web/content/app/components/shared/controllers/headerController.js` calls `GET /api/users/current/user`.

**Confirmed Backend:** `GET /api/users/current/user` implemented by `UsersController.GetCurrentUserAsync`.

#### API-USER_ACCESS_CONTEXT-002 — GET /api/users/current/claims

**Role in this Feature:** Primary Business Api.

**Current Frontend:** `src/MyHealth.Web/content/app/components/shared/controllers/headerController.js` calls `GET /api/users/current/claims`.

**Confirmed Backend:** `GET /api/users/current/claims` implemented by `UsersController.GetCurrentClaimsAsync`.

#### API-USER_ACCESS_CONTEXT-003 — GET /api/users/current/claims

**Role in this Feature:** Primary Business Api.

**Current Frontend:** `src/MyHealth.Web/content/app/components/shared/services/initialPageService.js` calls `GET /api/users/current/claims`.

**Confirmed Backend:** `GET /api/users/current/claims` implemented by `UsersController.GetCurrentClaimsAsync`.

#### API-USER_ACCESS_CONTEXT-004 — GET /api/users/current/tenant

**Role in this Feature:** Primary Business Api.

**Current Frontend:** `src/MyHealth.Web/content/app/components/users/services/usersService.js` calls `GET /api/users/current/tenant`.

**Confirmed Backend:** `GET /api/users/current/tenant` implemented by `UsersController.GetCurrentTenantAsync`.

### Unresolved or Dynamic Integrations

#### API-USER_ACCESS_CONTEXT-DISCOVERED-001 — `/api/users/${username}`

**Role in this Feature:** Dynamic Primary Interaction.

**Current Frontend:** `src/MyHealth.Web/content/app/components/users/services/usersService.js` calls `GET `/api/users/${username}``.

**Candidate Existing Backend Contract**

The associated frontend interaction is established, but no deterministic frontend-to-backend mapping proves a contract. The following endpoint is a candidate only and requires confirmation:

- `GET /api/users/{username}` — `UsersController.GetAsync`; response `Task<ApplicationUser>`

**Modernization Requirement:** Confirm the existing integration before implementing this behavior in the target frontend.

#### API-USER_ACCESS_CONTEXT-DISCOVERED-002 — /api/users

**Role in this Feature:** Unresolved Primary Interaction.

**Current Frontend:** `src/MyHealth.Web/content/app/components/users/services/usersService.js` calls `GET /api/users`.

**Candidate Existing Backend Contract**

The associated frontend interaction is established, but no deterministic frontend-to-backend mapping proves a contract. The following endpoint is a candidate only and requires confirmation:

- `GET /api/users` — `UsersController.Get`; response `Task<IEnumerable<ApplicationUser>>`

**Modernization Requirement:** Confirm the existing integration before implementing this behavior in the target frontend.


## 6. Modernization Considerations

### Current Implementation Context

Relevant legacy surfaces: UsersController, user, users, usersService

### Preservation Requirements

- Preserve this approved business behavior during frontend modernization without changing backend contracts.

**Target Design:** Not yet analyzed. If a Figma design is supplied later, it will be mapped to approved Feature behavior, Stories, and Acceptance Criteria.

**Target Architecture:** Pending.

## 7. Decisions Required Before Modernization

| Decision / Question | Why It Matters | Validation Role | Status |
| --- | --- | --- | --- |
| Which claims-driven behaviors must be visible in later Stories without changing existing authorization semantics? | Claims loading is proven, but business meaning and desired presentation are not. | Product Owner / Business Analyst / Customer SME | Pending |

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

- Story IDs: story-user-access-context-access-user-management-views, story-user-access-context-resolve-current-user-and-claims, story-user-access-context-resolve-tenant-context-for-user-functions
- Acceptance Criteria IDs: ac-user-access-context-access-user-management-views-001, ac-user-access-context-resolve-current-user-and-claims-001, ac-user-access-context-resolve-tenant-context-for-user-functions-001
- Source references: src/MyHealth.API/Controllers/UsersController.cs
