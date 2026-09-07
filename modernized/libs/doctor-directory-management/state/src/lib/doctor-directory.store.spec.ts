import { TestBed } from '@angular/core/testing';
import { DoctorApiClient, type Doctor } from '@modernized/doctor-directory-management/data-access';
import { TenantContextService } from '@healthclinic/core/platform';
import { of, Subject, throwError } from 'rxjs';
import { DoctorDirectoryStore } from './doctor-directory.store';

describe('DoctorDirectoryStore', () => {
  const doctor = (id: number, name = String(id)) => ({ DoctorId: id, Name: name } as Doctor);
  let api: { getList: ReturnType<typeof vi.fn>; getById: ReturnType<typeof vi.fn>; create: ReturnType<typeof vi.fn>; update: ReturnType<typeof vi.fn>; delete: ReturnType<typeof vi.fn> };
  let tenant: Subject<number>;
  let store: DoctorDirectoryStore;
  beforeEach(() => {
    tenant = new Subject<number>();
    api = { getList: vi.fn(() => of([])), getById: vi.fn(() => of(doctor(1))), create: vi.fn(() => of(1)), update: vi.fn(() => of(undefined)), delete: vi.fn(() => of(undefined)) };
    TestBed.configureTestingModule({ providers: [DoctorDirectoryStore, { provide: DoctorApiClient, useValue: api }, { provide: TenantContextService, useValue: { tenantId$: tenant } }] });
    store = TestBed.inject(DoctorDirectoryStore);
  });
  it('waits for automatic tenant context, appends batches, sorts display and terminates on a short batch', () => {
    api.getList.mockReturnValueOnce(of([doctor(1, 'Z'), doctor(2, 'B'), doctor(3, 'C'), doctor(4, 'D')])).mockReturnValueOnce(of([doctor(5, 'A')]));
    store.loadNext(); expect(api.getList).not.toHaveBeenCalled(); tenant.next(7);
    expect(api.getList).toHaveBeenCalledWith(4, 0, 7); expect(store.noMoreData()).toBe(false);
    store.loadNext(); tenant.next(7);
    expect(store.items()?.map(item => item.DoctorId)).toEqual([1, 2, 3, 4, 5]);
    expect(store.orderedItems()?.map(item => item.Name)).toEqual(['A', 'B', 'C', 'D', 'Z']);
    expect(store.noMoreData()).toBe(true); store.loadNext(); expect(api.getList).toHaveBeenCalledTimes(2);
  });
  it('keeps existing results and page position after a failed continuation', () => {
    store.items.set([doctor(1)]); api.getList.mockReturnValue(throwError(() => new Error('network')));
    store.loadNext(); tenant.next(7); expect(store.items()).toHaveLength(1);
    expect(store.errorMessage()).toBeTruthy(); expect(store.loading()).toBe(false);
    store.loadNext(); tenant.next(7); expect(api.getList).toHaveBeenLastCalledWith(4, 0, 7);
  });
  it('selects individual and all displayed records and removes only successful deletes', () => {
    store.items.set([doctor(1), doctor(2)]); store.selectAll(true); expect(store.allSelected()).toBe(true);
    store.selectRecord(1, false); expect(store.anySelected()).toBe(true); expect(store.allSelected()).toBe(false);
    store.selectAll(true);
    api.delete.mockImplementation((id: number) => id === 2 ? throwError(() => new Error('denied')) : of(undefined));
    const success = vi.fn(); store.deleteConfirmed([1, 2], success); tenant.next(7);
    expect(api.delete).toHaveBeenCalledWith(1, 7); expect(api.delete).toHaveBeenCalledWith(2, 7);
    expect(store.items()?.map(item => item.DoctorId)).toEqual([2]); expect([...store.selectedIds()]).toEqual([2]);
    expect(store.errorMessage()).toBeTruthy(); expect(store.saving()).toBe(false); expect(success).not.toHaveBeenCalled();
  });
  it('completes create and update only after a successful API response', () => {
    const input = { Name: 'N', Address: 'A', Description: 'D', Email: 'E', Phone: 'P', Mobile: 'M', Picture: '' };
    const success = vi.fn(); store.save(input, success); expect(success).not.toHaveBeenCalled(); tenant.next(7);
    expect(api.create).toHaveBeenCalledWith(input, 7); expect(success).toHaveBeenCalledOnce();
    store.save({ ...input, DoctorId: 9 }, success); tenant.next(7); expect(api.update).toHaveBeenCalled();
    api.update.mockReturnValue(throwError(() => new Error('failed')));
    store.save({ ...input, DoctorId: 9 }, success); tenant.next(7);
    expect(success).toHaveBeenCalledTimes(2); expect(store.errorMessage()).toBeTruthy(); expect(store.saving()).toBe(false);
  });
  it('loads detail and reports failed detail requests', () => {
    store.loadDetail(1); tenant.next(7); expect(store.selected()?.DoctorId).toBe(1);
    api.getById.mockReturnValue(throwError(() => new Error('failed')));
    store.loadDetail(2); tenant.next(7); expect(store.selected()).toBeNull(); expect(store.errorMessage()).toBeTruthy();
  });
});
