import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { DoctorDirectoryStore, type Doctor } from '@modernized/doctor-directory-management/state';

@Component({
  selector: 'modernized-doctor-directory-management-detail', standalone: true, imports: [RouterLink],
  providers: [DoctorDirectoryStore], templateUrl: './doctor-detail.component.html',
  styleUrl: './doctor-directory.component.css', changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DoctorDetailComponent {
  protected readonly store = inject(DoctorDirectoryStore);
  private readonly route = inject(ActivatedRoute);
  constructor() {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    if (Number.isInteger(id) && id > 0) this.store.loadDetail(id);
    else this.store.errorMessage.set('The requested record identifier is invalid.');
  }
  protected pictureUrl(item: Doctor): string { return item.Picture ? `data:image/png;base64,${item.Picture}` : ''; }
}
