# Doctor Directory Management Acceptance Criteria

## Review Doctor Directory behavior

- Given the approved feature behavior is available
- When the user performs review doctor directory
- Then The existing application behavior requires users to review doctor directory. This behavior also preserves the approved fixed ordering, the approved tenant context. The feature uses GET /api/doctors.

## View Doctor Details behavior

- Given the approved feature behavior is available
- When the user performs view doctor details
- Then The existing application behavior requires users to view doctor details. This behavior also preserves the approved tenant context. The feature uses GET /api/doctors/{id}.

## Create Doctor behavior

- Given the approved feature behavior is available
- When the user performs create doctor
- Then The existing application behavior requires users to create doctor. This behavior also preserves the approved tenant context. The feature uses POST /api/doctors.

## Update Doctor behavior

- Given the approved feature behavior is available
- When the user performs update doctor
- Then The existing application behavior requires users to update doctor. This behavior also preserves the approved tenant context. The feature uses PUT /api/doctors.

## Delete Doctor behavior

- Given the approved feature behavior is available
- When the user performs delete doctor
- Then The existing application behavior requires users to delete doctor. This behavior also preserves the approved bulk operation behavior, the approved tenant context. The feature uses DELETE /api/doctors/{id}.

## Continue Through Doctor Results behavior

- Given the approved feature behavior is available
- When the user performs continue through doctor results
- Then The existing application behavior requires users to continue through doctor results.

## Maintain Doctor Profile Media behavior

- Given the approved feature behavior is available
- When the user performs maintain doctor profile media
- Then The existing application behavior requires users to maintain doctor profile media.

## Validate Doctor Input behavior

- Given the approved feature behavior is available
- When the user performs validate doctor input
- Then The existing application behavior requires users to validate doctor input.

## Navigate from the Doctor Experience behavior

- Given the approved feature behavior is available
- When the user performs navigate from the doctor experience
- Then The existing application behavior requires users to navigate from the doctor experience.

## Establish Current Tenant Context behavior

- Given the approved feature behavior is available
- When the user performs establish current tenant context
- Then The existing application behavior requires users to establish current tenant context. The feature uses GET /api/users/current/tenant.
