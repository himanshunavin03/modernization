# HealthClinic Local Runbook

This runbook records the verified commands for running the modern Angular application, the original HealthClinic .NET backend, and Playwright on this Windows POC machine.

## Important boundaries

- Run all repository commands from this repository: `C:\Users\himan\OneDrive\Documents\polaris-modernization-poc\modernization\modernization`.
- Treat everything under `source\` as read-only.
- The backend is a legacy ASP.NET 5 RC1 application hosted by DNX. It is **not** a modern SDK-style application, so do not use `dotnet run`.
- Do not run `dnx web` from `source\HealthClinic.biz`. Use the existing disposable runtime copy and the absolute DNX path below.
- Docker/Neo4j is not part of the HealthClinic application runtime.
- Before starting a server, check whether its port is already listening. Reuse an existing healthy server instead of starting a duplicate.
- Keep the backend and Angular commands running in separate PowerShell windows.

## URLs and ports

| Service | URL |
| --- | --- |
| Original HealthClinic application | `http://localhost:5000/` |
| Original dashboard | `http://localhost:5000/Dashboard#/dashboard` |
| Original Doctors page | `http://localhost:5000/Dashboard#/doctors` |
| Modern Angular application | `http://localhost:4200/` |
| Modern Doctors page | `http://localhost:4200/doctors` |
| Modern New Doctor page | `http://localhost:4200/doctors/new` |

Angular proxies `/api` requests to `http://127.0.0.1:5000` by default. This is defined in `modernized\apps\healthclinic-web\proxy.conf.mjs` and can be overridden for the current process with `API_BASE_URL` if a different approved backend is intentionally used.

## 1. Check for existing servers

Run this first from any PowerShell directory:

```powershell
Get-NetTCPConnection -State Listen -LocalPort 4200,5000 -ErrorAction SilentlyContinue |
    Select-Object LocalAddress, LocalPort, OwningProcess
```

If a port is present, inspect its process without stopping it:

```powershell
$listener = Get-NetTCPConnection -State Listen -LocalPort 4200,5000 -ErrorAction SilentlyContinue
$listener | ForEach-Object {
    Get-CimInstance Win32_Process -Filter "ProcessId=$($_.OwningProcess)" |
        Select-Object ProcessId, Name, ExecutablePath, CommandLine
}
```

Verify any already-running servers:

```powershell
curl.exe -s -o NUL -w "backend=%{http_code}`n" http://127.0.0.1:5000/
curl.exe -s -o NUL -w "angular=%{http_code}`n" http://localhost:4200/
```

An HTTP `200` means the corresponding root page is available.

## 2. Start the legacy .NET backend

The existing backend runtime uses:

- DNX: `C:\Users\himan\AppData\Local\PolarisLegacyDnx\runtimes\dnx-clr-win-x86.1.0.0-rc1-final\bin\dnx.exe`
- DNX packages: `C:\Users\himan\AppData\Local\PolarisLegacyDnx\packages-cache`
- Runtime web project: `C:\Users\himan\AppData\Local\PolarisOriginalHealthClinicRun\current\HealthClinic.biz\src\MyHealth.Web`
- LocalDB: `C:\Program Files\Microsoft SQL Server\160\Tools\Binn\SqlLocalDB.exe`

In the backend PowerShell window, run:

```powershell
$sqlLocalDb = 'C:\Program Files\Microsoft SQL Server\160\Tools\Binn\SqlLocalDB.exe'
$dnx = 'C:\Users\himan\AppData\Local\PolarisLegacyDnx\runtimes\dnx-clr-win-x86.1.0.0-rc1-final\bin\dnx.exe'
$web = 'C:\Users\himan\AppData\Local\PolarisOriginalHealthClinicRun\current\HealthClinic.biz\src\MyHealth.Web'

& $sqlLocalDb start MSSQLLocalDB
$env:DNX_PACKAGES = 'C:\Users\himan\AppData\Local\PolarisLegacyDnx\packages-cache'
Set-Location $web
& $dnx web
```

Keep the window open. The expected startup message includes:

```text
Now listening on: http://localhost:5000
Application started. Press Ctrl+C to shut down.
```

Verify it from another PowerShell window:

```powershell
curl.exe -s -o NUL -w "backend=%{http_code}`n" http://127.0.0.1:5000/
curl.exe -s -o NUL -w "api=%{http_code}`n" http://127.0.0.1:5000/api/reports/expenses/$((Get-Date).Year)
```

The root should return `200`. Protected API behavior depends on authentication; a redirect to the login page is expected for unauthenticated protected requests.

For deeper legacy-runtime setup and troubleshooting, see `docs\ORIGINAL-HEALTHCLINIC-LEGACY-SETUP.md`. Do not install another DNX or .NET runtime as part of routine startup.

## 3. Start the modern Angular application

In a separate PowerShell window:

```powershell
Set-Location 'C:\Users\himan\OneDrive\Documents\polaris-modernization-poc\modernization\modernization\modernized'
npm start -- --port 4200
```

Keep the window open, then browse to `http://localhost:4200/` or `http://localhost:4200/doctors`.

