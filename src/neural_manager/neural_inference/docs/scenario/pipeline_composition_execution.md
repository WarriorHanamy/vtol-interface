# Scenario: Pipeline Composition and Execution
- Given: A feature registry with valid transform pipelines
- When: The loader composes callable pipelines from transform steps
- Then: The callable pipeline executes transforms sequentially and returns numpy arrays

## Test Steps

- Case 1 (happy path): Single transform pipeline executes and returns expected output
- Case 2 (multi-step pipeline): Multi-step pipeline passes output from each step to next
- Case 3 (context dict): Pipeline accepts context dict with robot state and runtime context
- Case 4 (input resolution): Pipeline resolves inputs from robot state keys
- Case 5 (runtime context resolution): Pipeline resolves runtime_context keys from context dict

## Status
- [x] Write scenario document
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
