import { expect, test, type Page, type Route } from '@playwright/test';

type DoctorRecord = {
  DoctorId: number;
  Name: string;
  Address: string;
  Description: string;
  Phone: string;
  Mobile: string;
  Email: string;
  Picture: string;
  Deleted: boolean;
  TenantId: number;
  Tenant: null;
  Speciality: string;
  CurrentRoomNumber: number;
  PatientCount: number;
  Synchronized: boolean;
  CreatedAt: string;
  Id: string;
  UpdatedAt: string | null;
  Version: string;
};

const doctor = (DoctorId: number, Name: string): DoctorRecord => ({
  DoctorId, Name, Address: `${DoctorId} Clinic Avenue`, Description: `${Name} profile`, Phone: '555-0100',
  Mobile: '555-0199', Email: `${Name.toLowerCase().replaceAll(' ', '.')}@example.test`, Picture: '', Deleted: false,
  TenantId: 7, Tenant: null, Speciality: 'Cardiology', CurrentRoomNumber: DoctorId, PatientCount: DoctorId + 2,
  Synchronized: false, CreatedAt: '2015-04-12T00:00:00Z', Id: String(DoctorId), UpdatedAt: null, Version: '1',
});

async function mockTenant(page: Page): Promise<void> {
  await page.route('**/api/users/current/tenant', async (route) => route.fulfill({ json: 7 }));
}

async function fulfillDoctors(route: Route, records: DoctorRecord[]): Promise<void> {
  expect(route.request().headers()['tenantid']).toBe('7');
  await route.fulfill({ json: records });
}

test('ac-doctor-directory-management-fr-14-automatic-tenant-context-001: reads the authenticated tenant and Doctor directory from the real legacy backend', async ({ page }) => {
  const username = process.env['HEALTHCLINIC_E2E_USERNAME'];
  const password = process.env['HEALTHCLINIC_E2E_PASSWORD'];
  test.skip(!username || !password, 'Authorized legacy credentials are required for the real-backend integration scenario.');

  await page.goto('http://localhost:5000/Account/Login');
  await page.locator('[name="UserName"]').fill(username!);
  await page.locator('[name="Password"]').fill(password!);
  await Promise.all([
    page.waitForURL(/\/Dashboard/),
    page.getByRole('button', { name: 'LOGIN' }).click(),
  ]);

  const [tenantResponse, doctorsResponse] = await Promise.all([
    page.waitForResponse((response) => response.url().includes('/api/users/current/tenant')),
    page.waitForResponse((response) => response.url().includes('/api/doctors?')),
    page.goto('http://localhost:4200/doctors'),
  ]);
  expect(tenantResponse.status()).toBe(200);
  expect(await tenantResponse.json()).toBe(1);
  expect(doctorsResponse.status()).toBe(200);
  expect(doctorsResponse.request().headers()['tenantid']).toBe('1');
  await expect(page.locator('.grid-row')).not.toHaveCount(0);
});

test('ac-doctor-directory-management-fr-05-load-more-001 ac-doctor-directory-management-fr-05-load-more-003 ac-doctor-directory-management-fr-05-load-more-004 ac-doctor-directory-management-fr-06-directory-presentation-001 ac-doctor-directory-management-fr-06-directory-presentation-003 ac-doctor-directory-management-fr-06-directory-presentation-004: appends, orders, and terminates directory continuation', async ({ page }) => {
  await mockTenant(page);
  await page.route('**/api/doctors?*', async (route) => {
    const pageCount = Number(new URL(route.request().url()).searchParams.get('pageCount'));
    await fulfillDoctors(route, pageCount === 0
      ? [doctor(4, 'Zed Doctor'), doctor(2, 'Beta Doctor'), doctor(3, 'Delta Doctor'), doctor(1, 'Alpha Doctor')]
      : [doctor(6, 'Yara Doctor'), doctor(5, 'Aaron Doctor')]);
  });

  await page.goto('/doctors');
  await expect(page.locator('.name-cell')).toHaveText(['Alpha Doctor', 'Beta Doctor', 'Delta Doctor', 'Zed Doctor']);
  await page.getByRole('button', { name: 'Load more' }).click();
  await expect(page.locator('.name-cell')).toHaveText(['Aaron Doctor', 'Alpha Doctor', 'Beta Doctor', 'Delta Doctor', 'Yara Doctor', 'Zed Doctor']);
  await expect(page.getByRole('button', { name: 'Load more' })).toHaveCount(0);
});

