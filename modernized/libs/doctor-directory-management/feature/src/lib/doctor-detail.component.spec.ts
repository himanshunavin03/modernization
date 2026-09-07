import { signal } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { ActivatedRoute, convertToParamMap, provideRouter, Router } from '@angular/router';
import { DoctorDirectoryStore, type Doctor } from '@modernized/doctor-directory-management/state';
import { DoctorDetailComponent } from './doctor-detail.component';

describe('DoctorDetailComponent', () => {
  const record = { DoctorId: 3, Name: 'Name', Description: 'Description', Address: 'Address', Email: 'Email', Phone: 'Phone', Mobile: 'Mobile', Picture: '', PatientCount: 2 } as Doctor;
  async function setup(edit = false) {
    const store = { selected: signal<Doctor | null>(edit ? record : null), loading: signal(false), saving: signal(false), errorMessage: signal<string | null>(null), loadDetail: vi.fn(), save: vi.fn(), deleteConfirmed: vi.fn() };
    await TestBed.configureTestingModule({ imports: [DoctorDetailComponent], providers: [provideRouter([]), { provide: ActivatedRoute, useValue: { snapshot: { paramMap: convertToParamMap(edit ? { id: '3' } : {}) } } }] })
      .overrideComponent(DoctorDetailComponent, { set: { providers: [{ provide: DoctorDirectoryStore, useValue: store }] } }).compileComponents();
    const fixture = TestBed.createComponent(DoctorDetailComponent); fixture.detectChanges();
    const root: HTMLElement = fixture.nativeElement;
    return { fixture, root, store };
  }
  it('requires exactly the six approved fields before Add and navigates only on success', async () => {
    const { fixture, root, store } = await setup();
    const submit = root.querySelector<HTMLButtonElement>('button[type="submit"]')!;
    expect(submit.textContent).toBe('Add'); expect(submit.disabled).toBe(true);
    expect(root.textContent).toContain('Add a profile photo');
    const fields = ['Name', 'Description', 'Address', 'Email', 'Phone', 'Mobile'];
    for (const field of fields) {
      const input = root.querySelector<HTMLInputElement>('#' + field)!;
      expect(root.querySelector('label[for="' + field + '"]')).not.toBeNull();
      input.value = field; input.dispatchEvent(new Event('input')); fixture.detectChanges();
    }
    expect(submit.disabled).toBe(false);
    for (const field of fields) {
      const input = root.querySelector<HTMLInputElement>('#' + field)!;
      input.value = ''; input.dispatchEvent(new Event('input')); fixture.detectChanges(); expect(submit.disabled).toBe(true);
      input.value = field; input.dispatchEvent(new Event('input')); fixture.detectChanges();
    }
    const navigate = vi.spyOn(TestBed.inject(Router), 'navigate').mockResolvedValue(true);
    root.querySelector('form')!.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
    expect(store.save).toHaveBeenCalledOnce(); expect(navigate).not.toHaveBeenCalled();
    store.save.mock.calls[0][1](); expect(navigate).toHaveBeenCalledWith(['/doctors']);
  });
  it('populates the edit form, gates Save, confirms deletion and returns on success', async () => {
    const { fixture, root, store } = await setup(true);
    expect(store.loadDetail).toHaveBeenCalledWith(3);
    expect(root.querySelector<HTMLInputElement>('#Name')!.value).toBe('Name');
    const submit = root.querySelector<HTMLButtonElement>('button[type="submit"]')!;
    expect(submit.textContent).toBe('Save'); expect(submit.disabled).toBe(false);
    const name = root.querySelector<HTMLInputElement>('#Name')!;
    name.value = ''; name.dispatchEvent(new Event('input')); fixture.detectChanges(); expect(submit.disabled).toBe(true);
    name.value = 'Updated'; name.dispatchEvent(new Event('input')); fixture.detectChanges();
    root.querySelector('form')!.dispatchEvent(new Event('submit', { cancelable: true }));
    expect(store.save.mock.calls[0][0]).toMatchObject({ DoctorId: 3, Name: 'Updated' });
    const navigate = vi.spyOn(TestBed.inject(Router), 'navigate').mockResolvedValue(true);
    store.save.mock.calls[0][1](); expect(navigate).toHaveBeenCalledWith(['/doctors']);
    const confirm = vi.spyOn(window, 'confirm').mockReturnValue(false);
    root.querySelector<HTMLButtonElement>('button[type="button"]')!.click(); expect(store.deleteConfirmed).not.toHaveBeenCalled();
    confirm.mockReturnValue(true); root.querySelector<HTMLButtonElement>('button[type="button"]')!.click();
    expect(store.deleteConfirmed.mock.calls[0][0]).toEqual([3]); store.deleteConfirmed.mock.calls[0][1]();
    expect(navigate).toHaveBeenCalledTimes(2); confirm.mockRestore();
  });
  it('reads selected file bytes into picture state and preview without an upload request', async () => {
    const { fixture, root } = await setup();
    const input = root.querySelector<HTMLInputElement>('#profile-file')!;
    Object.defineProperty(input, 'files', { value: [new File(['picture'], 'profile.png', { type: 'image/png' })] });
    input.dispatchEvent(new Event('change'));
    await vi.waitFor(() => { fixture.detectChanges(); expect(root.querySelector('img.portrait')).not.toBeNull(); });
    expect(root.querySelector('img')!.getAttribute('src')).toBe('data:image/png;base64,cGljdHVyZQ==');
    expect(root.textContent).not.toContain('Add a profile photo');
  });
});
