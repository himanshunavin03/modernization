# POLARIS — Final Doctor UI Fidelity + Playwright POC Freeze

Model: Sol. Base commit: `66ecb11`. Target Feature: `doctor-directory-management`.

Finish the Doctor POC without reopening the frozen KG, Application Understanding, requirements, Feature Specification, architecture, technical-task plan, Dashboard, or legacy source. Preserve the validated Doctor list unless shared detail/form styling directly regresses it.

Use the actual legacy Doctor create/edit template, controller, styles, assets, and running page as the authoritative visual and behavioral reference. Repair the shared modern Angular create/edit presentation to reproduce the legacy hierarchy: top Back/Add-or-Save actions; left main panel with Name, Description, Address and a three-column Email/Phone/Mobile row; right profile-photo, patient-count, and registration-date panels. Preserve typed Reactive Forms, validation, POST/PUT, success navigation, media selection/preview, standalone Angular 22, Signals/computed state, OnPush, strict typing, modern template control flow, and RxJS boundaries. Do not use Signal Forms or invent APIs/values.

Actually render legacy and modern create views at the same viewport and render modern edit where possible. Validate all requested action, form, field-row, photo, patient, registration, and overall-layout gates. Run the Angular build and configured focused Doctor/tenant tests. Reuse the current legacy backend on port 5000 and Angular on port 4200 when healthy.

Implement frozen technical task TT-016 using the 41 frozen Doctor Acceptance Criteria. Update the existing Doctor Playwright suite only with evidence-backed scenarios for exercisable behavior; explicitly classify the two Patient-navigation criteria as `BLOCKED_BY_PATIENT_FEATURE` if the Patient Feature remains absent. Distinguish real-backend from mocked scenarios. Run only the Doctor Playwright suite, generate the existing HTML report and normal failure artifacts, and publish a concise Doctor E2E coverage artifact mapping all 41 AC to a Playwright scenario or explicit dependency status. Required totals are 41 AC, 41 traceable, and zero unexplained.

Update the final POC validation records required by repository policy. If create/edit fidelity, build, focused tests, Playwright, complete AC traceability, and frozen-boundary checks all pass, create exactly one commit named `Complete Doctor POC UI and E2E validation`, report the requested runtime/test/coverage/task/commit fields, and stop.
