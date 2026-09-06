# Doctor Directory Management Stories

## Review Doctor Directory

As a user, I want to select "LOAD MORE", so that I can complete the supported doctor directory management interaction.

A user can select "LOAD MORE"; additional items are appended to $scope.doctors. This behavior also preserves the approved fixed ordering, the approved tenant context.

## View Doctor Details

As a user, I want to view doctor details, so that I can complete the supported doctor directory management interaction.

The system resolves the required context before dependent feature operations run. This behavior also preserves the approved tenant context.

## Create Doctor

As a user, I want to select "Save", so that I can complete the supported doctor directory management interaction.

A user can select the "Add", "Save" actions. This behavior also preserves the approved tenant context.

## Update Doctor

As a user, I want to select "Save", so that I can complete the supported doctor directory management interaction.

A user can select the "Add", "Save" actions. This behavior also preserves the approved tenant context.

## Delete Doctor

As a user, I want to select "Delete this doctor", so that I can complete the supported doctor directory management interaction.

A user can select "Delete", "Delete this doctor"; $scope.doctors is modified by the splice operation. confirmation is requested before the guarded operation. the view changes to doctors. This behavior also preserves the approved bulk operation behavior, the approved tenant context.

## Maintain Doctor Profile Media

As a user, I want to maintain doctor profile media, so that I can complete the supported doctor directory management interaction.

The feature preserves the supported maintain doctor profile media interaction.

## Validate Doctor Input

As a user, I want to validate doctor input, so that I can complete the supported doctor directory management interaction.

The form prevents its related action until the required inputs are provided.

## Navigate from the Doctor Experience

As a user, I want to select "New doctor", so that I can complete the supported doctor directory management interaction.

A user can select the "Back to doctors", "New doctor", "Patients" actions.

## Use Doctor Interaction Controls

As a user, I want to select "Save", so that I can complete the supported doctor directory management interaction.

The directory supports record selection and selection-state changes before related actions are used.
