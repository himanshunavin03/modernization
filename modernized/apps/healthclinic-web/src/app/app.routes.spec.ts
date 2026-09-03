import { appRoutes } from './app.routes';
describe('appRoutes', () => { it('AC-04 AC-05: lazy-loads the Dashboard route', () => { const shell = appRoutes[0]; const dashboard = shell.children?.find((route) => route.path === 'dashboard'); expect(dashboard?.loadChildren).toBeDefined(); }); });
