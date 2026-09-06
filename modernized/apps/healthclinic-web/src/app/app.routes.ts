import { Routes } from '@angular/router';
import { dashboardRouteGuard } from '@healthclinic/core/platform';
import { PrivateShellComponent } from './private-shell.component';

export const appRoutes: Routes = [
  { path: '', component: PrivateShellComponent, children: [
    { path: '', pathMatch: 'full', redirectTo: 'dashboard' },
    { path: 'dashboard', canActivate: [dashboardRouteGuard], loadChildren: () => import('@healthclinic/dashboard/feature').then((entry) => entry.DASHBOARD_ROUTES) },
    { path: 'doctors', canActivate: [dashboardRouteGuard], loadChildren: () => import('@modernized/doctor-directory-management/feature').then((entry) => entry.DOCTOR_DIRECTORY_ROUTES) },
  ] },
  { path: '**', redirectTo: 'dashboard' },
];
