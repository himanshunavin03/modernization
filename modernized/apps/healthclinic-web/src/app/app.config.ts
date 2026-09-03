import { ApplicationConfig } from '@angular/core';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { provideRouter } from '@angular/router';
import { correlationInterceptor, errorInterceptor, provideRuntimeConfig, type RuntimeConfig } from '@healthclinic/core/platform';
import { appRoutes } from './app.routes';

const runtimeConfig = (globalThis as typeof globalThis & { __HEALTHCLINIC_CONFIG__?: RuntimeConfig }).__HEALTHCLINIC_CONFIG__ ?? { apiBaseUrl: '' };

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(appRoutes),
    provideHttpClient(withInterceptors([correlationInterceptor, errorInterceptor])),
    provideRuntimeConfig(runtimeConfig),
  ],
};
