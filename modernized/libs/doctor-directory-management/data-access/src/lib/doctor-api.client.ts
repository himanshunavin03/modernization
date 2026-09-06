import { HttpClient, HttpParams } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { RUNTIME_CONFIG, withTenantContext } from '@healthclinic/core/platform';
import { Observable } from 'rxjs';
import type { Doctor } from './doctor.models';

@Injectable({ providedIn: 'root' })
export class DoctorApiClient {
  private readonly http = inject(HttpClient);
  private readonly config = inject(RUNTIME_CONFIG);

  getList(pageSize: number, pageCount: number, tenantId: number): Observable<Doctor[]> {
    const params = new HttpParams({ fromObject: { pageSize: pageSize, pageCount: pageCount } });
    return this.http.get<Doctor[]>(this.url('/api/doctors'), { params, context: withTenantContext(tenantId) });
  }

  getById(id: number, tenantId: number): Observable<Doctor> {
    return this.http.get<Doctor>(this.url(`/api/doctors/${id}`), { context: withTenantContext(tenantId) });
  }

  private url(path: string): string { return `${this.config.apiBaseUrl.replace(/\/$/, '')}${path}`; }
}
