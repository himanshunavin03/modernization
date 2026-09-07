import { chromium } from '../modernized/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import { fileURLToPath } from 'node:url';

const base = 'http://localhost:8088/poc-dashboard';
const pages = [
  ['dashboard', `${base}/`, 'Application Modernization POC'],
  ['feature-specification', `${base}/generated/feature-specification.html`, 'Doctor Directory Management'],
  ['technical-tasks', `${base}/generated/technical-tasks.html`, 'Technical Delivery Plan'],
  ['application-understanding', `${base}/generated/application-understanding.html`, 'Application Understanding'],
  ['playwright-coverage', `${base}/generated/playwright-coverage.html`, 'Playwright Validation Traceability'],
];
const viewports = [
  ['desktop', { width: 1920, height: 1080 }],
  ['laptop', { width: 1366, height: 768 }],
];

await fs.mkdir(new URL('./validation/', import.meta.url), { recursive: true });
const browser = await chromium.launch({ headless: true });
const results = { pages: {}, responsive: true, accessibility: true, graphLink: false, reportLink: false };

function luminance([red, green, blue]) {
  const values = [red, green, blue].map((value) => {
    const channel = value / 255;
    return channel <= .03928 ? channel / 12.92 : ((channel + .055) / 1.055) ** 2.4;
  });
  return .2126 * values[0] + .7152 * values[1] + .0722 * values[2];
}
function contrast(foreground, background) {
  const high = Math.max(luminance(foreground), luminance(background));
  const low = Math.min(luminance(foreground), luminance(background));
  return (high + .05) / (low + .05);
}
function rgb(value) {
  const channels = value.match(/[\d.]+/g)?.slice(0, 3).map(Number);
  return channels?.length === 3 ? channels : [0, 0, 0];
}

try {
  for (const [viewportName, viewport] of viewports) {
    const context = await browser.newContext({ viewport });
    for (const [name, url, heading] of pages) {
      const page = await context.newPage();
      const response = await page.goto(url, { waitUntil: 'networkidle' });
      if (!response?.ok()) throw new Error(`${url} returned ${response?.status()}`);
      const pageHeading = page.locator('h1').first();
      await pageHeading.waitFor({ state: 'visible' });
      const headingText = (await pageHeading.innerText()).replace(/\s+/g, ' ').trim();
      if (!heading.split(/\s+/).every((word) => headingText.includes(word))) throw new Error(`Unexpected heading on ${url}: ${headingText}`);
      const horizontalOverflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 2);
      if (horizontalOverflow) results.responsive = false;
      const pageResult = results.pages[name] ?? { desktop: false, laptop: false };
      pageResult[viewportName] = !horizontalOverflow;
      results.pages[name] = pageResult;
      if (name === 'dashboard') {
        for (const section of ['overview', 'architecture', 'understanding', 'requirements', 'angular', 'live-demo', 'validation', 'outcome']) {
          if (!(await page.locator(`#${section}`).count())) throw new Error(`Dashboard section missing: ${section}`);
        }
        if (viewportName === 'desktop') {
          const metric = await page.locator('[data-metric="graphNodes"]').first().textContent();
          if (metric?.trim() !== '71,936') throw new Error('Generated metric did not load');
          const links = await page.locator('a').evaluateAll((items) => items.map((item) => ({ name: item.textContent?.trim(), href: item.getAttribute('href') })));
          if (links.some((link) => !link.name)) results.accessibility = false;
          await page.keyboard.press('Tab');
          const focusedTag = await page.evaluate(() => document.activeElement?.tagName);
          if (!['A', 'BUTTON'].includes(focusedTag)) results.accessibility = false;
          await page.evaluate(() => document.activeElement?.blur());
          const samples = await page.locator('.value-card p').evaluateAll((items) => items.map((item) => {
            const style = getComputedStyle(item);
            const background = getComputedStyle(item.closest('.value-card')).backgroundColor;
            return [style.color, background];
          }));
          if (samples.some(([foreground, background]) => contrast(rgb(foreground), rgb(background)) < 4.5)) results.accessibility = false;
          const report = page.locator('[data-link="playwrightReport"]').first();
          results.reportLink = (await report.getAttribute('href'))?.includes('playwright-report/index.html') ?? false;
          const graph = page.locator('[data-link="knowledgeGraph"]').first();
          results.graphLink = (await graph.getAttribute('href')) === 'http://127.0.0.1:5175/?token=polaris-layout-readonly';
          for (const section of ['architecture', 'understanding', 'requirements', 'angular', 'live-demo', 'validation', 'outcome']) {
            await page.evaluate((identifier) => {
              const element = document.querySelector(`#${identifier}`);
              if (element) window.scrollTo({ top: element.offsetTop, left: 0, behavior: 'instant' });
            }, section);
            await page.waitForTimeout(750);
            await page.screenshot({ path: fileURLToPath(new URL(`./validation/dashboard-${section}.png`, import.meta.url)), fullPage: false });
          }
        }
      } else {
        const textLength = await page.locator('.artifact-document').innerText().then((value) => value.length);
        if (textLength < 500) throw new Error(`Generated page content too short: ${name}`);
      }
      if (name === 'dashboard' || viewportName === 'desktop') {
        await page.evaluate(() => window.scrollTo(0, 0));
        await page.screenshot({ path: fileURLToPath(new URL(`./validation/${name}-${viewportName}.png`, import.meta.url)), fullPage: false });
      }
      await page.close();
    }
    await context.close();
  }
} finally {
  await browser.close();
}

await fs.writeFile(new URL('./validation/browser-validation.json', import.meta.url), JSON.stringify(results, null, 2) + '\n');
console.log(`DASHBOARD_VISUAL_RUNTIME=${Object.values(results.pages).every((item) => item.desktop && item.laptop) ? 'PASS' : 'FAIL'}`);
console.log(`RESPONSIVE_CHECK=${results.responsive ? 'PASS' : 'FAIL'}`);
console.log(`ACCESSIBILITY_CHECK=${results.accessibility ? 'PASS' : 'FAIL'}`);
console.log(`KNOWLEDGE_GRAPH_RUNTIME_LINK=${results.graphLink ? 'PASS' : 'FAIL'}`);
console.log(`PLAYWRIGHT_REPORT_RUNTIME_LINK=${results.reportLink ? 'PASS' : 'FAIL'}`);
