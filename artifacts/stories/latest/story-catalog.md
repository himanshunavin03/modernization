# Jira-Style User Story Catalog

Readiness: `STORIES_READY_WITH_LIMITATIONS`

Acceptance Criteria are intentionally excluded from this stage.

## Operational Dashboard Insights

Presents clinic-context operational summaries and yearly reporting through the legacy Dashboard experience.

### Access Yearly Operational Reports

As a user of the existing application, I want access year-dependent expense and patient reporting information, so that I can access the supported behavior in the existing experience.

**Story ID:** `story-operational-dashboard-insights-access-yearly-operational-reports`  
**Priority:** `HIGH`  
**Confidence:** `MEDIUM`  
**Business value:** `INFERRED_BUSINESS_VALUE` - The Feature appears to support operational visibility by bringing clinic summary and yearly reporting information into one dashboard experience.

Represents the approved yearly expense and patient-report interactions while retaining their dynamic URL status.

**Current state:** The existing application supports: The expense-reporting flow has current tenant context. The patient-reporting flow has current tenant context. Yearly expense information is requested. Yearly patient-report information is requested.

**Modernization relevance:** Preserve this approved business behavior during frontend modernization without changing backend contracts.

**Workflows:** Dashboard expenses load current tenant, Dashboard patient report loads current tenant, Dashboard requests yearly expenses, Dashboard requests yearly patient report

**Open questions:** Q-DASH-002

**Limitations:** Two yearly report relationships remain DYNAMIC and are not treated as proven endpoint mappings.

### View Tenant-Aware Dashboard Summary

As a user of the existing application, I want access dashboard summary information in current tenant context, so that I can access the supported behavior in the existing experience.

**Story ID:** `story-operational-dashboard-insights-view-tenant-aware-dashboard-summary`  
**Priority:** `HIGH`  
**Confidence:** `MEDIUM`  
**Business value:** `INFERRED_BUSINESS_VALUE` - The Feature appears to support operational visibility by bringing clinic summary and yearly reporting information into one dashboard experience.

Represents tenant-context retrieval and clinic-summary request behavior as one dashboard summary interaction.

**Current state:** The existing application supports: The dashboard summary flow has current tenant context. Clinic summary information is requested for the dashboard.

**Modernization relevance:** Preserve this approved business behavior during frontend modernization without changing backend contracts.

**Workflows:** Dashboard summary loads current tenant, Dashboard requests clinic summary

**Open questions:** Q-DASH-003

**Limitations:** The clinic-summary frontend-to-backend relationship remains UNRESOLVED.

### Open Operational Dashboard

As a user of the existing application, I want open the existing operational dashboard experience, so that I can access the supported behavior in the existing experience.

**Story ID:** `story-operational-dashboard-insights-open-operational-dashboard`  
**Priority:** `HIGH`  
**Confidence:** `HIGH`  
**Business value:** `INFERRED_BUSINESS_VALUE` - The Feature appears to support operational visibility by bringing clinic summary and yearly reporting information into one dashboard experience.

Represents entry into the operational Dashboard across its Razor host and AngularJS client surface.

**Current state:** The existing application supports: The Dashboard experience is available.

**Modernization relevance:** Preserve this approved business behavior during frontend modernization without changing backend contracts.

**Workflows:** Route dashboard

**Open questions:** Q-DASH-001

**Limitations:** None beyond approved evidence

## Doctor Directory Management

Provides navigation and tenant-aware access to doctor information.

### View Doctor Details in Tenant Context

As a user of the existing application, I want access doctor detail information with current tenant context, so that I can access the supported behavior in the existing experience.

**Story ID:** `story-doctor-directory-management-view-doctor-details-in-tenant-context`  
**Priority:** `MEDIUM`  
**Confidence:** `HIGH`  
**Business value:** `INFERRED_BUSINESS_VALUE` - The Feature appears to support information accessibility by organizing doctor navigation and doctor information in one functional area.

Combines the approved doctor detail navigation and its proven tenant-context dependency as one coherent interaction.

**Current state:** The existing application supports: A doctor detail experience is available. Doctor functionality has current tenant context.

**Modernization relevance:** Preserve this approved business behavior during frontend modernization without changing backend contracts.

**Workflows:** Route doctor, Doctors load current tenant

**Open questions:** Q-DOC-001

**Limitations:** None beyond approved evidence

### Review Doctor Directory

As a user of the existing application, I want access the existing doctor directory, so that I can access the supported behavior in the existing experience.

**Story ID:** `story-doctor-directory-management-review-doctor-directory`  
**Priority:** `MEDIUM`  
**Confidence:** `HIGH`  
**Business value:** `INFERRED_BUSINESS_VALUE` - The Feature appears to support information accessibility by organizing doctor navigation and doctor information in one functional area.

Represents the approved doctor-directory navigation behavior.

**Current state:** The existing application supports: A doctor list experience is available.

**Modernization relevance:** Preserve this approved business behavior during frontend modernization without changing backend contracts.

**Workflows:** Route doctors

**Open questions:** None

**Limitations:** None beyond approved evidence

## Patient Directory Management

Provides tenant-aware navigation and access to patient information.

### Establish Patient Tenant Context

As a user of the existing application, I want obtain tenant context for patient functionality, so that I can access the supported behavior in the existing experience.

**Story ID:** `story-patient-directory-management-establish-patient-tenant-context`  
**Priority:** `MEDIUM`  
**Confidence:** `HIGH`  
**Business value:** `INFERRED_BUSINESS_VALUE` - The Feature appears to support information accessibility by providing a dedicated patient information area.

