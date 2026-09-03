import { ChangeDetectionStrategy, Component, computed, input } from '@angular/core';

export interface ChartSeries { label: string; color: string; values: number[]; }

@Component({
  selector: 'healthclinic-dashboard-chart', standalone: true, changeDetection: ChangeDetectionStrategy.OnPush,
  template: `<div class="chart"><svg viewBox="0 0 1100 300" role="img" [attr.aria-label]="accessibleLabel()"><g class="grid">@for (line of gridLines; track line) { <line x1="40" x2="1080" [attr.y1]="line" [attr.y2]="line" /> }</g>@if (kind() === 'line') { @for (item of normalizedSeries(); track item.label) { <polyline fill="none" [attr.stroke]="item.color" stroke-width="4" [attr.points]="points(item.values)" /> } } @else { @for (value of firstValues(); track $index) { <rect [attr.x]="barX($index)" [attr.y]="barY(value)" width="48" [attr.height]="barHeight(value)" fill="#00d8cc" /> } }</svg><div class="months" aria-hidden="true">@for (month of months; track month) { <span>{{ month }}</span> }</div><ul class="legend">@for (item of normalizedSeries(); track item.label) { <li><span [style.background]="item.color"></span>{{ item.label }}</li> }</ul></div>`,
  styles: [`.chart{padding:0 30px}svg{display:block;height:auto;max-height:300px;width:100%}.grid line{stroke:#0000000d;stroke-width:1}.months{color:#7c7c81;display:grid;font:11px 'Roboto',sans-serif;grid-template-columns:repeat(12,1fr);padding-left:3.5%}.months span{text-align:center}.legend{display:flex;gap:45px;list-style:none;margin:28px 10px 0;padding:0}.legend li{color:#7c7c81;font:13px 'Roboto',sans-serif}.legend span{border-radius:5px;display:inline-block;height:4px;margin-right:10px;vertical-align:middle;width:15px}@media(max-width:700px){.chart{overflow-x:auto;padding:0 12px}.chart svg,.months{min-width:680px}.legend{gap:20px}}`],
})
export class DashboardChartComponent {
  readonly kind = input.required<'line' | 'bar'>(); readonly series = input.required<ChartSeries[]>();
  readonly months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']; readonly gridLines = [40, 95, 150, 205, 260];
  protected readonly normalizedSeries = computed(() => this.series().map((item) => ({ ...item, values: Array.from({ length: 12 }, (_, index) => item.values[index] ?? 0) })));
  protected readonly firstValues = computed(() => this.normalizedSeries()[0]?.values ?? []);
  private readonly maximum = computed(() => Math.max(1, ...this.normalizedSeries().flatMap((item) => item.values)));
  protected readonly accessibleLabel = computed(() => this.normalizedSeries().map((item) => `${item.label}: ${item.values.join(', ')}`).join('. '));
  protected points(values: number[]): string { return values.map((value, index) => `${50 + index * 93},${this.barY(value)}`).join(' '); }
  protected barX(index: number): number { return 65 + index * 86; }
  protected barY(value: number): number { return 260 - this.barHeight(value); }
  protected barHeight(value: number): number { return Math.max(0, value) / this.maximum() * 220; }
}
