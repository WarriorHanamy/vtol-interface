# Scenario: Feature Registry API
- Given: A loaded feature registry
- When: Users interact with the FeatureRegistry API
- Then: API methods provide access to callable pipelines and feature metadata

## Test Steps

- Case 1 (happy path): Get callable pipeline for a feature by name
- Case 2 (list features): List all registered feature names
- Case 3 (list dependencies): List required transforms and input keys for a feature
- Case 4 (feature not found): Raise KeyError when requesting non-existent feature
- Case 5 (get metadata): Retrieve feature metadata (entrypoint, description, pipeline steps)
- Case 6 (load from file): Load registry from YAML file path

## Status
- [x] Write scenario document
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
