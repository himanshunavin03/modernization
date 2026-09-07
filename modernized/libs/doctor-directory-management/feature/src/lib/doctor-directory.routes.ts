import { Routes } from '@angular/router';
import { DoctorDetailComponent } from './doctor-detail.component';
import { DoctorListComponent } from './doctor-list.component';

export const DOCTOR_DIRECTORY_ROUTES: Routes = [
  { path: '', component: DoctorListComponent },
  { path: 'new', component: DoctorDetailComponent },
  { path: ':id', component: DoctorDetailComponent },
];
