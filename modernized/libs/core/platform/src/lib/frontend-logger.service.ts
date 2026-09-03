import { Injectable } from '@angular/core';
export interface LogContext { [key: string]: string | number | boolean | null | undefined; }
@Injectable({ providedIn: 'root' })
export class FrontendLogger {
  error(event: string, context: LogContext): void { console.error(event, context); }
}
