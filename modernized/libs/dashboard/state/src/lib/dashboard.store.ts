import { computed, inject, Injectable, signal } from '@angular/core';
import { toObservable, toSignal } from '@angular/core/rxjs-interop';
import { DashboardApiClient, type ClinicSummary, type ExpensesSummary, type PatientsSummary } from '@healthclinic/dashboard/data-access';
import { TenantContextService } from '@healthclinic/core/platform';
import { catchError, defer, distinctUntilChanged, finalize, Observable, of, switchMap } from 'rxjs';

@Injectable()
export class DashboardStore {
  private readonly api = inject(DashboardApiClient); private readonly tenant = inject(TenantContextService);
  readonly currentYear = new Date().getFullYear(); readonly incomeExpenseYear = signal(this.currentYear); readonly patientYear = signal(this.currentYear);
  private readonly activeRequests = signal(0); readonly loading = computed(() => this.activeRequests() > 0); readonly errorMessage = signal<string | null>(null);
  readonly summary = toSignal(this.request(() => this.tenant.tenantId$.pipe(switchMap((tenantId) => this.api.getClinicSummary(tenantId)))), { initialValue: null });
  readonly expenses = toSignal(toObservable(this.incomeExpenseYear).pipe(distinctUntilChanged(), switchMap((year) => this.request(() => this.tenant.tenantId$.pipe(switchMap((tenantId) => this.api.getExpenses(year, tenantId)))))), { initialValue: null });
  readonly patients = toSignal(toObservable(this.patientYear).pipe(distinctUntilChanged(), switchMap((year) => this.request(() => this.tenant.tenantId$.pipe(switchMap((tenantId) => this.api.getPatients(year, tenantId)))))), { initialValue: null });
  previousIncomeExpenseYear(): void { this.incomeExpenseYear.update((year) => year - 1); }
  nextIncomeExpenseYear(): void { this.incomeExpenseYear.update((year) => Math.min(this.currentYear, year + 1)); }
  previousPatientYear(): void { this.patientYear.update((year) => year - 1); }
  nextPatientYear(): void { this.patientYear.update((year) => Math.min(this.currentYear, year + 1)); }
  private request<T>(factory: () => Observable<T>): Observable<T | null> { return defer(() => { this.activeRequests.update((count) => count + 1); this.errorMessage.set(null); return factory().pipe(catchError(() => { this.errorMessage.set('Dashboard information could not be loaded. Please try again.'); return of(null); }), finalize(() => this.activeRequests.update((count) => Math.max(0, count - 1)))); }); }
}
