import { ChangeDetectionStrategy, Component, computed, inject } from '@angular/core';
import { DashboardChartComponent, SummaryCardComponent, YearNavigatorComponent, type ChartSeries } from '@healthclinic/dashboard/ui';
import { DashboardStore } from '@healthclinic/dashboard/state';

@Component({
  selector: 'healthclinic-dashboard-feature',
  standalone: true,
  imports: [DashboardChartComponent, SummaryCardComponent, YearNavigatorComponent],
  providers: [DashboardStore],
  templateUrl: './dashboard-feature.component.html',
  styleUrl: './dashboard-feature.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DashboardFeatureComponent {
  protected readonly store = inject(DashboardStore);
  protected readonly incomeExpenseSeries = computed<ChartSeries[]>(() => [
    { label: 'INCOMES', color: '#00d8cc', values: (this.store.expenses() ?? []).map((item) => item.Incomes) },
    { label: 'EXPENSES', color: '#ff1770', values: (this.store.expenses() ?? []).map((item) => item.Expenses) },
  ]);
  protected readonly patientSeries = computed<ChartSeries[]>(() => [
    { label: 'PATIENTS', color: '#00d8cc', values: (this.store.patients() ?? []).map((item) => item.PatientsCount) },
  ]);
}
