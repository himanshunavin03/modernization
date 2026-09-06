# Evidence-Backed Modernization Features

- Readiness: `FEATURES_READY_WITH_LIMITATIONS`
- KG run: `legacy-dashboard-complete-application-demo-v1-2026-09-06-092108`
- Application Understanding run: `legacy-dashboard-complete-application-demo-v1-2026-09-06-092424-957063`
- Feature run: `legacy-dashboard-complete-application-demo-v1-2026-09-06-092505-109274`
- Features: 5

## feature-operational-dashboard-insights: Operational Dashboard Insights

Clinic users can view dashboard summaries and year-based operational reporting while retaining the existing API contracts.

- Module: Dashboard and reporting
- Capabilities: Dashboard visualization, Clinic summary reporting
- Priority: `HIGH`
- API statuses: DYNAMIC, PROVEN, UNRESOLVED
- Workflows: Route dashboard, Dashboard summary loads current tenant, Dashboard expenses load current tenant, Dashboard patient report loads current tenant, Dashboard requests clinic summary, Dashboard requests yearly expenses, Dashboard requests yearly patient report

## feature-doctor-directory-management: Doctor Directory Management

Clinic users can navigate and manage doctor information through a modernized frontend while preserving doctor APIs.

- Module: Doctor management
- Capabilities: Manage doctors
- Priority: `MEDIUM`
- API statuses: PROVEN
- Workflows: Route doctor, Route doctors, Doctors load current tenant

## feature-patient-directory-management: Patient Directory Management

Clinic users can navigate and manage patient information through a modernized frontend while preserving patient APIs.

- Module: Patient management
- Capabilities: Manage patients
- Priority: `MEDIUM`
- API statuses: PROVEN
- Workflows: Route patients, Patients load current tenant

## feature-clinic-appointment-experience: Clinic Appointment Experience

Users can access a modernized clinic appointment experience while the existing appointment contracts remain preserved.

- Module: Appointment management
- Capabilities: Manage clinic appointments
- Priority: `LOW`
- API statuses: PROVEN
- Workflows: Route clinic, Route clinics, Clinics load current tenant

## feature-user-access-context: User Access and Tenant Context

Frontend experiences consistently obtain current user identity, authorization claims, and tenant context from preserved APIs.

- Module: User access and tenant context
- Capabilities: Resolve current user context
- Priority: `HIGH`
- API statuses: PROVEN
- Workflows: Route user, Route users, Users load current tenant, Header loads current user, Header loads current claims, Initial page loads current claims

## POC Selection

- Feature IDs: feature-operational-dashboard-insights
- Razor: `src/MyHealth.Web/Views/Dashboard/Index.cshtml`
- AngularJS: `DashboardController`

## Uncovered Workflows

- Route app
- Route calendar
- Route calendar.daily
- Route calendar.monthly
- Route dailyReport
- Route default
- Route error
