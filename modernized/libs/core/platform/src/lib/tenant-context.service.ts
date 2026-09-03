import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { shareReplay } from 'rxjs';
import { RUNTIME_CONFIG } from './runtime-config';
@Injectable({ providedIn: 'root' })
export class TenantContextService {
  private readonly http = inject(HttpClient); private readonly config = inject(RUNTIME_CONFIG);
  readonly tenantId$ = this.http.get<number>(`${this.config.apiBaseUrl.replace(/\/$/, '')}/api/users/current/tenant`).pipe(shareReplay({ bufferSize: 1, refCount: true }));
}
