import { ChangeDetectionStrategy, Component, signal } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

@Component({
  selector: 'healthclinic-private-shell',
  standalone: true,
  imports: [RouterLink, RouterLinkActive, RouterOutlet],
  templateUrl: './private-shell.component.html',
  styleUrl: './private-shell.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PrivateShellComponent {
  protected readonly menuOpen = signal(false);
  protected toggleMenu(): void { this.menuOpen.update((open) => !open); }
  protected closeMenu(): void { this.menuOpen.set(false); }
}
