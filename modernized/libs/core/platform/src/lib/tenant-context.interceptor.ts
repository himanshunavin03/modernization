import { HttpContext, HttpContextToken, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { RUNTIME_CONFIG } from './runtime-config';

const TENANT_ID = new HttpContextToken<number | null>(() => null);

export function withTenantContext(tenantId: number): HttpContext {
  return new HttpContext().set(TENANT_ID, tenantId);
}

export const tenantContextInterceptor: HttpInterceptorFn = (request, next) => {
  const tenantId = request.context.get(TENANT_ID);
  if (tenantId === null) {
    return next(request);
  }

  const { tenantHeaderName } = inject(RUNTIME_CONFIG);
  return next(request.clone({ setHeaders: { [tenantHeaderName]: String(tenantId) } }));
};
