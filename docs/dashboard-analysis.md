# Dashboard Source Discovery

## Scope and Method

Inspected only these requested paths in the read-only reference checkout:

- `source/HealthClinic.biz/src/MyHealth.Web/Views/Dashboard`
- `source/HealthClinic.biz/src/MyHealth.Web/Views/Shared`
- `source/HealthClinic.biz/src/MyHealth.Web/Controllers`
- `source/HealthClinic.biz/src/MyHealth.Web/Models`

The final requested Models path does not exist in this checkout. This report does not infer details from paths outside that scope.

## Verified Dashboard Flow

`DashboardController` has an `[Authorize]` attribute and its `Index` action returns the default Dashboard view (`source/HealthClinic.biz/src/MyHealth.Web/Controllers/DashboardController.cs:6-11`). `Views/Dashboard/Index.cshtml` selects `_LayoutPrivate` and composes `_Header`, `_LeftMenu`, `_Content`, and `_Footer` (`source/HealthClinic.biz/src/MyHealth.Web/Views/Dashboard/Index.cshtml:1-13`).

The private layout renders the body, includes private-site CSS, emits Application Insights JavaScript, and loads `lib.js`, `site.js`, and `app.js` in both development and production variants (`source/HealthClinic.biz/src/MyHealth.Web/Views/Shared/_LayoutPrivate.cshtml:1-31`).

## Dashboard Razor Views and Shared Layouts

| Source | Verified purpose |
| --- | --- |
| `Views/Dashboard/Index.cshtml` | Protected Dashboard page composition and `_LayoutPrivate` selection. |
| `Views/Dashboard/_Header.cshtml` | Header wrapper containing a `header-bar` custom element. |
| `Views/Dashboard/_LeftMenu.cshtml` | Sidebar wrapper with collapsible state and a `left-menu` custom element. |
| `Views/Dashboard/_Content.cshtml` | Main content outlet (`ui-view`), toaster container, and loading overlay. |
| `Views/Dashboard/_Footer.cshtml` | HealthClinic footer and four empty-href sitemap links. |
| `Views/Shared/_LayoutPrivate.cshtml` | Dashboard layout; private CSS, Application Insights, and client scripts. |
| `Views/Shared/_Layout.cshtml` | General public layout with public CSS and scripts; not selected by Dashboard Index. |
| `Views/Shared/_LayoutAppointments.cshtml` | Appointment-specific layout; not selected by Dashboard Index. |
| `Views/Shared/_Footer.cshtml` | Shared duplicate-style footer; not directly included by Dashboard Index. |
| `Views/Shared/_ValidationScriptsPartial.cshtml` | jQuery validation scripts; not referenced by the inspected Dashboard view. |
| `Views/Shared/Error.cshtml` | Generic error page. |

## Navigation and User Actions

- The Dashboard header delegates its actual content to `header-bar` (`Views/Dashboard/_Header.cshtml:1-3`).
- The sidebar is labeled `MENU`; its hamburger control toggles `menuOpen`, which changes the sidebar `show` class (`Views/Dashboard/_LeftMenu.cshtml:1-10`).
- The actual menu entries and their destinations are delegated to `left-menu` and are not present in the approved Razor scope (`Views/Dashboard/_LeftMenu.cshtml:8-10`).
- Routed content is inserted into the AngularJS `ui-view` outlet (`Views/Dashboard/_Content.cshtml:1-4`).
- The footer exposes Terms, Privacy, Contact, and Sitemap links, but each has an empty `href`, so a destination is not proven (`Views/Dashboard/_Footer.cshtml:6-12`).
- A successful account login redirects to a local return URL, otherwise `Dashboard/Index` (`Controllers/AccountController.cs:35-40`, `Controllers/AccountController.cs:49-58`).

## UI Controls

| Control or capability | Evidence |
| --- | --- |
| Collapsible sidebar/menu | `ng-click="menuOpen = !menuOpen"` and `ng-class` in `Views/Dashboard/_LeftMenu.cshtml:1-6`. |
| Header component host | `<header-bar />` in `Views/Dashboard/_Header.cshtml:1-3`. |
| Menu component host | `<left-menu>` in `Views/Dashboard/_LeftMenu.cshtml:8-10`. |
| Routed feature-content host | `ui-view` attribute in `Views/Dashboard/_Content.cshtml:1-4`. |
| Toast notifications | `toaster-container` in `Views/Dashboard/_Content.cshtml:7`. |
| Loading indicator and message | Overlay controlled by `loading` and `loadingInfo` in `Views/Dashboard/_Content.cshtml:9-12`. |
| Footer links | Terms, Privacy, Contact, Sitemap in `Views/Dashboard/_Footer.cshtml:6-12`. |

No cards, tables, charts, forms, filters, or feature-level buttons are present in the inspected Dashboard Razor files.

## Controllers, Models, and View Models

- `DashboardController.Index()` returns the Dashboard view and exposes no model or service dependency in the inspected controller (`Controllers/DashboardController.cs:6-12`).
- `AccountController` uses `UserManager<ApplicationUser>` and `SignInManager<ApplicationUser>` (`Controllers/AccountController.cs:11-20`), serves GET Login (`Controllers/AccountController.cs:22-25`), and accepts `LoginViewModel` on POST (`Controllers/AccountController.cs:27-46`).
- The POST Login endpoint validates model state, calls `PasswordSignInAsync`, and presents an `Invalid login attempt` model error on failure (`Controllers/AccountController.cs:29-46`).
- `HomeController.Index()` returns its default view; it has no shown Dashboard dependency (`Controllers/HomeController.cs:5-10`).
- The requested `src/MyHealth.Web/Models` directory was absent. `AccountController` instead imports `MyHealth.Model` and `MyHealth.Web.Viewmodels` (`Controllers/AccountController.cs:3-4`); their definitions are outside the permitted source scope.

