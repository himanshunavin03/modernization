Make one final Roslyn graph-label correction before Step 4.

Read the project memory and save this request as:
docs/prompts/008-step-3b-2-return-type-label-correction.md

Issue:
In merge_roslyn(), Action -> RETURNS_TYPE currently uses reference("DTO", ...).
This incorrectly labels every action return type as DTO.

Fix:

- Build an identity-to-semantic-label map from proven Roslyn facts.
- For RETURNS_TYPE, use DTO only when the resolved return type has a proven `dto` fact.
- Otherwise use Type.
- For HAS_PROPERTY, use the resolved owner label: DTO if it is a DTO, otherwise Type.
- Do not create duplicate Type and DTO nodes for the same fully qualified symbol identity.
- Preserve project isolation and all evidence.

Tests:

- Keep the existing ShipmentSummary DTO test.
- Add a generic action returning a normal non-DTO type, such as string or IActionResult.
- Verify its RETURNS_TYPE target has label Type, not DTO.
- Verify the DTO return remains label DTO.
- Run python -m pytest -q.
- If dotnet is available, run the Roslyn integration test too.

Update PROJECT_MEMORY.md, PROGRESS.md, and DECISIONS.md only after validation passes.
Do not begin Step 4 and do not commit/push unless I ask.
