"""Central registry for feature extraction functions.

The ObservationRegistry provides a way to register and retrieve feature
functions by name, enabling configuration-driven observation composition.
"""

from typing import Dict, Callable, List
import numpy as np

from .features import FeatureFn


class ObservationRegistry:
    """Central registry for feature extraction functions.

    Feature functions can be registered and retrieved by name,
    enabling declarative configuration of observation spaces.
    """

    _REGISTRY: Dict[str, FeatureFn] = {}

    @classmethod
    def register(cls, name: str, func: FeatureFn) -> None:
        """Register a new feature function.

        Args:
            name: Unique identifier for the feature
            func: Function that takes RobotState and returns np.ndarray

        Raises:
            ValueError: If a feature with this name already exists
        """
        if name in cls._REGISTRY:
            raise ValueError(f"Feature '{name}' is already registered")
        cls._REGISTRY[name] = func

    @classmethod
    def get(cls, name: str) -> FeatureFn:
        """Get a feature function by name.

        Args:
            name: Name of the registered feature

        Returns:
            Feature function

        Raises:
            ValueError: If feature name is not found
        """
        if name not in cls._REGISTRY:
            available = list(cls._REGISTRY.keys())
            raise ValueError(f"Unknown feature: '{name}'. Available: {available}")
        return cls._REGISTRY[name]

    @classmethod
    def list_features(cls) -> List[str]:
        """List all registered feature names.

        Returns:
            List of feature names
        """
        return list(cls._REGISTRY.keys())

    @classmethod
    def clear(cls) -> None:
        """Clear all registered features (mainly for testing)."""
        cls._REGISTRY.clear()


def _register_defaults() -> None:
    """Register default feature functions."""
    from . import features

    defaults = {
        "body_velocity": features.get_body_linear_velocity,
        "gravity_projection": features.get_gravity_projection,
        "angular_velocity": features.get_angular_velocity,
        "target_error": features.get_target_position_error,
        "yaw_encoding": features.get_yaw_encoding,
        "target_yaw_encoding": features.get_target_yaw_encoding,
    }

    for name, func in defaults.items():
        ObservationRegistry.register(name, func)


# Auto-register default features on import
_register_defaults()
