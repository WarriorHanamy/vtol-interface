# Scenario: get_last_action Feature
- Given: Action has been buffered via update_last_action()
- When: get_last_action() is called
- Then: Returns previously buffered action with dimension 4

## Test Steps

- Case 1 (happy path): Returns previously buffered action with dimension 4
- Case 2 (edge case): Returns None when no action has been buffered
- Case 3 (edge case): Action vector has correct format [thrust, roll_rate, pitch_rate, yaw_rate]
- Case 4 (edge case): Action is returned as numpy array with dtype float32

## Status
- [x] Write scenario document
- [ ] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
