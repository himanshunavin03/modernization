# Doctor Directory Management Technical Delivery Plan

- Status: `TECHNICAL_TASKS_READY`
- Feature: `feature-doctor-directory-management`
- Architecture: `LOCKED`
- Design: `NOT_PROVIDED` / `NONE`

## Delivery Sequence

### TT-001 · Establish the delivery workspace for Doctor Directory Management

**Category:** `SCAFFOLD`
**Depends on:** None
**Existing implementation:** `IMPLEMENTED`

Create the selected frontend workspace foundation.

**Implementation requirements**
- Configure the selected frontend platform and strict compiler settings.
- Apply workspace boundary, build, and quality policies.

**Validation**
- Workspace build and quality commands pass.

**Architecture:** ARCH-001, ARCH-002, ARCH-003, ARCH-004, ARCH-005, ARCH-006, ARCH-008, ARCH-009, ARCH-010, ARCH-017, ARCH-052
**Requirements:** Infrastructure task
**Stories:** Infrastructure task
**Acceptance criteria:** Infrastructure task
**APIs:** None
**Implementation evidence:** modernized\libs\doctor-directory-management\data-access\src\lib\doctor-api.client.ts, modernized\libs\doctor-directory-management\data-access\src\lib\doctor-api.client.spec.ts, modernized\libs\doctor-directory-management\state\src\lib\doctor-directory.store.ts, modernized\libs\doctor-directory-management\state\src\lib\doctor-directory.store.spec.ts, modernized\libs\doctor-directory-management\feature\src\lib\doctor-list.component.ts, modernized\libs\doctor-directory-management\feature\src\lib\doctor-detail.component.ts, modernized\libs\doctor-directory-management\feature\src\lib\doctor-directory.component.spec.ts
**Design:** NOT_PROVIDED

### TT-002 · Define the Doctor Directory Management domain boundary

**Category:** `CONFIGURATION`
**Depends on:** TT-001
**Existing implementation:** `IMPLEMENTED`

Create enforceable ownership and dependency boundaries.

**Implementation requirements**
- Create feature, data-access, and reusable UI boundaries.
- Prevent presentation code from bypassing integration boundaries.

**Validation**
- Dependency validation passes.

**Architecture:** ARCH-006, ARCH-008, ARCH-009, ARCH-010, ARCH-034
**Requirements:** Infrastructure task
**Stories:** Infrastructure task
**Acceptance criteria:** Infrastructure task
**APIs:** None
**Implementation evidence:** modernized\libs\doctor-directory-management\data-access\project.json, modernized\libs\doctor-directory-management\state\project.json, modernized\libs\doctor-directory-management\feature\project.json
**Design:** NOT_PROVIDED

### TT-003 · Prepare accessible presentation primitives for Doctor Directory Management

**Category:** `DESIGN_SYSTEM`
**Depends on:** TT-001
**Existing implementation:** `IMPLEMENTED`

Provide reusable presentation foundations without inventing behavior.

**Implementation requirements**
- Use existing application UI evidence and accessible implementation defaults because customer design input is unavailable.
- Apply normalized design evidence only when available.

**Validation**
- Presentation primitives meet keyboard, contrast, and responsive expectations.

**Architecture:** ARCH-006, ARCH-008, ARCH-009, ARCH-010, ARCH-046, ARCH-048
**Requirements:** Infrastructure task
**Stories:** Infrastructure task
**Acceptance criteria:** Infrastructure task
**APIs:** None
**Implementation evidence:** modernized\libs\doctor-directory-management\feature\src\lib\doctor-list.component.html, modernized\libs\doctor-directory-management\feature\src\lib\doctor-detail.component.html, modernized\libs\doctor-directory-management\feature\src\lib\doctor-directory.component.css
**Design:** NOT_PROVIDED

### TT-004 · Model approved Doctor Directory Management API contracts

**Category:** `API`
**Depends on:** TT-002
**Existing implementation:** `PARTIALLY_IMPLEMENTED`

Create typed client models while preserving backend semantics.

**Implementation requirements**
- Represent every approved method, route, parameter, and response contract exactly.
- Keep transport logic outside presentation components.
- Implement FR-01: The "Add" action is disabled while the form is invalid. The "Add" action is displayed when edit mode is inactive. The doctors view opens when the operation completes successfully. The new record is saved when the operation completes successfully.
- Implement FR-02: Confirmation is requested before the guarded action proceeds. The "Delete" action is displayed when at least one record is selected. The affected doctors are removed from the displayed collection when the operation completes successfully.
- Implement FR-03: Confirmation is requested before the guarded action proceeds. The affected doctors are removed from the displayed collection when the operation completes successfully.
- Implement FR-04: Confirmation is requested before the guarded action proceeds. The doctors view opens when the operation completes successfully.
- Implement FR-05: Additional doctors are appended after the displayed records when the operation completes successfully. Records retain fixed name ordering (ascending) when the operation completes successfully. The "LOAD MORE" action is hidden when the returned batch contains fewer records than the requested batch size. The "NO DATA" message is displayed when the doctors collection is empty.
- Implement FR-06: Additional doctors are appended after the displayed records when the operation completes successfully. Records retain fixed name ordering (ascending) when the operation completes successfully. The "LOAD MORE" action is hidden when the returned batch contains fewer records than the requested batch size. The "NO DATA" message is displayed when the doctors collection is empty.
- Implement FR-09: The doctor view opens. The returned doctor details populate the form.
- Implement FR-12: The "Save" action is disabled while the form is invalid. The "Save" action is displayed when edit mode is active. The changes to the selected record are saved when the operation completes successfully. The doctors view opens when the operation completes successfully.
- Implement FR-14: The tenant context is obtained automatically before the dependent request runs.
- Preserve DELETE /api/doctors/{id} as an existing approved backend contract.
- Preserve GET /api/doctors as an existing approved backend contract.
- Preserve GET /api/doctors/{id} as an existing approved backend contract.
- Preserve GET /api/users/current/tenant as an existing approved backend contract.
- Preserve POST /api/doctors as an existing approved backend contract.
- Preserve PUT /api/doctors as an existing approved backend contract.

**Validation**
- Contract tests cover every approved API without inventing endpoints.

**Architecture:** ARCH-006, ARCH-008, ARCH-009, ARCH-010, ARCH-037, ARCH-038
**Requirements:** FR-01, FR-02, FR-03, FR-04, FR-05, FR-06, FR-09, FR-12, FR-14
**Stories:** story-doctor-directory-management-fr-01-add-doctor, story-doctor-directory-management-fr-02-delete-selected-doctor-records, story-doctor-directory-management-fr-03-delete-an-individual-doctor, story-doctor-directory-management-fr-04-delete-this-doctor, story-doctor-directory-management-fr-05-load-more, story-doctor-directory-management-fr-06-directory-presentation, story-doctor-directory-management-fr-09-open-doctor-details, story-doctor-directory-management-fr-12-save-doctor, story-doctor-directory-management-fr-14-automatic-tenant-context
**Acceptance criteria:** ac-doctor-directory-management-fr-01-add-doctor-001, ac-doctor-directory-management-fr-01-add-doctor-002, ac-doctor-directory-management-fr-01-add-doctor-003, ac-doctor-directory-management-fr-01-add-doctor-004, ac-doctor-directory-management-fr-02-delete-selected-doctor-records-001, ac-doctor-directory-management-fr-02-delete-selected-doctor-records-002, ac-doctor-directory-management-fr-02-delete-selected-doctor-records-003, ac-doctor-directory-management-fr-03-delete-an-individual-doctor-001, ac-doctor-directory-management-fr-03-delete-an-individual-doctor-002, ac-doctor-directory-management-fr-04-delete-this-doctor-001, ac-doctor-directory-management-fr-04-delete-this-doctor-002, ac-doctor-directory-management-fr-05-load-more-001, ac-doctor-directory-management-fr-05-load-more-002, ac-doctor-directory-management-fr-05-load-more-003, ac-doctor-directory-management-fr-05-load-more-004, ac-doctor-directory-management-fr-06-directory-presentation-001, ac-doctor-directory-management-fr-06-directory-presentation-002, ac-doctor-directory-management-fr-06-directory-presentation-003, ac-doctor-directory-management-fr-06-directory-presentation-004, ac-doctor-directory-management-fr-09-open-doctor-details-001, ac-doctor-directory-management-fr-09-open-doctor-details-002, ac-doctor-directory-management-fr-12-save-doctor-001, ac-doctor-directory-management-fr-12-save-doctor-002, ac-doctor-directory-management-fr-12-save-doctor-003, ac-doctor-directory-management-fr-12-save-doctor-004, ac-doctor-directory-management-fr-14-automatic-tenant-context-001
**APIs:** API-01, API-02, API-03, API-04, API-05, API-06
**Implementation evidence:** modernized\libs\doctor-directory-management\feature\src\lib\doctor-list.component.ts, modernized\libs\doctor-directory-management\feature\src\lib\doctor-list.component.html, modernized\libs\doctor-directory-management\feature\src\lib\doctor-detail.component.ts, modernized\libs\doctor-directory-management\feature\src\lib\doctor-detail.component.html, modernized\libs\doctor-directory-management\data-access\src\lib\doctor-api.client.ts, modernized\libs\doctor-directory-management\data-access\src\lib\doctor-api.client.spec.ts, modernized\apps\healthclinic-web-e2e\src\doctor-directory-management.spec.ts, modernized\libs\doctor-directory-management\data-access\project.json, modernized\libs\doctor-directory-management\data-access\src\index.ts, modernized\libs\doctor-directory-management\data-access\src\lib\doctor.models.ts, modernized\libs\doctor-directory-management\state\project.json, modernized\libs\doctor-directory-management\state\src\index.ts, modernized\libs\doctor-directory-management\state\src\lib\doctor-directory.store.ts, modernized\libs\doctor-directory-management\state\src\lib\doctor-directory.store.spec.ts, modernized\libs\doctor-directory-management\feature\project.json, modernized\libs\doctor-directory-management\feature\src\index.ts, modernized\libs\doctor-directory-management\feature\src\lib\doctor-directory.routes.ts, modernized\libs\doctor-directory-management\feature\src\lib\doctor-directory.component.css, modernized\libs\doctor-directory-management\feature\src\lib\doctor-directory.component.spec.ts
**Design:** NOT_PROVIDED

### TT-005 · Plan gateway policies for Doctor Directory Management

**Category:** `GATEWAY`
**Depends on:** TT-004
**Existing implementation:** `NOT_IMPLEMENTED`

Apply the selected ingress architecture without changing business APIs.

**Implementation requirements**
- Preserve approved backend contracts through gateway routing.
- Define authentication, correlation, and observability policy responsibilities.
- Implement FR-01: The "Add" action is disabled while the form is invalid. The "Add" action is displayed when edit mode is inactive. The doctors view opens when the operation completes successfully. The new record is saved when the operation completes successfully.
- Implement FR-02: Confirmation is requested before the guarded action proceeds. The "Delete" action is displayed when at least one record is selected. The affected doctors are removed from the displayed collection when the operation completes successfully.
- Implement FR-03: Confirmation is requested before the guarded action proceeds. The affected doctors are removed from the displayed collection when the operation completes successfully.
- Implement FR-04: Confirmation is requested before the guarded action proceeds. The doctors view opens when the operation completes successfully.
- Implement FR-05: Additional doctors are appended after the displayed records when the operation completes successfully. Records retain fixed name ordering (ascending) when the operation completes successfully. The "LOAD MORE" action is hidden when the returned batch contains fewer records than the requested batch size. The "NO DATA" message is displayed when the doctors collection is empty.
- Implement FR-06: Additional doctors are appended after the displayed records when the operation completes successfully. Records retain fixed name ordering (ascending) when the operation completes successfully. The "LOAD MORE" action is hidden when the returned batch contains fewer records than the requested batch size. The "NO DATA" message is displayed when the doctors collection is empty.
- Implement FR-09: The doctor view opens. The returned doctor details populate the form.
- Implement FR-12: The "Save" action is disabled while the form is invalid. The "Save" action is displayed when edit mode is active. The changes to the selected record are saved when the operation completes successfully. The doctors view opens when the operation completes successfully.
- Implement FR-14: The tenant context is obtained automatically before the dependent request runs.
- Preserve DELETE /api/doctors/{id} as an existing approved backend contract.
- Preserve GET /api/doctors as an existing approved backend contract.
- Preserve GET /api/doctors/{id} as an existing approved backend contract.
- Preserve GET /api/users/current/tenant as an existing approved backend contract.
- Preserve POST /api/doctors as an existing approved backend contract.
- Preserve PUT /api/doctors as an existing approved backend contract.

