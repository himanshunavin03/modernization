import { computed, DestroyRef, inject, Injectable, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { DoctorApiClient, type Doctor, type DoctorInput } from '@modernized/doctor-directory-management/data-access';
import { TenantContextService } from '@healthclinic/core/platform';
import { concatMap, finalize, from, switchMap, take, tap } from 'rxjs';

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
  readonly saving = signal(false);
  readonly selectedIds = signal<ReadonlySet<number>>(new Set());
  readonly anySelected = computed(() => this.selectedIds().size > 0);
  readonly allSelected = computed(() => !!this.items()?.length && this.items()!.every(item => this.selectedIds().has(item.DoctorId)));
  readonly orderedItems = computed(() => this.items() === null ? null : [...this.items()!].sort((left, right) => left.Name.localeCompare(right.Name)));

  selectRecord(id: number, checked: boolean): void {
    this.selectedIds.update(current => {
      const next = new Set(current);
      if (checked) next.add(id); else next.delete(id);
      return next;
    });
  }

  selectAll(checked: boolean): void {
    this.selectedIds.set(new Set(checked ? this.items()?.map(item => item.DoctorId) : []));
  }

  save(value: DoctorInput, onSuccess: () => void): void {
    if (this.saving()) return;
    this.saving.set(true);
    this.errorMessage.set(null);
    this.tenant.tenantId$.pipe(
      take(1),
      switchMap(tenantId => value.DoctorId ? this.api.update(value, tenantId) : this.api.create(value, tenantId)),
      takeUntilDestroyed(this.destroyRef),
      finalize(() => this.saving.set(false)),
    ).subscribe({
      next: () => onSuccess(),
      error: () => this.errorMessage.set('The doctor could not be saved.'),
    });
  }

  deleteConfirmed(ids: readonly number[], onSuccess: () => void = () => undefined): void {
    if (this.saving() || !ids.length) return;
    this.saving.set(true);
    this.errorMessage.set(null);
    this.tenant.tenantId$.pipe(
      take(1),
      switchMap(tenantId => from([...new Set(ids)]).pipe(concatMap(id => this.api.delete(id, tenantId).pipe(tap(() => {
        this.items.update(items => items?.filter(item => item.DoctorId !== id) ?? null);
        this.selectRecord(id, false);
      }))))),
      takeUntilDestroyed(this.destroyRef),
      finalize(() => this.saving.set(false)),
    ).subscribe({
      complete: () => { if (!this.destroyRef.destroyed) onSuccess(); },
      error: () => this.errorMessage.set('The requested deletion could not be completed. Records not deleted remain selected.'),
    });
  }

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