Verify Angular and its backend proxy:

```powershell
curl.exe -s -o NUL -w "angular=%{http_code}`n" http://localhost:4200/
curl.exe -s -o NUL -w "proxy-api=%{http_code}`n" http://localhost:4200/api/reports/expenses/$((Get-Date).Year)
```

Both checks should return `200` when the applications and proxy are healthy.

## 4. Build and unit tests

Run these from the `modernized` directory while the servers remain running.

Build the Angular application:

```powershell
npm run build
```

Run all configured unit-test targets:

```powershell
npm test
```

Run the focused Doctor and tenant-context unit tests:

```powershell
npx nx test healthclinic-web --watch=false --include='../../../libs/doctor-directory-management/**/*.spec.ts' --include='../../../libs/core/platform/src/lib/tenant-context*.spec.ts'
```

## 5. Run focused Doctor Playwright tests

Playwright reuses an Angular server already running on port 4200. The backend must be available on port 5000 for authenticated API flows.

From the `modernized` directory, load the existing seeded credentials into only the current PowerShell process and run the focused suite:

```powershell
$settings = Get-Content -LiteralPath '..\source\HealthClinic.biz\src\MyHealth.Web\appsettings.json' -Raw | ConvertFrom-Json
$env:HEALTHCLINIC_E2E_USERNAME = $settings.DefaultUsername
$env:HEALTHCLINIC_E2E_PASSWORD = $settings.DefaultPassword

npx nx e2e healthclinic-web-e2e --grep='doctor-directory-management'

Remove-Item Env:HEALTHCLINIC_E2E_USERNAME, Env:HEALTHCLINIC_E2E_PASSWORD -ErrorAction SilentlyContinue
```

Do not print, paste, or commit the credential values. The command above reads them at runtime and removes the environment variables afterward.

The last verified focused result was 9 tests total: 8 passed, 0 failed, and 1 skipped because it depends on the Patient feature.

## 6. Run the full Playwright suite

Use this only when the full cross-feature suite is intended:

```powershell
Set-Location 'C:\Users\himan\OneDrive\Documents\polaris-modernization-poc\modernization\modernization\modernized'

$settings = Get-Content -LiteralPath '..\source\HealthClinic.biz\src\MyHealth.Web\appsettings.json' -Raw | ConvertFrom-Json
$env:HEALTHCLINIC_E2E_USERNAME = $settings.DefaultUsername
$env:HEALTHCLINIC_E2E_PASSWORD = $settings.DefaultPassword

npm run e2e

Remove-Item Env:HEALTHCLINIC_E2E_USERNAME, Env:HEALTHCLINIC_E2E_PASSWORD -ErrorAction SilentlyContinue
```

The full suite can include tests for unrelated features such as Dashboard, so a failure there does not automatically mean the Doctor feature failed.

## 7. Open the Playwright HTML report

From the `modernized` directory:

```powershell
npx playwright show-report apps\healthclinic-web-e2e\playwright-report
```

The report file is `modernized\apps\healthclinic-web-e2e\playwright-report\index.html`. Failure screenshots, traces, and retained videos are generated according to `modernized\apps\healthclinic-web-e2e\playwright.config.ts`.

## 8. Stop applications safely

For a foreground server, use `Ctrl+C` in that server's own PowerShell window.

If the window is unavailable, first identify and verify the listener and executable. Never stop a process based only on a guessed or previously recorded PID, because PIDs change between runs.

```powershell
Get-NetTCPConnection -State Listen -LocalPort 4200,5000 -ErrorAction SilentlyContinue |
    Select-Object LocalAddress, LocalPort, OwningProcess
```

The Angular process is normally `node.exe`; the backend must resolve to the isolated `dnx.exe` path documented above. Stop only the process you have verified belongs to the intended server.

## Quick everyday sequence

1. Check ports 4200 and 5000 and reuse healthy servers already running.
2. If needed, start LocalDB and the legacy backend using section 2.
3. If needed, start Angular using section 3.
4. Verify both roots and the Angular `/api` proxy.
5. Open `http://localhost:4200/doctors`.
6. Run the focused Doctor Playwright command in section 5 when browser validation is needed.

