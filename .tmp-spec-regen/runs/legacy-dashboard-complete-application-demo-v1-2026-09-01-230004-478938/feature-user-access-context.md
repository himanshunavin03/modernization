# feature-user-access-context — User Access and Tenant Context

## 1. Feature Summary

### Purpose

Provide current user, claims, and tenant context to shared and user-management frontend flows.

### Current Business Capability

The current application makes the established user list and detail views available to users. The header has current user identity. The header has current claims. Initial-page behavior has current claims. User functionality has tenant context.

### Business Value

Maintains the established current user identity and claims used by shared application behavior. Maintains the established current tenant context used by user functionality. Specific stakeholder outcomes for one or more access capabilities are not established and require confirmation.

**Business Value Status:** Requires Stakeholder Enrichment.

### Modernization Objective

Preserve proven identity, claims, and tenant contracts as reusable target-frontend context behavior without redesigning backend authorization.

## 2. Functional Behavior

### Access User Management Views

The current application makes the established user list and detail views available to users.

### Resolve Current User and Claims

The header has current user identity. The header has current claims. Initial-page behavior has current claims.

### Resolve Tenant Context for User Functions

User functionality has tenant context.

The available requirements establish a general application user; no more specific business persona is authoritative.

**Feature Name / Behavior Alignment:** Aligned.

## 3. Scope

### In Scope

- Approved user routes, user surfaces, identity/claims/tenant workflows, one tenant-context rule, and four proven API relationships.

### Not Established by Current Evidence

- Backend identity redesign, authorization policy redesign, and inferred meaning for individual claims.

## 4. User Stories & Acceptance Criteria

### STORY-USER-ACCESS-CONTEXT-ACCESS-USER-MANAGEMENT-VIEWS — Access User Management Views

**Story**

As an application user,

I want to access existing user list and detail views.

Business outcome: Requires stakeholder confirmation; current evidence establishes the capability but not its specific business purpose.

**Business Context**

Represents the approved user-management navigation behavior.

**Business Value Status:** Not Established.

#### Acceptance Criteria

##### AC-USER-ACCESS-CONTEXT-ACCESS-USER-MANAGEMENT-VIEWS-001 — Access User Management Views Behavior

**Quality Status:** Testable With Evidence Limitation.

**Given** User detail navigation is initiated

**When** the user accesses existing user list and detail views

**Then** the established user list and detail views are available.

**Evidence Limitation**

Current evidence does not establish a complete customer-approved definition of the information or presentation details that must be retained.

**Current Backend Contract References**

- `API-USER_ACCESS_CONTEXT-DISCOVERED-001`
- `API-USER_ACCESS_CONTEXT-DISCOVERED-002`

### STORY-USER-ACCESS-CONTEXT-RESOLVE-CURRENT-USER-AND-CLAIMS — Resolve Current User and Claims

**Story**

As an application user,

I want to make current user identity and claims available to shared application behavior,

so that shared application behavior retains its established identity and claims context.

**Business Context**

Combines the approved identity and claims retrieval workflows used by shared header and initial-page behavior.

**Business Value Status:** Supported Interpretation.

#### Acceptance Criteria

##### AC-USER-ACCESS-CONTEXT-RESOLVE-CURRENT-USER-AND-CLAIMS-001 — Resolve Current User and Claims Behavior

**Quality Status:** Fully Testable From Evidence.

**Given** Shared header initialization needs current user identity

**When** the application makes current user identity and claims available to shared application behavior

**Then** the header has current user identity; and the header has current claims; and initial-page behavior has current claims.

**Current Backend Contract References**

- `API-USER_ACCESS_CONTEXT-001`
- `API-USER_ACCESS_CONTEXT-002`
- `API-USER_ACCESS_CONTEXT-003`

### STORY-USER-ACCESS-CONTEXT-RESOLVE-TENANT-CONTEXT-FOR-USER-FUNCTIONS — Resolve Tenant Context for User Functions

**Story**

As an application user,

I want to make current tenant context available to user functionality,

so that user functionality retains its established tenant-aware behavior.

