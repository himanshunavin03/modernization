"""Deterministic Angular 22/Nx workspace templates for the hero Feature."""
from __future__ import annotations

import json


def workspace_files() -> dict[str, str]:
    package = {
        "name": "healthclinic-modernized",
        "version": "0.1.0",
        "private": True,
        "scripts": {
            "start": "nx serve healthclinic-web",
            "build": "nx build healthclinic-web",
            "test": "nx run-many -t test",
            "e2e": "nx e2e healthclinic-web-e2e",
        },
        "dependencies": {
            "@angular/common": "22.1.4", "@angular/compiler": "22.1.4", "@angular/core": "22.1.4",
            "@angular/platform-browser": "22.1.4", "@angular/router": "22.1.4",
            "rxjs": "7.8.2", "tslib": "2.8.1",
        },
        "devDependencies": {
            "@angular/build": "22.1.4", "@angular/compiler-cli": "22.1.4",
            "@nx/angular": "23.2.0", "@nx/eslint": "23.2.0", "@nx/eslint-plugin": "23.2.0",
            "@nx/js": "23.2.0", "@nx/playwright": "23.2.0", "@playwright/test": "1.55.0",
            "@types/node": "24.3.0", "eslint": "9.35.0", "nx": "23.2.0",
            "typescript": "6.0.2", "vitest": "3.2.4",
        },
    }
    nx = {"$schema": "./node_modules/nx/schemas/nx-schema.json", "plugins": [{"plugin": "@nx/eslint/plugin", "options": {"targetName": "lint"}}], "namedInputs": {"default": ["{projectRoot}/**/*", "sharedGlobals"], "production": ["default", "!{projectRoot}/**/*.spec.ts"], "sharedGlobals": []}, "targetDefaults": {"build": {"cache": True, "inputs": ["production", "^production"]}, "test": {"cache": True, "inputs": ["default", "^production"]}}}
    tsconfig = {"compileOnSave": False, "compilerOptions": {"baseUrl": ".", "strict": True, "noImplicitOverride": True, "noPropertyAccessFromIndexSignature": True, "noImplicitReturns": True, "noFallthroughCasesInSwitch": True, "sourceMap": True, "declaration": False, "experimentalDecorators": True, "moduleResolution": "bundler", "importHelpers": True, "target": "ES2022", "module": "preserve", "lib": ["ES2022", "dom"], "paths": {"@healthclinic/dashboard/feature": ["libs/dashboard/feature/src/index.ts"], "@healthclinic/dashboard/ui": ["libs/dashboard/ui/src/index.ts"], "@healthclinic/dashboard/data-access": ["libs/dashboard/data-access/src/index.ts"], "@healthclinic/dashboard/state": ["libs/dashboard/state/src/index.ts"], "@healthclinic/core/platform": ["libs/core/platform/src/index.ts"]}}, "angularCompilerOptions": {"enableI18nLegacyMessageIdFormat": False, "strictInjectionParameters": True, "strictInputAccessModifiers": True, "strictTemplates": True}}
    app_project = {"name": "healthclinic-web", "$schema": "../../node_modules/nx/schemas/project-schema.json", "projectType": "application", "sourceRoot": "apps/healthclinic-web/src", "tags": ["scope:app", "type:application"], "targets": {"build": {"executor": "@angular/build:application", "outputs": ["{options.outputPath}"], "options": {"outputPath": "dist/apps/healthclinic-web", "browser": "apps/healthclinic-web/src/main.ts", "index": "apps/healthclinic-web/src/index.html", "tsConfig": "apps/healthclinic-web/tsconfig.app.json", "assets": [{"glob": "**/*", "input": "apps/healthclinic-web/public"}], "styles": ["apps/healthclinic-web/src/styles.css"]}}, "serve": {"executor": "@angular/build:dev-server", "options": {"buildTarget": "healthclinic-web:build"}}, "test": {"executor": "@angular/build:unit-test", "options": {"tsConfig": "apps/healthclinic-web/tsconfig.spec.json"}}}}
    files = {
        "package.json": json.dumps(package, indent=2) + "\n",
        "nx.json": json.dumps(nx, indent=2) + "\n",
        "tsconfig.base.json": json.dumps(tsconfig, indent=2) + "\n",
        ".gitignore": "node_modules/\ndist/\n.nx/\ntest-results/\nplaywright-report/\n",
        "eslint.config.mjs": ESLINT_CONFIG,
        "README.md": "# HealthClinic Angular 22 Hero Feature\n\nGenerated from the existing application UI, approved requirements, locked architecture, and approved technical tasks. The Prompt 062 Figma fixture was not used.\n\nBuild and generated tests are intentionally `NOT_YET_EXECUTED`; Prompt 064 owns build, test, diagnosis, and repair.\n",
        "apps/healthclinic-web/project.json": json.dumps(app_project, indent=2) + "\n",
        "apps/healthclinic-web/tsconfig.app.json": json.dumps({"extends": "../../tsconfig.base.json", "compilerOptions": {"outDir": "../../dist/out-tsc", "types": []}, "files": ["src/main.ts"], "include": ["src/**/*.d.ts"]}, indent=2) + "\n",
        "apps/healthclinic-web/tsconfig.spec.json": json.dumps({"extends": "../../tsconfig.base.json", "compilerOptions": {"outDir": "../../dist/out-tsc", "types": ["vitest/globals", "node"]}, "include": ["src/**/*.spec.ts", "../../libs/**/*.spec.ts", "src/**/*.d.ts"]}, indent=2) + "\n",
        "apps/healthclinic-web/src/index.html": '<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><title>HealthClinic.biz</title><base href="/"><meta name="viewport" content="width=device-width, initial-scale=1"><script src="runtime-config.js"></script></head><body><healthclinic-root></healthclinic-root></body></html>\n',
        "apps/healthclinic-web/public/runtime-config.js": "globalThis.__HEALTHCLINIC_CONFIG__ = { apiBaseUrl: '' };\n",
        "apps/healthclinic-web/src/main.ts": "import { bootstrapApplication } from '@angular/platform-browser';\nimport { AppComponent } from './app/app.component';\nimport { appConfig } from './app/app.config';\n\nbootstrapApplication(AppComponent, appConfig).catch((error: unknown) => console.error(error));\n",
        "apps/healthclinic-web/src/app/app.component.ts": "import { ChangeDetectionStrategy, Component } from '@angular/core';\nimport { RouterOutlet } from '@angular/router';\n\n@Component({ selector: 'healthclinic-root', standalone: true, imports: [RouterOutlet], template: '<router-outlet />', changeDetection: ChangeDetectionStrategy.OnPush })\nexport class AppComponent {}\n",
        "apps/healthclinic-web/src/app/app.config.ts": "import { ApplicationConfig } from '@angular/core';\nimport { provideHttpClient, withInterceptors } from '@angular/common/http';\nimport { provideRouter } from '@angular/router';\nimport { correlationInterceptor, errorInterceptor, provideRuntimeConfig, type RuntimeConfig } from '@healthclinic/core/platform';\nimport { appRoutes } from './app.routes';\n\nconst runtimeConfig = (globalThis as typeof globalThis & { __HEALTHCLINIC_CONFIG__?: RuntimeConfig }).__HEALTHCLINIC_CONFIG__ ?? { apiBaseUrl: '' };\n\nexport const appConfig: ApplicationConfig = {\n  providers: [\n    provideRouter(appRoutes),\n    provideHttpClient(withInterceptors([correlationInterceptor, errorInterceptor])),\n    provideRuntimeConfig(runtimeConfig),\n  ],\n};\n",
        "apps/healthclinic-web/src/app/app.routes.ts": "import { Routes } from '@angular/router';\nimport { dashboardRouteGuard } from '@healthclinic/core/platform';\nimport { PrivateShellComponent } from './private-shell.component';\n\nexport const appRoutes: Routes = [\n  { path: '', component: PrivateShellComponent, children: [\n    { path: '', pathMatch: 'full', redirectTo: 'dashboard' },\n    { path: 'dashboard', canActivate: [dashboardRouteGuard], loadChildren: () => import('@healthclinic/dashboard/feature').then((entry) => entry.DASHBOARD_ROUTES) },\n  ] },\n  { path: '**', redirectTo: 'dashboard' },\n];\n",
        "apps/healthclinic-web/src/app/private-shell.component.ts": PRIVATE_SHELL_TS,
        "apps/healthclinic-web/src/app/private-shell.component.html": PRIVATE_SHELL_HTML,
        "apps/healthclinic-web/src/app/private-shell.component.css": PRIVATE_SHELL_CSS,
        "apps/healthclinic-web/src/styles.css": GLOBAL_STYLES,
    }
    files.update(_library_files())
    files.update(_test_files())
    return files


