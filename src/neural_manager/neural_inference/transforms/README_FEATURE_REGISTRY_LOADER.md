# Feature Registry Loader

This module provides a loader for `feature_registry.yaml` files that manages transform registration, dynamic imports, and pipeline composition.

## Features

- **YAML Parsing**: Load and validate feature registry YAML files
- **Transform Validation**: Verify that all referenced transforms exist in the transform registry
- **Pipeline Composition**: Build callable pipelines that execute transforms sequentially
- **Dimension Validation**: Validate that pipeline outputs match expected dimensions
- **Feature Registry API**: Query features, get callable pipelines, and list dependencies

## Quick Start

```python
from transforms.feature_registry_loader import FeatureRegistry
import numpy as np

# Load feature registry from file
registry = FeatureRegistry.load_from_file("feature_registry.yaml")

# List all features
features = registry.list_features()
print(f"Available features: {features}")

# Get a callable pipeline for a feature
pipeline = registry.get_pipeline("target_error")

# Execute pipeline with context dict
context = {
    "position_ned": np.array([0.0, 0.0, -3.0]),
    "target_position_ned": np.array([1.0, 1.0, -5.0]),
    "orientation_quat": np.array([0.9, 0.1, 0.2, 0.3])
}
result = pipeline(context)
print(f"Feature output: {result}")

# Validate dimensions
expected_dims = {"target_error": 3, "current_yaw_encoding": 2}
registry.validate_dimensions(expected_dims, context)

# Get feature metadata
metadata = registry.get_feature_metadata("target_error")
print(f"Metadata: {metadata}")

# Get dependencies
deps = registry.get_dependencies("target_error")
print(f"Dependencies: {deps}")
```

## Registry File Format

```yaml
registry_version: 1

features:
  - name: feature_name
    entrypoint: module.path.to.feature
    description: "Human-readable description"
    pipeline:
      - transform: transform_name
        inputs: [input_key1, input_key2]
        params:
          param_name: value
        runtime_context:
          param_name: context_key
```

## Error Handling

The loader raises explicit errors for various failure modes:

- `FileNotFoundError`: Registry file not found
- `MalformedYAMLError`: YAML syntax errors
- `InvalidRegistryError`: Invalid registry structure, missing fields, unknown transforms
- `DimensionMismatchError`: Output dimension does not match expected dimension
- `KeyError`: Feature not found in registry

## Pipeline Execution Model

Pipelines execute transforms sequentially. Each transform step:

1. **First step**: Extracts inputs from context dict using `inputs` keys
2. **Subsequent steps**: Receives output from previous step as first argument
3. **Parameters**: Adds `params` dict as keyword arguments
4. **Runtime context**: Adds values from context dict using `runtime_context` mapping

Example pipeline execution:

```yaml
pipeline:
  - transform: subtract
    inputs: [position_ned, target_position_ned]
  - transform: rotate_to_body
    params:
      frame: flu
```

Executes as:

```python
temp = subtract(context["position_ned"], context["target_position_ned"])
result = rotate_to_body(temp, frame="flu")
```

## Testing

Run tests with pytest:

```bash
pytest tests/scenario/ -v
```

All 38 tests pass successfully.

## API Reference

### FeatureRegistry

#### `load_from_file(file_path)`
Load feature registry from YAML file.

#### `from_dict(data)`
Create FeatureRegistry from dictionary.

#### `list_features()`
List all registered feature names.

#### `get_pipeline(feature_name)`
Get a callable pipeline for a feature.

#### `get_dependencies(feature_name)`
List dependencies (transforms, input keys) for a feature.

#### `get_feature_metadata(feature_name)`
Retrieve feature metadata.

#### `validate_dimensions(expected_dimensions, context)`
Validate pipeline output dimensions.

### Data Classes

#### `TransformStep`
Represents a single transform step with:
- `transform`: Transform name
- `inputs`: List of input keys
- `params`: Dict of parameters
- `runtime_context`: Dict of runtime context mappings

#### `FeatureSpecPipeline`
Represents a feature specification with:
- `name`: Feature name
- `entrypoint`: Dotted import path
- `description`: Human-readable description
- `pipeline`: List of TransformStep objects

## Example Registry

See `examples/feature_registry.yaml` for a complete example registry with multiple features.