**Validation**
- Route review proves existing contracts remain unchanged.

**Architecture:** ARCH-039, ARCH-044, ARCH-051
**Requirements:** FR-01, FR-02, FR-03, FR-04, FR-05, FR-06, FR-09, FR-12, FR-14
**Stories:** story-doctor-directory-management-fr-01-add-doctor, story-doctor-directory-management-fr-02-delete-selected-doctor-records, story-doctor-directory-management-fr-03-delete-an-individual-doctor, story-doctor-directory-management-fr-04-delete-this-doctor, story-doctor-directory-management-fr-05-load-more, story-doctor-directory-management-fr-06-directory-presentation, story-doctor-directory-management-fr-09-open-doctor-details, story-doctor-directory-management-fr-12-save-doctor, story-doctor-directory-management-fr-14-automatic-tenant-context
**Acceptance criteria:** ac-doctor-directory-management-fr-01-add-doctor-001, ac-doctor-directory-management-fr-01-add-doctor-002, ac-doctor-directory-management-fr-01-add-doctor-003, ac-doctor-directory-management-fr-01-add-doctor-004, ac-doctor-directory-management-fr-02-delete-selected-doctor-records-001, ac-doctor-directory-management-fr-02-delete-selected-doctor-records-002, ac-doctor-directory-management-fr-02-delete-selected-doctor-records-003, ac-doctor-directory-management-fr-03-delete-an-individual-doctor-001, ac-doctor-directory-management-fr-03-delete-an-individual-doctor-002, ac-doctor-directory-management-fr-04-delete-this-doctor-001, ac-doctor-directory-management-fr-04-delete-this-doctor-002, ac-doctor-directory-management-fr-05-load-more-001, ac-doctor-directory-management-fr-05-load-more-002, ac-doctor-directory-management-fr-05-load-more-003, ac-doctor-directory-management-fr-05-load-more-004, ac-doctor-directory-management-fr-06-directory-presentation-001, ac-doctor-directory-management-fr-06-directory-presentation-002, ac-doctor-directory-management-fr-06-directory-presentation-003, ac-doctor-directory-management-fr-06-directory-presentation-004, ac-doctor-directory-management-fr-09-open-doctor-details-001, ac-doctor-directory-management-fr-09-open-doctor-details-002, ac-doctor-directory-management-fr-12-save-doctor-001, ac-doctor-directory-management-fr-12-save-doctor-002, ac-doctor-directory-management-fr-12-save-doctor-003, ac-doctor-directory-management-fr-12-save-doctor-004, ac-doctor-directory-management-fr-14-automatic-tenant-context-001
**APIs:** API-01, API-02, API-03, API-04, API-05, API-06
**Implementation evidence:** None found
**Design:** NOT_PROVIDED

### TT-006 · Design the future Doctor Directory Management BFF boundary

**Category:** `BFF`
**Depends on:** TT-005
**Existing implementation:** `NOT_IMPLEMENTED`

Plan frontend-specific orchestration without inventing business behavior.

**Implementation requirements**
- Label every future facade TARGET_CONTRACT_TO_BE_DESIGNED.
- Trace justified orchestration to approved APIs and requirements.
- Implement FR-01: The "Add" action is disabled while the form is invalid. The "Add" action is displayed when edit mode is inactive. The doctors view opens when the operation completes successfully. The new record is saved when the operation completes successfully.
- Implement FR-02: Confirmation is requested before the guarded action proceeds. The "Delete" action is displayed when at least one record is selected. The affected doctors are removed from the displayed collection when the operation completes successfully.
- Implement FR-03: Confirmation is requested before the guarded action proceeds. The affected doctors are removed from the displayed collection when the operation completes successfully.
- Implement FR-04: Confirmation is requested before the guarded action proceeds. The doctors view opens when the operation completes successfully.
- Implement FR-05: Additional doctors are appended after the displayed records when the operation completes successfully. Records retain fixed name ordering (ascending) when the operation completes successfully. The "LOAD MORE" action is hidden when the returned batch contains fewer records than the requested batch size. The "NO DATA" message is displayed when the doctors collection is empty.
- Implement FR-06: Additional doctors are appended after the displayed records when the operation completes successfully. Records retain fixed name ordering (ascending) when the operation completes successfully. The "LOAD MORE" action is hidden when the returned batch contains fewer records than the requested batch size. The "NO DATA" message is displayed when the doctors collection is empty.
- Implement FR-09: The doctor view opens. The returned doctor details populate the form.
- Implement FR-12: The "Save" action is disabled while the form is invalid. The "Save" action is displayed when edit mode is active. The changes to the selected record are saved when the operation completes successfully. The doctors view opens when the operation completes successfully.
- Implement FR-14: The tenant context is obtained automatically before the dependent request runs.

**Validation**
- No future facade is represented as an existing API.

**Architecture:** ARCH-041, ARCH-044, ARCH-051
**Requirements:** FR-01, FR-02, FR-03, FR-04, FR-05, FR-06, FR-09, FR-12, FR-14
**Stories:** story-doctor-directory-management-fr-01-add-doctor, story-doctor-directory-management-fr-02-delete-selected-doctor-records, story-doctor-directory-management-fr-03-delete-an-individual-doctor, story-doctor-directory-management-fr-04-delete-this-doctor, story-doctor-directory-management-fr-05-load-more, story-doctor-directory-management-fr-06-directory-presentation, story-doctor-directory-management-fr-09-open-doctor-details, story-doctor-directory-management-fr-12-save-doctor, story-doctor-directory-management-fr-14-automatic-tenant-context
**Acceptance criteria:** ac-doctor-directory-management-fr-01-add-doctor-001, ac-doctor-directory-management-fr-01-add-doctor-002, ac-doctor-directory-management-fr-01-add-doctor-003, ac-doctor-directory-management-fr-01-add-doctor-004, ac-doctor-directory-management-fr-02-delete-selected-doctor-records-001, ac-doctor-directory-management-fr-02-delete-selected-doctor-records-002, ac-doctor-directory-management-fr-02-delete-selected-doctor-records-003, ac-doctor-directory-management-fr-03-delete-an-individual-doctor-001, ac-doctor-directory-management-fr-03-delete-an-individual-doctor-002, ac-doctor-directory-management-fr-04-delete-this-doctor-001, ac-doctor-directory-management-fr-04-delete-this-doctor-002, ac-doctor-directory-management-fr-05-load-more-001, ac-doctor-directory-management-fr-05-load-more-002, ac-doctor-directory-management-fr-05-load-more-003, ac-doctor-directory-management-fr-05-load-more-004, ac-doctor-directory-management-fr-06-directory-presentation-001, ac-doctor-directory-management-fr-06-directory-presentation-002, ac-doctor-directory-management-fr-06-directory-presentation-003, ac-doctor-directory-management-fr-06-directory-presentation-004, ac-doctor-directory-management-fr-09-open-doctor-details-001, ac-doctor-directory-management-fr-09-open-doctor-details-002, ac-doctor-directory-management-fr-12-save-doctor-001, ac-doctor-directory-management-fr-12-save-doctor-002, ac-doctor-directory-management-fr-12-save-doctor-003, ac-doctor-directory-management-fr-12-save-doctor-004, ac-doctor-directory-management-fr-14-automatic-tenant-context-001
**APIs:** API-01, API-02, API-03, API-04, API-05, API-06
**Implementation evidence:** None found
**Design:** NOT_PROVIDED

### TT-007 · Define the Doctor Directory Management integration boundary

**Category:** `INTEGRATION`
**Depends on:** TT-004, TT-006
**Existing implementation:** `PARTIALLY_IMPLEMENTED`

Connect the Feature to selected target integration layers.

**Implementation requirements**
- Create typed integration ports for approved contracts.
- Keep future facade contracts explicitly unapproved until designed.
- Implement FR-01: The "Add" action is disabled while the form is invalid. The "Add" action is displayed when edit mode is inactive. The doctors view opens when the operation completes successfully. The new record is saved when the operation completes successfully.
- Implement FR-02: Confirmation is requested before the guarded action proceeds. The "Delete" action is displayed when at least one record is selected. The affected doctors are removed from the displayed collection when the operation completes successfully.
- Implement FR-03: Confirmation is requested before the guarded action proceeds. The affected doctors are removed from the displayed collection when the operation completes successfully.
- Implement FR-04: Confirmation is requested before the guarded action proceeds. The doctors view opens when the operation completes successfully.
- Implement FR-05: Additional doctors are appended after the displayed records when the operation completes successfully. Records retain fixed name ordering (ascending) when the operation completes successfully. The "LOAD MORE" action is hidden when the returned batch contains fewer records than the requested batch size. The "NO DATA" message is displayed when the doctors collection is empty.
- Implement FR-06: Additional doctors are appended after the displayed records when the operation completes successfully. Records retain fixed name ordering (ascending) when the operation completes successfully. The "LOAD MORE" action is hidden when the returned batch contains fewer records than the requested batch size. The "NO DATA" message is displayed when the doctors collection is empty.
- Implement FR-09: The doctor view opens. The returned doctor details populate the form.
- Implement FR-12: The "Save" action is disabled while the form is invalid. The "Save" action is displayed when edit mode is active. The changes to the selected record are saved when the operation completes successfully. The doctors view opens when the operation completes successfully.
- Implement FR-14: The tenant context is obtained automatically before the dependent request runs.
- Preserve DELETE /api/doctors/{id} as an existing approved backend contract.
- Preserve GET /api/doctors as an existing approved backend contract.
- Preserve GET /api/doctors/{id} as an existing approved backend contract.
- Preserve GET /api/users/current/tenant as an existing approved backend contract.
- Preserve POST /api/doctors as an existing approved backend contract.
- Preserve PUT /api/doctors as an existing approved backend contract.

**Validation**
- Feature code depends on typed integration ports.

**Architecture:** ARCH-037, ARCH-038, ARCH-041
**Requirements:** FR-01, FR-02, FR-03, FR-04, FR-05, FR-06, FR-09, FR-12, FR-14
**Stories:** story-doctor-directory-management-fr-01-add-doctor, story-doctor-directory-management-fr-02-delete-selected-doctor-records, story-doctor-directory-management-fr-03-delete-an-individual-doctor, story-doctor-directory-management-fr-04-delete-this-doctor, story-doctor-directory-management-fr-05-load-more, story-doctor-directory-management-fr-06-directory-presentation, story-doctor-directory-management-fr-09-open-doctor-details, story-doctor-directory-management-fr-12-save-doctor, story-doctor-directory-management-fr-14-automatic-tenant-context
**Acceptance criteria:** ac-doctor-directory-management-fr-01-add-doctor-001, ac-doctor-directory-management-fr-01-add-doctor-002, ac-doctor-directory-management-fr-01-add-doctor-003, ac-doctor-directory-management-fr-01-add-doctor-004, ac-doctor-directory-management-fr-02-delete-selected-doctor-records-001, ac-doctor-directory-management-fr-02-delete-selected-doctor-records-002, ac-doctor-directory-management-fr-02-delete-selected-doctor-records-003, ac-doctor-directory-management-fr-03-delete-an-individual-doctor-001, ac-doctor-directory-management-fr-03-delete-an-individual-doctor-002, ac-doctor-directory-management-fr-04-delete-this-doctor-001, ac-doctor-directory-management-fr-04-delete-this-doctor-002, ac-doctor-directory-management-fr-05-load-more-001, ac-doctor-directory-management-fr-05-load-more-002, ac-doctor-directory-management-fr-05-load-more-003, ac-doctor-directory-management-fr-05-load-more-004, ac-doctor-directory-management-fr-06-directory-presentation-001, ac-doctor-directory-management-fr-06-directory-presentation-002, ac-doctor-directory-management-fr-06-directory-presentation-003, ac-doctor-directory-management-fr-06-directory-presentation-004, ac-doctor-directory-management-fr-09-open-doctor-details-001, ac-doctor-directory-management-fr-09-open-doctor-details-002, ac-doctor-directory-management-fr-12-save-doctor-001, ac-doctor-directory-management-fr-12-save-doctor-002, ac-doctor-directory-management-fr-12-save-doctor-003, ac-doctor-directory-management-fr-12-save-doctor-004, ac-doctor-directory-management-fr-14-automatic-tenant-context-001
**APIs:** API-01, API-02, API-03, API-04, API-05, API-06
**Implementation evidence:** modernized\libs\doctor-directory-management\feature\src\lib\doctor-list.component.ts, modernized\libs\doctor-directory-management\feature\src\lib\doctor-list.component.html, modernized\libs\doctor-directory-management\feature\src\lib\doctor-detail.component.ts, modernized\libs\doctor-directory-management\feature\src\lib\doctor-detail.component.html, modernized\libs\doctor-directory-management\data-access\src\lib\doctor-api.client.ts, modernized\libs\doctor-directory-management\data-access\src\lib\doctor-api.client.spec.ts, modernized\apps\healthclinic-web-e2e\src\doctor-directory-management.spec.ts, modernized\libs\doctor-directory-management\data-access\project.json, modernized\libs\doctor-directory-management\data-access\src\index.ts, modernized\libs\doctor-directory-management\data-access\src\lib\doctor.models.ts, modernized\libs\doctor-directory-management\state\project.json, modernized\libs\doctor-directory-management\state\src\index.ts, modernized\libs\doctor-directory-management\state\src\lib\doctor-directory.store.ts, modernized\libs\doctor-directory-management\state\src\lib\doctor-directory.store.spec.ts, modernized\libs\doctor-directory-management\feature\project.json, modernized\libs\doctor-directory-management\feature\src\index.ts, modernized\libs\doctor-directory-management\feature\src\lib\doctor-directory.routes.ts, modernized\libs\doctor-directory-management\feature\src\lib\doctor-directory.component.css, modernized\libs\doctor-directory-management\feature\src\lib\doctor-directory.component.spec.ts
**Design:** NOT_PROVIDED