**Business Context**

Represents the proven tenant-context interaction and its approved tenant-scoped behavior rule.

**Business Value Status:** Supported Interpretation.

#### Acceptance Criteria

##### AC-USER-ACCESS-CONTEXT-RESOLVE-TENANT-CONTEXT-FOR-USER-FUNCTIONS-001 — Resolve Tenant Context for User Functions Behavior

**Quality Status:** Fully Testable From Evidence.

**Given** User functionality needs tenant context

**When** the application makes current tenant context available to user functionality

**Then** user functionality has tenant context.

**Current Backend Contract References**

- `API-USER_ACCESS_CONTEXT-004`

## 5. Existing Backend Integration

Confirmed existing backend API contracts are preserved integration boundaries for the target frontend unless an explicitly approved change modifies them.

### Primary Business APIs

#### API-USER_ACCESS_CONTEXT-001 — /api/users/current/user

**Role in this Feature:** Primary Business Api.

**Current Frontend:** `src/MyHealth.Web/content/app/components/shared/controllers/headerController.js` calls `GET /api/users/current/user`.

**Confirmed Backend:** `GET /api/users/current/user` implemented by `UsersController.GetCurrentUserAsync`.

#### API-USER_ACCESS_CONTEXT-002 — /api/users/current/claims

**Role in this Feature:** Primary Business Api.

**Current Frontend:** `src/MyHealth.Web/content/app/components/shared/controllers/headerController.js` calls `GET /api/users/current/claims`.

**Confirmed Backend:** `GET /api/users/current/claims` implemented by `UsersController.GetCurrentClaimsAsync`.

#### API-USER_ACCESS_CONTEXT-003 — /api/users/current/claims

**Role in this Feature:** Primary Business Api.

**Current Frontend:** `src/MyHealth.Web/content/app/components/shared/services/initialPageService.js` calls `GET /api/users/current/claims`.

**Confirmed Backend:** `GET /api/users/current/claims` implemented by `UsersController.GetCurrentClaimsAsync`.

#### API-USER_ACCESS_CONTEXT-004 — /api/users/current/tenant

**Role in this Feature:** Primary Business Api.

**Current Frontend:** `src/MyHealth.Web/content/app/components/users/services/usersService.js` calls `GET /api/users/current/tenant`.

**Confirmed Backend:** `GET /api/users/current/tenant` implemented by `UsersController.GetCurrentTenantAsync`.

#### API-USER_ACCESS_CONTEXT-DISCOVERED-001 — `/api/users/${username}`

**Role in this Feature:** Primary Business Api.

**Current Frontend:** `src/MyHealth.Web/content/app/components/users/services/usersService.js` calls `GET `/api/users/${username}`.

**Confirmed Backend:** `GET /api/users/{username}` implemented by `UsersController.GetAsync`.

#### API-USER_ACCESS_CONTEXT-DISCOVERED-002 — /api/users

**Role in this Feature:** Primary Business Api.

**Current Frontend:** `src/MyHealth.Web/content/app/components/users/services/usersService.js` calls `GET /api/users`.

**Confirmed Backend:** `GET /api/users` implemented by `UsersController.Get`.

## 6. Modernization Considerations

### Current Implementation Context

Relevant legacy surfaces: UsersController, user, users, usersService

### Preservation Requirements

- Preserve this approved business behavior during frontend modernization without changing backend contracts.

**Target Design:** Not yet analyzed.

**Target Architecture:** Pending.

## 7. Decisions Required Before Modernization

### Business Clarifications

| Question | Why It Matters | Impact | Owner |
| --- | --- | --- | --- |
| What business outcome should users achieve through Access User Management Views beyond access to the currently established capability? | Current evidence establishes the behavior but not the stakeholder's intended business outcome. | NON_BLOCKING | Product Owner / Business Analyst / Customer SME |
| Which information must be considered mandatory when validating Access User Management Views in the modernized experience? | Current evidence does not establish a complete customer-approved definition of the information or presentation details that must be retained. | BLOCKING | Product Owner / Business Analyst / Customer SME / QA Lead |

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
