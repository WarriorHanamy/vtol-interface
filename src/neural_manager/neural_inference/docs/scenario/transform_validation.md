# Scenario: Transform Validation
- Given: A feature registry with pipeline steps referencing transforms
- When: The loader validates transform names against the transform registry
- Then: Valid transforms pass validation, invalid transforms raise KeyError

## Test Steps

- Case 1 (happy path): All referenced transforms exist in transform registry
- Case 2 (unknown transform): Pipeline step references a transform not in registry
- Case 3 (helpful error message): Error message lists available transforms when transform not found
- Case 4 (empty transform name): Pipeline step has empty transform name
- Case 5 (case sensitivity): Transform name matching is case-sensitive

## Status
- [x] Write scenario document
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