def _project(name: str, root: str, tags: list[str]) -> str:
    return json.dumps({"name": name, "$schema": "../../../../node_modules/nx/schemas/project-schema.json", "sourceRoot": f"{root}/src", "projectType": "library", "tags": tags, "targets": {}}, indent=2) + "\n"


def _library_files() -> dict[str, str]:
    return {
        "libs/dashboard/feature/project.json": _project("dashboard-feature", "libs/dashboard/feature", ["scope:dashboard", "type:feature"]),
        "libs/dashboard/feature/src/index.ts": "export { DASHBOARD_ROUTES } from './lib/dashboard.routes';\nexport { DashboardFeatureComponent } from './lib/dashboard-feature.component';\n",
        "libs/dashboard/feature/src/lib/dashboard.routes.ts": "import { Routes } from '@angular/router';\nimport { DashboardFeatureComponent } from './dashboard-feature.component';\n\nexport const DASHBOARD_ROUTES: Routes = [{ path: '', component: DashboardFeatureComponent, title: 'Dashboard' }];\n",
        "libs/dashboard/feature/src/lib/dashboard-feature.component.ts": DASHBOARD_FEATURE_TS,
        "libs/dashboard/feature/src/lib/dashboard-feature.component.html": DASHBOARD_FEATURE_HTML,
        "libs/dashboard/feature/src/lib/dashboard-feature.component.css": DASHBOARD_FEATURE_CSS,
        "libs/dashboard/ui/project.json": _project("dashboard-ui", "libs/dashboard/ui", ["scope:dashboard", "type:ui"]),
        "libs/dashboard/ui/src/index.ts": "export { DashboardChartComponent, type ChartSeries } from './lib/dashboard-chart.component';\nexport { SummaryCardComponent } from './lib/summary-card.component';\nexport { YearNavigatorComponent } from './lib/year-navigator.component';\n",
        "libs/dashboard/ui/src/lib/summary-card.component.ts": SUMMARY_CARD_TS,
        "libs/dashboard/ui/src/lib/year-navigator.component.ts": YEAR_NAVIGATOR_TS,
        "libs/dashboard/ui/src/lib/dashboard-chart.component.ts": DASHBOARD_CHART_TS,
        "libs/dashboard/data-access/project.json": _project("dashboard-data-access", "libs/dashboard/data-access", ["scope:dashboard", "type:data-access"]),
        "libs/dashboard/data-access/src/index.ts": "export { DashboardApiClient } from './lib/dashboard-api.client';\nexport type { ClinicSummary, ExpensesSummary, PatientsSummary } from './lib/dashboard.models';\n",
        "libs/dashboard/data-access/src/lib/dashboard.models.ts": DASHBOARD_MODELS,
        "libs/dashboard/data-access/src/lib/dashboard-api.client.ts": DASHBOARD_API_CLIENT,
        "libs/dashboard/state/project.json": _project("dashboard-state", "libs/dashboard/state", ["scope:dashboard", "type:state"]),
        "libs/dashboard/state/src/index.ts": "export { DashboardStore } from './lib/dashboard.store';\n",
        "libs/dashboard/state/src/lib/dashboard.store.ts": DASHBOARD_STORE,
        "libs/core/platform/project.json": _project("core-platform", "libs/core/platform", ["scope:core", "type:platform"]),
        "libs/core/platform/src/index.ts": "export { RUNTIME_CONFIG, provideRuntimeConfig, type RuntimeConfig } from './lib/runtime-config';\nexport { TenantContextService } from './lib/tenant-context.service';\nexport { dashboardRouteGuard } from './lib/dashboard-route.guard';\nexport { correlationInterceptor } from './lib/correlation.interceptor';\nexport { errorInterceptor, FrontendErrorService } from './lib/error.interceptor';\nexport { FrontendLogger } from './lib/frontend-logger.service';\n",
        "libs/core/platform/src/lib/runtime-config.ts": RUNTIME_CONFIG,
        "libs/core/platform/src/lib/tenant-context.service.ts": TENANT_CONTEXT,
        "libs/core/platform/src/lib/dashboard-route.guard.ts": DASHBOARD_ROUTE_GUARD,
        "libs/core/platform/src/lib/correlation.interceptor.ts": CORRELATION_INTERCEPTOR,
        "libs/core/platform/src/lib/frontend-logger.service.ts": FRONTEND_LOGGER,
        "libs/core/platform/src/lib/error.interceptor.ts": ERROR_INTERCEPTOR,
    }