### TT-008 · Configure lazy routes for Doctor Directory Management

**Category:** `ROUTING`
**Depends on:** TT-002
**Existing implementation:** `PARTIALLY_IMPLEMENTED`

Expose approved Feature surfaces through selected routing patterns.

**Implementation requirements**
- Register lazy Feature routes and selected guard boundaries.
- Do not invent identity-provider behavior.
- Implement FR-01: The "Add" action is disabled while the form is invalid. The "Add" action is displayed when edit mode is inactive. The doctors view opens when the operation completes successfully. The new record is saved when the operation completes successfully.
- Implement FR-04: Confirmation is requested before the guarded action proceeds. The doctors view opens when the operation completes successfully.
- Implement FR-07: The doctor view opens.
- Implement FR-08: The doctors view opens.
- Implement FR-09: The doctor view opens. The returned doctor details populate the form.
- Implement FR-10: The "Patients" action is displayed when edit mode is active. The patients view opens.
- Implement FR-12: The "Save" action is disabled while the form is invalid. The "Save" action is displayed when edit mode is active. The changes to the selected record are saved when the operation completes successfully. The doctors view opens when the operation completes successfully.

**Validation**
- Routes load lazily and preserve approved access behavior.

**Architecture:** ARCH-024, ARCH-025, ARCH-026, ARCH-028
**Requirements:** FR-01, FR-04, FR-07, FR-08, FR-09, FR-10, FR-12
**Stories:** story-doctor-directory-management-fr-01-add-doctor, story-doctor-directory-management-fr-04-delete-this-doctor, story-doctor-directory-management-fr-07-new-doctor, story-doctor-directory-management-fr-08-back-to-doctors, story-doctor-directory-management-fr-09-open-doctor-details, story-doctor-directory-management-fr-10-patients, story-doctor-directory-management-fr-12-save-doctor
**Acceptance criteria:** ac-doctor-directory-management-fr-01-add-doctor-001, ac-doctor-directory-management-fr-01-add-doctor-002, ac-doctor-directory-management-fr-01-add-doctor-003, ac-doctor-directory-management-fr-01-add-doctor-004, ac-doctor-directory-management-fr-04-delete-this-doctor-001, ac-doctor-directory-management-fr-04-delete-this-doctor-002, ac-doctor-directory-management-fr-07-new-doctor-001, ac-doctor-directory-management-fr-08-back-to-doctors-001, ac-doctor-directory-management-fr-09-open-doctor-details-001, ac-doctor-directory-management-fr-09-open-doctor-details-002, ac-doctor-directory-management-fr-10-patients-001, ac-doctor-directory-management-fr-10-patients-002, ac-doctor-directory-management-fr-12-save-doctor-001, ac-doctor-directory-management-fr-12-save-doctor-002, ac-doctor-directory-management-fr-12-save-doctor-003, ac-doctor-directory-management-fr-12-save-doctor-004
**APIs:** None
**Implementation evidence:** modernized\libs\doctor-directory-management\feature\src\lib\doctor-list.component.ts, modernized\libs\doctor-directory-management\feature\src\lib\doctor-list.component.html, modernized\libs\doctor-directory-management\feature\src\lib\doctor-detail.component.ts, modernized\libs\doctor-directory-management\feature\src\lib\doctor-detail.component.html, modernized\libs\doctor-directory-management\data-access\src\lib\doctor-api.client.ts, modernized\libs\doctor-directory-management\data-access\src\lib\doctor-api.client.spec.ts, modernized\apps\healthclinic-web-e2e\src\doctor-directory-management.spec.ts, modernized\libs\doctor-directory-management\data-access\project.json, modernized\libs\doctor-directory-management\data-access\src\index.ts, modernized\libs\doctor-directory-management\data-access\src\lib\doctor.models.ts, modernized\libs\doctor-directory-management\state\project.json, modernized\libs\doctor-directory-management\state\src\index.ts, modernized\libs\doctor-directory-management\state\src\lib\doctor-directory.store.ts, modernized\libs\doctor-directory-management\state\src\lib\doctor-directory.store.spec.ts, modernized\libs\doctor-directory-management\feature\project.json, modernized\libs\doctor-directory-management\feature\src\index.ts, modernized\libs\doctor-directory-management\feature\src\lib\doctor-directory.routes.ts, modernized\libs\doctor-directory-management\feature\src\lib\doctor-directory.component.css, modernized\libs\doctor-directory-management\feature\src\lib\doctor-directory.component.spec.ts
**Design:** NOT_PROVIDED

### TT-009 · Implement the Doctor Directory Management feature shell

**Category:** `UI`
**Depends on:** TT-003, TT-008
**Existing implementation:** `PARTIALLY_IMPLEMENTED`

Create the Feature container and approved presentation regions.

**Implementation requirements**
- Use existing application UI evidence and accessible implementation defaults because customer design input is unavailable.
- Render only behavior and information established by approved requirements.
- Implement FR-01: The "Add" action is disabled while the form is invalid. The "Add" action is displayed when edit mode is inactive. The doctors view opens when the operation completes successfully. The new record is saved when the operation completes successfully.
- Implement FR-02: Confirmation is requested before the guarded action proceeds. The "Delete" action is displayed when at least one record is selected. The affected doctors are removed from the displayed collection when the operation completes successfully.
- Implement FR-05: Additional doctors are appended after the displayed records when the operation completes successfully. Records retain fixed name ordering (ascending) when the operation completes successfully. The "LOAD MORE" action is hidden when the returned batch contains fewer records than the requested batch size. The "NO DATA" message is displayed when the doctors collection is empty.
- Implement FR-06: Additional doctors are appended after the displayed records when the operation completes successfully. Records retain fixed name ordering (ascending) when the operation completes successfully. The "LOAD MORE" action is hidden when the returned batch contains fewer records than the requested batch size. The "NO DATA" message is displayed when the doctors collection is empty.
- Implement FR-10: The "Patients" action is displayed when edit mode is active. The patients view opens.
- Implement FR-12: The "Save" action is disabled while the form is invalid. The "Save" action is displayed when edit mode is active. The changes to the selected record are saved when the operation completes successfully. The doctors view opens when the operation completes successfully.
- Implement FR-15: The "Add a profile photo" prompt is shown when no file content is set. The doctor picture preview is displayed when file content is set. The selected file content updates the doctor picture.

**Validation**
- The shell exposes all approved Feature workflows.

**Architecture:** ARCH-001, ARCH-002, ARCH-003, ARCH-004, ARCH-005, ARCH-034, ARCH-046
**Requirements:** FR-01, FR-02, FR-05, FR-06, FR-10, FR-12, FR-15
**Stories:** story-doctor-directory-management-fr-01-add-doctor, story-doctor-directory-management-fr-02-delete-selected-doctor-records, story-doctor-directory-management-fr-05-load-more, story-doctor-directory-management-fr-06-directory-presentation, story-doctor-directory-management-fr-10-patients, story-doctor-directory-management-fr-12-save-doctor, story-doctor-directory-management-fr-15-maintain-doctor-profile-media
**Acceptance criteria:** ac-doctor-directory-management-fr-01-add-doctor-001, ac-doctor-directory-management-fr-01-add-doctor-002, ac-doctor-directory-management-fr-01-add-doctor-003, ac-doctor-directory-management-fr-01-add-doctor-004, ac-doctor-directory-management-fr-02-delete-selected-doctor-records-001, ac-doctor-directory-management-fr-02-delete-selected-doctor-records-002, ac-doctor-directory-management-fr-02-delete-selected-doctor-records-003, ac-doctor-directory-management-fr-05-load-more-001, ac-doctor-directory-management-fr-05-load-more-002, ac-doctor-directory-management-fr-05-load-more-003, ac-doctor-directory-management-fr-05-load-more-004, ac-doctor-directory-management-fr-06-directory-presentation-001, ac-doctor-directory-management-fr-06-directory-presentation-002, ac-doctor-directory-management-fr-06-directory-presentation-003, ac-doctor-directory-management-fr-06-directory-presentation-004, ac-doctor-directory-management-fr-10-patients-001, ac-doctor-directory-management-fr-10-patients-002, ac-doctor-directory-management-fr-12-save-doctor-001, ac-doctor-directory-management-fr-12-save-doctor-002, ac-doctor-directory-management-fr-12-save-doctor-003, ac-doctor-directory-management-fr-12-save-doctor-004, ac-doctor-directory-management-fr-15-maintain-doctor-profile-media-001, ac-doctor-directory-management-fr-15-maintain-doctor-profile-media-002, ac-doctor-directory-management-fr-15-maintain-doctor-profile-media-003
**APIs:** None
**Implementation evidence:** modernized\libs\doctor-directory-management\feature\src\lib\doctor-list.component.ts, modernized\libs\doctor-directory-management\feature\src\lib\doctor-list.component.html, modernized\libs\doctor-directory-management\feature\src\lib\doctor-detail.component.ts, modernized\libs\doctor-directory-management\feature\src\lib\doctor-detail.component.html, modernized\libs\doctor-directory-management\data-access\src\lib\doctor-api.client.ts, modernized\libs\doctor-directory-management\data-access\src\lib\doctor-api.client.spec.ts, modernized\apps\healthclinic-web-e2e\src\doctor-directory-management.spec.ts, modernized\libs\doctor-directory-management\data-access\project.json, modernized\libs\doctor-directory-management\data-access\src\index.ts, modernized\libs\doctor-directory-management\data-access\src\lib\doctor.models.ts, modernized\libs\doctor-directory-management\state\project.json, modernized\libs\doctor-directory-management\state\src\index.ts, modernized\libs\doctor-directory-management\state\src\lib\doctor-directory.store.ts, modernized\libs\doctor-directory-management\state\src\lib\doctor-directory.store.spec.ts, modernized\libs\doctor-directory-management\feature\project.json, modernized\libs\doctor-directory-management\feature\src\index.ts, modernized\libs\doctor-directory-management\feature\src\lib\doctor-directory.routes.ts, modernized\libs\doctor-directory-management\feature\src\lib\doctor-directory.component.css, modernized\libs\doctor-directory-management\feature\src\lib\doctor-directory.component.spec.ts
**Design:** NOT_PROVIDED

### TT-010 · Implement Doctor Directory Management state and asynchronous flow

**Category:** `STATE`
**Depends on:** TT-004, TT-007, TT-009
**Existing implementation:** `PARTIALLY_IMPLEMENTED`

Separate synchronous UI state from asynchronous integration work.

