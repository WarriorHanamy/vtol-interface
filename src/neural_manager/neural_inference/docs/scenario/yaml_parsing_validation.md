# Scenario: YAML Parsing and Validation
- Given: A feature_registry.yaml file with valid or invalid structure
- When: The loader attempts to parse and validate the file
- Then: The loader correctly parses valid YAML or raises explicit errors for malformed YAML

## Test Steps

- Case 1 (happy path): Parse a valid feature_registry.yaml file with all required fields
- Case 2 (missing required field): Parse YAML missing registry_version field
- Case 3 (invalid type): Parse YAML with registry_version as string instead of integer
- Case 4 (malformed YAML): Parse YAML with syntax errors (invalid indentation, missing colons)
- Case 5 (empty features list): Parse YAML with empty features list

## Status
- [x] Write scenario document
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