def _test_files() -> dict[str, str]:
    return {
        "apps/healthclinic-web/src/app/app.routes.spec.ts": APP_ROUTES_SPEC,
        "libs/dashboard/ui/src/lib/year-navigator.component.spec.ts": YEAR_NAVIGATOR_SPEC,
        "libs/dashboard/data-access/src/lib/dashboard-api.client.spec.ts": API_CLIENT_SPEC,
        "libs/dashboard/state/src/lib/dashboard.store.spec.ts": DASHBOARD_STORE_SPEC,
        "libs/dashboard/feature/src/lib/dashboard-feature.component.spec.ts": DASHBOARD_FEATURE_SPEC,
        "apps/healthclinic-web-e2e/project.json": json.dumps({"name": "healthclinic-web-e2e", "$schema": "../../node_modules/nx/schemas/project-schema.json", "projectType": "application", "sourceRoot": "apps/healthclinic-web-e2e/src", "implicitDependencies": ["healthclinic-web"], "tags": ["scope:e2e", "type:test"], "targets": {"e2e": {"executor": "@nx/playwright:playwright", "outputs": ["{workspaceRoot}/dist/.playwright/apps/healthclinic-web-e2e"], "options": {"config": "apps/healthclinic-web-e2e/playwright.config.ts"}}}}, indent=2) + "\n",
        "apps/healthclinic-web-e2e/playwright.config.ts": "import { defineConfig, devices } from '@playwright/test';\n\nexport default defineConfig({ testDir: './src', use: { baseURL: 'http://localhost:4200', trace: 'on-first-retry' }, webServer: { command: 'npx nx serve healthclinic-web', url: 'http://localhost:4200', reuseExistingServer: true }, projects: [{ name: 'chromium', use: devices['Desktop Chrome'] }] });\n",
        "apps/healthclinic-web-e2e/src/dashboard.spec.ts": PLAYWRIGHT_SPEC,
    }


PRIVATE_SHELL_TS = """import { ChangeDetectionStrategy, Component, signal } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

@Component({
  selector: 'healthclinic-private-shell',
  standalone: true,
  imports: [RouterLink, RouterLinkActive, RouterOutlet],
  templateUrl: './private-shell.component.html',
  styleUrl: './private-shell.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PrivateShellComponent {
  protected readonly menuOpen = signal(false);
  protected toggleMenu(): void { this.menuOpen.update((open) => !open); }
  protected closeMenu(): void { this.menuOpen.set(false); }
}
"""

PRIVATE_SHELL_HTML = """<div class="app-shell">
  <header class="header">
    <button class="menu-button" type="button" aria-label="Open menu" [attr.aria-expanded]="menuOpen()" (click)="toggleMenu()"><span aria-hidden="true">&#9776;</span></button>
    <a routerLink="/dashboard" class="header-logo" aria-label="HealthClinic.biz dashboard"></a>
    <span class="header-separator" aria-hidden="true"></span><span class="header-title">Dashboard</span>
  </header>
  <aside class="sidebar" [class.open]="menuOpen()" aria-label="Primary navigation">
    <div class="sidebar-title"><span>MENU</span><button type="button" aria-label="Close menu" (click)="closeMenu()">&lsaquo;</button></div>
    <nav><a routerLink="/dashboard" routerLinkActive="selected" (click)="closeMenu()"><span class="nav-icon" aria-hidden="true">&#9638;</span> Dashboard</a></nav>
  </aside>
  @if (menuOpen()) { <button class="scrim" type="button" aria-label="Close menu" (click)="closeMenu()"></button> }
  <main id="main-content" class="content"><router-outlet /></main>
  <footer class="footer"><img src="assets/private/logo_private_area_footer.png" alt="HealthClinic.biz"><div><span>&copy; 2015 HealthClinic.biz</span><nav aria-label="Footer"><span>Terms</span><span>Privacy</span><span>Contact</span><span>Sitemap</span></nav></div></footer>
</div>
"""

