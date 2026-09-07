import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { DoctorDirectoryStore, type Doctor } from '@modernized/doctor-directory-management/state';

@Component({
  selector: 'modernized-doctor-directory-management-list', standalone: true, imports: [RouterLink],
  providers: [DoctorDirectoryStore], templateUrl: './doctor-list.component.html',
  styleUrl: './doctor-directory.component.css', changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DoctorListComponent {
  protected readonly store = inject(DoctorDirectoryStore);
  constructor() { this.store.loadNext(); }
  protected remove(ids: number[]): void {
    if (ids.length && window.confirm('Delete the selected doctor records?')) this.store.deleteConfirmed(ids);
  }
  protected removeSelected(): void { this.remove([...this.store.selectedIds()]); }
  protected pictureUrl(item: Doctor): string { return item.Picture ? `data:image/png;base64,${item.Picture}` : ''; }
}
