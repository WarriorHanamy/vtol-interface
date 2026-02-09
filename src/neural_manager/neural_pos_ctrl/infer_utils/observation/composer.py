"""Config-driven observation composer.

The ObservationComposer orchestrates the feature extraction pipeline
based on a declarative schema configuration.
"""

import numpy as np
from typing import List, Dict, Any

from .robot_state import RobotState
from .registry import ObservationRegistry
from .schema import ObservationSchema, FeatureConfig


class ObservationComposer:
    """Config-driven observation composer.

    Executes feature extraction pipeline based on declarative schema.
    Supports scaling and clipping of individual features.

    Example:
        config = [
            {"name": "body_velocity", "scale": 1.0},
            {"name": "gravity_projection"},
            {"name": "target_error", "scale": 1.0, "clip": 5.0}
        ]
        composer = ObservationComposer(config)
        obs = composer.compute(state)
    """

    def __init__(self, config: List[Dict[str, Any]]):
        """Initialize the composer with a configuration.

        Args:
            config: List of feature configs, e.g.:
                [
                    {"name": "body_velocity", "scale": 1.0},
                    {"name": "gravity_projection"},
                    {"name": "target_error", "scale": 1.0, "clip": 5.0}
                ]

        Raises:
            ValueError: If a feature name is not registered
        """
        self.pipeline: List[Dict[str, Any]] = []

        for item in config:
            name = item["name"]
            func = ObservationRegistry.get(name)

            self.pipeline.append({
                "name": name,
                "func": func,
                "scale": item.get("scale", 1.0),
                "clip": item.get("clip", None),
            })

    @classmethod
    def from_schema(cls, schema: ObservationSchema) -> "ObservationComposer":
        """Create composer from ObservationSchema.

        Args:
            schema: ObservationSchema instance

        Returns:
            ObservationComposer instance
        """
        return cls(schema.to_dict_list())

    def compute(self, state: RobotState) -> np.ndarray:
        """Compute full observation vector from RobotState.

        Args:
            state: RobotState instance

        Returns:
            Concatenated observation vector as float32 array
        """
        observations = []

        for node in self.pipeline:
            # Compute raw feature
            val = node["func"](state)

            # Apply scaling
            if node["scale"] != 1.0:
                val = val * node["scale"]

            # Apply clipping
            if node["clip"] is not None:
                clip = node["clip"]
                if isinstance(clip, (list, tuple)):
                    val = np.clip(val, clip[0], clip[1])
                else:
                    val = np.clip(val, -clip, clip)

            observations.append(val)

        return np.concatenate(observations, dtype=np.float32)

    def get_obs_dim(self, state: RobotState) -> int:
        """Compute total observation dimension.

        Args:
            state: Sample RobotState for dimension computation

        Returns:
            Total dimension of the observation vector
        """
        dim = 0
        for node in self.pipeline:
            dim += len(node["func"](state))
        return dim

    def get_feature_names(self) -> List[str]:
        """Get list of feature names in the pipeline.

        Returns:
            List of feature names in order
        """
        return [node["name"] for node in self.pipeline]

    def get_info(self) -> Dict[str, Any]:
        """Get information about the observation pipeline.

        Returns:
            Dict with feature names and their dimensions
        """
        # Create a dummy state for dimension calculation
        dummy_state = RobotState(
            timestamp=0.0,
            timestamp_sample=0.0,
            position_ned=np.zeros(3, dtype=np.float32),
            velocity_ned=np.zeros(3, dtype=np.float32),
            orientation_quat=np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32),
            angular_velocity_body=np.zeros(3, dtype=np.float32),
            target_position_ned=np.zeros(3, dtype=np.float32),
            target_yaw=0.0,
        )

        info = {}
        for node in self.pipeline:
            info[node["name"]] = {
                "dim": len(node["func"](dummy_state)),
                "scale": node["scale"],
                "clip": node["clip"],
            }
        return info
