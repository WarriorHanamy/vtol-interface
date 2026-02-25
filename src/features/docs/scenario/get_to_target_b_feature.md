# Scenario: get_to_target_b Feature
- Given: Vehicle odometry and target data are available
- When: get_to_target_b() is called
- Then: Returns target error vector in FLU body frame with dimension 3

## Test Steps

- Case 1 (happy path): Returns correct error vector for known position and target
- Case 2 (edge case): Returns None when vehicle_odom data is missing
- Case 3 (edge case): Returns None when target data is missing
- Case 4 (edge case): Output vector has dimension 3 matching metadata

## Status
- [x] Write scenario document
- [ ] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
