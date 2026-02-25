# Scenario: VtolFeatureProvider Class Initialization
- Given: observation_metadata.yaml file exists with to_target_b, grav_dir_b, ang_vel_b, last_action features
- When: VtolFeatureProvider is instantiated with metadata path
- Then: Class inherits from FeatureProviderBase and initializes successfully

## Test Steps

- Case 1 (happy path): VtolFeatureProvider initializes correctly with valid metadata path
- Case 2 (edge case): VtolFeatureProvider initializes with metadata containing all required features
- Case 3 (edge case): VtolFeatureProvider inherits all methods from FeatureProviderBase

## Status
- [x] Write scenario document
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
