import { expect, test } from '@playwright/test';

test('ac-doctor-directory-management-review-doctor-directory-001 ac-doctor-directory-management-view-doctor-details-in-tenant-context-001: supports list and detail navigation', async ({ page }) => {
  await page.route('**/api/users/current/tenant', (route) => route.fulfill({ json: 7 }));
  await page.route('**/api/doctors?*', (route) => route.fulfill({ json: [{ DoctorId: 3, Name: 'Directory record' }] }));
  await page.route('**/api/doctors/3', (route) => route.fulfill({ json: { DoctorId: 3, Name: 'Directory record' } }));
  await page.goto('/doctors'); await expect(page.getByRole('heading', { name: 'Doctors' })).toBeVisible();
  await page.getByRole('link', { name: /View Directory record/ }).click(); await expect(page).toHaveURL(/\/doctors\/3$/); await expect(page.getByRole('heading', { name: 'Directory record' })).toBeVisible();
});
