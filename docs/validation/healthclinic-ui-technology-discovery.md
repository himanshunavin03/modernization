# HealthClinic UI Technology Discovery

## Scope and Method

This is a read-only inventory of `source/HealthClinic.biz`. It uses solution membership, manifests, file paths, and source references only. No graph, Neo4j, Docker, generated artifact, or source change was made.

## Repository/Application Map

| Area | Evidence | Classification |
| --- | --- | --- |
| ASP.NET application family | `01_Demos_ASPNET5.sln` includes `MyHealth.Web`, `MyHealth.API`, `MyHealth.Data`, `MyHealth.Model`, and `MyHealth.Office365`. | Primary web and backend family. |
| Primary web application | `src/MyHealth.Web/MyHealth.Web.xproj` and `project.json` declare ASP.NET MVC, Razor tooling, Kestrel, static files, and project references to API, data, model, and Office365 layers. | Legacy ASP.NET MVC/Razor UI. |
| API/backend | `src/MyHealth.API/MyHealth.API.xproj`; `project.json` declares ASP.NET MVC and HTTP server dependencies; `Controllers/` includes `ReportsController`, `UsersController`, `DoctorsController`, and other API controllers. | ASP.NET API/backend. |
| Data and domain | `src/MyHealth.Data/MyHealth.Data.xproj` contains Entity Framework repositories and `MyHealthContext`; `src/MyHealth.Model/MyHealth.Model.xproj` contains domain entities. `MyHealth.Office365` is an integration library. | Shared backend libraries. |
| Additional web applications | `src/MyHealth.Web.Stress/MyHealth.Web.Stress.xproj` has Razor `Views/`; `07_Demos_NodeClinics.sln` contains `MyHealth.Web.Clinics.njsproj`, whose `package.json` declares Express. `SugarTrackerWeb` is a separate .NET web project in `08_Demos_IoT.sln`. | Separate UI/web applications, not the Dashboard application. |
| Cordova/mobile | `03_Demos_Cordova.sln` contains `MyHealth.Client.Cordova.jsproj`. Its `config.xml` identifies a Cordova widget and plugins; `package.json` contains mobile build dependencies. | Cordova mobile application. |
| Native/mobile | `02_Demos_NativeMicrosoftApps.sln`, `04_Demos_NativeXamarinApps.sln`, `05_Demos_NativeApps.sln`, and `06_Demos_MobileApp.sln` contain UWP, desktop, Android, iOS, WatchKit, Xamarin, and mobile projects. | Native/mobile applications, outside this web POC. |
| Other solutions | Ten solution files are present: `01_Demos_ASPNET5.sln`, `02_Demos_NativeMicrosoftApps.sln`, `03_Demos_Cordova.sln`, `04_Demos_NativeXamarinApps.sln`, `04_Demos_NativeXamariniOSApps.sln`, `05_Demos_NativeApps.sln`, `06_Demos_MobileApp.sln`, `07_Demos_NodeClinics.sln`, `08_Demos_IoT.sln`, and `10_Demos_Deployment.sln`. | Multi-application sample repository. |

## UI Technology Inventory

### Legacy ASP.NET MVC/Razor UI

- `src/MyHealth.Web/project.json` declares `Microsoft.AspNet.Mvc`, `Microsoft.AspNet.Tooling.Razor`, Kestrel, and static-file dependencies.
- Razor views are under `src/MyHealth.Web/Views/`, including `Home/Index.cshtml`, `Dashboard/Index.cshtml`, `Appointments/Index.cshtml`, `Account/Login.cshtml`, shared layouts, and Dashboard partials.
- `src/MyHealth.Web/Controllers/` contains `AccountController.cs`, `DashboardController.cs`, and `HomeController.cs`.
- `DashboardController.Index()` is `[Authorize]` and returns the Dashboard view.

### Legacy AngularJS 1.x Client-Side Code

- `src/MyHealth.Web/bower.json` declares `angular` `~1.4.5`, `angular-ui-router` `~0.2.15`, `angular-animate` `1.4.7`, Angular Bootstrap, and AngularJS toaster.
- `src/MyHealth.Web/content/app/app.module.js` calls `angular.module('myHealth', [...])`, including `ui.router`, and configures `dashboard`, doctor, patient, report, user, and clinic routes.
- Feature folders under `src/MyHealth.Web/content/app/components/` include `dashboard`, `doctors`, `patients`, `dailyReport`, `users`, `clinics`, and `shared`.
- This is **Legacy AngularJS 1.x client-side code**, not modern Angular.

