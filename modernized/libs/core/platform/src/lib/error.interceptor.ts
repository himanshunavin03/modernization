import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { catchError, throwError } from 'rxjs';
import { FrontendLogger } from './frontend-logger.service';
@Injectable({ providedIn: 'root' }) export class FrontendErrorService { private readonly logger = inject(FrontendLogger); report(error: HttpErrorResponse): void { this.logger.error('dashboard_http_request_failed', { status: error.status, url: error.url }); } }
export const errorInterceptor: HttpInterceptorFn = (request, next) => { const errors = inject(FrontendErrorService); return next(request).pipe(catchError((error: HttpErrorResponse) => { errors.report(error); return throwError(() => error); })); };
