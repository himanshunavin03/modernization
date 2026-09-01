# feature-user-access-context — User Access and Tenant Context

## 1. Feature Summary

Supplies current user identity, authorization claims, and tenant context to shared frontend behavior.

The Feature appears to support consistent access to user and tenant context across frontend areas.

The Feature provides the business interactions described below through the current application.

Preserve proven identity, claims, and tenant contracts as reusable target-frontend context behavior without redesigning backend authorization.

## 2. Functional Behavior

### Access User Management Views

A user detail experience is available. A user list experience is available.

### Resolve Current User and Claims

The header has current user identity. The header has current claims. Initial-page behavior has current claims.

### Resolve Tenant Context for User Functions

User functionality has tenant context.

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
so that I can use access user management views.

**Business Context**

Represents the approved user-management navigation behavior.

#### Acceptance Criteria

##### AC-USER-ACCESS-CONTEXT-ACCESS-USER-MANAGEMENT-VIEWS-001 — Access User Management Views Behavior

**Given** User detail navigation is initiated.  
**When** Access existing user list and detail views  
**Then** A user detail experience is available. A user list experience is available.

### STORY-USER-ACCESS-CONTEXT-RESOLVE-CURRENT-USER-AND-CLAIMS — Resolve Current User and Claims

**Story**

As an application user,  
I want to make current user identity and claims available to shared application behavior,  
so that the header has current user identity. The header has current claims. Initial-page behavior has current claims.

**Business Context**

Combines the approved identity and claims retrieval workflows used by shared header and initial-page behavior.

#### Acceptance Criteria

##### AC-USER-ACCESS-CONTEXT-RESOLVE-CURRENT-USER-AND-CLAIMS-001 — Resolve Current User and Claims Behavior

**Given** Shared header initialization needs current user identity.  
**When** Make current user identity and claims available to shared application behavior  
**Then** The header has current user identity. The header has current claims. Initial-page behavior has current claims.

### STORY-USER-ACCESS-CONTEXT-RESOLVE-TENANT-CONTEXT-FOR-USER-FUNCTIONS — Resolve Tenant Context for User Functions

**Story**

As an application user,  
I want to make current tenant context available to user functionality,  
so that user functionality has tenant context.

**Business Context**

Represents the proven tenant-context interaction and its approved tenant-scoped behavior rule.

#### Acceptance Criteria

##### AC-USER-ACCESS-CONTEXT-RESOLVE-TENANT-CONTEXT-FOR-USER-FUNCTIONS-001 — Resolve Tenant Context for User Functions Behavior

**Given** User functionality needs tenant context.  
**When** Make current tenant context available to user functionality  
**Then** User functionality has tenant context.

## 5. Integration & Data Context

### Header loads current user

Established relationship must be preserved.

### Header loads current claims

Established relationship must be preserved.

### Initial page loads current claims

Established relationship must be preserved.

### Users load current tenant

Established relationship must be preserved.

- **Application user request:** Information used when requesting an application-user operation.
- **Tenant request:** Information associated with tenant operations.

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
