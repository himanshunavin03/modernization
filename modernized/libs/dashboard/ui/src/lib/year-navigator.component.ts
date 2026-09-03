import { ChangeDetectionStrategy, Component, input, output } from '@angular/core';

@Component({
  selector: 'healthclinic-year-navigator', standalone: true, changeDetection: ChangeDetectionStrategy.OnPush,
  template: `<div class="year-control" role="group" [attr.aria-label]="label()"><button type="button" (click)="previous.emit()" [attr.aria-label]="'Previous ' + label()">&lsaquo;</button><output [attr.aria-label]="label()">{{ year() }}</output><button type="button" (click)="next.emit()" [disabled]="year() >= maximumYear()" [attr.aria-label]="'Next ' + label()">&rsaquo;</button></div>`,
  styles: [`.year-control{align-items:center;color:#7c7c81;display:flex;font:400 19px 'Roboto',sans-serif;gap:20px}.year-control button{background:transparent;border:0;color:#7c7c81;cursor:pointer;font-size:2rem;line-height:1;padding:2px 8px}.year-control button:disabled{cursor:not-allowed;opacity:.3}.year-control button:focus-visible{outline:3px solid #ff1770;outline-offset:2px}output{min-width:4ch;text-align:center}`],
})
export class YearNavigatorComponent {
  readonly label = input.required<string>(); readonly year = input.required<number>(); readonly maximumYear = input.required<number>();
  readonly previous = output<void>(); readonly next = output<void>();
}
