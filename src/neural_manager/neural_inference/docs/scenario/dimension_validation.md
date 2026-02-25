# Scenario: Dimension Validation
- Given: A feature registry with pipelines and expected output dimensions
- When: The loader validates output dimensions
- Then: Dimensions are validated and mismatched dimensions raise explicit errors

## Test Steps

- Case 1 (happy path): Pipeline output dimension matches expected dimension
- Case 2 (dimension mismatch): Pipeline output dimension does not match expected dimension
- Case 3 (vector dimension): 3D vector pipeline validates against dim=3
- Case 4 (scalar encoding): Scalar encoding pipeline validates against dim=2 (sin/cos)
- Case 5 (helpful error message): Error message includes expected and actual dimensions

## Status
- [x] Write scenario document
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
