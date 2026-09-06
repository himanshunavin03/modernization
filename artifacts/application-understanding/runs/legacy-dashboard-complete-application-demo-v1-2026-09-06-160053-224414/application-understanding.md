# Application Understanding

- Status: `COMPLETE`
- Readiness: `APPLICATION_UNDERSTANDING_READY_WITH_LIMITATIONS`
- Project: `legacy-dashboard-complete-application-demo-v1`
- KG run: `legacy-dashboard-complete-application-demo-v1-2026-09-06-102441`
- Reasoning mode: `INTERACTIVE_AGENT_MODE`
- Evidence packages: 138
- Evidence manifest validation: `PASS`
- Agent claims rejected: 0
- Independently addressable source capabilities: 137

## Application Purpose

Healthcare operations application: A multi-surface application supporting dashboard reporting and the management of clinics, doctors, patients, appointments, and users.

- Primary application type: Hybrid server-rendered and client-side healthcare web application with supporting APIs and mobile clients
- Technical composition: Legacy ASP.NET MVC/Razor, Legacy AngularJS 1.x, ASP.NET Web API, C# domain and data projects, Cordova and native mobile clients
- Major user-facing areas: Dashboard and reporting, Clinics, Doctors, Patients, Appointments, Users
- Major backend areas: HTTP API controllers and actions, Domain and DTO models, Appointment, doctor, patient, report, tenant, and user services

## Business Modules

- **Dashboard and reporting**: Dashboard UI and report API surfaces for clinic summaries, expenses, and patient statistics.
- **Clinic management**: Clinic list and detail client surfaces with tenant API interactions.
- **Doctor management**: Doctor list/detail UI and doctor API operations.
- **Patient management**: Patient list/detail UI and patient API operations.
- **Appointment management**: Razor appointment surface and clinic appointment API operations.
- **User access and tenant context**: User administration plus current-user, claims, and tenant context used by client flows.

## Business Capabilities

- **Dashboard visualization**: Present dashboard information through the Razor host and AngularJS dashboard controller.
- **Clinic summary reporting**: Request clinic summary, yearly expenses, and yearly patient report data.
- **Manage doctors**: List, retrieve, add, update, and delete doctors through exposed UI/API surfaces.
- **Manage patients**: List, retrieve, search, and delete patients through exposed UI/API surfaces.
- **Manage clinic appointments**: Retrieve upcoming appointments and add clinic appointments.
- **Resolve current user context**: Load current user identity, authorization claims, and tenant context for client flows.

## User Workflows

- **Clinics load current tenant**: The clinics service calls the proven current-tenant endpoint.
- **Dashboard summary loads current tenant**: Dashboard summary flow resolves tenant context before report use.
- **Dashboard expenses load current tenant**: Dashboard expenses flow resolves tenant context.
- **Dashboard patient report loads current tenant**: Dashboard patient report flow resolves tenant context.
- **Doctors load current tenant**: The doctors service calls the proven current-tenant endpoint.
- **Patients load current tenant**: The patients service calls the proven current-tenant endpoint.
- **Users load current tenant**: The users service calls the proven current-tenant endpoint.
- **Header loads current user**: The shared header calls the proven current-user endpoint.
- **Header loads current claims**: The shared header calls the proven current-claims endpoint.
- **Initial page loads current claims**: Initial-page setup calls the proven current-claims endpoint.
- **Dashboard requests clinic summary**: The client call exists and a matching endpoint is visible, but this KG does not contain a proven IMPLEMENTED_BY relationship for the pair.
- **Dashboard requests yearly expenses**: The client constructs a year-dependent report URL; it remains dynamic rather than proven.
- **Dashboard requests yearly patient report**: The client constructs a year-dependent report URL; it remains dynamic rather than proven.

## Domain Concepts

- **Patient**: A patient domain type used by application surfaces.
- **Doctor**: A doctor DTO/domain type used by doctor operations.
- **Clinic appointment**: A clinic appointment DTO/domain type.
- **Home appointment**: A home appointment DTO/domain type.
- **Application user request**: A request DTO for adding an application user.
- **Tenant request**: A request DTO for tenant operations.

## Business Rules

- **Client initialization uses current authorization claims**: Header and initial-page client flows obtain claims from the current-claims endpoint.
- **Tenant-scoped client flows resolve current tenant context**: Clinic, dashboard, doctor, patient, and user services call the current-tenant endpoint before tenant-scoped operations.

## Dependencies

- **Dashboard depends on tenant context API**: Dashboard service uses the current-tenant endpoint.
- **Header depends on current-user API**: Header controller uses current-user and claims endpoints.
- **Dashboard depends on reports API contract**: Dashboard service has clinic-summary and year-dependent report calls backed by visible report endpoints, with unresolved/dynamic mappings retained.
- **Doctor UI depends on doctor API contract**: Doctor UI and service operations correspond to visible doctor endpoints, but non-tenant call mappings remain unresolved.
- **Patient UI depends on patient API contract**: Patient UI and service operations correspond to visible patient endpoints, but non-tenant call mappings remain unresolved.

## API Mapping

- Backend endpoints visible: `58`
- Frontend API calls visible: `33`
- Proven API mappings used: `32`
- Unresolved structural calls retained: `0`
- Dynamic API relationships retained: `0`
- External API relationships retained: `1`

## Demonstration Candidates

- Razor: `src/MyHealth.Web/Views/Dashboard/Index.cshtml`
- AngularJS: `DashboardController`

## Limitations

- API evidence retains 0 unresolved structural calls, 0 dynamic URLs, 1 external API, and 0 call without a backend route.
- Roslyn and opaque-dependency limitations remain as approved by the KG readiness gate.
