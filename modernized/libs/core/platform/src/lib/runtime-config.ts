import { EnvironmentProviders, InjectionToken, makeEnvironmentProviders } from '@angular/core';
export interface RuntimeConfig {
  apiBaseUrl: string;
  tenantContextPath: string;
  tenantHeaderName: string;
}
export const RUNTIME_CONFIG = new InjectionToken<RuntimeConfig>('HEALTHCLINIC_RUNTIME_CONFIG');
export function provideRuntimeConfig(config: RuntimeConfig): EnvironmentProviders { return makeEnvironmentProviders([{ provide: RUNTIME_CONFIG, useValue: config }]); }