**Implementation requirements**
- Use selected state primitives for local and derived UI state.
- Use selected asynchronous composition for API work and cancellation.
- Implement FR-02: Confirmation is requested before the guarded action proceeds. The "Delete" action is displayed when at least one record is selected. The affected doctors are removed from the displayed collection when the operation completes successfully.
- Implement FR-03: Confirmation is requested before the guarded action proceeds. The affected doctors are removed from the displayed collection when the operation completes successfully.
- Implement FR-05: Additional doctors are appended after the displayed records when the operation completes successfully. Records retain fixed name ordering (ascending) when the operation completes successfully. The "LOAD MORE" action is hidden when the returned batch contains fewer records than the requested batch size. The "NO DATA" message is displayed when the doctors collection is empty.
- Implement FR-06: Additional doctors are appended after the displayed records when the operation completes successfully. Records retain fixed name ordering (ascending) when the operation completes successfully. The "LOAD MORE" action is hidden when the returned batch contains fewer records than the requested batch size. The "NO DATA" message is displayed when the doctors collection is empty.
- Implement FR-11: All displayed record checkboxes reflect the select-all state.
- Implement FR-13: The chosen record reflects its checkbox selection state.
- Implement FR-14: The tenant context is obtained automatically before the dependent request runs.
- Preserve DELETE /api/doctors/{id} as an existing approved backend contract.
- Preserve GET /api/doctors as an existing approved backend contract.
- Preserve GET /api/doctors/{id} as an existing approved backend contract.
- Preserve GET /api/users/current/tenant as an existing approved backend contract.
- Preserve POST /api/doctors as an existing approved backend contract.
- Preserve PUT /api/doctors as an existing approved backend contract.

**Validation**
- State and asynchronous behavior are independently testable.

**Architecture:** ARCH-012, ARCH-013, ARCH-015, ARCH-016, ARCH-017, ARCH-021
**Requirements:** FR-02, FR-03, FR-05, FR-06, FR-11, FR-13, FR-14
**Stories:** story-doctor-directory-management-fr-02-delete-selected-doctor-records, story-doctor-directory-management-fr-03-delete-an-individual-doctor, story-doctor-directory-management-fr-05-load-more, story-doctor-directory-management-fr-06-directory-presentation, story-doctor-directory-management-fr-11-change-all-displayed-record-selections, story-doctor-directory-management-fr-13-change-an-individual-record-selection, story-doctor-directory-management-fr-14-automatic-tenant-context
**Acceptance criteria:** ac-doctor-directory-management-fr-02-delete-selected-doctor-records-001, ac-doctor-directory-management-fr-02-delete-selected-doctor-records-002, ac-doctor-directory-management-fr-02-delete-selected-doctor-records-003, ac-doctor-directory-management-fr-03-delete-an-individual-doctor-001, ac-doctor-directory-management-fr-03-delete-an-individual-doctor-002, ac-doctor-directory-management-fr-05-load-more-001, ac-doctor-directory-management-fr-05-load-more-002, ac-doctor-directory-management-fr-05-load-more-003, ac-doctor-directory-management-fr-05-load-more-004, ac-doctor-directory-management-fr-06-directory-presentation-001, ac-doctor-directory-management-fr-06-directory-presentation-002, ac-doctor-directory-management-fr-06-directory-presentation-003, ac-doctor-directory-management-fr-06-directory-presentation-004, ac-doctor-directory-management-fr-11-change-all-displayed-record-selections-001, ac-doctor-directory-management-fr-13-change-an-individual-record-selection-001, ac-doctor-directory-management-fr-14-automatic-tenant-context-001
**APIs:** API-01, API-02, API-03, API-04, API-05, API-06
**Implementation evidence:** modernized\libs\doctor-directory-management\feature\src\lib\doctor-list.component.html, modernized\libs\doctor-directory-management\feature\src\lib\doctor-detail.component.html, modernized\libs\doctor-directory-management\data-access\project.json, modernized\libs\doctor-directory-management\data-access\src\index.ts, modernized\libs\doctor-directory-management\data-access\src\lib\doctor.models.ts, modernized\libs\doctor-directory-management\data-access\src\lib\doctor-api.client.ts, modernized\libs\doctor-directory-management\data-access\src\lib\doctor-api.client.spec.ts, modernized\libs\doctor-directory-management\state\project.json, modernized\libs\doctor-directory-management\state\src\index.ts, modernized\libs\doctor-directory-management\state\src\lib\doctor-directory.store.ts, modernized\libs\doctor-directory-management\state\src\lib\doctor-directory.store.spec.ts, modernized\libs\doctor-directory-management\feature\project.json, modernized\libs\doctor-directory-management\feature\src\index.ts, modernized\libs\doctor-directory-management\feature\src\lib\doctor-directory.routes.ts, modernized\libs\doctor-directory-management\feature\src\lib\doctor-list.component.ts, modernized\libs\doctor-directory-management\feature\src\lib\doctor-detail.component.ts, modernized\libs\doctor-directory-management\feature\src\lib\doctor-directory.component.css, modernized\libs\doctor-directory-management\feature\src\lib\doctor-directory.component.spec.ts, modernized\apps\healthclinic-web-e2e\src\doctor-directory-management.spec.ts
**Design:** NOT_PROVIDED

### TT-011 · Apply security and tenant context to Doctor Directory Management

**Category:** `SECURITY_CONTEXT`
**Depends on:** TT-005, TT-006, TT-010
**Existing implementation:** `IMPLEMENTED`

Preserve approved access context through target integration boundaries.

**Implementation requirements**
- Propagate approved security, tenant, and correlation context.
- Keep unresolved identity-provider choices explicit.
- Implement FR-14: The tenant context is obtained automatically before the dependent request runs.
- Preserve DELETE /api/doctors/{id} as an existing approved backend contract.
- Preserve GET /api/doctors as an existing approved backend contract.
- Preserve GET /api/doctors/{id} as an existing approved backend contract.
- Preserve GET /api/users/current/tenant as an existing approved backend contract.
- Preserve POST /api/doctors as an existing approved backend contract.
- Preserve PUT /api/doctors as an existing approved backend contract.

**Validation**
- Tests prove context propagation without unsupported assumptions.

**Architecture:** ARCH-024, ARCH-025, ARCH-026, ARCH-037, ARCH-038, ARCH-044
**Requirements:** FR-14
**Stories:** story-doctor-directory-management-fr-14-automatic-tenant-context
**Acceptance criteria:** ac-doctor-directory-management-fr-14-automatic-tenant-context-001
**APIs:** API-01, API-02, API-03, API-04, API-05, API-06
**Implementation evidence:** modernized\libs\doctor-directory-management\data-access\src\lib\doctor-api.client.ts, modernized\libs\doctor-directory-management\data-access\src\lib\doctor-api.client.spec.ts, modernized\libs\doctor-directory-management\state\src\lib\doctor-directory.store.ts, modernized\libs\doctor-directory-management\state\src\lib\doctor-directory.store.spec.ts, modernized\libs\doctor-directory-management\feature\src\lib\doctor-detail.component.ts, modernized\apps\healthclinic-web-e2e\src\doctor-directory-management.spec.ts
**Design:** NOT_PROVIDED

### TT-012 · Implement approved Doctor Directory Management interactions

**Category:** `UI`
**Depends on:** TT-010, TT-011
**Existing implementation:** `PARTIALLY_IMPLEMENTED`

Connect approved workflows to Feature state and integrations.

**Implementation requirements**
- Implement approved interactions and observable outcomes.
- Do not invent fields, validation rules, or business behavior.
- Implement FR-01: The "Add" action is disabled while the form is invalid. The "Add" action is displayed when edit mode is inactive. The doctors view opens when the operation completes successfully. The new record is saved when the operation completes successfully.
- Implement FR-02: Confirmation is requested before the guarded action proceeds. The "Delete" action is displayed when at least one record is selected. The affected doctors are removed from the displayed collection when the operation completes successfully.
- Implement FR-03: Confirmation is requested before the guarded action proceeds. The affected doctors are removed from the displayed collection when the operation completes successfully.
- Implement FR-04: Confirmation is requested before the guarded action proceeds. The doctors view opens when the operation completes successfully.
- Implement FR-11: All displayed record checkboxes reflect the select-all state.
- Implement FR-12: The "Save" action is disabled while the form is invalid. The "Save" action is displayed when edit mode is active. The changes to the selected record are saved when the operation completes successfully. The doctors view opens when the operation completes successfully.
- Implement FR-13: The chosen record reflects its checkbox selection state.
- Implement FR-15: The "Add a profile photo" prompt is shown when no file content is set. The doctor picture preview is displayed when file content is set. The selected file content updates the doctor picture.
- Implement FR-16: Doctor address remains invalid until a value is provided.
- Implement FR-17: Doctor description remains invalid until a value is provided.
- Implement FR-18: Doctor email remains invalid until a value is provided.
- Implement FR-19: Doctor mobile remains invalid until a value is provided.
- Implement FR-20: Doctor phone remains invalid until a value is provided.
- Implement FR-21: Doctor name remains invalid until a value is provided.
- Preserve DELETE /api/doctors/{id} as an existing approved backend contract.
- Preserve GET /api/doctors as an existing approved backend contract.
- Preserve GET /api/doctors/{id} as an existing approved backend contract.
- Preserve GET /api/users/current/tenant as an existing approved backend contract.
- Preserve POST /api/doctors as an existing approved backend contract.
- Preserve PUT /api/doctors as an existing approved backend contract.

**Validation**
- Every interaction traces to approved requirements and contracts.

**Architecture:** ARCH-001, ARCH-002, ARCH-003, ARCH-004, ARCH-005, ARCH-034, ARCH-046
**Requirements:** FR-01, FR-02, FR-03, FR-04, FR-11, FR-12, FR-13, FR-15, FR-16, FR-17, FR-18, FR-19, FR-20, FR-21
**Stories:** story-doctor-directory-management-fr-01-add-doctor, story-doctor-directory-management-fr-02-delete-selected-doctor-records, story-doctor-directory-management-fr-03-delete-an-individual-doctor, story-doctor-directory-management-fr-04-delete-this-doctor, story-doctor-directory-management-fr-11-change-all-displayed-record-selections, story-doctor-directory-management-fr-12-save-doctor, story-doctor-directory-management-fr-13-change-an-individual-record-selection, story-doctor-directory-management-fr-15-maintain-doctor-profile-media, story-doctor-directory-management-fr-16-validate-doctor-address, story-doctor-directory-management-fr-17-validate-doctor-description, story-doctor-directory-management-fr-18-validate-doctor-email, story-doctor-directory-management-fr-19-validate-doctor-mobile, story-doctor-directory-management-fr-20-validate-doctor-phone, story-doctor-directory-management-fr-21-validate-doctor-name
**Acceptance criteria:** ac-doctor-directory-management-fr-01-add-doctor-001, ac-doctor-directory-management-fr-01-add-doctor-002, ac-doctor-directory-management-fr-01-add-doctor-003, ac-doctor-directory-management-fr-01-add-doctor-004, ac-doctor-directory-management-fr-02-delete-selected-doctor-records-001, ac-doctor-directory-management-fr-02-delete-selected-doctor-records-002, ac-doctor-directory-management-fr-02-delete-selected-doctor-records-003, ac-doctor-directory-management-fr-03-delete-an-individual-doctor-001, ac-doctor-directory-management-fr-03-delete-an-individual-doctor-002, ac-doctor-directory-management-fr-04-delete-this-doctor-001, ac-doctor-directory-management-fr-04-delete-this-doctor-002, ac-doctor-directory-management-fr-11-change-all-displayed-record-selections-001, ac-doctor-directory-management-fr-12-save-doctor-001, ac-doctor-directory-management-fr-12-save-doctor-002, ac-doctor-directory-management-fr-12-save-doctor-003, ac-doctor-directory-management-fr-12-save-doctor-004, ac-doctor-directory-management-fr-13-change-an-individual-record-selection-001, ac-doctor-directory-management-fr-15-maintain-doctor-profile-media-001, ac-doctor-directory-management-fr-15-maintain-doctor-profile-media-002, ac-doctor-directory-management-fr-15-maintain-doctor-profile-media-003, ac-doctor-directory-management-fr-16-validate-doctor-address-001, ac-doctor-directory-management-fr-17-validate-doctor-description-001, ac-doctor-directory-management-fr-18-validate-doctor-email-001, ac-doctor-directory-management-fr-19-validate-doctor-mobile-001, ac-doctor-directory-management-fr-20-validate-doctor-phone-001, ac-doctor-directory-management-fr-21-validate-doctor-name-001
**APIs:** API-01, API-02, API-03, API-04, API-05, API-06
**Implementation evidence:** modernized\libs\doctor-directory-management\feature\src\lib\doctor-list.component.ts, modernized\libs\doctor-directory-management\feature\src\lib\doctor-list.component.html, modernized\libs\doctor-directory-management\feature\src\lib\doctor-detail.component.ts, modernized\libs\doctor-directory-management\feature\src\lib\doctor-detail.component.html, modernized\libs\doctor-directory-management\data-access\src\lib\doctor-api.client.ts, modernized\libs\doctor-directory-management\data-access\src\lib\doctor-api.client.spec.ts, modernized\apps\healthclinic-web-e2e\src\doctor-directory-management.spec.ts, modernized\libs\doctor-directory-management\data-access\project.json, modernized\libs\doctor-directory-management\data-access\src\index.ts, modernized\libs\doctor-directory-management\data-access\src\lib\doctor.models.ts, modernized\libs\doctor-directory-management\state\project.json, modernized\libs\doctor-directory-management\state\src\index.ts, modernized\libs\doctor-directory-management\state\src\lib\doctor-directory.store.ts, modernized\libs\doctor-directory-management\state\src\lib\doctor-directory.store.spec.ts, modernized\libs\doctor-directory-management\feature\project.json, modernized\libs\doctor-directory-management\feature\src\index.ts, modernized\libs\doctor-directory-management\feature\src\lib\doctor-directory.routes.ts, modernized\libs\doctor-directory-management\feature\src\lib\doctor-directory.component.css, modernized\libs\doctor-directory-management\feature\src\lib\doctor-directory.component.spec.ts
**Design:** NOT_PROVIDED

