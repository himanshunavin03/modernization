import { expect, test } from '@playwright/test';
test.beforeEach(async ({ page }) => { await page.goto('/dashboard'); });
test('AC-04: opens the Operational Dashboard', async ({ page }) => { await expect(page.getByRole('heading', { name: 'Operational Dashboard' })).toBeAttached(); });
test('AC-05: keeps the Dashboard experience available at its route', async ({ page }) => { await expect(page).toHaveURL(/\/dashboard$/); });
test('AC-01: exposes independently labeled yearly operational reports', async ({ page }) => { await expect(page.getByRole('group', { name: 'Income and expense reporting year' })).toBeVisible(); await expect(page.getByRole('group', { name: 'Patient reporting year' })).toBeVisible(); });
test('AC-02: presents organization-specific clinic summary regions', async ({ page }) => { await expect(page.getByLabel('Clinic summary')).toBeVisible(); });
test('AC-03: loads clinic summary through the approved service integration', async ({ page }) => { const response = await page.waitForResponse((item) => item.url().includes('/api/reports/clinicsummary')); expect(response.request().method()).toBe('GET'); });
