"""Schema types for observation configuration."""

from dataclasses import dataclass
from typing import Optional, Union, List


@dataclass
class FeatureConfig:
    """Configuration for a single feature in the observation pipeline.

    Attributes:
        name: Name of the registered feature function
        scale: Scaling factor to apply to the feature output (default: 1.0)
        clip: Clipping value - can be:
            - None: No clipping
            - float: Symmetric clipping [-clip, clip]
            - tuple[float, float]: Asymmetric clipping [min, max]
    """

    name: str
    scale: float = 1.0
    clip: Optional[Union[float, tuple[float, float]]] = None


@dataclass
class ObservationSchema:
    """Schema definition for observation space.

    A complete observation schema consists of a list of feature configurations
    that define how to construct the observation vector from RobotState.

    Example:
        schema = ObservationSchema(features=[
            FeatureConfig(name="body_velocity", scale=1.0),
            FeatureConfig(name="gravity_projection", scale=1.0),
            FeatureConfig(name="target_error", scale=1.0, clip=5.0),
        ])
    """

    features: List[FeatureConfig]

    def to_dict_list(self) -> List[dict]:
        """Convert to list of dictionaries for YAML serialization.

        Returns:
            List of dicts with keys: name, scale, clip
        """
        result = []
        for feat in self.features:
            d = {"name": feat.name, "scale": feat.scale}
            if feat.clip is not None:
                d["clip"] = feat.clip
            result.append(d)
        return result

    @classmethod
    def from_dict_list(cls, config_list: List[dict]) -> "ObservationSchema":
        """Create from list of dictionaries (e.g., from YAML parsing).

        Args:
            config_list: List of dicts with keys: name, scale (optional), clip (optional)

        Returns:
            ObservationSchema instance
        """
        features = []
        for item in config_list:
            features.append(
                FeatureConfig(
                    name=item["name"],
                    scale=item.get("scale", 1.0),
                    clip=item.get("clip", None),
                )
            )
        return cls(features=features)