### TT-013 · Validate accessible Doctor Directory Management behavior

**Category:** `ACCESSIBILITY`
**Depends on:** TT-012
**Existing implementation:** `PARTIALLY_IMPLEMENTED`

Apply selected accessibility and responsive standards.

**Implementation requirements**
- Verify semantics, keyboard operation, focus, labels, contrast, and responsive reflow.
- Implement FR-01: The "Add" action is disabled while the form is invalid. The "Add" action is displayed when edit mode is inactive. The doctors view opens when the operation completes successfully. The new record is saved when the operation completes successfully.
- Implement FR-02: Confirmation is requested before the guarded action proceeds. The "Delete" action is displayed when at least one record is selected. The affected doctors are removed from the displayed collection when the operation completes successfully.
- Implement FR-03: Confirmation is requested before the guarded action proceeds. The affected doctors are removed from the displayed collection when the operation completes successfully.
- Implement FR-04: Confirmation is requested before the guarded action proceeds. The doctors view opens when the operation completes successfully.
- Implement FR-05: Additional doctors are appended after the displayed records when the operation completes successfully. Records retain fixed name ordering (ascending) when the operation completes successfully. The "LOAD MORE" action is hidden when the returned batch contains fewer records than the requested batch size. The "NO DATA" message is displayed when the doctors collection is empty.
- Implement FR-06: Additional doctors are appended after the displayed records when the operation completes successfully. Records retain fixed name ordering (ascending) when the operation completes successfully. The "LOAD MORE" action is hidden when the returned batch contains fewer records than the requested batch size. The "NO DATA" message is displayed when the doctors collection is empty.
- Implement FR-07: The doctor view opens.
- Implement FR-08: The doctors view opens.
- Implement FR-09: The doctor view opens. The returned doctor details populate the form.
- Implement FR-10: The "Patients" action is displayed when edit mode is active. The patients view opens.
- Implement FR-11: All displayed record checkboxes reflect the select-all state.
- Implement FR-12: The "Save" action is disabled while the form is invalid. The "Save" action is displayed when edit mode is active. The changes to the selected record are saved when the operation completes successfully. The doctors view opens when the operation completes successfully.
- Implement FR-13: The chosen record reflects its checkbox selection state.
- Implement FR-14: The tenant context is obtained automatically before the dependent request runs.
- Implement FR-15: The "Add a profile photo" prompt is shown when no file content is set. The doctor picture preview is displayed when file content is set. The selected file content updates the doctor picture.
- Implement FR-16: Doctor address remains invalid until a value is provided.
- Implement FR-17: Doctor description remains invalid until a value is provided.
- Implement FR-18: Doctor email remains invalid until a value is provided.
- Implement FR-19: Doctor mobile remains invalid until a value is provided.
- Implement FR-20: Doctor phone remains invalid until a value is provided.
- Implement FR-21: Doctor name remains invalid until a value is provided.

**Validation**
- Automated and manual accessibility evidence is recorded.

**Architecture:** ARCH-046, ARCH-048
**Requirements:** FR-01, FR-02, FR-03, FR-04, FR-05, FR-06, FR-07, FR-08, FR-09, FR-10, FR-11, FR-12, FR-13, FR-14, FR-15, FR-16, FR-17, FR-18, FR-19, FR-20, FR-21
**Stories:** story-doctor-directory-management-fr-01-add-doctor, story-doctor-directory-management-fr-02-delete-selected-doctor-records, story-doctor-directory-management-fr-03-delete-an-individual-doctor, story-doctor-directory-management-fr-04-delete-this-doctor, story-doctor-directory-management-fr-05-load-more, story-doctor-directory-management-fr-06-directory-presentation, story-doctor-directory-management-fr-07-new-doctor, story-doctor-directory-management-fr-08-back-to-doctors, story-doctor-directory-management-fr-09-open-doctor-details, story-doctor-directory-management-fr-10-patients, story-doctor-directory-management-fr-11-change-all-displayed-record-selections, story-doctor-directory-management-fr-12-save-doctor, story-doctor-directory-management-fr-13-change-an-individual-record-selection, story-doctor-directory-management-fr-14-automatic-tenant-context, story-doctor-directory-management-fr-15-maintain-doctor-profile-media, story-doctor-directory-management-fr-16-validate-doctor-address, story-doctor-directory-management-fr-17-validate-doctor-description, story-doctor-directory-management-fr-18-validate-doctor-email, story-doctor-directory-management-fr-19-validate-doctor-mobile, story-doctor-directory-management-fr-20-validate-doctor-phone, story-doctor-directory-management-fr-21-validate-doctor-name
**Acceptance criteria:** ac-doctor-directory-management-fr-01-add-doctor-001, ac-doctor-directory-management-fr-01-add-doctor-002, ac-doctor-directory-management-fr-01-add-doctor-003, ac-doctor-directory-management-fr-01-add-doctor-004, ac-doctor-directory-management-fr-02-delete-selected-doctor-records-001, ac-doctor-directory-management-fr-02-delete-selected-doctor-records-002, ac-doctor-directory-management-fr-02-delete-selected-doctor-records-003, ac-doctor-directory-management-fr-03-delete-an-individual-doctor-001, ac-doctor-directory-management-fr-03-delete-an-individual-doctor-002, ac-doctor-directory-management-fr-04-delete-this-doctor-001, ac-doctor-directory-management-fr-04-delete-this-doctor-002, ac-doctor-directory-management-fr-05-load-more-001, ac-doctor-directory-management-fr-05-load-more-002, ac-doctor-directory-management-fr-05-load-more-003, ac-doctor-directory-management-fr-05-load-more-004, ac-doctor-directory-management-fr-06-directory-presentation-001, ac-doctor-directory-management-fr-06-directory-presentation-002, ac-doctor-directory-management-fr-06-directory-presentation-003, ac-doctor-directory-management-fr-06-directory-presentation-004, ac-doctor-directory-management-fr-07-new-doctor-001, ac-doctor-directory-management-fr-08-back-to-doctors-001, ac-doctor-directory-management-fr-09-open-doctor-details-001, ac-doctor-directory-management-fr-09-open-doctor-details-002, ac-doctor-directory-management-fr-10-patients-001, ac-doctor-directory-management-fr-10-patients-002, ac-doctor-directory-management-fr-11-change-all-displayed-record-selections-001, ac-doctor-directory-management-fr-12-save-doctor-001, ac-doctor-directory-management-fr-12-save-doctor-002, ac-doctor-directory-management-fr-12-save-doctor-003, ac-doctor-directory-management-fr-12-save-doctor-004, ac-doctor-directory-management-fr-13-change-an-individual-record-selection-001, ac-doctor-directory-management-fr-14-automatic-tenant-context-001, ac-doctor-directory-management-fr-15-maintain-doctor-profile-media-001, ac-doctor-directory-management-fr-15-maintain-doctor-profile-media-002, ac-doctor-directory-management-fr-15-maintain-doctor-profile-media-003, ac-doctor-directory-management-fr-16-validate-doctor-address-001, ac-doctor-directory-management-fr-17-validate-doctor-description-001, ac-doctor-directory-management-fr-18-validate-doctor-email-001, ac-doctor-directory-management-fr-19-validate-doctor-mobile-001, ac-doctor-directory-management-fr-20-validate-doctor-phone-001, ac-doctor-directory-management-fr-21-validate-doctor-name-001
**APIs:** None
**Implementation evidence:** modernized\libs\doctor-directory-management\feature\src\lib\doctor-list.component.ts, modernized\libs\doctor-directory-management\feature\src\lib\doctor-list.component.html, modernized\libs\doctor-directory-management\feature\src\lib\doctor-detail.component.ts, modernized\libs\doctor-directory-management\feature\src\lib\doctor-detail.component.html, modernized\libs\doctor-directory-management\data-access\src\lib\doctor-api.client.ts, modernized\libs\doctor-directory-management\data-access\src\lib\doctor-api.client.spec.ts, modernized\apps\healthclinic-web-e2e\src\doctor-directory-management.spec.ts, modernized\libs\doctor-directory-management\data-access\project.json, modernized\libs\doctor-directory-management\data-access\src\index.ts, modernized\libs\doctor-directory-management\data-access\src\lib\doctor.models.ts, modernized\libs\doctor-directory-management\state\project.json, modernized\libs\doctor-directory-management\state\src\index.ts, modernized\libs\doctor-directory-management\state\src\lib\doctor-directory.store.ts, modernized\libs\doctor-directory-management\state\src\lib\doctor-directory.store.spec.ts, modernized\libs\doctor-directory-management\feature\project.json, modernized\libs\doctor-directory-management\feature\src\index.ts, modernized\libs\doctor-directory-management\feature\src\lib\doctor-directory.routes.ts, modernized\libs\doctor-directory-management\feature\src\lib\doctor-directory.component.css, modernized\libs\doctor-directory-management\feature\src\lib\doctor-directory.component.spec.ts
**Design:** NOT_PROVIDED

### TT-014 · Add correlated telemetry for Doctor Directory Management

**Category:** `OBSERVABILITY`
**Depends on:** TT-007, TT-010, TT-011
**Existing implementation:** `PARTIALLY_IMPLEMENTED`

Make integration failures diagnosable without selecting a vendor.

**Implementation requirements**
- Propagate correlation context across selected integration layers.
- Avoid recording sensitive business or tenant data.
- Implement FR-01: The "Add" action is disabled while the form is invalid. The "Add" action is displayed when edit mode is inactive. The doctors view opens when the operation completes successfully. The new record is saved when the operation completes successfully.
- Implement FR-02: Confirmation is requested before the guarded action proceeds. The "Delete" action is displayed when at least one record is selected. The affected doctors are removed from the displayed collection when the operation completes successfully.
- Implement FR-03: Confirmation is requested before the guarded action proceeds. The affected doctors are removed from the displayed collection when the operation completes successfully.
- Implement FR-04: Confirmation is requested before the guarded action proceeds. The doctors view opens when the operation completes successfully.
- Implement FR-05: Additional doctors are appended after the displayed records when the operation completes successfully. Records retain fixed name ordering (ascending) when the operation completes successfully. The "LOAD MORE" action is hidden when the returned batch contains fewer records than the requested batch size. The "NO DATA" message is displayed when the doctors collection is empty.
- Implement FR-06: Additional doctors are appended after the displayed records when the operation completes successfully. Records retain fixed name ordering (ascending) when the operation completes successfully. The "LOAD MORE" action is hidden when the returned batch contains fewer records than the requested batch size. The "NO DATA" message is displayed when the doctors collection is empty.
- Implement FR-09: The doctor view opens. The returned doctor details populate the form.
- Implement FR-12: The "Save" action is disabled while the form is invalid. The "Save" action is displayed when edit mode is active. The changes to the selected record are saved when the operation completes successfully. The doctors view opens when the operation completes successfully.
- Implement FR-14: The tenant context is obtained automatically before the dependent request runs.
- Preserve DELETE /api/doctors/{id} as an existing approved backend contract.
- Preserve GET /api/doctors as an existing approved backend contract.
- Preserve GET /api/doctors/{id} as an existing approved backend contract.
- Preserve GET /api/users/current/tenant as an existing approved backend contract.
- Preserve POST /api/doctors as an existing approved backend contract.
- Preserve PUT /api/doctors as an existing approved backend contract.

**Validation**
- Telemetry and failure handling are covered by tests.

