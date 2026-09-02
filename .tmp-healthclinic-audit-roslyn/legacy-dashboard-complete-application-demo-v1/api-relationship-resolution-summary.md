# API Relationship Resolution Summary

- Project ID: `legacy-dashboard-complete-application-demo-v1`
- Resolver version: `2026-09-02`
- Total frontend calls: 33
- Proven before: 10
- Proven after: 32
- New exact static matches: 21
- New exact template matches: 11
- New unique parameterized matches: 0
- Remaining dynamic: 0
- Remaining ambiguous: 0
- External: 1
- No backend match: 0
- Unresolved: 0

## Root Cause

The previous resolver only promoted inline literal AngularJS URLs. Calls routed through `url` variables or simple dynamic template/concatenation expressions never reached deterministic method-plus-route reconciliation, so uniquely matchable endpoints remained unresolved or dynamic.

## Promotions

- ``/api/calendars/user/${user}/year/${year}/month/${month}`` in `src/MyHealth.Web.Stress/content/app/components/calendar/services/calendarService.js` -> `PROVEN_EXACT_TEMPLATE`
- ``/api/calendars/user/${user}/year/${year}/month/${month}/day/${day}`` in `src/MyHealth.Web.Stress/content/app/components/calendar/services/calendarService.js` -> `PROVEN_EXACT_TEMPLATE`
- ``/api/tenants/${tenantId}`` in `src/MyHealth.Web/content/app/components/clinics/services/clinicsService.js` -> `PROVEN_EXACT_TEMPLATE`
- `/api/tenants/list` in `src/MyHealth.Web/content/app/components/clinics/services/clinicsService.js` -> `PROVEN_EXACT_STATIC`
- `/api/tenants/` in `src/MyHealth.Web/content/app/components/clinics/services/clinicsService.js` -> `PROVEN_EXACT_STATIC`
- `/api/tenants/` in `src/MyHealth.Web/content/app/components/clinics/services/clinicsService.js` -> `PROVEN_EXACT_STATIC`
- ``/api/tenants/${tenantId}`` in `src/MyHealth.Web/content/app/components/clinics/services/clinicsService.js` -> `PROVEN_EXACT_TEMPLATE`
- `/api/reports/clinicsummary` in `src/MyHealth.Web/content/app/components/dashboard/services/dashboardService.js` -> `PROVEN_EXACT_STATIC`
- `'/api/reports/expenses/' + year` in `src/MyHealth.Web/content/app/components/dashboard/services/dashboardService.js` -> `PROVEN_EXACT_TEMPLATE`
- `'/api/reports/patients/' + year` in `src/MyHealth.Web/content/app/components/dashboard/services/dashboardService.js` -> `PROVEN_EXACT_TEMPLATE`
- ``/api/doctors/${doctorId}`` in `src/MyHealth.Web/content/app/components/doctors/services/doctorsService.js` -> `PROVEN_EXACT_TEMPLATE`
- `/api/doctors` in `src/MyHealth.Web/content/app/components/doctors/services/doctorsService.js` -> `PROVEN_EXACT_STATIC`
- `/api/doctors/` in `src/MyHealth.Web/content/app/components/doctors/services/doctorsService.js` -> `PROVEN_EXACT_STATIC`
- `/api/doctors/` in `src/MyHealth.Web/content/app/components/doctors/services/doctorsService.js` -> `PROVEN_EXACT_STATIC`
- `'/api/doctors/' + doctorId` in `src/MyHealth.Web/content/app/components/doctors/services/doctorsService.js` -> `PROVEN_EXACT_TEMPLATE`
- `/api/patients` in `src/MyHealth.Web/content/app/components/patients/services/patientsService.js` -> `PROVEN_EXACT_STATIC`
- ``/api/patients/${patientId}`` in `src/MyHealth.Web/content/app/components/patients/services/patientsService.js` -> `PROVEN_EXACT_TEMPLATE`
- ``/api/users/${username}`` in `src/MyHealth.Web/content/app/components/users/services/usersService.js` -> `PROVEN_EXACT_TEMPLATE`
- `/api/users` in `src/MyHealth.Web/content/app/components/users/services/usersService.js` -> `PROVEN_EXACT_STATIC`
- `/api/users/` in `src/MyHealth.Web/content/app/components/users/services/usersService.js` -> `PROVEN_EXACT_STATIC`

## Important Cases

- `/api/doctors` in `src/MyHealth.Web/content/app/components/doctors/services/doctorsService.js` -> `PROVEN_EXACT_STATIC` (HTTP method and normalized route/template uniquely identify one backend endpoint.)
- ``/api/doctors/${doctorId}`` in `src/MyHealth.Web/content/app/components/doctors/services/doctorsService.js` -> `PROVEN_EXACT_TEMPLATE` (HTTP method and normalized route/template uniquely identify one backend endpoint.)
- `/api/patients` in `src/MyHealth.Web/content/app/components/patients/services/patientsService.js` -> `PROVEN_EXACT_STATIC` (HTTP method and normalized route/template uniquely identify one backend endpoint.)
- `'/api/reports/expenses/' + year` in `src/MyHealth.Web/content/app/components/dashboard/services/dashboardService.js` -> `PROVEN_EXACT_TEMPLATE` (HTTP method and normalized route/template uniquely identify one backend endpoint.)
- `'/api/reports/patients/' + year` in `src/MyHealth.Web/content/app/components/dashboard/services/dashboardService.js` -> `PROVEN_EXACT_TEMPLATE` (HTTP method and normalized route/template uniquely identify one backend endpoint.)
- `/api/reports/clinicsummary` in `src/MyHealth.Web/content/app/components/dashboard/services/dashboardService.js` -> `PROVEN_EXACT_STATIC` (HTTP method and normalized route/template uniquely identify one backend endpoint.)
- ``/api/tenants/${tenantId}`` in `src/MyHealth.Web/content/app/components/clinics/services/clinicsService.js` -> `PROVEN_EXACT_TEMPLATE` (HTTP method and normalized route/template uniquely identify one backend endpoint.)
- `/api/tenants/list` in `src/MyHealth.Web/content/app/components/clinics/services/clinicsService.js` -> `PROVEN_EXACT_STATIC` (HTTP method and normalized route/template uniquely identify one backend endpoint.)
- `/api/users/current/user` in `src/MyHealth.Web/content/app/components/shared/controllers/headerController.js` -> `PROVEN_EXACT_STATIC` (HTTP method and normalized route/template uniquely identify one backend endpoint.)
- `/api/users/current/claims` in `src/MyHealth.Web/content/app/components/shared/controllers/headerController.js` -> `PROVEN_EXACT_STATIC` (HTTP method and normalized route/template uniquely identify one backend endpoint.)
