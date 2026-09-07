# Doctor integration responsibility design

TT-005 deliverable: gateway routing and policy plan. TT-006 deliverable: BFF responsibility design. These are the planning deliverables required by the frozen tasks, not claims of deployed gateway or BFF infrastructure.

The existing runtime-configured API base, typed DoctorApiClient and TenantContextService remain the integration ports. Preserve these contracts through ingress routing:

| Method | Route | Frontend responsibility |
| --- | --- | --- |
| GET | /api/doctors | pageSize/pageCount transport parameters; append and fixed-name display order |
| GET | /api/doctors/{id} | Load the selected record into the existing detail form |
| POST | /api/doctors | Submit approved form values and current tenant; navigate after success |
| PUT | /api/doctors | Retain record identity and unchanged metadata while updating approved fields |
| DELETE | /api/doctors/{id} | Confirm in the UI; issue one existing request per selected ID; remove only successful results |
| GET | /api/users/current/tenant | Resolve context automatically before dependent operations |

Gateway policy responsibilities: preserve method/path/query/body/response semantics and the authenticated session; validate identity and tenant authorization at the existing backend boundary. A browser tenant header is context, never authorization proof. Carry X-Correlation-ID through ingress and downstream calls; redact payloads, credentials, profile data and tenant data from telemetry. Production ingress must terminate TLS and enforce the existing access policy; the development proxy does not prove those controls deployed. Do not introduce identity-provider rules absent from the approved architecture.

Future BFF facade contracts remain TARGET_CONTRACT_TO_BE_DESIGNED. No new endpoint, DTO or aggregation is selected or implemented in this stage. The six existing calls already serve the approved behavior. A future adapter may replace the typed transport implementation only after its contract is explicitly approved; presentation and state should continue to depend on typed ports. Bulk deletion does not justify a new bulk endpoint, and profile bytes travel in the existing Doctor model rather than a new upload endpoint.

Error handling: preserve service errors for the state boundary, show the existing loading/error feedback, retain failed records after partial deletion and navigate only after successful writes. Reuse the existing platform correlation interceptor; no credentials or business payloads are added to logs.
