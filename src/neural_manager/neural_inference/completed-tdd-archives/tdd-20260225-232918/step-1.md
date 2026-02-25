# Step 1 - Understand Intent

## Functional Requirements

### FR-1: YAML Parsing and Validation
The loader must parse feature_registry.yaml files, validating structure and content, and raising explicit errors for malformed YAML.

Description:
- Parse YAML files according to the schema defined in FEATURE_REGISTRY_CONTRACT.md
- Validate required fields (registry_version, features list)
- Validate feature entry fields (name, entrypoint, pipeline)
- Validate pipeline step fields (transform name)
- Raise explicit errors for missing required fields, invalid types, or malformed YAML

### FR-2: Transform Validation
The loader must validate that all transform names referenced in the registry exist in the transform registry.

Description:
- Check each pipeline step's transform name against registered transforms
- Raise KeyError with helpful message listing available transforms when a transform is not found
- Validate that transform registry has been populated with transforms

### FR-3: Pipeline Composition and Execution
The loader must compose callable pipelines from transform steps that execute transforms sequentially.

Description:
- Create dataclasses to represent FeatureSpecPipeline and TransformStep
- Compose a callable function that:
  - Executes pipeline steps in order
  - Passes outputs of each step as input to the next
  - Accepts a context dict containing robot state and runtime context
  - Returns numpy arrays as final output
- Handle input resolution from robot state keys
- Handle runtime context resolution

### FR-4: Feature Registry API
The registry must provide an API to fetch callable pipelines and list dependencies.

Description:
- Expose FeatureRegistry class with methods to:
  - Get a callable pipeline for a feature by name
  - List all registered feature names
  - List dependencies (required transforms, input keys) for a feature
  - Load registry from YAML file path
- Support querying feature metadata (entrypoint, description, pipeline steps)

### FR-5: Dimension Validation
The loader must validate that declared output dimensions match transform outputs.

Description:
- Validate output dimensions against schema expectations
- Raise explicit errors when pipeline output dimension does not match expected dimension
- Support dimension inference from transform outputs (via transform metadata or actual execution)

### FR-6: Dynamic Import Support
The loader must support importing transform functions dynamically from modules.

Description:
- Import callable objects using dotted paths (entrypoint field)
- Handle ImportError with helpful messages
- Support optional import for transforms not in core registry

## Assumptions

- Transform registry (_TRANSFORM_REGISTRY) is populated when transforms module is imported
- Robot state is provided as a dict with keys matching the `inputs` fields in pipeline steps
- Runtime context is provided as a separate dict for runtime-augmented features
- Dimension validation will be done by comparing against a schema (separate system)
- Existing transforms in coordinate.py and encoding.py serve as examples for transform registration
- The loader will be placed in a new module: feature_registry_loader.py in the transforms directory
- Tests will use pytest and follow the existing test structure in tests/transforms/
