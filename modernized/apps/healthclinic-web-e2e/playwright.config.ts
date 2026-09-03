import { defineConfig, devices } from '@playwright/test';

export default defineConfig({ testDir: './src', use: { baseURL: 'http://localhost:4200', trace: 'on-first-retry' }, webServer: { command: 'npx nx serve healthclinic-web', url: 'http://localhost:4200', reuseExistingServer: true }, projects: [{ name: 'chromium', use: devices['Desktop Chrome'] }] });