### Modern Angular, React, and Vue

- No `angular.json` was found in `source/HealthClinic.biz`.
- No inspected `package.json` or `bower.json` declares `@angular/core`, React, or Vue.
- Therefore, there is no source evidence of a modern Angular, React, or Vue application in this repository inventory.

### Cordova

- `src/MyHealth.Client.Cordova/config.xml` declares the Cordova XML namespace, `healthclinic.client.doctors` widget, Android/iOS/Windows/WP8 platforms, and Cordova plugins such as device, dialogs, file, in-app browser, and splashscreen.
- `src/MyHealth.Client.Cordova/package.json` includes Cordova-era build tooling; this is a Cordova/mobile application, not the `MyHealth.Web` Dashboard UI.

## `src/MyHealth.Web` Discovery

The primary application is a **Legacy ASP.NET MVC/Razor UI** with an embedded **Legacy AngularJS 1.x client-side code** area.

- Server-rendered entry points: `Views/Home/Index.cshtml` is public Razor content; `Views/Dashboard/Index.cshtml` uses `_LayoutPrivate` and composes Dashboard `_Header`, `_LeftMenu`, `_Content`, and `_Footer`; `Views/Appointments/Index.cshtml` similarly composes Razor partials.
- MVC controllers: `DashboardController`, `AccountController`, and `HomeController`; the protected Dashboard is served by `DashboardController.Index()`.
- Embedded client-side area: `_LayoutPrivate.cshtml` loads `/app/app.js`; `Views/Dashboard/_Content.cshtml` contains `<div ... ui-view>`. `app.module.js` configures AngularJS UI Router states and templates under `/app/components/...`.
- Conclusion: AngularJS is embedded inside the authenticated Razor-rendered Dashboard shell, not a separately hosted SPA. The Razor layout and partials provide the shell/navigation regions while AngularJS owns routed content in `ui-view`.
- Dashboard API calls in `content/app/components/dashboard/services/dashboardService.js`: `GET /api/users/current/tenant`, `GET /api/reports/clinicsummary`, `GET /api/reports/expenses/` plus year, and `GET /api/reports/patients/` plus year. The latter three use the tenant result in a `TenantId` request header.

## Modernization Recommendation

| Candidate scope | Boundary | Suitability |
| --- | --- | --- |
| Razor-first Angular 22 migration | Replace a small server-rendered Razor page/partial set while retaining server MVC boundaries initially. | Lower-risk, but does not demonstrate replacement of the Dashboard's client-side routed content. |
| Hybrid Razor plus AngularJS-to-Angular-22 migration | Rebuild the authenticated Dashboard shell, AngularJS route, Dashboard template, service, and proven Dashboard API calls as a **Target Angular 22 application**. | Best choice for a two-to-three-day customer POC: it proves a complete protected UI flow and makes the legacy technology boundary explicit without widening into other application families. |

The hybrid Dashboard flow is recommended. It is bounded by existing evidence, includes both real legacy UI layers, and avoids incorrectly representing AngularJS as modern Angular.

## Customer Terminology

- Use **Legacy ASP.NET MVC/Razor UI** for `MyHealth.Web` controllers, Razor views, layouts, and partials.
- Use **Legacy AngularJS 1.x client-side code** for `content/app`, `angular.module(...)`, AngularJS UI Router, and the `ui-view` content region.
- Use **Target Angular 22 application** only for the proposed modernization output.
- Do not call AngularJS “Angular 22” or “modern Angular.”

## Current Profile Assessment

`config/profiles/healthclinic-dashboard.yaml` is suitable as a bounded **complete legacy UI-flow demo** for the Dashboard because it selects Razor Dashboard/shared files, `DashboardController.cs`, `app.module.js`, Dashboard AngularJS code, and shared AngularJS directives. It is not a pure .NET/Razor-to-Angular demo because it intentionally includes Legacy AngularJS 1.x client-side code.

For a pure .NET/Razor-to-Angular demo, a separate profile would need to remove `content/app/app.module.js`, `content/app/components/dashboard`, and shared AngularJS directive/module paths, then explicitly select the Razor page/layout/partials and supporting MVC controller(s). That narrower profile would not demonstrate the legacy routed Dashboard content currently hosted in `ui-view`.
