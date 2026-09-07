# Application Modernization POC Presentation Dashboard

This is a standalone, offline-friendly presentation surface. It reads approved Polaris artifacts only when the generated pages are refreshed; it does not alter the legacy or modern applications.

## Refresh presentation data and pages

From the repository root:

```powershell
python poc-dashboard\build-dashboard.py
```

The repeatable build writes only to `poc-dashboard/generated/`.

## Start and open the dashboard

Serve the repository root so the dashboard can also link to the existing Playwright report:

```powershell
python -m http.server 8088
```

Open:

```text
http://localhost:8088/poc-dashboard/
```

No package installation or internet connection is required.

## Live application expectations

- Legacy reference application: `http://localhost:5000/`
- Modern Angular application: `http://localhost:4200/`
- Modern Doctor directory: `http://localhost:4200/doctors`
- New Doctor workflow: `http://localhost:4200/doctors/new`

The presentation remains available when these runtimes are offline.

## Playwright report

The dashboard links to the existing configured report at `modernized/apps/healthclinic-web-e2e/playwright-report/index.html`. To regenerate the full report, keep the legacy backend and Angular application running, then from `modernized/` load the existing seeded credentials into the current process and run:

```powershell
$settings = Get-Content -LiteralPath '..\source\HealthClinic.biz\src\MyHealth.Web\appsettings.json' -Raw | ConvertFrom-Json
$env:HEALTHCLINIC_E2E_USERNAME = $settings.DefaultUsername
$env:HEALTHCLINIC_E2E_PASSWORD = $settings.DefaultPassword
try { npm run e2e } finally { Remove-Item Env:HEALTHCLINIC_E2E_USERNAME,Env:HEALTHCLINIC_E2E_PASSWORD -ErrorAction SilentlyContinue }
```

The credential values are read at runtime and must never be printed or committed. The focused Doctor suite is:

```powershell
npx nx e2e healthclinic-web-e2e --grep='doctor-directory-management'
```
