import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { correlationInterceptor, provideRuntimeConfig, tenantContextInterceptor } from '@healthclinic/core/platform';
import { DoctorApiClient } from './doctor-api.client';

describe('DoctorApiClient', () => {
  let http: HttpTestingController;
  let client: DoctorApiClient;
  beforeEach(() => {
    TestBed.configureTestingModule({ providers: [provideHttpClient(withInterceptors([correlationInterceptor, tenantContextInterceptor])), provideHttpClientTesting(), provideRuntimeConfig({ apiBaseUrl: '', tenantContextPath: '/api/users/current/tenant', tenantHeaderName: 'TenantId' })] });
    http = TestBed.inject(HttpTestingController); client = TestBed.inject(DoctorApiClient);
  });
  afterEach(() => http.verify());
  it('preserves collection parameters, detail route, tenant and correlation headers', () => {
    client.getList(4, 0, 7).subscribe();
    const list = http.expectOne(request => request.url === '/api/doctors');
    expect(list.request.method).toBe('GET'); expect(list.request.params.get('pageSize')).toBe('4');
    expect(list.request.params.get('pageCount')).toBe('0'); expect(list.request.headers.get('TenantId')).toBe('7');
    expect(list.request.headers.get('X-Correlation-ID')).toBeTruthy(); list.flush([]);
    client.getById(3, 7).subscribe();
    const detail = http.expectOne('/api/doctors/3'); expect(detail.request.method).toBe('GET'); detail.flush({});
  });
  it('preserves POST/PUT/DELETE contracts without a bulk or upload endpoint', () => {
    const input = { Name: 'N', Address: 'A', Description: 'D', Email: 'E', Phone: 'P', Mobile: 'M', Picture: 'aGVsbG8=' };
    client.create(input, 7).subscribe();
    const create = http.expectOne('/api/doctors'); expect(create.request.method).toBe('POST');
    expect(create.request.body).toEqual({ ...input, TenantId: 7 }); expect(create.request.headers.get('TenantId')).toBe('7'); create.flush(3);
    client.update({ ...input, DoctorId: 3 }, 7).subscribe();
    const update = http.expectOne('/api/doctors'); expect(update.request.method).toBe('PUT');
    expect(update.request.body.DoctorId).toBe(3); expect(update.request.headers.get('X-Correlation-ID')).toBeTruthy(); update.flush(null);
    client.delete(3, 7).subscribe();
    const deletion = http.expectOne('/api/doctors/3'); expect(deletion.request.method).toBe('DELETE');
    expect(deletion.request.headers.get('TenantId')).toBe('7'); deletion.flush(null);
  });
  it('propagates write failures to the state boundary', () => {
    const error = vi.fn(); client.delete(3, 7).subscribe({ error });
    http.expectOne('/api/doctors/3').flush('denied', { status: 403, statusText: 'Forbidden' });
    expect(error).toHaveBeenCalledOnce();
  });
});
