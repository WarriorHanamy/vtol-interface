"""Schema-first observation processor module.

This module provides a modern, config-driven, component-based architecture
for computing observation vectors from robot state, following Isaac Lab/RSL-RL patterns.

Example usage:
    >>> from infer_utils.observation import ObservationComposer, Px4ToRobotStateAdapter
    >>> adapter = Px4ToRobotStateAdapter(target_position, target_yaw)
    >>> composer = ObservationComposer(config)
    >>> state = adapter.from_odometry(px4_msg)
    >>> obs = composer.compute(state)
"""

from .robot_state import RobotState
from .features import (
    get_body_linear_velocity,
    get_gravity_projection,
    get_angular_velocity,
    get_target_position_error,
    get_yaw_encoding,
    get_target_yaw_encoding,
    FeatureFn,
)
from .registry import ObservationRegistry
from .schema import ObservationSchema, FeatureConfig
from .composer import ObservationComposer
from .px4_adapter import Px4ToRobotStateAdapter

__all__ = [
    # Core types
    "RobotState",
    # Feature functions
    "get_body_linear_velocity",
    "get_gravity_projection",
    "get_angular_velocity",
    "get_target_position_error",
    "get_yaw_encoding",
    "get_target_yaw_encoding",
    "FeatureFn",
    # Registry
    "ObservationRegistry",
    # Schema
    "ObservationSchema",
    "FeatureConfig",
    # Composer
    "ObservationComposer",
    # Adapter
    "Px4ToRobotStateAdapter",
]
