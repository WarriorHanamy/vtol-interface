# Scenario: get_ang_vel_b Feature
- Given: IMU or odometry data with angular velocity is available
- When: get_ang_vel_b() is called
- Then: Returns FRD->FLU transformed angular velocity with dimension 3

## Test Steps

- Case 1 (happy path): Returns FRD->FLU transformed angular velocity with dimension 3
- Case 2 (edge case): Returns None when IMU data is missing
- Case 3 (edge case): Returns None when odom data is missing
- Case 4 (edge case): FRD->FLU conversion negates Y and Z components correctly

## Status
- [x] Write scenario document
- [ ] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
