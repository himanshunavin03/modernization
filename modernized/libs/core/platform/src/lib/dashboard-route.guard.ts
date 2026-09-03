import { CanActivateFn } from '@angular/router';
// Identity and authorization rules remain unselected; this functional boundary preserves that explicit extension point.
export const dashboardRouteGuard: CanActivateFn = () => true;
