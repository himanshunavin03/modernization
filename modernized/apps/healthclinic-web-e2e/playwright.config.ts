import { defineConfig, devices } from '@playwright/test';

const port = process.env['PLAYWRIGHT_PORT'] ?? '4200';
const baseURL = `http://localhost:${port}`;

export default defineConfig({ testDir: './src', use: { baseURL, trace: 'on-first-retry' }, webServer: { command: `npx nx serve healthclinic-web --port ${port}`, url: baseURL, reuseExistingServer: true }, projects: [{ name: 'chromium', use: devices['Desktop Chrome'] }] });