PRIVATE_SHELL_CSS = """:host{display:block;min-width:320px}.app-shell{min-height:100vh;position:relative;padding-bottom:200px}.header{align-items:center;background:#1d1e2a;color:#fff;display:flex;height:105px;padding:0 30px;position:fixed;top:0;width:100%;z-index:20}.menu-button{background:transparent;border:0;color:#ff1770;cursor:pointer;font-size:2rem;margin-right:28px}.header-logo{background:url('/assets/private/logo_private_area.png') no-repeat left center/90%;height:100%;width:250px}.header-separator{background:#363744;height:65px;width:1px}.header-title{font-size:1.1rem;margin-left:20px;text-transform:uppercase}.sidebar{background:#1d1e2a;box-shadow:3px 0 5px #000;height:100%;left:0;position:fixed;top:0;transform:translateX(-355px);transition:transform .35s ease;width:min(348px,88vw);z-index:30}.sidebar.open{transform:translateX(0)}.sidebar-title{align-items:center;color:#fff;display:flex;height:105px;justify-content:space-between;padding:0 30px}.sidebar-title button{background:transparent;border:0;color:#ff1770;font-size:2.2rem}.sidebar nav{padding-top:30px}.sidebar a{border-left:3px solid transparent;color:#aaa;display:block;padding:16px 30px;text-decoration:none}.sidebar a.selected,.sidebar a:hover{border-left-color:#ff1770;color:#f0f0f0}.nav-icon{display:inline-block;font-size:1.5rem;width:50px}.scrim{background:#0008;border:0;height:100%;inset:0;position:fixed;width:100%;z-index:25}.content{margin:auto;max-width:1366px;padding:150px 30px 80px}.footer{align-items:flex-end;background:#1d1e2a;bottom:0;color:#b3b3b3;display:flex;font-size:.8rem;height:200px;justify-content:space-between;padding:30px;position:absolute;width:100%}.footer img{max-width:220px;opacity:.2}.footer div{display:flex;gap:48px}.footer nav span{color:#b3b3b3;margin-left:30px}:focus-visible{outline:3px solid #ff1770;outline-offset:4px}@media(max-width:768px){.header{height:84px;padding:0 20px}.header-logo{width:190px}.header-separator,.header-title{display:none}.content{padding:112px 20px 60px}.footer{align-items:center;height:180px}.footer div{display:block;text-align:right}.footer nav{margin-top:12px}.footer nav span{margin-left:16px}}@media(max-width:560px){.footer img{display:none}.footer div{width:100%}.footer nav{display:flex;flex-wrap:wrap;justify-content:flex-end}.app-shell{padding-bottom:180px}}
"""

GLOBAL_STYLES = """@import url('https://fonts.googleapis.com/css2?family=Raleway:wght@300;400;500;600&family=Roboto:wght@200;400;500;700&display=swap');
:root{color-scheme:light;font-family:'Raleway',sans-serif;background:#f0f0f0;color:#3d3d4c}*{box-sizing:border-box}html,body{margin:0;min-height:100%}body{background:#f0f0f0}button,input{font:inherit}h1,h2,h3,p{margin-top:0}.visually-hidden{clip:rect(0 0 0 0);clip-path:inset(50%);height:1px;overflow:hidden;position:absolute;white-space:nowrap;width:1px}
"""

DASHBOARD_FEATURE_TS = """import { ChangeDetectionStrategy, Component, computed, inject } from '@angular/core';
import { DashboardChartComponent, SummaryCardComponent, YearNavigatorComponent, type ChartSeries } from '@healthclinic/dashboard/ui';
import { DashboardStore } from '@healthclinic/dashboard/state';

@Component({
  selector: 'healthclinic-dashboard-feature',
  standalone: true,
  imports: [DashboardChartComponent, SummaryCardComponent, YearNavigatorComponent],
  providers: [DashboardStore],
  templateUrl: './dashboard-feature.component.html',
  styleUrl: './dashboard-feature.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DashboardFeatureComponent {
  protected readonly store = inject(DashboardStore);
  protected readonly incomeExpenseSeries = computed<ChartSeries[]>(() => [
    { label: 'INCOMES', color: '#00d8cc', values: (this.store.expenses() ?? []).map((item) => item.Incomes) },
    { label: 'EXPENSES', color: '#ff1770', values: (this.store.expenses() ?? []).map((item) => item.Expenses) },
  ]);
  protected readonly patientSeries = computed<ChartSeries[]>(() => [
    { label: 'PATIENTS', color: '#00d8cc', values: (this.store.patients() ?? []).map((item) => item.PatientsCount) },
  ]);
}
"""

