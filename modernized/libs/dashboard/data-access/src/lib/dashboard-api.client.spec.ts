import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { provideRuntimeConfig, tenantContextInterceptor } from '@healthclinic/core/platform';
import { DashboardApiClient } from './dashboard-api.client';

describe('DashboardApiClient', () => {
  let client: DashboardApiClient;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({ providers: [
      provideHttpClient(withInterceptors([tenantContextInterceptor])),
      provideHttpClientTesting(),
      provideRuntimeConfig({ apiBaseUrl: '', tenantContextPath: '/api/users/current/tenant', tenantHeaderName: 'TenantId' }),
    ] });
    client = TestBed.inject(DashboardApiClient);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  it('AC-02 AC-03: preserves the tenant-aware clinic summary contract', () => {
    client.getClinicSummary(7).subscribe();
    expect(http.expectOne('/api/reports/clinicsummary').request.headers.get('TenantId')).toBe('7');
  });

  it('AC-01: preserves both selected-year report contracts and tenant context', () => {
    client.getExpenses(2025, 7).subscribe();
    expect(http.expectOne('/api/reports/expenses/2025').request.headers.get('TenantId')).toBe('7');
    client.getPatients(2025, 7).subscribe();
    expect(http.expectOne('/api/reports/patients/2025').request.headers.get('TenantId')).toBe('7');
  });
});
