# POLARIS — Repair Doctor List UI Fidelity Only

The Angular Doctor list is running, but its layout does not faithfully match the legacy HealthClinic Doctor list.

Use the existing legacy Doctor list source/templates/styles under `source/HealthClinic.biz` as the authoritative UI reference. Do not redesign the page or change business behavior, APIs, frozen upstream artifacts, Dashboard, or Playwright.

Repair only the Doctor Angular list template/style fidelity so that each doctor is one horizontal row containing its checkbox, photo, name, patient count, email, speciality, edit action, and delete action. Match the legacy Select All, header alignment, row sizing/spacing, New Doctor placement, Load More placement, and available action visuals while preserving accessibility and all existing selection, deletion, navigation, creation, and loading behavior.

Retain Angular 22 standalone components, Signals/computed state, OnPush, typed Reactive Forms, RxJS HTTP boundaries, strict typing, and modern template control flow.

After repair, actually render and visually compare the Doctor list with the legacy UI; verify one-row structure and all requested alignments. Run the Angular build and focused Doctor tests, but do not run Playwright. Keep changes within the Doctor list template/styles and the minimum Doctor component code if structurally required. If all gates pass, create exactly one commit named `Align Doctor list with legacy UI` and report the structure, visual/functional gates, build/tests, changed files, commit SHA, and worktree status.
