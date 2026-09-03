import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { provideRuntimeConfig } from './runtime-config';
import { TenantContextService } from './tenant-context.service';

describe('TenantContextService', () => {
  it('loads the configured authenticated tenant endpoint', () => {
    TestBed.configureTestingModule({ providers: [
      provideHttpClient(),
      provideHttpClientTesting(),
      provideRuntimeConfig({ apiBaseUrl: '', tenantContextPath: '/api/users/current/tenant', tenantHeaderName: 'TenantId' }),
    ] });
    const tenant = TestBed.inject(TenantContextService);
    const http = TestBed.inject(HttpTestingController);
    let result: number | undefined;

    tenant.tenantId$.subscribe((tenantId) => result = tenantId);
    http.expectOne('/api/users/current/tenant').flush(7);

    expect(result).toBe(7);
    http.verify();
  });
});
