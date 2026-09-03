# Polaris Modernization Prompt 064

## Build, Test, PEP Repair, And Runtime Validation

Baseline: `a7d00a2`

Validate and minimally repair the generated Angular 22/Nx Dashboard under
`modernized/`. Treat the observed `npm install` conflict between
`@angular/build@22.1.4` (`vitest ^4.0.8`) and the generated `vitest@3.2.4` as
the first real PEP failure.

Use the lifecycle ATTEMPT -> FAILURE -> CONTEXT -> DIAGNOSIS -> REPAIR PLAN ->
MINIMAL REPAIR -> REVALIDATION. Preserve Angular 22, Nx, the generated Feature,
all requirements, architecture, technical tasks, existing APIs, and the
existing-application UI design source. Do not use `--force` or
`--legacy-peer-deps`, downgrade Angular, regenerate the application, invent
APIs, or modify `source/` or frozen upstream artifacts.

After a standards-compliant dependency repair, install dependencies and record
the actual Node, npm, Angular, Nx, TypeScript, Vitest, and Playwright versions.
Run the real Nx build and generated unit/component/data-access tests. Diagnose
each new failure before a minimal repair, with no more than five automatic
repair iterations.

After build and tests pass, start `healthclinic-web`, validate the Dashboard in
a browser where possible, distinguish unavailable backend connectivity from a
frontend failure, compare the rendered result with the existing UI
reconstruction, and run generated Playwright tests. Validate all four existing
API contracts and classify runtime coverage for all five hero AC and all 16
approved technical tasks.

Generate `artifacts/modernization/latest/pep-run.json`, `pep-run.md`, and
`runtime-validation.json`; update the customer modernization HTML and final
traceability with actual evidence. Run focused and full Polaris regressions,
update permanent project records, and create one focused commit titled
`Validate and repair Angular 22 hero modernization` if repairs or artifact
updates are required. Exclude dependencies, build output, coverage, browser
binaries, and logs from Git. Return the exact required report and stop.

The complete user-supplied prompt is retained in the conversation attachment
`49c0825d-aebe-465b-9833-4b3a238a0dd6/pasted-text.txt`; this repository archive
captures its executable contract without environment-specific attachment paths.
