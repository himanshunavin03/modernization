import { DatePipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, DestroyRef, effect, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { DoctorDirectoryStore, type Doctor } from '@modernized/doctor-directory-management/state';

@Component({
  selector: 'modernized-doctor-directory-management-detail', standalone: true, imports: [RouterLink, ReactiveFormsModule, DatePipe],
  providers: [DoctorDirectoryStore], templateUrl: './doctor-detail.component.html',
  styleUrl: './doctor-directory.component.css', changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DoctorDetailComponent {
  protected readonly store = inject(DoctorDirectoryStore);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly destroyRef = inject(DestroyRef);
  private readonly builder = inject(FormBuilder).nonNullable;
  protected readonly editMode = this.route.snapshot.paramMap.has('id');
  protected readonly registrationDate = new Date();
  protected readonly fields = ['Name', 'Description', 'Address', 'Email', 'Phone', 'Mobile'] as const;
  protected readonly form = this.builder.group({
    Name: ['', Validators.required], Description: ['', Validators.required],
    Address: ['', Validators.required], Email: ['', Validators.required],
    Phone: ['', Validators.required], Mobile: ['', Validators.required], Picture: '',
  });
  protected readonly preview = signal('');
  protected readonly readingFile = signal(false);
  private reader: FileReader | null = null;
  constructor() {
    effect(() => {
      const item = this.store.selected();
      if (item) { this.form.patchValue(item); this.preview.set(this.pictureUrl(item)); }
    });
    this.destroyRef.onDestroy(() => this.reader?.abort());
    const id = Number(this.route.snapshot.paramMap.get('id'));
    if (this.editMode) {
      if (Number.isInteger(id) && id > 0) this.store.loadDetail(id);
      else this.store.errorMessage.set('The requested record identifier is invalid.');
    }
  }
  protected submit(): void {
    if (this.form.invalid || this.readingFile() || (this.editMode && !this.store.selected())) return;
    this.store.save({ ...this.store.selected(), ...this.form.getRawValue() }, () => { void this.router.navigate(['/doctors']); });
  }
  protected deleteDoctor(): void {
    const item = this.store.selected();
    if (item && window.confirm('Delete this doctor?')) this.store.deleteConfirmed([item.DoctorId], () => { void this.router.navigate(['/doctors']); });
  }
  protected selectPicture(event: Event): void {
    const input = event.target;
    if (!(input instanceof HTMLInputElement)) return;
    const file = input.files?.[0];
    if (!file) return;
    this.reader?.abort();
    const reader = new FileReader();
    this.reader = reader;
    this.readingFile.set(true);
    reader.onload = () => {
      if (typeof reader.result === 'string' && !this.destroyRef.destroyed) {
        const encoded = reader.result.substring(reader.result.indexOf(',') + 1);
        this.form.controls.Picture.setValue(encoded);
        this.preview.set(`data:image/png;base64,${encoded}`);
        this.readingFile.set(false);
      }
    };
    reader.onerror = () => { this.readingFile.set(false); this.store.errorMessage.set('The selected profile file could not be read.'); };
    reader.readAsDataURL(file);
  }
  protected pictureUrl(item: Doctor): string { return item.Picture ? `data:image/png;base64,${item.Picture}` : ''; }
}
