import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { provideRuntimeConfig } from '@healthclinic/core/platform';
import { DoctorApiClient } from './doctor-api.client';

describe('DoctorApiClient', () => {
  it('preserves the approved collection and detail GET contracts', () => {
    TestBed.configureTestingModule({ providers: [provideHttpClient(), provideHttpClientTesting(), provideRuntimeConfig({ apiBaseUrl: '', tenantContextPath: '/tenant', tenantHeaderName: 'TenantId' })] });
    const client = TestBed.inject(DoctorApiClient); const http = TestBed.inject(HttpTestingController);
    client.getList(4, 0, 7).subscribe();
    const list = http.expectOne((request) => request.url === '/api/doctors'); expect(list.request.method).toBe('GET'); expect(list.request.headers.get('TenantId')).toBe('7'); list.flush([]);
    client.getById(3, 7).subscribe();
    const detail = http.expectOne('/api/doctors/3'); expect(detail.request.method).toBe('GET'); detail.flush({});
  });
});
