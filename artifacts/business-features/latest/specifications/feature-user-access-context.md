# User Access and Tenant Context

**Feature ID:** `feature-user-access-context`  
**Module:** User access and tenant context  
**Capabilities:** Resolve current user context  
**Confidence:** `HIGH`

## Executive Description

User Access and Tenant Context represents shared frontend behavior for obtaining current user identity, current authorization claims, and current tenant context. It also includes user routes and user service/controller surfaces.
The Feature supports other frontend areas by preserving common context contracts. Evidence proves the current-user, current-claims, and current-tenant relationships, but it does not establish broader authorization policy meaning beyond observed claims loading.

## Business Objectives

**CURRENT_OBJECTIVE:** Provide current user, claims, and tenant context to shared and user-management frontend flows.

**MODERNIZATION_OBJECTIVE:** Preserve proven identity, claims, and tenant contracts as reusable target-frontend context behavior without redesigning backend authorization.

## Business Value

- **INFERRED_BUSINESS_VALUE:** The Feature appears to support consistent access to user and tenant context across frontend areas.

## Primary Users / Actors

The endpoints refer to the current application user, but approved Feature evidence does not define a business persona or role.

## Current Business Functionality

- Provides user routes and loads current user identity, claims, and tenant context for frontend use.

## Business Workflows

### Route user

- Trigger: User detail navigation is initiated.
- Steps: Resolve the user route.; Present the user detail surface.
- Outcome: A user detail experience is available.
- Supporting UI: user, UsersController
- API status: `NOT_APPLICABLE`

### Route users

- Trigger: User list navigation is initiated.
- Steps: Resolve the users route.; Present the user list surface.
- Outcome: A user list experience is available.
- Supporting UI: users, UsersController
- API status: `NOT_APPLICABLE`

### Users load current tenant

- Trigger: User functionality needs tenant context.
- Steps: Request current tenant context.; Make tenant context available to user functionality.
- Outcome: User functionality has tenant context.
- Supporting UI: UsersController, usersService
- API status: `PROVEN`

### Header loads current user

- Trigger: Shared header initialization needs current user identity.
- Steps: Request current user identity.; Make identity available to shared header behavior.
- Outcome: The header has current user identity.
- Supporting UI: Not identified
- API status: `PROVEN`

### Header loads current claims

- Trigger: Shared header initialization needs current claims.
- Steps: Request current claims.; Make claims available to shared header behavior.
- Outcome: The header has current claims.
- Supporting UI: Not identified
- API status: `PROVEN`

### Initial page loads current claims

- Trigger: Initial page setup needs current claims.
- Steps: Request current claims.; Make claims available to initial-page behavior.
- Outcome: Initial-page behavior has current claims.
- Supporting UI: Not identified
- API status: `PROVEN`

## Business Rules

- **BR-USER-001:** Tenant-scoped frontend flows obtain current tenant context before continuing.


## Domain Concepts and Information

- **Application user request:** Information used when requesting an application-user operation. Represents user-related information at the preserved API boundary.
- **Tenant request:** Information associated with tenant operations. Represents tenant-related information used by the broader user/tenant context area.
- The Feature exchanges current user identity, authorization claims, current tenant context, and approved user/tenant request concepts.

## Dependencies

- **TECHNICAL:** Header depends on current-user API - Shared header behavior requires preserved current-user and claims integrations.

## API Integration Profile

- PROVEN: 4
- UNRESOLVED: 0
- DYNAMIC: 0
- EXTERNAL: 0
- NO_BACKEND_ROUTE: 0
- `PROVEN`: `src/MyHealth.Web/content/app/components/users/services/usersService.js` -> `/api/users/current/tenant` -> `GET /api/users/current/tenant`
- `PROVEN`: `src/MyHealth.Web/content/app/components/shared/controllers/headerController.js` -> `/api/users/current/user` -> `GET /api/users/current/user`
- `PROVEN`: `src/MyHealth.Web/content/app/components/shared/controllers/headerController.js` -> `/api/users/current/claims` -> `GET /api/users/current/claims`
- `PROVEN`: `src/MyHealth.Web/content/app/components/shared/services/initialPageService.js` -> `/api/users/current/claims` -> `GET /api/users/current/claims`
- Limitation: All approved API relationships are proven, but evidence does not define authorization semantics beyond observed claims loading.

## Current User Experience

- AngularJS user routes and shared initialization behavior obtain identity, claims, and tenant context from existing APIs.

## Current-State Limitations and Concerns

- **BUSINESS_ANALYSIS_LIMITATION:** The approved evidence proves claims loading but not the business interpretation of individual claims or authorization decisions.
- **MODERNIZATION_CONCERN:** Shared user and tenant context should be implemented once for reuse rather than duplicated across modernized Feature areas.

## Modernization Scope

### In Scope

- Approved user routes, user surfaces, identity/claims/tenant workflows, one tenant-context rule, and four proven API relationships.

### Out of Scope

- Backend identity redesign, authorization policy redesign, and inferred meaning for individual claims.

## Assumptions

- None identified from approved evidence.

## Open Questions

- **Q-USER-001:** Which claims-driven behaviors must be visible in later Stories without changing existing authorization semantics? Reason: Claims loading is proven, but business meaning and desired presentation are not.

## Risks and Limitations

- **BUSINESS_ANALYSIS_LIMITATION:** Interpreting claims beyond observed retrieval could create unsupported authorization requirements.
- **TECHNICAL_MODERNIZATION_RISK:** Duplicating shared context behavior across target Features could create inconsistent frontend state handling.

## MODERNIZATION_SUCCESS_INDICATORS

- All four proven identity, claims, and tenant API relationships remain unchanged and reusable in the target frontend.
- No authorization behavior unsupported by approved claims evidence is introduced.

## STORY_DECOMPOSITION_GUIDANCE

- **Navigate user management surfaces:** Groups approved user navigation. Workflows: Route user, Route users
- **Resolve current user and claims for shared UI:** Groups shared identity/claims behavior. Workflows: Header loads current user, Header loads current claims, Initial page loads current claims
- **Resolve tenant context for user functionality:** Separates the tenant-scoped rule and proven integration. Workflows: Users load current tenant

## Technical Traceability

- `src/MyHealth.API/Controllers/UsersController.cs:124` -> `legacy-dashboard-complete-application-demo-v1:Endpoint:GET /api/users/current/user`
- `src/MyHealth.API/Controllers/UsersController.cs:133` -> `legacy-dashboard-complete-application-demo-v1:Endpoint:GET /api/users/current/claims`
- `src/MyHealth.API/Controllers/UsersController.cs:146` -> `legacy-dashboard-complete-application-demo-v1:Endpoint:GET /api/users/current/tenant`