**Architecture:** ARCH-039, ARCH-041, ARCH-051
**Requirements:** FR-01, FR-02, FR-03, FR-04, FR-05, FR-06, FR-09, FR-12, FR-14
**Stories:** story-doctor-directory-management-fr-01-add-doctor, story-doctor-directory-management-fr-02-delete-selected-doctor-records, story-doctor-directory-management-fr-03-delete-an-individual-doctor, story-doctor-directory-management-fr-04-delete-this-doctor, story-doctor-directory-management-fr-05-load-more, story-doctor-directory-management-fr-06-directory-presentation, story-doctor-directory-management-fr-09-open-doctor-details, story-doctor-directory-management-fr-12-save-doctor, story-doctor-directory-management-fr-14-automatic-tenant-context
**Acceptance criteria:** ac-doctor-directory-management-fr-01-add-doctor-001, ac-doctor-directory-management-fr-01-add-doctor-002, ac-doctor-directory-management-fr-01-add-doctor-003, ac-doctor-directory-management-fr-01-add-doctor-004, ac-doctor-directory-management-fr-02-delete-selected-doctor-records-001, ac-doctor-directory-management-fr-02-delete-selected-doctor-records-002, ac-doctor-directory-management-fr-02-delete-selected-doctor-records-003, ac-doctor-directory-management-fr-03-delete-an-individual-doctor-001, ac-doctor-directory-management-fr-03-delete-an-individual-doctor-002, ac-doctor-directory-management-fr-04-delete-this-doctor-001, ac-doctor-directory-management-fr-04-delete-this-doctor-002, ac-doctor-directory-management-fr-05-load-more-001, ac-doctor-directory-management-fr-05-load-more-002, ac-doctor-directory-management-fr-05-load-more-003, ac-doctor-directory-management-fr-05-load-more-004, ac-doctor-directory-management-fr-06-directory-presentation-001, ac-doctor-directory-management-fr-06-directory-presentation-002, ac-doctor-directory-management-fr-06-directory-presentation-003, ac-doctor-directory-management-fr-06-directory-presentation-004, ac-doctor-directory-management-fr-09-open-doctor-details-001, ac-doctor-directory-management-fr-09-open-doctor-details-002, ac-doctor-directory-management-fr-12-save-doctor-001, ac-doctor-directory-management-fr-12-save-doctor-002, ac-doctor-directory-management-fr-12-save-doctor-003, ac-doctor-directory-management-fr-12-save-doctor-004, ac-doctor-directory-management-fr-14-automatic-tenant-context-001
**APIs:** API-01, API-02, API-03, API-04, API-05, API-06
**Implementation evidence:** modernized\libs\doctor-directory-management\feature\src\lib\doctor-list.component.ts, modernized\libs\doctor-directory-management\feature\src\lib\doctor-list.component.html, modernized\libs\doctor-directory-management\feature\src\lib\doctor-detail.component.ts, modernized\libs\doctor-directory-management\feature\src\lib\doctor-detail.component.html, modernized\libs\doctor-directory-management\data-access\src\lib\doctor-api.client.ts, modernized\libs\doctor-directory-management\data-access\src\lib\doctor-api.client.spec.ts, modernized\apps\healthclinic-web-e2e\src\doctor-directory-management.spec.ts, modernized\libs\doctor-directory-management\data-access\project.json, modernized\libs\doctor-directory-management\data-access\src\index.ts, modernized\libs\doctor-directory-management\data-access\src\lib\doctor.models.ts, modernized\libs\doctor-directory-management\state\project.json, modernized\libs\doctor-directory-management\state\src\index.ts, modernized\libs\doctor-directory-management\state\src\lib\doctor-directory.store.ts, modernized\libs\doctor-directory-management\state\src\lib\doctor-directory.store.spec.ts, modernized\libs\doctor-directory-management\feature\project.json, modernized\libs\doctor-directory-management\feature\src\index.ts, modernized\libs\doctor-directory-management\feature\src\lib\doctor-directory.routes.ts, modernized\libs\doctor-directory-management\feature\src\lib\doctor-directory.component.css, modernized\libs\doctor-directory-management\feature\src\lib\doctor-directory.component.spec.ts
**Design:** NOT_PROVIDED

### TT-015 · Implement unit and component coverage for Doctor Directory Management

**Category:** `TEST`
**Depends on:** TT-012, TT-013, TT-014
**Existing implementation:** `PARTIALLY_IMPLEMENTED`

Verify Feature state, UI, routing, contracts, and accessibility.

**Implementation requirements**
- Cover approved synchronous, asynchronous, presentation, routing, and contract behavior.
- Implement FR-01: The "Add" action is disabled while the form is invalid. The "Add" action is displayed when edit mode is inactive. The doctors view opens when the operation completes successfully. The new record is saved when the operation completes successfully.
- Implement FR-02: Confirmation is requested before the guarded action proceeds. The "Delete" action is displayed when at least one record is selected. The affected doctors are removed from the displayed collection when the operation completes successfully.
- Implement FR-03: Confirmation is requested before the guarded action proceeds. The affected doctors are removed from the displayed collection when the operation completes successfully.
- Implement FR-04: Confirmation is requested before the guarded action proceeds. The doctors view opens when the operation completes successfully.
- Implement FR-05: Additional doctors are appended after the displayed records when the operation completes successfully. Records retain fixed name ordering (ascending) when the operation completes successfully. The "LOAD MORE" action is hidden when the returned batch contains fewer records than the requested batch size. The "NO DATA" message is displayed when the doctors collection is empty.
- Implement FR-06: Additional doctors are appended after the displayed records when the operation completes successfully. Records retain fixed name ordering (ascending) when the operation completes successfully. The "LOAD MORE" action is hidden when the returned batch contains fewer records than the requested batch size. The "NO DATA" message is displayed when the doctors collection is empty.
- Implement FR-07: The doctor view opens.
- Implement FR-08: The doctors view opens.
- Implement FR-09: The doctor view opens. The returned doctor details populate the form.
- Implement FR-10: The "Patients" action is displayed when edit mode is active. The patients view opens.
- Implement FR-11: All displayed record checkboxes reflect the select-all state.
- Implement FR-12: The "Save" action is disabled while the form is invalid. The "Save" action is displayed when edit mode is active. The changes to the selected record are saved when the operation completes successfully. The doctors view opens when the operation completes successfully.
- Implement FR-13: The chosen record reflects its checkbox selection state.
- Implement FR-14: The tenant context is obtained automatically before the dependent request runs.
- Implement FR-15: The "Add a profile photo" prompt is shown when no file content is set. The doctor picture preview is displayed when file content is set. The selected file content updates the doctor picture.
- Implement FR-16: Doctor address remains invalid until a value is provided.
- Implement FR-17: Doctor description remains invalid until a value is provided.
- Implement FR-18: Doctor email remains invalid until a value is provided.
- Implement FR-19: Doctor mobile remains invalid until a value is provided.
- Implement FR-20: Doctor phone remains invalid until a value is provided.
- Implement FR-21: Doctor name remains invalid until a value is provided.
- Preserve DELETE /api/doctors/{id} as an existing approved backend contract.
- Preserve GET /api/doctors as an existing approved backend contract.
- Preserve GET /api/doctors/{id} as an existing approved backend contract.
- Preserve GET /api/users/current/tenant as an existing approved backend contract.
- Preserve POST /api/doctors as an existing approved backend contract.
- Preserve PUT /api/doctors as an existing approved backend contract.

**Validation**
- Affected unit and component suites pass.
- ac-doctor-directory-management-fr-01-add-doctor-001: Given the doctor view is displayed after the user selects "Add"; when the operation completes successfully; then the doctors view opens.
- ac-doctor-directory-management-fr-01-add-doctor-002: Given edit mode is inactive; when the view evaluates which actions to display; then the "Add" action is displayed.
- ac-doctor-directory-management-fr-01-add-doctor-003: Given the doctor view is displayed; when the form contains incomplete or invalid input; then the "Add" action is disabled while the form is invalid.
- ac-doctor-directory-management-fr-01-add-doctor-004: Given the doctor view is displayed after the user selects "Add"; when the operation completes successfully; then the new record is saved.
- ac-doctor-directory-management-fr-02-delete-selected-doctor-records-001: Given the doctors view is displayed; when the user selects "Delete"; then confirmation is requested before the guarded action proceeds.
- ac-doctor-directory-management-fr-02-delete-selected-doctor-records-002: Given the doctors view is displayed after the user selects "Delete" and the user has confirmed the action; when the operation completes successfully; then the affected doctors are removed from the displayed collection.
- ac-doctor-directory-management-fr-02-delete-selected-doctor-records-003: Given at least one record is selected; when the view evaluates which actions to display; then the "Delete" action is displayed.
- ac-doctor-directory-management-fr-03-delete-an-individual-doctor-001: Given the doctors view is displayed; when the user selects the record's delete control; then confirmation is requested before the guarded action proceeds.
- ac-doctor-directory-management-fr-03-delete-an-individual-doctor-002: Given the doctors view is displayed and the user has confirmed the action; when the operation completes successfully; then the affected doctors are removed from the displayed collection.
- ac-doctor-directory-management-fr-04-delete-this-doctor-001: Given the doctor view is displayed; when the user selects "Delete this doctor"; then confirmation is requested before the guarded action proceeds.
- ac-doctor-directory-management-fr-04-delete-this-doctor-002: Given the doctor view is displayed after the user selects "Delete this doctor" and the user has confirmed the action; when the operation completes successfully; then the doctors view opens.
- ac-doctor-directory-management-fr-05-load-more-001: Given the doctors view is displayed after the user selects "LOAD MORE"; when the operation completes successfully; then additional doctors are appended after the displayed records.
- ac-doctor-directory-management-fr-05-load-more-002: Given the doctors view is displayed after the user selects "LOAD MORE"; when the doctors collection is empty; then the "NO DATA" message is displayed.
- ac-doctor-directory-management-fr-05-load-more-003: Given the doctors view is displayed after the user selects "LOAD MORE"; when the returned batch contains fewer records than the requested batch size; then the "LOAD MORE" action is hidden.
- ac-doctor-directory-management-fr-05-load-more-004: Given the doctors view is displayed after the user selects "LOAD MORE"; when the operation completes successfully; then records retain fixed name ordering (ascending).
- ac-doctor-directory-management-fr-06-directory-presentation-001: Given the directory view is opening; when the operation completes successfully; then additional doctors are appended after the displayed records.
- ac-doctor-directory-management-fr-06-directory-presentation-002: Given the directory view is opening; when the doctors collection is empty; then the "NO DATA" message is displayed.
- ac-doctor-directory-management-fr-06-directory-presentation-003: Given the directory view is opening; when the returned batch contains fewer records than the requested batch size; then the "LOAD MORE" action is hidden.
- ac-doctor-directory-management-fr-06-directory-presentation-004: Given the directory view is opening; when the operation completes successfully; then records retain fixed name ordering (ascending).
- ac-doctor-directory-management-fr-07-new-doctor-001: Given the doctors view is displayed; when the user selects "New doctor"; then the doctor view opens.
- ac-doctor-directory-management-fr-08-back-to-doctors-001: Given the doctor view is displayed; when the user selects "Back to doctors"; then the doctors view opens.
- ac-doctor-directory-management-fr-09-open-doctor-details-001: Given the doctors view is displayed; when the user selects the record's detail control; then the doctor view opens.
- ac-doctor-directory-management-fr-09-open-doctor-details-002: Given the doctors view is displayed; when the user selects the record's detail control; then the returned doctor details populate the form.
- ac-doctor-directory-management-fr-10-patients-001: Given the doctor view is displayed; when the user selects "Patients"; then the patients view opens.
- ac-doctor-directory-management-fr-10-patients-002: Given edit mode is active; when the view evaluates which actions to display; then the "Patients" action is displayed.
- ac-doctor-directory-management-fr-11-change-all-displayed-record-selections-001: Given the directory displays selectable records; when the user toggles the select-all checkbox; then all displayed record checkboxes reflect the select-all state.
- ac-doctor-directory-management-fr-12-save-doctor-001: Given the doctor view is displayed after the user selects "Save"; when the operation completes successfully; then the doctors view opens.
- ac-doctor-directory-management-fr-12-save-doctor-002: Given edit mode is active; when the view evaluates which actions to display; then the "Save" action is displayed.
- ac-doctor-directory-management-fr-12-save-doctor-003: Given the doctor view is displayed; when the form contains incomplete or invalid input; then the "Save" action is disabled while the form is invalid.
- ac-doctor-directory-management-fr-12-save-doctor-004: Given the doctor view is displayed after the user selects "Save"; when the operation completes successfully; then the changes to the selected record are saved.
- ac-doctor-directory-management-fr-13-change-an-individual-record-selection-001: Given the directory displays selectable records; when the user toggles a record checkbox; then the chosen record reflects its checkbox selection state.
- ac-doctor-directory-management-fr-14-automatic-tenant-context-001: Given a dependent operation is requested; when dependent operation initialization; then the tenant context is obtained automatically before the dependent request runs.
- ac-doctor-directory-management-fr-15-maintain-doctor-profile-media-001: Given the doctor view is displayed with its file input; when the selected file finishes reading; then the selected file content updates the doctor picture.
- ac-doctor-directory-management-fr-15-maintain-doctor-profile-media-002: Given the doctor view is displayed with its file input; when the profile file value changes; then the "Add a profile photo" prompt is shown when no file content is set.
- ac-doctor-directory-management-fr-15-maintain-doctor-profile-media-003: Given the doctor view is displayed with its file input; when the profile file value changes; then the doctor picture preview is displayed when file content is set.
- ac-doctor-directory-management-fr-16-validate-doctor-address-001: Given the doctor view is displayed; when the user leaves doctor address empty; then doctor address remains invalid until a value is provided.
- ac-doctor-directory-management-fr-17-validate-doctor-description-001: Given the doctor view is displayed; when the user leaves doctor description empty; then doctor description remains invalid until a value is provided.
- ac-doctor-directory-management-fr-18-validate-doctor-email-001: Given the doctor view is displayed; when the user leaves doctor email empty; then doctor email remains invalid until a value is provided.
- ac-doctor-directory-management-fr-19-validate-doctor-mobile-001: Given the doctor view is displayed; when the user leaves doctor mobile empty; then doctor mobile remains invalid until a value is provided.
- ac-doctor-directory-management-fr-20-validate-doctor-phone-001: Given the doctor view is displayed; when the user leaves doctor phone empty; then doctor phone remains invalid until a value is provided.
- ac-doctor-directory-management-fr-21-validate-doctor-name-001: Given the doctor view is displayed; when the user leaves doctor name empty; then doctor name remains invalid until a value is provided.

