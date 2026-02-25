# Scenario: Sensor Update Methods
- Given: VtolFeatureProvider instance exists
- When: Sensor data is received via update methods
- Then: Internal sensor data buffers are updated correctly

## Test Steps

- Case 1 (happy path): update_vehicle_odom() stores position, velocity, quaternion, angular velocity
- Case 2 (happy path): update_imu() stores IMU data
- Case 3 (happy path): update_target() stores target position in NED frame
- Case 4 (happy path): update_last_action() buffers action vector

## Status
- [x] Write scenario document
- [ ] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
