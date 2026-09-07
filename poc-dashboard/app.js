const demoConfig = Object.freeze({
  legacyApp: 'http://localhost:5000/',
  modernApp: 'http://localhost:4200/',
  modernDoctors: 'http://localhost:4200/doctors',
  modernNewDoctor: 'http://localhost:4200/doctors/new',
  knowledgeGraph: 'http://127.0.0.1:5175/?token=polaris-layout-readonly',
  featureSpec: './generated/feature-specification.html',
  technicalTasks: './generated/technical-tasks.html',
  applicationUnderstanding: './generated/application-understanding.html',
  playwrightCoverage: './generated/playwright-coverage.html',
  playwrightReport: '../modernized/apps/healthclinic-web-e2e/playwright-report/index.html',
});

const isRuntimeLink = (key) => ['legacyApp', 'modernApp', 'modernDoctors', 'modernNewDoctor', 'knowledgeGraph'].includes(key);

function configureLinks() {
  document.querySelectorAll('[data-link]').forEach((link) => {
    const key = link.dataset.link;
    const target = demoConfig[key];
    if (!target) return;
    link.href = target;
    if (isRuntimeLink(key)) {
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
    }
  });
}

function formatMetric(value) {
  return typeof value === 'number' ? new Intl.NumberFormat('en-US').format(value) : String(value);
}

async function loadPresentationData() {
  try {
    const response = await fetch('./generated/dashboard-data.json', { cache: 'no-store' });
    if (!response.ok) throw new Error('Presentation data unavailable');
    const data = await response.json();
    document.querySelectorAll('[data-metric]').forEach((element) => {
      const value = data.metrics?.[element.dataset.metric];
      if (value !== undefined) element.textContent = formatMetric(value);
    });
    document.querySelectorAll('[data-coverage]').forEach((element) => {
      const value = data.playwright?.[element.dataset.coverage];
      if (value !== undefined) element.textContent = formatMetric(value);
    });
  } catch {
    document.documentElement.dataset.presentationData = 'fallback';
  }
}

async function checkPlaywrightReport() {
  const reportLinks = [...document.querySelectorAll('[data-link="playwrightReport"]')];
  const labels = document.querySelectorAll('[data-report-status]');
  try {
    const response = await fetch(demoConfig.playwrightReport, { method: 'HEAD', cache: 'no-store' });
    if (!response.ok) throw new Error('Report unavailable');
    labels.forEach((label) => { label.textContent = 'Current execution evidence'; });
  } catch {
    reportLinks.forEach((link) => {
      link.removeAttribute('href');
      link.setAttribute('aria-disabled', 'true');
      link.title = 'Generate the latest Playwright report before the demo.';
    });
    labels.forEach((label) => { label.textContent = 'Generate the latest report before the demo'; });
  }
}

function configureReveal() {
  const elements = document.querySelectorAll('.reveal');
  if (!('IntersectionObserver' in window) || window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    elements.forEach((element) => element.classList.add('visible'));
    return;
  }
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.08, rootMargin: '0px 0px -5% 0px' });
  elements.forEach((element) => observer.observe(element));
}

function configureActiveNavigation() {
  const sections = [...document.querySelectorAll('[data-section]')];
  const navLinks = [...document.querySelectorAll('.primary-nav a')];
  const sectionLabel = document.querySelector('[data-section-label]');
  if (!sections.length || !('IntersectionObserver' in window)) return;
  const observer = new IntersectionObserver((entries) => {
    const visible = entries.filter((entry) => entry.isIntersecting).sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
    if (!visible) return;
    const sectionName = visible.target.dataset.section;
    navLinks.forEach((link) => link.classList.toggle('active', link.hash === `#${visible.target.id}`));
    if (sectionLabel) sectionLabel.textContent = sectionName;
  }, { rootMargin: '-25% 0px -55% 0px', threshold: [0, .15, .4] });
  sections.forEach((section) => observer.observe(section));
}

function configurePresentationMode() {
  const toggle = document.querySelector('.presentation-toggle');
  if (!toggle) return;
  const setMode = (active) => {
    document.body.classList.toggle('presentation-mode', active);
    toggle.setAttribute('aria-pressed', String(active));
    toggle.querySelector('span').textContent = active ? 'Exit' : 'Present';
  };
  toggle.addEventListener('click', () => setMode(!document.body.classList.contains('presentation-mode')));
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && document.body.classList.contains('presentation-mode')) setMode(false);
  });
}

function configureSectionControls() {
  const sections = [...document.querySelectorAll('[data-section]')];
  document.querySelectorAll('[data-direction]').forEach((button) => {
    button.addEventListener('click', () => {
      const currentIndex = sections.findIndex((section) => {
        const bounds = section.getBoundingClientRect();
        return bounds.top <= window.innerHeight * .45 && bounds.bottom >= window.innerHeight * .45;
      });
      const delta = button.dataset.direction === 'next' ? 1 : -1;
      const targetIndex = Math.min(sections.length - 1, Math.max(0, (currentIndex < 0 ? 0 : currentIndex) + delta));
      sections[targetIndex]?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });
}

function configureAgenda() {
  const agenda = document.querySelector('.demo-agenda');
  const toggle = document.querySelector('.agenda-toggle');
  if (!agenda || !toggle) return;
  toggle.addEventListener('click', () => {
    const open = agenda.classList.toggle('open');
    toggle.setAttribute('aria-expanded', String(open));
  });
  agenda.querySelectorAll('a').forEach((link) => link.addEventListener('click', () => {
    agenda.classList.remove('open');
    toggle.setAttribute('aria-expanded', 'false');
  }));
}

configureLinks();
loadPresentationData();
checkPlaywrightReport();
configureReveal();
configureActiveNavigation();
configurePresentationMode();
configureSectionControls();
configureAgenda();