**Architecture:** ARCH-049, ARCH-050, ARCH-052
**Requirements:** FR-01, FR-02, FR-03, FR-04, FR-05, FR-06, FR-07, FR-08, FR-09, FR-10, FR-11, FR-12, FR-13, FR-14, FR-15, FR-16, FR-17, FR-18, FR-19, FR-20, FR-21
**Stories:** story-doctor-directory-management-fr-01-add-doctor, story-doctor-directory-management-fr-02-delete-selected-doctor-records, story-doctor-directory-management-fr-03-delete-an-individual-doctor, story-doctor-directory-management-fr-04-delete-this-doctor, story-doctor-directory-management-fr-05-load-more, story-doctor-directory-management-fr-06-directory-presentation, story-doctor-directory-management-fr-07-new-doctor, story-doctor-directory-management-fr-08-back-to-doctors, story-doctor-directory-management-fr-09-open-doctor-details, story-doctor-directory-management-fr-10-patients, story-doctor-directory-management-fr-11-change-all-displayed-record-selections, story-doctor-directory-management-fr-12-save-doctor, story-doctor-directory-management-fr-13-change-an-individual-record-selection, story-doctor-directory-management-fr-14-automatic-tenant-context, story-doctor-directory-management-fr-15-maintain-doctor-profile-media, story-doctor-directory-management-fr-16-validate-doctor-address, story-doctor-directory-management-fr-17-validate-doctor-description, story-doctor-directory-management-fr-18-validate-doctor-email, story-doctor-directory-management-fr-19-validate-doctor-mobile, story-doctor-directory-management-fr-20-validate-doctor-phone, story-doctor-directory-management-fr-21-validate-doctor-name
**Acceptance criteria:** ac-doctor-directory-management-fr-01-add-doctor-001, ac-doctor-directory-management-fr-01-add-doctor-002, ac-doctor-directory-management-fr-01-add-doctor-003, ac-doctor-directory-management-fr-01-add-doctor-004, ac-doctor-directory-management-fr-02-delete-selected-doctor-records-001, ac-doctor-directory-management-fr-02-delete-selected-doctor-records-002, ac-doctor-directory-management-fr-02-delete-selected-doctor-records-003, ac-doctor-directory-management-fr-03-delete-an-individual-doctor-001, ac-doctor-directory-management-fr-03-delete-an-individual-doctor-002, ac-doctor-directory-management-fr-04-delete-this-doctor-001, ac-doctor-directory-management-fr-04-delete-this-doctor-002, ac-doctor-directory-management-fr-05-load-more-001, ac-doctor-directory-management-fr-05-load-more-002, ac-doctor-directory-management-fr-05-load-more-003, ac-doctor-directory-management-fr-05-load-more-004, ac-doctor-directory-management-fr-06-directory-presentation-001, ac-doctor-directory-management-fr-06-directory-presentation-002, ac-doctor-directory-management-fr-06-directory-presentation-003, ac-doctor-directory-management-fr-06-directory-presentation-004, ac-doctor-directory-management-fr-07-new-doctor-001, ac-doctor-directory-management-fr-08-back-to-doctors-001, ac-doctor-directory-management-fr-09-open-doctor-details-001, ac-doctor-directory-management-fr-09-open-doctor-details-002, ac-doctor-directory-management-fr-10-patients-001, ac-doctor-directory-management-fr-10-patients-002, ac-doctor-directory-management-fr-11-change-all-displayed-record-selections-001, ac-doctor-directory-management-fr-12-save-doctor-001, ac-doctor-directory-management-fr-12-save-doctor-002, ac-doctor-directory-management-fr-12-save-doctor-003, ac-doctor-directory-management-fr-12-save-doctor-004, ac-doctor-directory-management-fr-13-change-an-individual-record-selection-001, ac-doctor-directory-management-fr-14-automatic-tenant-context-001, ac-doctor-directory-management-fr-15-maintain-doctor-profile-media-001, ac-doctor-directory-management-fr-15-maintain-doctor-profile-media-002, ac-doctor-directory-management-fr-15-maintain-doctor-profile-media-003, ac-doctor-directory-management-fr-16-validate-doctor-address-001, ac-doctor-directory-management-fr-17-validate-doctor-description-001, ac-doctor-directory-management-fr-18-validate-doctor-email-001, ac-doctor-directory-management-fr-19-validate-doctor-mobile-001, ac-doctor-directory-management-fr-20-validate-doctor-phone-001, ac-doctor-directory-management-fr-21-validate-doctor-name-001
**APIs:** API-01, API-02, API-03, API-04, API-05, API-06
**Implementation evidence:** modernized\libs\doctor-directory-management\feature\src\lib\doctor-list.component.ts, modernized\libs\doctor-directory-management\feature\src\lib\doctor-list.component.html, modernized\libs\doctor-directory-management\feature\src\lib\doctor-detail.component.ts, modernized\libs\doctor-directory-management\feature\src\lib\doctor-detail.component.html, modernized\libs\doctor-directory-management\data-access\src\lib\doctor-api.client.ts, modernized\libs\doctor-directory-management\data-access\src\lib\doctor-api.client.spec.ts, modernized\apps\healthclinic-web-e2e\src\doctor-directory-management.spec.ts, modernized\libs\doctor-directory-management\data-access\project.json, modernized\libs\doctor-directory-management\data-access\src\index.ts, modernized\libs\doctor-directory-management\data-access\src\lib\doctor.models.ts, modernized\libs\doctor-directory-management\state\project.json, modernized\libs\doctor-directory-management\state\src\index.ts, modernized\libs\doctor-directory-management\state\src\lib\doctor-directory.store.ts, modernized\libs\doctor-directory-management\state\src\lib\doctor-directory.store.spec.ts, modernized\libs\doctor-directory-management\feature\project.json, modernized\libs\doctor-directory-management\feature\src\index.ts, modernized\libs\doctor-directory-management\feature\src\lib\doctor-directory.routes.ts, modernized\libs\doctor-directory-management\feature\src\lib\doctor-directory.component.css, modernized\libs\doctor-directory-management\feature\src\lib\doctor-directory.component.spec.ts
**Design:** NOT_PROVIDED

### TT-016 · Automate approved Doctor Directory Management flows with Playwright

**Category:** `TEST`
**Depends on:** TT-015
**Existing implementation:** `PARTIALLY_IMPLEMENTED`

Provide end-to-end evidence for approved acceptance criteria.

**Implementation requirements**
- Map each browser scenario to authoritative acceptance criteria.
- Use controlled data without redefining unresolved behavior.
- Implement FR-01: The "Add" action is disabled while the form is invalid. The "Add" action is displayed when edit mode is inactive. The doctors view opens when the operation completes successfully. The new record is saved when the operation completes successfully.
- Implement FR-02: Confirmation is requested before the guarded action proceeds. The "Delete" action is displayed when at least one record is selected. The affected doctors are removed from the displayed collection when the operation completes successfully.
- Implement FR-03: Confirmation is requested before the guarded action proceeds. The affected doctors are removed from the displayed collection when the operation completes successfully.
- Implement FR-04: Confirmation is requested before the guarded action proceeds. The doctors view opens when the operation completes successfully.
- Implement FR-05: Additional doctors are appended after the displayed records when the operation completes successfully. Records retain fixed name ordering (ascending) when the operation completes successfully. The "LOAD MORE" action is hidden when the returned batch contains fewer records than the requested batch size. The "NO DATA" message is displayed when the doctors collection is empty.
- Implement FR-06: Additional doctors are appended after the displayed records when the operation completes successfully. Records retain fixed name ordering (ascending) when the operation completes successfully. The "LOAD MORE" action is hidden when the returned batch contains fewer records than the requested batch size. The "NO DATA" message is displayed when the doctors collection is empty.
- Implement FR-07: The doctor view opens.
- Implement FR-08: The doctors view opens.
- Implement FR-09: The doctor view opens. The returned doctor details populate the form.
- Implement FR-10: The "Patients" action is displayed when edit mode is active. The patients view opens.
- Implement FR-11: All displayed record checkboxes reflect the select-all state.
- Implement FR-12: The "Save" action is disabled while the form is invalid. The "Save" action is displayed when edit mode is active. The changes to the selected record are saved when the operation completes successfully. The doctors view opens when the operation completes successfully.
- Implement FR-13: The chosen record reflects its checkbox selection state.
- Implement FR-14: The tenant context is obtained automatically before the dependent request runs.
- Implement FR-15: The "Add a profile photo" prompt is shown when no file content is set. The doctor picture preview is displayed when file content is set. The selected file content updates the doctor picture.
- Implement FR-16: Doctor address remains invalid until a value is provided.
- Implement FR-17: Doctor description remains invalid until a value is provided.
- Implement FR-18: Doctor email remains invalid until a value is provided.
- Implement FR-19: Doctor mobile remains invalid until a value is provided.
- Implement FR-20: Doctor phone remains invalid until a value is provided.
- Implement FR-21: Doctor name remains invalid until a value is provided.
- Preserve DELETE /api/doctors/{id} as an existing approved backend contract.
- Preserve GET /api/doctors as an existing approved backend contract.
- Preserve GET /api/doctors/{id} as an existing approved backend contract.
- Preserve GET /api/users/current/tenant as an existing approved backend contract.
- Preserve POST /api/doctors as an existing approved backend contract.
- Preserve PUT /api/doctors as an existing approved backend contract.

