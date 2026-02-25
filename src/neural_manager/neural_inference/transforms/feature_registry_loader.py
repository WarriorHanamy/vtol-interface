"""
Copyright (c) 2025, Differential Robotics
All rights reserved.

SPDX-License-Identifier: BSD-3-Clause

Feature Registry Loader Module

This module provides a loader system for feature_registry.yaml files that manages
transform registration, dynamic imports, and pipeline composition.

Main features:
1. Dataclasses for FeatureSpecPipeline and TransformStep
2. YAML parsing and validation
3. Transform validation against registry
4. Pipeline composition and execution
5. FeatureRegistry API for fetching callable pipelines
6. Dimension validation
"""

from __future__ import annotations

import importlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

import numpy as np
import yaml

from .transform_registry import (
    get_transform,
    has_transform,
    list_transforms,
)


# =============================================================================
# Custom Exceptions
# =============================================================================


class MalformedYAMLError(Exception):
    """Raised when YAML file has syntax errors."""

    pass


class InvalidRegistryError(Exception):
    """Raised when feature registry has invalid structure or content."""

    pass


class DimensionMismatchError(Exception):
    """Raised when pipeline output dimension does not match expected dimension."""

    pass


class ImportValidationError(Exception):
    """Raised when entrypoint import validation fails."""

    pass


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class TransformStep:
    """
    Represents a single transform step in a pipeline.

    Attributes:
        transform: Name of the registered transform.
        inputs: List of RobotState keys consumed as positional arguments.
        params: Dictionary of keyword parameters passed to the transform.
        runtime_context: Dictionary of runtime-only context fields.
    """

    transform: str
    inputs: Optional[List[str]] = None
    params: Optional[Dict[str, Any]] = None
    runtime_context: Optional[Dict[str, str]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TransformStep:
        """
        Create TransformStep from dictionary.

        Args:
            data: Dictionary containing transform step data.

        Returns:
            TransformStep instance.

        Raises:
            InvalidRegistryError: If required fields are missing.
        """
        if "transform" not in data:
            raise InvalidRegistryError(
                "Transform step missing required 'transform' field"
            )

        transform_name = data["transform"]
        if not transform_name:
            raise InvalidRegistryError("Transform name cannot be empty")

        return cls(
            transform=transform_name,
            inputs=data.get("inputs"),
            params=data.get("params"),
            runtime_context=data.get("runtime_context"),
        )


@dataclass
class FeatureSpecPipeline:
    """
    Represents a feature specification with its pipeline.

    Attributes:
        name: Feature name (must match schema).
        entrypoint: Dotted Python import path to feature function module.
        description: Human-readable description of the feature.
        pipeline: List of TransformStep objects.
    """

    name: str
    entrypoint: Optional[str]
    description: Optional[str]
    pipeline: List[TransformStep] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> FeatureSpecPipeline:
        """
        Create FeatureSpecPipeline from dictionary.

        Args:
            data: Dictionary containing feature specification data.

        Returns:
            FeatureSpecPipeline instance.

        Raises:
            InvalidRegistryError: If required fields are missing or invalid.
        """
        if "name" not in data:
            raise InvalidRegistryError("Feature missing required 'name' field")

        name = data["name"]
        if not name:
            raise InvalidRegistryError("Feature name cannot be empty")

        pipeline_steps = []
        if "pipeline" in data and data["pipeline"]:
            for step_data in data["pipeline"]:
                pipeline_steps.append(TransformStep.from_dict(step_data))

        return cls(
            name=name,
            entrypoint=data.get("entrypoint"),
            description=data.get("description"),
            pipeline=pipeline_steps,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "entrypoint": self.entrypoint,
            "description": self.description,
            "pipeline": [
                {
                    "transform": step.transform,
                    "inputs": step.inputs,
                    "params": step.params,
                    "runtime_context": step.runtime_context,
                }
                for step in self.pipeline
            ],
        }


# =============================================================================
# Feature Registry Class
# =============================================================================


class FeatureRegistry:
    """
    Registry for feature specifications with callable pipelines.

    Provides methods to load registry from YAML, fetch callable pipelines,
    and list dependencies.
    """

    def __init__(self, version: int, features: List[FeatureSpecPipeline]):
        """
        Initialize FeatureRegistry.

        Args:
            version: Registry version for compatibility checks.
            features: List of feature specifications.
        """
        self.version = version
        self._features: Dict[str, FeatureSpecPipeline] = {f.name: f for f in features}

    @classmethod
    def load_from_file(cls, file_path: Union[str, Path]) -> FeatureRegistry:
        """
        Load feature registry from YAML file.

        Args:
            file_path: Path to feature_registry.yaml file.

        Returns:
            FeatureRegistry instance.

        Raises:
            FileNotFoundError: If file does not exist.
            MalformedYAMLError: If YAML has syntax errors.
            InvalidRegistryError: If registry structure is invalid.
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Feature registry file not found: {file_path}")

        try:
            with open(file_path, "r") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise MalformedYAMLError(f"Failed to parse YAML: {e}") from e

        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> FeatureRegistry:
        """
        Create FeatureRegistry from dictionary.

        Args:
            data: Dictionary containing registry data.

        Returns:
            FeatureRegistry instance.

        Raises:
            InvalidRegistryError: If registry structure is invalid.
        """
        version = cls._validate_registry_version(data)
        features = cls._parse_features(data.get("features", []))
        cls._validate_transforms(features)

        return cls(version=version, features=features)

    @staticmethod
    def _validate_registry_version(data: Dict[str, Any]) -> int:
        """Validate and extract registry version from data."""
        if "registry_version" not in data:
            raise InvalidRegistryError("Missing required field 'registry_version'")

        version = data["registry_version"]
        if not isinstance(version, int):
            raise InvalidRegistryError(
                f"registry_version must be integer, got {type(version).__name__}"
            )

        return version

    @staticmethod
    def _parse_features(
        features_data: List[Dict[str, Any]],
    ) -> List[FeatureSpecPipeline]:
        """Parse feature specifications from data."""
        if not isinstance(features_data, list):
            raise InvalidRegistryError(
                f"'features' must be a list, got {type(features_data).__name__}"
            )

        features = []
        for feature_data in features_data:
            feature = FeatureSpecPipeline.from_dict(feature_data)
            features.append(feature)

        return features

    @staticmethod
    def _validate_transforms(features: List[FeatureSpecPipeline]) -> None:
        """
        Validate that all transform names exist in transform registry.

        Args:
            features: List of feature specifications.

        Raises:
            InvalidRegistryError: If any transform is not registered.
        """
        available = list_transforms()

        for feature in features:
            for step in feature.pipeline:
                transform_name = step.transform
                if not has_transform(transform_name):
                    raise InvalidRegistryError(
                        f"Transform '{transform_name}' not found in registry. "
                        f"Available transforms: {available}"
                    )

    @property
    def features(self) -> List[FeatureSpecPipeline]:
        """Get list of all features."""
        return list(self._features.values())

    def list_features(self) -> List[str]:
        """
        List all registered feature names.

        Returns:
            Sorted list of feature names.
        """
        return sorted(self._features.keys())

    def get_pipeline(self, feature_name: str) -> Callable[[Dict[str, Any]], Any]:
        """
        Get a callable pipeline for a feature.

        The pipeline accepts a context dict containing robot state and runtime context,
        and returns the output as a numpy array.

        Args:
            feature_name: Name of the feature.

        Returns:
            Callable pipeline function.

        Raises:
            KeyError: If feature name is not found.
        """
        if feature_name not in self._features:
            raise KeyError(f"Feature '{feature_name}' not found in registry")

        feature = self._features[feature_name]

        def pipeline(context: Dict[str, Any]) -> Any:
            """Execute the pipeline steps sequentially."""
            result = None

            for i, step in enumerate(feature.pipeline):
                transform = get_transform(step.transform)
                args, kwargs = self._build_step_arguments(step, i, result, context)
                result = transform(*args, **kwargs)

            # Ensure result is numpy array
            if not isinstance(result, np.ndarray):
                result = np.array(result)

            return result

        return pipeline

    def _build_step_arguments(
        self,
        step: TransformStep,
        step_index: int,
        previous_result: Any,
        context: Dict[str, Any],
    ) -> tuple[List[Any], Dict[str, Any]]:
        """
        Build arguments for a transform step.

        Args:
            step: The transform step.
            step_index: Index of the step in the pipeline.
            previous_result: Output from previous step (None for first step).
            context: Runtime context dict.

        Returns:
            Tuple of (args, kwargs) for the transform.
        """
        args: List[Any] = []
        kwargs: Dict[str, Any] = {}

        # First step: use inputs from context
        if step_index == 0 and step.inputs:
            args = self._resolve_inputs(step.inputs, context)
        elif step_index > 0:
            # Subsequent steps: use output from previous step
            args.append(previous_result)

        # Add static params
        if step.params:
            kwargs.update(step.params)

        # Add runtime context
        if step.runtime_context:
            self._add_runtime_context(step.runtime_context, context, kwargs)

        return args, kwargs

    @staticmethod
    def _resolve_inputs(input_keys: List[str], context: Dict[str, Any]) -> List[Any]:
        """
        Resolve input keys from context.

        Supports nested keys (e.g., "robot_state.temperature").

        Args:
            input_keys: List of input key strings.
            context: Context dict to resolve from.

        Returns:
            List of resolved values.
        """
        values = []
        for input_key in input_keys:
            value = context
            for key_part in input_key.split("."):
                if isinstance(value, dict):
                    value = value.get(key_part)
                else:
                    value = None
                    break
            values.append(value)
        return values

    @staticmethod
    def _add_runtime_context(
        runtime_context: Dict[str, str],
        context: Dict[str, Any],
        kwargs: Dict[str, Any],
    ) -> None:
        """
        Add runtime context to kwargs.

        Args:
            runtime_context: Dict mapping param names to context keys.
            context: Runtime context dict.
            kwargs: Keyword arguments dict to populate.
        """
        for param_name, context_key in runtime_context.items():
            kwargs[param_name] = context.get(context_key)

    def get_dependencies(self, feature_name: str) -> Dict[str, Any]:
        """
        List dependencies (required transforms, input keys) for a feature.

        Args:
            feature_name: Name of the feature.

        Returns:
            Dictionary with 'transforms' and 'input_keys' keys.

        Raises:
            KeyError: If feature name is not found.
        """
        if feature_name not in self._features:
            raise KeyError(f"Feature '{feature_name}' not found in registry")

        feature = self._features[feature_name]

        transforms = [step.transform for step in feature.pipeline]
        input_keys = []

        for step in feature.pipeline:
            if step.inputs:
                input_keys.extend(step.inputs)
            if step.runtime_context:
                input_keys.extend(step.runtime_context.values())

        return {"transforms": transforms, "input_keys": list(set(input_keys))}

    def get_feature_metadata(self, feature_name: str) -> Dict[str, Any]:
        """
        Retrieve feature metadata.

        Args:
            feature_name: Name of the feature.

        Returns:
            Dictionary with feature metadata.

        Raises:
            KeyError: If feature name is not found.
        """
        if feature_name not in self._features:
            raise KeyError(f"Feature '{feature_name}' not found in registry")

        feature = self._features[feature_name]
        return feature.to_dict()

    def validate_dimensions(
        self,
        expected_dimensions: Dict[str, int],
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Validate that pipeline output dimensions match expected dimensions.

        If context is None, dimension validation is skipped (not implemented without execution).

        Args:
            expected_dimensions: Dictionary mapping feature names to expected dimensions.
            context: Optional context dict for executing pipelines to determine actual dimensions.

        Raises:
            DimensionMismatchError: If any dimension does not match.
            KeyError: If feature name not found.
        """
        if context is None:
            # Cannot validate dimensions without context - skip validation
            # In real usage, dimensions should be validated with a sample context
            return

        for feature_name, expected_dim in expected_dimensions.items():
            if feature_name not in self._features:
                raise KeyError(f"Feature '{feature_name}' not found in registry")

            pipeline = self.get_pipeline(feature_name)
            result = pipeline(context)

            if isinstance(result, np.ndarray):
                actual_dim = result.size
            else:
                actual_dim = 1

            if actual_dim != expected_dim:
                raise DimensionMismatchError(
                    f"Feature '{feature_name}': expected dimension {expected_dim}, "
                    f"but pipeline output has dimension {actual_dim}"
                )
