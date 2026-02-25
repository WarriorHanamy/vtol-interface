# Scenario: Coordinate Transformation Helpers
- Given: VtolFeatureProvider instance exists
- When: Helper methods are called
- Then: Coordinate transformations are performed correctly

## Test Steps

- Case 1 (happy path): _ned_to_frd() transforms vector from NED to FRD using quaternion
- Case 2 (happy path): _frd_to_flu() transforms vector from FRD to FLU by negating Y and Z
- Case 3 (edge case): _ned_to_frd() handles valid quaternion input
- Case 4 (edge case): _frd_to_flu() handles 3D vector input

## Status
- [x] Write scenario document
- [ ] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