DASHBOARD_FEATURE_HTML = """<section class="dashboard" aria-labelledby="dashboard-heading">
  <h1 id="dashboard-heading" class="visually-hidden">Operational Dashboard</h1>
  @if (store.errorMessage()) { <div class="error" role="alert">{{ store.errorMessage() }}</div> }
  @if (store.summary(); as summary) {
    <div class="summaries" aria-label="Clinic summary">
      <healthclinic-summary-card variant="patients" [value]="summary.NewPatients" label="NEW PATIENTS" [variation]="summary.NewPatientsVariation" />
      <healthclinic-summary-card variant="month" [value]="summary.MonthProfit" label="MONTH BENEFITS" [variation]="summary.MonthProfitVariation" currency />
      <healthclinic-summary-card variant="annual" [value]="summary.AnualProfit" label="ANNUAL BENEFITS" [variation]="summary.AnualProfitVariation" currency />
    </div>
  } @else if (store.loading()) { <p class="status" role="status">Loading clinic summary...</p> }

  <section class="chart-section" aria-labelledby="income-expense-title">
    <div class="chart-heading"><h2 id="income-expense-title">INCOMES AND EXPENSES</h2><healthclinic-year-navigator label="Income and expense reporting year" [year]="store.incomeExpenseYear()" [maximumYear]="store.currentYear" (previous)="store.previousIncomeExpenseYear()" (next)="store.nextIncomeExpenseYear()" /></div>
    @if (store.expenses(); as expenses) {
      @if (expenses.length) { <healthclinic-dashboard-chart kind="line" [series]="incomeExpenseSeries()" /> } @else { <p class="status">No income or expense information is available for this year.</p> }
    } @else { <p class="status" role="status">Loading income and expense information...</p> }
  </section>

  <section class="chart-section" aria-labelledby="patient-title">
    <div class="chart-heading"><h2 id="patient-title">PATIENT VISITS</h2><healthclinic-year-navigator label="Patient reporting year" [year]="store.patientYear()" [maximumYear]="store.currentYear" (previous)="store.previousPatientYear()" (next)="store.nextPatientYear()" /></div>
    @if (store.patients(); as patients) {
      @if (patients.length) { <healthclinic-dashboard-chart kind="bar" [series]="patientSeries()" /> } @else { <p class="status">No patient information is available for this year.</p> }
    } @else { <p class="status" role="status">Loading patient information...</p> }
  </section>
</section>
"""

DASHBOARD_FEATURE_CSS = """:host{display:block}.summaries{display:grid;gap:20px;grid-template-columns:repeat(3,1fr)}.chart-section{background:#fff;border:1px solid #f2f2f2;border-radius:2px;box-shadow:0 0 18px -10px #3d3d4c;margin:30px 0;padding-bottom:30px}.chart-heading{align-items:center;display:flex;justify-content:space-between;padding:30px}.chart-heading h2{color:#7c7c81;font-size:19px;font-weight:500;margin:0}.status{color:#71717f;min-height:180px;padding:55px 30px;text-align:center}.error{background:#fff0f3;border-left:4px solid #ff1770;color:#7d1640;margin-bottom:20px;padding:16px}@media(max-width:992px){.summaries{grid-template-columns:1fr}.chart-heading{align-items:flex-start;gap:20px;padding:24px}.chart-section{margin:20px 0}}@media(max-width:600px){.chart-heading{flex-direction:column}}
"""

SUMMARY_CARD_TS = """import { ChangeDetectionStrategy, Component, input } from '@angular/core';
import { DecimalPipe } from '@angular/common';

@Component({
  selector: 'healthclinic-summary-card', standalone: true, imports: [DecimalPipe], changeDetection: ChangeDetectionStrategy.OnPush,
  host: { '[class]': "'summary ' + variant()" },
  template: `<p class="quantity">@if (currency()) { <span aria-hidden="true">$</span> }{{ value() | number:'1.0-0' }}</p><h2>{{ label() }} <span class="variation"><span class="trend" aria-hidden="true"></span> {{ variation() | number:'1.0-1' }} %</span></h2>`,
  styles: [`:host{background-position:center;background-size:cover;border-radius:2px;color:#fff;display:block;min-height:197px;padding:35px}.patients{background-color:#00d8cc;background-image:url('/assets/dashboard/summary/bg_graph_01.png')}.month{background-color:#71717f;background-image:url('/assets/dashboard/summary/bg_graph_02.png')}.annual{background-color:#b8b8b9;background-image:url('/assets/dashboard/summary/bg_graph_03.png')}.quantity{font:200 70px/1 'Roboto',sans-serif;margin:0 0 30px}.quantity span{font-size:30px;vertical-align:top}h2{font-size:19px;font-weight:500;margin:0}.variation{float:right;font-weight:300}.trend{background:url('/assets/dashboard/arrow_01.png') no-repeat center/contain;display:inline-block;height:18px;margin-right:8px;vertical-align:middle;width:10px}@media(max-width:992px){.patients{background-image:url('/assets/dashboard/summary/bg_graph_01_snap.png')}.month{background-image:url('/assets/dashboard/summary/bg_graph_02_snap.png')}.annual{background-image:url('/assets/dashboard/summary/bg_graph_03_snap.png')}}@media(max-width:520px){:host{min-height:160px;padding:26px}.quantity{font-size:52px}}`],
})
export class SummaryCardComponent {
  readonly variant = input.required<'patients' | 'month' | 'annual'>();
  readonly value = input.required<number>(); readonly label = input.required<string>();
  readonly variation = input.required<number>(); readonly currency = input(false);
}
"""

YEAR_NAVIGATOR_TS = """import { ChangeDetectionStrategy, Component, input, output } from '@angular/core';

@Component({
  selector: 'healthclinic-year-navigator', standalone: true, changeDetection: ChangeDetectionStrategy.OnPush,
  template: `<div class="year-control" role="group" [attr.aria-label]="label()"><button type="button" (click)="previous.emit()" [attr.aria-label]="'Previous ' + label()">&lsaquo;</button><output [attr.aria-label]="label()">{{ year() }}</output><button type="button" (click)="next.emit()" [disabled]="year() >= maximumYear()" [attr.aria-label]="'Next ' + label()">&rsaquo;</button></div>`,
  styles: [`.year-control{align-items:center;color:#7c7c81;display:flex;font:400 19px 'Roboto',sans-serif;gap:20px}.year-control button{background:transparent;border:0;color:#7c7c81;cursor:pointer;font-size:2rem;line-height:1;padding:2px 8px}.year-control button:disabled{cursor:not-allowed;opacity:.3}.year-control button:focus-visible{outline:3px solid #ff1770;outline-offset:2px}output{min-width:4ch;text-align:center}`],
})
export class YearNavigatorComponent {
  readonly label = input.required<string>(); readonly year = input.required<number>(); readonly maximumYear = input.required<number>();
  readonly previous = output<void>(); readonly next = output<void>();
}
"""

