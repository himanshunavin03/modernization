import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { map, shareReplay } from 'rxjs';
import { RUNTIME_CONFIG } from './runtime-config';
@Injectable({ providedIn: 'root' })
export class TenantContextService {
  private readonly http = inject(HttpClient); private readonly config = inject(RUNTIME_CONFIG);
  readonly tenantId$ = this.http.get<number | null>(this.url(this.config.tenantContextPath)).pipe(
    map((tenantId) => {
      if (!Number.isInteger(tenantId) || tenantId === null || tenantId <= 0) {
        throw new Error('The authenticated session did not provide a valid tenant context.');
      }
      return tenantId;
    }),
    shareReplay({ bufferSize: 1, refCount: true }),
  );

  private url(path: string): string { return `${this.config.apiBaseUrl.replace(/\/$/, '')}${path}`; }
}
