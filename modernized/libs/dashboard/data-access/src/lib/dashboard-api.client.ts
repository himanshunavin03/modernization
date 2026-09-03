import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { RUNTIME_CONFIG, withTenantContext } from '@healthclinic/core/platform';
import { Observable } from 'rxjs';
import type { ClinicSummary, ExpensesSummary, PatientsSummary, TenantId } from './dashboard.models';

@Injectable({ providedIn: 'root' })
export class DashboardApiClient {
  private readonly http = inject(HttpClient); private readonly config = inject(RUNTIME_CONFIG);
  getClinicSummary(tenantId: TenantId): Observable<ClinicSummary> { return this.http.get<ClinicSummary>(this.url('/api/reports/clinicsummary'), { context: withTenantContext(tenantId) }); }
  getExpenses(year: number, tenantId: TenantId): Observable<ExpensesSummary[]> { return this.http.get<ExpensesSummary[]>(this.url(`/api/reports/expenses/${year}`), { context: withTenantContext(tenantId) }); }
  getPatients(year: number, tenantId: TenantId): Observable<PatientsSummary[]> { return this.http.get<PatientsSummary[]>(this.url(`/api/reports/patients/${year}`), { context: withTenantContext(tenantId) }); }
  private url(path: string): string { return `${this.config.apiBaseUrl.replace(/\/$/, '')}${path}`; }
}