DASHBOARD_CHART_TS = """import { ChangeDetectionStrategy, Component, computed, input } from '@angular/core';

export interface ChartSeries { label: string; color: string; values: number[]; }

@Component({
  selector: 'healthclinic-dashboard-chart', standalone: true, changeDetection: ChangeDetectionStrategy.OnPush,
  template: `<div class="chart"><svg viewBox="0 0 1100 300" role="img" [attr.aria-label]="accessibleLabel()"><g class="grid">@for (line of gridLines; track line) { <line x1="40" x2="1080" [attr.y1]="line" [attr.y2]="line" /> }</g>@if (kind() === 'line') { @for (item of normalizedSeries(); track item.label) { <polyline fill="none" [attr.stroke]="item.color" stroke-width="4" [attr.points]="points(item.values)" /> } } @else { @for (value of firstValues(); track $index) { <rect [attr.x]="barX($index)" [attr.y]="barY(value)" width="48" [attr.height]="barHeight(value)" fill="#00d8cc" /> } }</svg><div class="months" aria-hidden="true">@for (month of months; track month) { <span>{{ month }}</span> }</div><ul class="legend">@for (item of normalizedSeries(); track item.label) { <li><span [style.background]="item.color"></span>{{ item.label }}</li> }</ul></div>`,
  styles: [`.chart{padding:0 30px}svg{display:block;height:auto;max-height:300px;width:100%}.grid line{stroke:#0000000d;stroke-width:1}.months{color:#7c7c81;display:grid;font:11px 'Roboto',sans-serif;grid-template-columns:repeat(12,1fr);padding-left:3.5%}.months span{text-align:center}.legend{display:flex;gap:45px;list-style:none;margin:28px 10px 0;padding:0}.legend li{color:#7c7c81;font:13px 'Roboto',sans-serif}.legend span{border-radius:5px;display:inline-block;height:4px;margin-right:10px;vertical-align:middle;width:15px}@media(max-width:700px){.chart{overflow-x:auto;padding:0 12px}.chart svg,.months{min-width:680px}.legend{gap:20px}}`],
})
export class DashboardChartComponent {
  readonly kind = input.required<'line' | 'bar'>(); readonly series = input.required<ChartSeries[]>();
  readonly months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']; readonly gridLines = [40, 95, 150, 205, 260];
  protected readonly normalizedSeries = computed(() => this.series().map((item) => ({ ...item, values: Array.from({ length: 12 }, (_, index) => item.values[index] ?? 0) })));
  protected readonly firstValues = computed(() => this.normalizedSeries()[0]?.values ?? []);
  private readonly maximum = computed(() => Math.max(1, ...this.normalizedSeries().flatMap((item) => item.values)));
  protected readonly accessibleLabel = computed(() => this.normalizedSeries().map((item) => `${item.label}: ${item.values.join(', ')}`).join('. '));
  protected points(values: number[]): string { return values.map((value, index) => `${50 + index * 93},${this.barY(value)}`).join(' '); }
  protected barX(index: number): number { return 65 + index * 86; }
  protected barY(value: number): number { return 260 - this.barHeight(value); }
  protected barHeight(value: number): number { return Math.max(0, value) / this.maximum() * 220; }
}
"""

DASHBOARD_MODELS = """export interface ClinicSummary {
  NewPatients: number; NewPatientsVariation: number; MonthProfit: number;
  MonthProfitVariation: number; AnualProfit: number; AnualProfitVariation: number;
}
export interface ExpensesSummary { Month: number; Year: number; Expenses: number; Incomes: number; }
export interface PatientsSummary { Month: number; Year: number; PatientsCount: number; }
export type TenantId = number;
"""

DASHBOARD_API_CLIENT = r"""import { HttpClient, HttpHeaders } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { RUNTIME_CONFIG } from '@healthclinic/core/platform';
import { Observable } from 'rxjs';
import type { ClinicSummary, ExpensesSummary, PatientsSummary, TenantId } from './dashboard.models';

@Injectable({ providedIn: 'root' })
export class DashboardApiClient {
  private readonly http = inject(HttpClient); private readonly config = inject(RUNTIME_CONFIG);
  getTenant(): Observable<TenantId> { return this.http.get<TenantId>(this.url('/api/users/current/tenant')); }
  getClinicSummary(tenantId: TenantId): Observable<ClinicSummary> { return this.http.get<ClinicSummary>(this.url('/api/reports/clinicsummary'), { headers: this.tenantHeaders(tenantId) }); }
  getExpenses(year: number, tenantId: TenantId): Observable<ExpensesSummary[]> { return this.http.get<ExpensesSummary[]>(this.url(`/api/reports/expenses/${year}`), { headers: this.tenantHeaders(tenantId) }); }
  getPatients(year: number, tenantId: TenantId): Observable<PatientsSummary[]> { return this.http.get<PatientsSummary[]>(this.url(`/api/reports/patients/${year}`), { headers: this.tenantHeaders(tenantId) }); }
  private tenantHeaders(tenantId: TenantId): HttpHeaders { return new HttpHeaders({ TenantId: String(tenantId) }); }
  private url(path: string): string { return `${this.config.apiBaseUrl.replace(/\/$/, '')}${path}`; }
}
"""

