import { TestBed } from '@angular/core/testing';
import { DoctorApiClient } from '@modernized/doctor-directory-management/data-access';
import { TenantContextService } from '@healthclinic/core/platform';
import { of } from 'rxjs';
import { DoctorDirectoryStore } from './doctor-directory.store';

describe('DoctorDirectoryStore', () => {
  it('loads the approved tenant-aware directory', () => {
    TestBed.configureTestingModule({ providers: [DoctorDirectoryStore, { provide: DoctorApiClient, useValue: { getList: () => of([]), getById: () => of({}) } }, { provide: TenantContextService, useValue: { tenantId$: of(7) } }] });
    const store = TestBed.inject(DoctorDirectoryStore); store.loadNext(); expect(store.items()).toEqual([]); expect(store.loading()).toBe(false);
  });
});