## Authentication and Authorization

- Dashboard access is protected by `[Authorize]` (`Controllers/DashboardController.cs:6`).
- Login uses ASP.NET Identity `UserManager`, `SignInManager`, and password sign-in (`Controllers/AccountController.cs:1`, `Controllers/AccountController.cs:11-20`, `Controllers/AccountController.cs:35-36`).
- The login POST is protected by `[ValidateAntiForgeryToken]` (`Controllers/AccountController.cs:27-29`).

## API, Service, Repository, and Database Dependencies

- Application Insights telemetry is injected into `_LayoutPrivate` and `_Layout` (`Views/Shared/_LayoutPrivate.cshtml:1,15`; `Views/Shared/_Layout.cshtml:1,11`).
- The Dashboard Razor/controller scope has no direct API, repository, database, or service call beyond the authentication managers in `AccountController`.
- `app.js` is loaded by `_LayoutPrivate` (`Views/Shared/_LayoutPrivate.cshtml:20-28`), but its client-side API calls and state configuration were not inspected because it is outside the authorized scope.

## Proposed Neo4j Knowledge Graph

| Node label | Proposed identifying properties | Relationships |
| --- | --- | --- |
| `Controller` | `name: DashboardController`, `path` | `AUTHORIZES -> AuthorizationPolicy`; `DECLARES -> Action`; `RETURNS -> View` |
| `Action` | `name: Index`, `httpMethod: GET` | `RETURNS -> View` |
| `View` | `name: Dashboard/Index`, `path` | `USES_LAYOUT -> Layout`; `RENDERS -> PartialView` |
| `Layout` | `name: _LayoutPrivate`, `path` | `LOADS -> ScriptAsset`; `LOADS -> StyleAsset`; `EMITS -> TelemetryIntegration` |
| `PartialView` | `name`, `path` | `HOSTS -> ClientComponent`; `HOSTS -> RouterOutlet`; `HOSTS -> UiControl` |
| `ClientComponent` | `name: header-bar` or `left-menu` | `UNRESOLVED_IMPLEMENTATION_IN -> ExternalSourceScope` |
| `UiControl` | `type: sidebar-toggle|toast-container|loading-overlay|footer-link` | `TRIGGERS -> ClientState` where proven |
| `AuthorizationPolicy` | `name: Authorize` | `PROTECTS -> Controller` |
| `Controller` | `name: AccountController`, `path` | `DEPENDS_ON -> AuthenticationManager`; `DECLARES -> Action` |
| `AuthenticationManager` | `type: UserManager|SignInManager` | `AUTHENTICATES -> ApplicationUser` |
| `ViewModel` | `name: LoginViewModel` | `BOUND_TO -> Action`; `UNRESOLVED_IMPLEMENTATION_IN -> ExternalSourceScope` |
| `ScriptAsset` | `path: ~/app/app.js` | `HOSTS_IMPLEMENTATION_FOR -> ClientComponent` (candidate; requires inspection) |

## Needs Review

- The `header-bar` and `left-menu` implementations, menu items, routes, and user interactions are not proven because their client-side sources were outside this task's scope.
- The states/views mounted under `ui-view` are not proven from the Razor files.
- Any dashboard cards, tables, charts, data filters, forms, or feature-level buttons require inspection of the client-side application sources before they can be modeled or generated.
- `LoginViewModel`, `ApplicationUser`, and the persistence/identity configuration are not available in the requested Models folder, which is absent in this checkout.
- The Application Insights integration is proven as a layout dependency; its configuration, destination, and privacy treatment are not proven.
- Footer destinations are unproven because their `href` values are empty.

## Recommended Angular 22 Target Feature

Proposed first target: a protected lazy route at `/dashboard` in an Nx modular monolith. Create a standalone `DashboardShellComponent` with `ChangeDetectionStrategy.OnPush`, composed of standalone header, sidebar, content-shell, notification, loading-overlay, and footer components. Use Signals for `menuOpen`, loading state, and loading message; replace the AngularJS `ui-view` with Angular Router's `router-outlet` and lazy feature routes once their route inventory is discovered.

No dashboard data form is proven, so do not generate a typed Reactive Form yet. Preserve a typed `LoginRequest` model and use a typed Reactive Form only for the separately confirmed login feature. Generate a typed Dashboard API client only after client/API contracts are discovered; an initial empty shell should not invent endpoints.

Recommended Nx boundaries: `libs/dashboard/feature-shell`, `libs/dashboard/ui-header`, `libs/dashboard/ui-sidebar`, `libs/dashboard/ui-footer`, `libs/dashboard/ui-loading`, `libs/auth/data-access`, and `libs/shared/util-state`. Guard `/dashboard` with an authentication guard and use an HTTP interceptor only after the chosen authentication/BFF policy is defined.

Generate later: unit tests for protected route guarding, sidebar Signal toggling, loading overlay visibility/message, footer link behavior after destinations are known, and contract tests for any discovered API client. Add component and navigation integration tests after `header-bar`, `left-menu`, and `ui-view` destinations are recovered from approved source evidence.