Represents the proven tenant-context interaction supporting the existing patient area.

**Current state:** The existing application supports: Patient functionality has current tenant context.

**Modernization relevance:** Preserve this approved business behavior during frontend modernization without changing backend contracts.

**Workflows:** Patients load current tenant

**Open questions:** None

**Limitations:** None beyond approved evidence

### Review Patient Directory

As a user of the existing application, I want access the existing patient directory, so that I can access the supported behavior in the existing experience.

**Story ID:** `story-patient-directory-management-review-patient-directory`  
**Priority:** `MEDIUM`  
**Confidence:** `HIGH`  
**Business value:** `INFERRED_BUSINESS_VALUE` - The Feature appears to support information accessibility by providing a dedicated patient information area.

Represents the approved patient-directory navigation behavior without asserting unsupported patient operations.

**Current state:** The existing application supports: The patient directory experience is available.

**Modernization relevance:** Preserve this approved business behavior during frontend modernization without changing backend contracts.

**Workflows:** Route patients

**Open questions:** Q-PAT-001

**Limitations:** None beyond approved evidence

## Clinic Appointment Experience

Provides clinic/appointment navigation and appointment information with proven tenant context but incomplete transaction flow evidence.

### Access Clinic Information

As a user of the existing application, I want access the existing clinic information views, so that I can access the supported behavior in the existing experience.

**Story ID:** `story-clinic-appointment-experience-access-clinic-information`  
**Priority:** `LOW`  
**Confidence:** `LOW`  
**Business value:** `INFERRED_BUSINESS_VALUE` - The Feature appears to provide a focused place to access clinic and appointment information, but its complete business value requires stakeholder validation.

Represents the approved clinic list and detail navigation behavior without asserting unsupported appointment transactions.

**Current state:** The existing application supports: A clinic detail experience is available. A clinic list experience is available.

**Modernization relevance:** Preserve this approved business behavior during frontend modernization without changing backend contracts.

**Workflows:** Route clinic, Route clinics

**Open questions:** Q-APT-001

**Limitations:** Complete appointment operations are not proven by the approved workflows.

### Establish Clinic Context

As a user of the existing application, I want obtain tenant context for clinic functionality, so that I can access the supported behavior in the existing experience.

**Story ID:** `story-clinic-appointment-experience-establish-clinic-context`  
**Priority:** `LOW`  
**Confidence:** `LOW`  
**Business value:** `INFERRED_BUSINESS_VALUE` - The Feature appears to provide a focused place to access clinic and appointment information, but its complete business value requires stakeholder validation.

Represents the proven tenant-context interaction that supports the existing clinic area.

**Current state:** The existing application supports: Clinic functionality has current tenant context.

**Modernization relevance:** Preserve this approved business behavior during frontend modernization without changing backend contracts.

**Workflows:** Clinics load current tenant

**Open questions:** Q-APT-002

**Limitations:** How clinic and appointment surfaces form a complete journey remains unresolved.

## User Access and Tenant Context

Supplies current user identity, authorization claims, and tenant context to shared frontend behavior.

### Access User Management Views

As a user of the existing application, I want access existing user list and detail views, so that I can access the supported behavior in the existing experience.

**Story ID:** `story-user-access-context-access-user-management-views`  
**Priority:** `HIGH`  
**Confidence:** `HIGH`  
**Business value:** `INFERRED_BUSINESS_VALUE` - The Feature appears to support consistent access to user and tenant context across frontend areas.

Represents the approved user-management navigation behavior.

**Current state:** The existing application supports: A user detail experience is available. A user list experience is available.

**Modernization relevance:** Preserve this approved business behavior during frontend modernization without changing backend contracts.

**Workflows:** Route user, Route users

**Open questions:** None

**Limitations:** None beyond approved evidence

### Resolve Current User and Claims

As a user of the existing application, I want make current user identity and claims available to shared application behavior, so that I can access the supported behavior in the existing experience.

**Story ID:** `story-user-access-context-resolve-current-user-and-claims`  
**Priority:** `HIGH`  
**Confidence:** `HIGH`  
**Business value:** `INFERRED_BUSINESS_VALUE` - The Feature appears to support consistent access to user and tenant context across frontend areas.

Combines the approved identity and claims retrieval workflows used by shared header and initial-page behavior.

**Current state:** The existing application supports: The header has current user identity. The header has current claims. Initial-page behavior has current claims.

**Modernization relevance:** Preserve this approved business behavior during frontend modernization without changing backend contracts.

**Workflows:** Header loads current user, Header loads current claims, Initial page loads current claims

**Open questions:** Q-USER-001

**Limitations:** The business meaning of individual claims and authorization decisions is not proven.

### Resolve Tenant Context for User Functions

As a user of the existing application, I want make current tenant context available to user functionality, so that I can access the supported behavior in the existing experience.

**Story ID:** `story-user-access-context-resolve-tenant-context-for-user-functions`  
**Priority:** `HIGH`  
**Confidence:** `HIGH`  
**Business value:** `INFERRED_BUSINESS_VALUE` - The Feature appears to support consistent access to user and tenant context across frontend areas.

Represents the proven tenant-context interaction and its approved tenant-scoped behavior rule.

**Current state:** The existing application supports: User functionality has tenant context.

**Modernization relevance:** Preserve this approved business behavior during frontend modernization without changing backend contracts.

**Workflows:** Users load current tenant

**Open questions:** None

**Limitations:** None beyond approved evidence