DASHBOARD_STORE = """import { computed, inject, Injectable, signal } from '@angular/core';
import { toObservable, toSignal } from '@angular/core/rxjs-interop';
import { DashboardApiClient, type ClinicSummary, type ExpensesSummary, type PatientsSummary } from '@healthclinic/dashboard/data-access';
import { TenantContextService } from '@healthclinic/core/platform';
import { catchError, defer, distinctUntilChanged, finalize, Observable, of, switchMap } from 'rxjs';

@Injectable()
export class DashboardStore {
  private readonly api = inject(DashboardApiClient); private readonly tenant = inject(TenantContextService);
  readonly currentYear = new Date().getFullYear(); readonly incomeExpenseYear = signal(this.currentYear); readonly patientYear = signal(this.currentYear);
  private readonly activeRequests = signal(0); readonly loading = computed(() => this.activeRequests() > 0); readonly errorMessage = signal<string | null>(null);
  readonly summary = toSignal(this.request(() => this.tenant.tenantId$.pipe(switchMap((tenantId) => this.api.getClinicSummary(tenantId)))), { initialValue: null });
  readonly expenses = toSignal(toObservable(this.incomeExpenseYear).pipe(distinctUntilChanged(), switchMap((year) => this.request(() => this.tenant.tenantId$.pipe(switchMap((tenantId) => this.api.getExpenses(year, tenantId)))))), { initialValue: null });
  readonly patients = toSignal(toObservable(this.patientYear).pipe(distinctUntilChanged(), switchMap((year) => this.request(() => this.tenant.tenantId$.pipe(switchMap((tenantId) => this.api.getPatients(year, tenantId)))))), { initialValue: null });
  previousIncomeExpenseYear(): void { this.incomeExpenseYear.update((year) => year - 1); }
  nextIncomeExpenseYear(): void { this.incomeExpenseYear.update((year) => Math.min(this.currentYear, year + 1)); }
  previousPatientYear(): void { this.patientYear.update((year) => year - 1); }
  nextPatientYear(): void { this.patientYear.update((year) => Math.min(this.currentYear, year + 1)); }
  private request<T>(factory: () => Observable<T>): Observable<T | null> { return defer(() => { this.activeRequests.update((count) => count + 1); this.errorMessage.set(null); return factory().pipe(catchError(() => { this.errorMessage.set('Dashboard information could not be loaded. Please try again.'); return of(null); }), finalize(() => this.activeRequests.update((count) => Math.max(0, count - 1)))); }); }
}
"""

RUNTIME_CONFIG = """import { EnvironmentProviders, InjectionToken, makeEnvironmentProviders } from '@angular/core';
export interface RuntimeConfig { apiBaseUrl: string; }
export const RUNTIME_CONFIG = new InjectionToken<RuntimeConfig>('HEALTHCLINIC_RUNTIME_CONFIG');
export function provideRuntimeConfig(config: RuntimeConfig): EnvironmentProviders { return makeEnvironmentProviders([{ provide: RUNTIME_CONFIG, useValue: config }]); }
"""

TENANT_CONTEXT = r"""import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { shareReplay } from 'rxjs';
import { RUNTIME_CONFIG } from './runtime-config';
@Injectable({ providedIn: 'root' })
export class TenantContextService {
  private readonly http = inject(HttpClient); private readonly config = inject(RUNTIME_CONFIG);
  readonly tenantId$ = this.http.get<number>(`${this.config.apiBaseUrl.replace(/\/$/, '')}/api/users/current/tenant`).pipe(shareReplay({ bufferSize: 1, refCount: true }));
}
"""

CORRELATION_INTERCEPTOR = """import { HttpInterceptorFn } from '@angular/common/http';
export const correlationInterceptor: HttpInterceptorFn = (request, next) => next(request.clone({ setHeaders: { 'X-Correlation-ID': globalThis.crypto.randomUUID() } }));
"""

FRONTEND_LOGGER = """import { Injectable } from '@angular/core';
export interface LogContext { [key: string]: string | number | boolean | null | undefined; }
@Injectable({ providedIn: 'root' })
export class FrontendLogger {
  error(event: string, context: LogContext): void { console.error(event, context); }
}
"""

ERROR_INTERCEPTOR = """import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { catchError, throwError } from 'rxjs';
import { FrontendLogger } from './frontend-logger.service';
@Injectable({ providedIn: 'root' }) export class FrontendErrorService { private readonly logger = inject(FrontendLogger); report(error: HttpErrorResponse): void { this.logger.error('dashboard_http_request_failed', { status: error.status, url: error.url }); } }
export const errorInterceptor: HttpInterceptorFn = (request, next) => { const errors = inject(FrontendErrorService); return next(request).pipe(catchError((error: HttpErrorResponse) => { errors.report(error); return throwError(() => error); })); };
"""

APP_ROUTES_SPEC = """import { appRoutes } from './app.routes';
describe('appRoutes', () => { it('AC-04 AC-05: lazy-loads the Dashboard route', () => { const shell = appRoutes[0]; const dashboard = shell.children?.find((route) => route.path === 'dashboard'); expect(dashboard?.loadChildren).toBeDefined(); }); });
"""

YEAR_NAVIGATOR_SPEC = """import { ComponentFixture, TestBed } from '@angular/core/testing';
import { YearNavigatorComponent } from './year-navigator.component';
describe('YearNavigatorComponent', () => { let fixture: ComponentFixture<YearNavigatorComponent>; beforeEach(async () => { await TestBed.configureTestingModule({ imports: [YearNavigatorComponent] }).compileComponents(); fixture = TestBed.createComponent(YearNavigatorComponent); fixture.componentRef.setInput('label', 'Reporting year'); fixture.componentRef.setInput('year', 2025); fixture.componentRef.setInput('maximumYear', 2025); fixture.detectChanges(); }); it('AC-01: exposes previous and bounded next year controls', () => { const buttons = fixture.nativeElement.querySelectorAll('button'); expect(buttons.length).toBe(2); expect(buttons[1].disabled).toBe(true); }); });
"""

