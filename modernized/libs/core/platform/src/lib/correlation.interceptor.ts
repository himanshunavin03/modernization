import { HttpInterceptorFn } from '@angular/common/http';
export const correlationInterceptor: HttpInterceptorFn = (request, next) => next(request.clone({ setHeaders: { 'X-Correlation-ID': globalThis.crypto.randomUUID() } }));