test('ac-doctor-directory-management-fr-05-load-more-002 ac-doctor-directory-management-fr-06-directory-presentation-002: presents the empty directory and hides continuation', async ({ page }) => {
  await mockTenant(page);
  await page.route('**/api/doctors?*', async (route) => fulfillDoctors(route, []));
  await page.goto('/doctors');
  await expect(page.getByText('NO DATA')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Load more' })).toHaveCount(0);
});

test('ac-doctor-directory-management-fr-07-new-doctor-001 ac-doctor-directory-management-fr-08-back-to-doctors-001 ac-doctor-directory-management-fr-09-open-doctor-details-001 ac-doctor-directory-management-fr-09-open-doctor-details-002: navigates between directory, create, and populated detail views', async ({ page }) => {
  await mockTenant(page);
  await page.route('**/api/doctors?*', async (route) => fulfillDoctors(route, [doctor(3, 'Directory Record')]));
  await page.route('**/api/doctors/3', async (route) => {
    expect(route.request().headers()['tenantid']).toBe('7');
    await route.fulfill({ json: doctor(3, 'Directory Record') });
  });

  await page.goto('/doctors');
  await page.getByRole('link', { name: 'New doctor' }).click();
  await expect(page).toHaveURL(/\/doctors\/new$/);
  await expect(page.getByRole('button', { name: 'Add', exact: true })).toBeVisible();
  await page.getByRole('link', { name: 'Back to doctors' }).click();
  await expect(page).toHaveURL(/\/doctors$/);
  await page.getByRole('link', { name: 'Edit Directory Record' }).first().click();
  await expect(page).toHaveURL(/\/doctors\/3$/);
  await expect(page.locator('#Name')).toHaveValue('Directory Record');
  await expect(page.locator('#Description')).toHaveValue('Directory Record profile');
});

test('ac-doctor-directory-management-fr-02-delete-selected-doctor-records-001 ac-doctor-directory-management-fr-02-delete-selected-doctor-records-002 ac-doctor-directory-management-fr-02-delete-selected-doctor-records-003 ac-doctor-directory-management-fr-11-change-all-displayed-record-selections-001 ac-doctor-directory-management-fr-13-change-an-individual-record-selection-001: selects and deletes displayed records after confirmation', async ({ page }) => {
  await mockTenant(page);
  await page.route('**/api/doctors?*', async (route) => fulfillDoctors(route, [doctor(1, 'Alpha Doctor'), doctor(2, 'Beta Doctor')]));
  const deleted: number[] = [];
  await page.route(/\/api\/doctors\/\d+$/, async (route) => {
    expect(route.request().method()).toBe('DELETE');
    expect(route.request().headers()['tenantid']).toBe('7');
    deleted.push(Number(route.request().url().split('/').pop()));
    await route.fulfill({ status: 200 });
  });

  await page.goto('/doctors');
  const alpha = page.getByRole('checkbox', { name: 'Select Alpha Doctor' });
  await alpha.check();
  await expect(alpha).toBeChecked();
  await expect(page.getByRole('button', { name: 'Delete', exact: true })).toBeVisible();
  await page.getByRole('checkbox', { name: 'Select all' }).check();
  const rowSelections = page.locator('.grid-row input[type="checkbox"]');
  await expect(rowSelections).toHaveCount(2);
  await expect(rowSelections.nth(0)).toBeChecked();
  await expect(rowSelections.nth(1)).toBeChecked();
  page.once('dialog', async (dialog) => { expect(dialog.type()).toBe('confirm'); await dialog.accept(); });
  await page.getByRole('button', { name: 'Delete', exact: true }).click();
  await expect(page.getByText('NO DATA')).toBeVisible();
  expect(deleted.sort()).toEqual([1, 2]);
});

test('ac-doctor-directory-management-fr-03-delete-an-individual-doctor-001 ac-doctor-directory-management-fr-03-delete-an-individual-doctor-002: confirms and removes one directory record', async ({ page }) => {
  await mockTenant(page);
  await page.route('**/api/doctors?*', async (route) => fulfillDoctors(route, [doctor(3, 'Single Doctor')]));
  let deleted = false;
  await page.route('**/api/doctors/3', async (route) => { deleted = true; await route.fulfill({ status: 200 }); });
  await page.goto('/doctors');
  page.once('dialog', async (dialog) => { expect(dialog.type()).toBe('confirm'); await dialog.accept(); });
  await page.getByRole('button', { name: 'Delete Single Doctor' }).click();
  await expect(page.getByText('NO DATA')).toBeVisible();
  expect(deleted).toBe(true);
});

test('ac-doctor-directory-management-fr-01-add-doctor-001 ac-doctor-directory-management-fr-01-add-doctor-002 ac-doctor-directory-management-fr-01-add-doctor-003 ac-doctor-directory-management-fr-01-add-doctor-004 ac-doctor-directory-management-fr-15-maintain-doctor-profile-media-001 ac-doctor-directory-management-fr-15-maintain-doctor-profile-media-002 ac-doctor-directory-management-fr-15-maintain-doctor-profile-media-003 ac-doctor-directory-management-fr-16-validate-doctor-address-001 ac-doctor-directory-management-fr-17-validate-doctor-description-001 ac-doctor-directory-management-fr-18-validate-doctor-email-001 ac-doctor-directory-management-fr-19-validate-doctor-mobile-001 ac-doctor-directory-management-fr-20-validate-doctor-phone-001 ac-doctor-directory-management-fr-21-validate-doctor-name-001: validates, previews, and creates a doctor', async ({ page }) => {
  await mockTenant(page);
  await page.route('**/api/doctors?*', async (route) => fulfillDoctors(route, []));
  let created: Record<string, unknown> | undefined;
  await page.route('**/api/doctors', async (route) => {
    expect(route.request().method()).toBe('POST');
    expect(route.request().headers()['tenantid']).toBe('7');
    created = route.request().postDataJSON();
    await route.fulfill({ status: 200, json: 9 });
  });

  await page.goto('/doctors/new');
  const add = page.getByRole('button', { name: 'Add', exact: true });
  await expect(add).toBeVisible();
  await expect(add).toBeDisabled();
  await expect(page.getByText('Add a profile photo')).toBeVisible();
  await page.locator('#profile-file').setInputFiles({ name: 'profile.png', mimeType: 'image/png', buffer: Buffer.from('picture') });
  await expect(page.getByRole('img', { name: 'Doctor picture preview' })).toBeVisible();
  await expect(page.getByText('Add a profile photo')).toHaveCount(0);

  const values: Record<string, string> = { Name: 'Created Doctor', Description: 'Created profile', Address: '1 New Avenue', Email: 'created@example.test', Phone: '555-1000', Mobile: '555-1001' };
  for (const [field, value] of Object.entries(values)) await page.locator(`#${field}`).fill(value);
  await expect(add).toBeEnabled();
  for (const [field, value] of Object.entries(values)) {
    await page.locator(`#${field}`).fill('');
    await expect(add).toBeDisabled();
    await page.locator(`#${field}`).fill(value);
  }
  await add.click();
  await expect(page).toHaveURL(/\/doctors$/);
  expect(created).toMatchObject({ Name: 'Created Doctor', TenantId: 7, Picture: 'cGljdHVyZQ==' });
});

test('ac-doctor-directory-management-fr-04-delete-this-doctor-001 ac-doctor-directory-management-fr-04-delete-this-doctor-002 ac-doctor-directory-management-fr-12-save-doctor-001 ac-doctor-directory-management-fr-12-save-doctor-002 ac-doctor-directory-management-fr-12-save-doctor-003 ac-doctor-directory-management-fr-12-save-doctor-004: validates, updates, and deletes an existing doctor', async ({ page }) => {
  await mockTenant(page);
  await page.route('**/api/doctors?*', async (route) => fulfillDoctors(route, []));
  let updated: Record<string, unknown> | undefined;
  let deleted = false;
  await page.route('**/api/doctors', async (route) => {
    expect(route.request().method()).toBe('PUT');
    updated = route.request().postDataJSON();
    await route.fulfill({ status: 200 });
  });
  await page.route('**/api/doctors/3', async (route) => {
    if (route.request().method() === 'DELETE') { deleted = true; await route.fulfill({ status: 200 }); }
    else await route.fulfill({ json: doctor(3, 'Existing Doctor') });
  });

  await page.goto('/doctors/3');
  const save = page.getByRole('button', { name: 'Save', exact: true });
  await expect(save).toBeVisible();
  await expect(page.locator('#Name')).toHaveValue('Existing Doctor');
  await page.locator('#Name').fill('');
  await expect(save).toBeDisabled();
  await page.locator('#Name').fill('Updated Doctor');
  await save.click();
  await expect(page).toHaveURL(/\/doctors$/);
  expect(updated).toMatchObject({ DoctorId: 3, Name: 'Updated Doctor', TenantId: 7 });

  await page.goto('/doctors/3');
  page.once('dialog', async (dialog) => { expect(dialog.type()).toBe('confirm'); await dialog.accept(); });
  await page.getByRole('button', { name: 'Delete this doctor' }).click();
  await expect(page).toHaveURL(/\/doctors$/);
  expect(deleted).toBe(true);
});

test.skip('ac-doctor-directory-management-fr-10-patients-001 ac-doctor-directory-management-fr-10-patients-002: BLOCKED_BY_PATIENT_FEATURE until the modern Patient route exists', async () => {
  // The frozen Doctor interaction targets the separate Patient Feature. No modern Patient shell or route exists yet.
});