**Validation**
- Every approved criterion has executable traceability.
- ac-doctor-directory-management-fr-01-add-doctor-001: Given the doctor view is displayed after the user selects "Add"; when the operation completes successfully; then the doctors view opens.
- ac-doctor-directory-management-fr-01-add-doctor-002: Given edit mode is inactive; when the view evaluates which actions to display; then the "Add" action is displayed.
- ac-doctor-directory-management-fr-01-add-doctor-003: Given the doctor view is displayed; when the form contains incomplete or invalid input; then the "Add" action is disabled while the form is invalid.
- ac-doctor-directory-management-fr-01-add-doctor-004: Given the doctor view is displayed after the user selects "Add"; when the operation completes successfully; then the new record is saved.
- ac-doctor-directory-management-fr-02-delete-selected-doctor-records-001: Given the doctors view is displayed; when the user selects "Delete"; then confirmation is requested before the guarded action proceeds.
- ac-doctor-directory-management-fr-02-delete-selected-doctor-records-002: Given the doctors view is displayed after the user selects "Delete" and the user has confirmed the action; when the operation completes successfully; then the affected doctors are removed from the displayed collection.
- ac-doctor-directory-management-fr-02-delete-selected-doctor-records-003: Given at least one record is selected; when the view evaluates which actions to display; then the "Delete" action is displayed.
- ac-doctor-directory-management-fr-03-delete-an-individual-doctor-001: Given the doctors view is displayed; when the user selects the record's delete control; then confirmation is requested before the guarded action proceeds.
- ac-doctor-directory-management-fr-03-delete-an-individual-doctor-002: Given the doctors view is displayed and the user has confirmed the action; when the operation completes successfully; then the affected doctors are removed from the displayed collection.
- ac-doctor-directory-management-fr-04-delete-this-doctor-001: Given the doctor view is displayed; when the user selects "Delete this doctor"; then confirmation is requested before the guarded action proceeds.
- ac-doctor-directory-management-fr-04-delete-this-doctor-002: Given the doctor view is displayed after the user selects "Delete this doctor" and the user has confirmed the action; when the operation completes successfully; then the doctors view opens.
- ac-doctor-directory-management-fr-05-load-more-001: Given the doctors view is displayed after the user selects "LOAD MORE"; when the operation completes successfully; then additional doctors are appended after the displayed records.
- ac-doctor-directory-management-fr-05-load-more-002: Given the doctors view is displayed after the user selects "LOAD MORE"; when the doctors collection is empty; then the "NO DATA" message is displayed.
- ac-doctor-directory-management-fr-05-load-more-003: Given the doctors view is displayed after the user selects "LOAD MORE"; when the returned batch contains fewer records than the requested batch size; then the "LOAD MORE" action is hidden.
- ac-doctor-directory-management-fr-05-load-more-004: Given the doctors view is displayed after the user selects "LOAD MORE"; when the operation completes successfully; then records retain fixed name ordering (ascending).
- ac-doctor-directory-management-fr-06-directory-presentation-001: Given the directory view is opening; when the operation completes successfully; then additional doctors are appended after the displayed records.
- ac-doctor-directory-management-fr-06-directory-presentation-002: Given the directory view is opening; when the doctors collection is empty; then the "NO DATA" message is displayed.
- ac-doctor-directory-management-fr-06-directory-presentation-003: Given the directory view is opening; when the returned batch contains fewer records than the requested batch size; then the "LOAD MORE" action is hidden.
- ac-doctor-directory-management-fr-06-directory-presentation-004: Given the directory view is opening; when the operation completes successfully; then records retain fixed name ordering (ascending).
- ac-doctor-directory-management-fr-07-new-doctor-001: Given the doctors view is displayed; when the user selects "New doctor"; then the doctor view opens.
- ac-doctor-directory-management-fr-08-back-to-doctors-001: Given the doctor view is displayed; when the user selects "Back to doctors"; then the doctors view opens.
- ac-doctor-directory-management-fr-09-open-doctor-details-001: Given the doctors view is displayed; when the user selects the record's detail control; then the doctor view opens.
- ac-doctor-directory-management-fr-09-open-doctor-details-002: Given the doctors view is displayed; when the user selects the record's detail control; then the returned doctor details populate the form.
- ac-doctor-directory-management-fr-10-patients-001: Given the doctor view is displayed; when the user selects "Patients"; then the patients view opens.
- ac-doctor-directory-management-fr-10-patients-002: Given edit mode is active; when the view evaluates which actions to display; then the "Patients" action is displayed.
- ac-doctor-directory-management-fr-11-change-all-displayed-record-selections-001: Given the directory displays selectable records; when the user toggles the select-all checkbox; then all displayed record checkboxes reflect the select-all state.
- ac-doctor-directory-management-fr-12-save-doctor-001: Given the doctor view is displayed after the user selects "Save"; when the operation completes successfully; then the doctors view opens.
- ac-doctor-directory-management-fr-12-save-doctor-002: Given edit mode is active; when the view evaluates which actions to display; then the "Save" action is displayed.
- ac-doctor-directory-management-fr-12-save-doctor-003: Given the doctor view is displayed; when the form contains incomplete or invalid input; then the "Save" action is disabled while the form is invalid.
- ac-doctor-directory-management-fr-12-save-doctor-004: Given the doctor view is displayed after the user selects "Save"; when the operation completes successfully; then the changes to the selected record are saved.
- ac-doctor-directory-management-fr-13-change-an-individual-record-selection-001: Given the directory displays selectable records; when the user toggles a record checkbox; then the chosen record reflects its checkbox selection state.
- ac-doctor-directory-management-fr-14-automatic-tenant-context-001: Given a dependent operation is requested; when dependent operation initialization; then the tenant context is obtained automatically before the dependent request runs.
- ac-doctor-directory-management-fr-15-maintain-doctor-profile-media-001: Given the doctor view is displayed with its file input; when the selected file finishes reading; then the selected file content updates the doctor picture.
- ac-doctor-directory-management-fr-15-maintain-doctor-profile-media-002: Given the doctor view is displayed with its file input; when the profile file value changes; then the "Add a profile photo" prompt is shown when no file content is set.
- ac-doctor-directory-management-fr-15-maintain-doctor-profile-media-003: Given the doctor view is displayed with its file input; when the profile file value changes; then the doctor picture preview is displayed when file content is set.
- ac-doctor-directory-management-fr-16-validate-doctor-address-001: Given the doctor view is displayed; when the user leaves doctor address empty; then doctor address remains invalid until a value is provided.
- ac-doctor-directory-management-fr-17-validate-doctor-description-001: Given the doctor view is displayed; when the user leaves doctor description empty; then doctor description remains invalid until a value is provided.
- ac-doctor-directory-management-fr-18-validate-doctor-email-001: Given the doctor view is displayed; when the user leaves doctor email empty; then doctor email remains invalid until a value is provided.
- ac-doctor-directory-management-fr-19-validate-doctor-mobile-001: Given the doctor view is displayed; when the user leaves doctor mobile empty; then doctor mobile remains invalid until a value is provided.
- ac-doctor-directory-management-fr-20-validate-doctor-phone-001: Given the doctor view is displayed; when the user leaves doctor phone empty; then doctor phone remains invalid until a value is provided.
- ac-doctor-directory-management-fr-21-validate-doctor-name-001: Given the doctor view is displayed; when the user leaves doctor name empty; then doctor name remains invalid until a value is provided.

**Architecture:** ARCH-049, ARCH-050, ARCH-052
**Requirements:** FR-01, FR-02, FR-03, FR-04, FR-05, FR-06, FR-07, FR-08, FR-09, FR-10, FR-11, FR-12, FR-13, FR-14, FR-15, FR-16, FR-17, FR-18, FR-19, FR-20, FR-21
**Stories:** story-doctor-directory-management-fr-01-add-doctor, story-doctor-directory-management-fr-02-delete-selected-doctor-records, story-doctor-directory-management-fr-03-delete-an-individual-doctor, story-doctor-directory-management-fr-04-delete-this-doctor, story-doctor-directory-management-fr-05-load-more, story-doctor-directory-management-fr-06-directory-presentation, story-doctor-directory-management-fr-07-new-doctor, story-doctor-directory-management-fr-08-back-to-doctors, story-doctor-directory-management-fr-09-open-doctor-details, story-doctor-directory-management-fr-10-patients, story-doctor-directory-management-fr-11-change-all-displayed-record-selections, story-doctor-directory-management-fr-12-save-doctor, story-doctor-directory-management-fr-13-change-an-individual-record-selection, story-doctor-directory-management-fr-14-automatic-tenant-context, story-doctor-directory-management-fr-15-maintain-doctor-profile-media, story-doctor-directory-management-fr-16-validate-doctor-address, story-doctor-directory-management-fr-17-validate-doctor-description, story-doctor-directory-management-fr-18-validate-doctor-email, story-doctor-directory-management-fr-19-validate-doctor-mobile, story-doctor-directory-management-fr-20-validate-doctor-phone, story-doctor-directory-management-fr-21-validate-doctor-name
**Acceptance criteria:** ac-doctor-directory-management-fr-01-add-doctor-001, ac-doctor-directory-management-fr-01-add-doctor-002, ac-doctor-directory-management-fr-01-add-doctor-003, ac-doctor-directory-management-fr-01-add-doctor-004, ac-doctor-directory-management-fr-02-delete-selected-doctor-records-001, ac-doctor-directory-management-fr-02-delete-selected-doctor-records-002, ac-doctor-directory-management-fr-02-delete-selected-doctor-records-003, ac-doctor-directory-management-fr-03-delete-an-individual-doctor-001, ac-doctor-directory-management-fr-03-delete-an-individual-doctor-002, ac-doctor-directory-management-fr-04-delete-this-doctor-001, ac-doctor-directory-management-fr-04-delete-this-doctor-002, ac-doctor-directory-management-fr-05-load-more-001, ac-doctor-directory-management-fr-05-load-more-002, ac-doctor-directory-management-fr-05-load-more-003, ac-doctor-directory-management-fr-05-load-more-004, ac-doctor-directory-management-fr-06-directory-presentation-001, ac-doctor-directory-management-fr-06-directory-presentation-002, ac-doctor-directory-management-fr-06-directory-presentation-003, ac-doctor-directory-management-fr-06-directory-presentation-004, ac-doctor-directory-management-fr-07-new-doctor-001, ac-doctor-directory-management-fr-08-back-to-doctors-001, ac-doctor-directory-management-fr-09-open-doctor-details-001, ac-doctor-directory-management-fr-09-open-doctor-details-002, ac-doctor-directory-management-fr-10-patients-001, ac-doctor-directory-management-fr-10-patients-002, ac-doctor-directory-management-fr-11-change-all-displayed-record-selections-001, ac-doctor-directory-management-fr-12-save-doctor-001, ac-doctor-directory-management-fr-12-save-doctor-002, ac-doctor-directory-management-fr-12-save-doctor-003, ac-doctor-directory-management-fr-12-save-doctor-004, ac-doctor-directory-management-fr-13-change-an-individual-record-selection-001, ac-doctor-directory-management-fr-14-automatic-tenant-context-001, ac-doctor-directory-management-fr-15-maintain-doctor-profile-media-001, ac-doctor-directory-management-fr-15-maintain-doctor-profile-media-002, ac-doctor-directory-management-fr-15-maintain-doctor-profile-media-003, ac-doctor-directory-management-fr-16-validate-doctor-address-001, ac-doctor-directory-management-fr-17-validate-doctor-description-001, ac-doctor-directory-management-fr-18-validate-doctor-email-001, ac-doctor-directory-management-fr-19-validate-doctor-mobile-001, ac-doctor-directory-management-fr-20-validate-doctor-phone-001, ac-doctor-directory-management-fr-21-validate-doctor-name-001
**APIs:** API-01, API-02, API-03, API-04, API-05, API-06
**Implementation evidence:** modernized\libs\doctor-directory-management\feature\src\lib\doctor-list.component.ts, modernized\libs\doctor-directory-management\feature\src\lib\doctor-list.component.html, modernized\libs\doctor-directory-management\feature\src\lib\doctor-detail.component.ts, modernized\libs\doctor-directory-management\feature\src\lib\doctor-detail.component.html, modernized\libs\doctor-directory-management\data-access\src\lib\doctor-api.client.ts, modernized\libs\doctor-directory-management\data-access\src\lib\doctor-api.client.spec.ts, modernized\apps\healthclinic-web-e2e\src\doctor-directory-management.spec.ts, modernized\libs\doctor-directory-management\data-access\project.json, modernized\libs\doctor-directory-management\data-access\src\index.ts, modernized\libs\doctor-directory-management\data-access\src\lib\doctor.models.ts, modernized\libs\doctor-directory-management\state\project.json, modernized\libs\doctor-directory-management\state\src\index.ts, modernized\libs\doctor-directory-management\state\src\lib\doctor-directory.store.ts, modernized\libs\doctor-directory-management\state\src\lib\doctor-directory.store.spec.ts, modernized\libs\doctor-directory-management\feature\project.json, modernized\libs\doctor-directory-management\feature\src\index.ts, modernized\libs\doctor-directory-management\feature\src\lib\doctor-directory.routes.ts, modernized\libs\doctor-directory-management\feature\src\lib\doctor-directory.component.css, modernized\libs\doctor-directory-management\feature\src\lib\doctor-directory.component.spec.ts
**Design:** NOT_PROVIDED
