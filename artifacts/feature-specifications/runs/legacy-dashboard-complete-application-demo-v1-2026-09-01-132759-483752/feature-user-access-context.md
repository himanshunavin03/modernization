# feature-user-access-context — User Access and Tenant Context

## 1. Feature Summary

Supplies current user identity, authorization claims, and tenant context to shared frontend behavior.

The Feature appears to support consistent access to user and tenant context across frontend areas.

The Feature provides the business interactions described below through the current application.

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

so that I can review user list and detail views.

**Business Context**

Represents the approved user-management navigation behavior.

#### Acceptance Criteria

##### AC-USER-ACCESS-CONTEXT-ACCESS-USER-MANAGEMENT-VIEWS-001 — Access User Management Views Behavior

**Given** the related existing application capability is available

**When** the user navigates user management surfaces

**Then** users can access existing user list and detail views

### STORY-USER-ACCESS-CONTEXT-RESOLVE-CURRENT-USER-AND-CLAIMS — Resolve Current User and Claims

**Story**

As an application user,

I want to make current user identity and claims available to shared application behavior,

so that shared application behavior can use current user identity and claims.

**Business Context**

Combines the approved identity and claims retrieval workflows used by shared header and initial-page behavior.

#### Acceptance Criteria

##### AC-USER-ACCESS-CONTEXT-RESOLVE-CURRENT-USER-AND-CLAIMS-001 — Resolve Current User and Claims Behavior

**Given** the related existing application capability is available

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

**Given** the related existing application capability is available

**When** the application resolves tenant context for user functionality

**Then** the application can make current tenant context available to user functionality

**Current Backend Contract References**

- `API-USER_ACCESS_CONTEXT-004`

## 5. Existing Backend API Contract

The existing backend is preserved within the current modernization scope. Confirmed API contracts in this specification are treated as existing integration contracts for the target frontend unless an explicitly approved change modifies them.

### API-USER_ACCESS_CONTEXT-001 — Header loads current user

**Used By**

- Stories: `story-user-access-context-resolve-current-user-and-claims`
- Acceptance Criteria: `ac-user-access-context-resolve-current-user-and-claims-001`

**Current Frontend**

| Item | Existing Implementation |
| --- | --- |
| Technology | Legacy AngularJS 1.x |
| Controller / Component | HeaderController |
| Service | Not established |
| API expression | `GET /api/users/current/user` |
| Source | `src/MyHealth.Web/content/app/components/shared/controllers/headerController.js` |

**Backend Endpoint**

| Item | Contract |
| --- | --- |
| HTTP Method | `GET` |
| Route | `/api/users/current/user` |
| Route Template | `api/[controller]/current/user` |
| Controller | `UsersController` |
| Action | `GetCurrentUserAsync` |
| Source | `src/MyHealth.API/Controllers/UsersController.cs` |

**Request**

No path, query, header, or body contract is established for this endpoint.

**Response**

Response type: `Task<string>`

Field-level contract: Not established from current deterministic evidence.

**Contract Status**

Contract confirmed from existing application evidence.

**Modernization Requirement**

Preserve this backend contract when implementing the target frontend unless an approved change explicitly modifies the integration contract.

### API-USER_ACCESS_CONTEXT-002 — Header loads current claims

**Used By**

- Stories: `story-user-access-context-resolve-current-user-and-claims`
- Acceptance Criteria: `ac-user-access-context-resolve-current-user-and-claims-001`

**Current Frontend**

| Item | Existing Implementation |
| --- | --- |
| Technology | Legacy AngularJS 1.x |
| Controller / Component | HeaderController |
| Service | Not established |
| API expression | `GET /api/users/current/claims` |
| Source | `src/MyHealth.Web/content/app/components/shared/controllers/headerController.js` |

**Backend Endpoint**

| Item | Contract |
| --- | --- |
| HTTP Method | `GET` |
| Route | `/api/users/current/claims` |
| Route Template | `api/[controller]/current/claims` |
| Controller | `UsersController` |
| Action | `GetCurrentClaimsAsync` |
| Source | `src/MyHealth.API/Controllers/UsersController.cs` |

**Request**

No path, query, header, or body contract is established for this endpoint.

**Response**

Response type: `JsonResult`

Field-level contract: Not established from current deterministic evidence.

**Contract Status**

Contract confirmed from existing application evidence.

**Modernization Requirement**

Preserve this backend contract when implementing the target frontend unless an approved change explicitly modifies the integration contract.

### API-USER_ACCESS_CONTEXT-003 — Initial page loads current claims

**Used By**

- Stories: `story-user-access-context-resolve-current-user-and-claims`
- Acceptance Criteria: `ac-user-access-context-resolve-current-user-and-claims-001`

**Current Frontend**

| Item | Existing Implementation |
| --- | --- |
| Technology | Legacy AngularJS 1.x |
| Controller / Component | Not established |
| Service | Not established |
| API expression | `GET /api/users/current/claims` |
| Source | `src/MyHealth.Web/content/app/components/shared/services/initialPageService.js` |

**Backend Endpoint**

| Item | Contract |
| --- | --- |
| HTTP Method | `GET` |
| Route | `/api/users/current/claims` |
| Route Template | `api/[controller]/current/claims` |
| Controller | `UsersController` |
| Action | `GetCurrentClaimsAsync` |
| Source | `src/MyHealth.API/Controllers/UsersController.cs` |

**Request**

No path, query, header, or body contract is established for this endpoint.

**Response**

Response type: `JsonResult`

Field-level contract: Not established from current deterministic evidence.

**Contract Status**

Contract confirmed from existing application evidence.

**Modernization Requirement**

Preserve this backend contract when implementing the target frontend unless an approved change explicitly modifies the integration contract.

### API-USER_ACCESS_CONTEXT-004 — Users load current tenant

**Used By**

- Stories: `story-user-access-context-resolve-tenant-context-for-user-functions`
- Acceptance Criteria: `ac-user-access-context-resolve-tenant-context-for-user-functions-001`

**Current Frontend**

| Item | Existing Implementation |
| --- | --- |
| Technology | Legacy AngularJS 1.x |
| Controller / Component | Not established |
| Service | Not established |
| API expression | `GET /api/users/current/tenant` |
| Source | `src/MyHealth.Web/content/app/components/users/services/usersService.js` |

**Backend Endpoint**

| Item | Contract |
| --- | --- |
| HTTP Method | `GET` |
| Route | `/api/users/current/tenant` |
| Route Template | `api/[controller]/current/tenant` |
| Controller | `UsersController` |
| Action | `GetCurrentTenantAsync` |
| Source | `src/MyHealth.API/Controllers/UsersController.cs` |

**Request**

No path, query, header, or body contract is established for this endpoint.

**Response**

Response type: `Task<int?>`

Field-level contract: Not established from current deterministic evidence.

**Contract Status**

Contract confirmed from existing application evidence.

**Modernization Requirement**

Preserve this backend contract when implementing the target frontend unless an approved change explicitly modifies the integration contract.


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
