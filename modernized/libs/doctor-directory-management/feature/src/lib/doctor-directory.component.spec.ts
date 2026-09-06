import { signal } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { DoctorDirectoryStore } from '@modernized/doctor-directory-management/state';
import { DoctorListComponent } from './doctor-list.component';

describe('DoctorListComponent', () => {
  it('ac-doctor-directory-management-review-doctor-directory-001 ac-doctor-directory-management-view-doctor-details-in-tenant-context-001: renders the approved directory experience', async () => {
    const store = { items: signal([{ DoctorId: 1, Name: 'Name', Address: 'Address', Description: 'Description', Phone: 'Phone', Mobile: 'Mobile', Email: 'Email', Picture: 'Picture', Deleted: false, TenantId: 1, Tenant: 'Tenant', Speciality: 'Speciality', CurrentRoomNumber: 1, PatientCount: 1, Synchronized: false, CreatedAt: null, Id: 'Id', UpdatedAt: null, Version: 'Version' }]), selected: signal(null), loading: signal(false), noMoreData: signal(true), errorMessage: signal(null), loadNext: vi.fn(), loadDetail: vi.fn() };
    await TestBed.configureTestingModule({ imports: [DoctorListComponent], providers: [provideRouter([])] }).overrideComponent(DoctorListComponent, { set: { providers: [{ provide: DoctorDirectoryStore, useValue: store }] } }).compileComponents();
    const fixture = TestBed.createComponent(DoctorListComponent); fixture.detectChanges(); expect(fixture.nativeElement.textContent).toContain('Doctors');
  });
});