API_CLIENT_SPEC = """import { provideHttpClient } from '@angular/common/http'; import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing'; import { TestBed } from '@angular/core/testing'; import { provideRuntimeConfig } from '@healthclinic/core/platform'; import { DashboardApiClient } from './dashboard-api.client';
describe('DashboardApiClient', () => { let client: DashboardApiClient; let http: HttpTestingController; beforeEach(() => { TestBed.configureTestingModule({ providers: [provideHttpClient(), provideHttpClientTesting(), provideRuntimeConfig({ apiBaseUrl: '' })] }); client = TestBed.inject(DashboardApiClient); http = TestBed.inject(HttpTestingController); }); afterEach(() => http.verify()); it('AC-02 AC-03: preserves tenant and clinic summary contracts', () => { client.getTenant().subscribe(); http.expectOne('/api/users/current/tenant').flush(7); client.getClinicSummary(7).subscribe(); expect(http.expectOne('/api/reports/clinicsummary').request.headers.get('TenantId')).toBe('7'); }); it('AC-01: preserves both selected-year report contracts', () => { client.getExpenses(2025, 7).subscribe(); http.expectOne('/api/reports/expenses/2025').flush([]); client.getPatients(2025, 7).subscribe(); http.expectOne('/api/reports/patients/2025').flush([]); }); });
"""

DASHBOARD_STORE_SPEC = """import { TestBed } from '@angular/core/testing'; import { DashboardApiClient } from '@healthclinic/dashboard/data-access'; import { TenantContextService } from '@healthclinic/core/platform'; import { of } from 'rxjs'; import { DashboardStore } from './dashboard.store';
describe('DashboardStore', () => { it('AC-01: keeps report years independent and bounded by current year', () => { TestBed.configureTestingModule({ providers: [DashboardStore, { provide: DashboardApiClient, useValue: { getClinicSummary: () => of({}), getExpenses: () => of([]), getPatients: () => of([]) } }, { provide: TenantContextService, useValue: { tenantId$: of(1) } }] }); const store = TestBed.inject(DashboardStore); store.previousIncomeExpenseYear(); expect(store.incomeExpenseYear()).toBe(store.currentYear - 1); expect(store.patientYear()).toBe(store.currentYear); store.nextIncomeExpenseYear(); store.nextIncomeExpenseYear(); expect(store.incomeExpenseYear()).toBe(store.currentYear); }); });
"""

DASHBOARD_FEATURE_SPEC = """import { TestBed } from '@angular/core/testing'; import { DashboardApiClient } from '@healthclinic/dashboard/data-access'; import { TenantContextService } from '@healthclinic/core/platform'; import { of } from 'rxjs'; import { DashboardFeatureComponent } from './dashboard-feature.component';
describe('DashboardFeatureComponent', () => { it('AC-01 AC-02 AC-03 AC-04 AC-05: reconstructs approved Dashboard regions', async () => { await TestBed.configureTestingModule({ imports: [DashboardFeatureComponent], providers: [{ provide: DashboardApiClient, useValue: { getClinicSummary: () => of({ NewPatients: 3, NewPatientsVariation: 1, MonthProfit: 2, MonthProfitVariation: 1, AnualProfit: 4, AnualProfitVariation: 1 }), getExpenses: () => of([]), getPatients: () => of([]) } }, { provide: TenantContextService, useValue: { tenantId$: of(1) } }] }).compileComponents(); const fixture = TestBed.createComponent(DashboardFeatureComponent); fixture.detectChanges(); expect(fixture.nativeElement.textContent).toContain('INCOMES AND EXPENSES'); expect(fixture.nativeElement.textContent).toContain('PATIENT VISITS'); }); });
"""

PLAYWRIGHT_SPEC = r"""import { expect, test } from '@playwright/test';
test.beforeEach(async ({ page }) => { await page.goto('/dashboard'); });
test('AC-04: opens the Operational Dashboard', async ({ page }) => { await expect(page.getByRole('heading', { name: 'Operational Dashboard' })).toBeAttached(); });
test('AC-05: keeps the Dashboard experience available at its route', async ({ page }) => { await expect(page).toHaveURL(/\/dashboard$/); });
test('AC-01: exposes independently labeled yearly operational reports', async ({ page }) => { await expect(page.getByRole('group', { name: 'Income and expense reporting year' })).toBeVisible(); await expect(page.getByRole('group', { name: 'Patient reporting year' })).toBeVisible(); });
test('AC-02: presents organization-specific clinic summary regions', async ({ page }) => { await expect(page.getByLabel('Clinic summary')).toBeVisible(); });
test('AC-03: loads clinic summary through the approved service integration', async ({ page }) => { const response = await page.waitForResponse((item) => item.url().includes('/api/reports/clinicsummary')); expect(response.request().method()).toBe('GET'); });
"""

DASHBOARD_ROUTE_GUARD = """import { CanActivateFn } from '@angular/router';
// Identity and authorization rules remain unselected; this functional boundary preserves that explicit extension point.
export const dashboardRouteGuard: CanActivateFn = () => true;
"""

ESLINT_CONFIG = """import nx from '@nx/eslint-plugin';

export default [
  ...nx.configs['flat/base'],
  ...nx.configs['flat/typescript'],
  {
    files: ['**/*.ts'],
    rules: {
      '@nx/enforce-module-boundaries': ['error', {
        enforceBuildableLibDependency: true,
        depConstraints: [
          { sourceTag: 'type:feature', onlyDependOnLibsWithTags: ['type:ui', 'type:state'] },
          { sourceTag: 'type:state', onlyDependOnLibsWithTags: ['type:data-access', 'type:platform'] },
          { sourceTag: 'type:data-access', onlyDependOnLibsWithTags: ['type:platform'] },
          { sourceTag: 'type:ui', onlyDependOnLibsWithTags: ['type:ui'] },
        ],
      }],
    },
  },
];
"""
