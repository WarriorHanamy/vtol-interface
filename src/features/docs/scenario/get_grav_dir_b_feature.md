# Scenario: get_grav_dir_b Feature
- Given: Vehicle odometry with orientation quaternion is available
- When: get_grav_dir_b() is called
- Then: Returns normalized gravity direction vector in FLU body frame with dimension 3

## Test Steps

- Case 1 (happy path): Returns normalized gravity direction vector with dimension 3
- Case 2 (edge case): Returns None when vehicle_odom data is missing
- Case 3 (edge case): Gravity vector is normalized (norm = 1.0)
- Case 4 (edge case): Gravity vector points in correct direction in body frame

## Status
- [x] Write scenario document
- [ ] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
