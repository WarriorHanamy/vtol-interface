# Scenario: Dynamic Import Support
- Given: A feature registry with entrypoint dotted paths
- When: The loader attempts to import transform functions dynamically
- Then: Valid entrypoints import successfully, invalid entrypoints raise ImportError

## Test Steps

- Case 1 (happy path): Import transform from valid dotted path (e.g., transforms.coordinate)
- Case 2 (invalid module): Import transform from non-existent module
- Case 3 (invalid function): Import transform from valid module but non-existent function
- Case 4 (circular import): Handle potential circular import issues gracefully
- Case 5 (helpful error message): ImportError includes the module path that failed

## Status
- [x] Write scenario document
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
