import { DestroyRef, inject, Injectable, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { DoctorApiClient, type Doctor } from '@modernized/doctor-directory-management/data-access';
import { TenantContextService } from '@healthclinic/core/platform';
import { switchMap, take } from 'rxjs';

@Injectable()
export class DoctorDirectoryStore {
  private readonly api = inject(DoctorApiClient);
  private readonly tenant = inject(TenantContextService);
  private readonly destroyRef = inject(DestroyRef);
  private pageCount = 0;
  readonly items = signal<Doctor[] | null>(null);
  readonly selected = signal<Doctor | null>(null);
  readonly loading = signal(false);
  readonly noMoreData = signal(false);
  readonly errorMessage = signal<string | null>(null);

  loadNext(): void {
    if (this.loading() || this.noMoreData()) return;
    this.loading.set(true); this.errorMessage.set(null);
    this.tenant.tenantId$.pipe(
      take(1), switchMap((tenantId) => this.api.getList(4, this.pageCount, tenantId)), takeUntilDestroyed(this.destroyRef),
    ).subscribe({
      next: (items) => { this.items.update((current) => [...(current ?? []), ...items]); this.pageCount += 1; this.noMoreData.set(items.length < 4); this.loading.set(false); },
      error: () => { this.errorMessage.set('The directory could not be loaded.'); this.loading.set(false); },
    });
  }

  loadDetail(id: number): void {
    this.loading.set(true); this.errorMessage.set(null); this.selected.set(null);
    this.tenant.tenantId$.pipe(
      take(1), switchMap((tenantId) => this.api.getById(id, tenantId)), takeUntilDestroyed(this.destroyRef),
    ).subscribe({
      next: (item) => { this.selected.set(item); this.loading.set(false); },
      error: () => { this.errorMessage.set('The requested record could not be loaded.'); this.loading.set(false); },
    });
  }
}
