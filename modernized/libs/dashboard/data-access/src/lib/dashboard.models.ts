export interface ClinicSummary {
  NewPatients: number; NewPatientsVariation: number; MonthProfit: number;
  MonthProfitVariation: number; AnualProfit: number; AnualProfitVariation: number;
}
export interface ExpensesSummary { Month: number; Year: number; Expenses: number; Incomes: number; }
export interface PatientsSummary { Month: number; Year: number; PatientsCount: number; }
export type TenantId = number;
