export type DoctorInput = Pick<Doctor, 'Name' | 'Address' | 'Description' | 'Phone' | 'Mobile' | 'Email' | 'Picture'> & Partial<Doctor>;

export interface Doctor {
  DoctorId: number;
  Name: string;
  Address: string;
  Description: string;
  Phone: string;
  Mobile: string;
  Email: string;
  Picture: string;
  Deleted: boolean;
  TenantId: number;
  Tenant: unknown;
  Speciality: unknown;
  CurrentRoomNumber: number;
  PatientCount: number;
  Synchronized: boolean;
  CreatedAt: string | null;
  Id: string;
  UpdatedAt: string | null;
  Version: string;
}
