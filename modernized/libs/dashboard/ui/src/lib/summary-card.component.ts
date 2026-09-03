import { ChangeDetectionStrategy, Component, input } from '@angular/core';
import { DecimalPipe } from '@angular/common';

@Component({
  selector: 'healthclinic-summary-card', standalone: true, imports: [DecimalPipe], changeDetection: ChangeDetectionStrategy.OnPush,
  host: { '[class]': "'summary ' + variant()" },
  template: `<p class="quantity">@if (currency()) { <span aria-hidden="true">$</span> }{{ value() | number:'1.0-0' }}</p><h2>{{ label() }} <span class="variation"><span class="trend" aria-hidden="true"></span> {{ variation() | number:'1.0-1' }} %</span></h2>`,
  styles: [`:host{background-position:center;background-size:cover;border-radius:2px;color:#fff;display:block;min-height:197px;padding:35px}.patients{background-color:#00d8cc;background-image:url('/assets/dashboard/summary/bg_graph_01.png')}.month{background-color:#71717f;background-image:url('/assets/dashboard/summary/bg_graph_02.png')}.annual{background-color:#b8b8b9;background-image:url('/assets/dashboard/summary/bg_graph_03.png')}.quantity{font:200 70px/1 'Roboto',sans-serif;margin:0 0 30px}.quantity span{font-size:30px;vertical-align:top}h2{font-size:19px;font-weight:500;margin:0}.variation{float:right;font-weight:300}.trend{background:url('/assets/dashboard/arrow_01.png') no-repeat center/contain;display:inline-block;height:18px;margin-right:8px;vertical-align:middle;width:10px}@media(max-width:992px){.patients{background-image:url('/assets/dashboard/summary/bg_graph_01_snap.png')}.month{background-image:url('/assets/dashboard/summary/bg_graph_02_snap.png')}.annual{background-image:url('/assets/dashboard/summary/bg_graph_03_snap.png')}}@media(max-width:520px){:host{min-height:160px;padding:26px}.quantity{font-size:52px}}`],
})
export class SummaryCardComponent {
  readonly variant = input.required<'patients' | 'month' | 'annual'>();
  readonly value = input.required<number>(); readonly label = input.required<string>();
  readonly variation = input.required<number>(); readonly currency = input(false);
}
