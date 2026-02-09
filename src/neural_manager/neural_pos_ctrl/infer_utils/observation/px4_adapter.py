"""PX4 message to RobotState adapter.

The Px4ToRobotStateAdapter converts PX4 ROS messages to the standardized
RobotState dataclass, decoupling the observation processor from ROS/PX4 specifics.
"""

import numpy as np
from typing import Optional

# PX4 message types - these are optional dependencies
try:
    from px4_msgs.msg import VehicleOdometry
    PX4_AVAILABLE = True
except ImportError:
    PX4_AVAILABLE = False
    VehicleOdometry = None

from .robot_state import RobotState


class Px4ToRobotStateAdapter:
    """Converts PX4 VehicleOdometry messages to RobotState.

    This adapter class encapsulates the conversion logic between PX4 ROS messages
    and the standardized RobotState representation.

    Example:
        adapter = Px4ToRobotStateAdapter(
            target_position=np.array([5.0, 5.0, -5.0]),
            target_yaw=np.pi / 2
        )
        state = adapter.from_odometry(px4_odometry_msg)
    """

    def __init__(
        self,
        target_position: np.ndarray,
        target_yaw: float,
    ):
        """Initialize the adapter with target/goal state.

        Args:
            target_position: Target position in NED frame [x, y, z] in meters
            target_yaw: Target yaw angle in radians
        """
        self.target_position = np.asarray(target_position, dtype=np.float32)
        self.target_yaw = float(target_yaw)

        # Validate target_position shape
        if self.target_position.shape != (3,):
            raise ValueError(f"target_position must be shape (3,), got {self.target_position.shape}")

    def set_target(self, target_position: np.ndarray, target_yaw: float) -> None:
        """Update the target state.

        Args:
            target_position: New target position in NED frame [x, y, z] in meters
            target_yaw: New target yaw angle in radians
        """
        self.target_position = np.asarray(target_position, dtype=np.float32)
        self.target_yaw = float(target_yaw)

        if self.target_position.shape != (3,):
            raise ValueError(f"target_position must be shape (3,), got {self.target_position.shape}")

    def from_odometry(self, msg) -> RobotState:
        """Convert VehicleOdometry to RobotState.

        Args:
            msg: PX4 VehicleOdometry message (or duck-typed equivalent with same attributes)

        Returns:
            RobotState instance

        Note:
            This method uses duck-typing and will work with any object that has
            the required attributes (timestamp, position, velocity, q, angular_velocity).
            The actual px4_msgs package is not required.
        """
        return RobotState(
            timestamp=float(msg.timestamp) / 1e6,  # microseconds -> seconds
            timestamp_sample=float(msg.timestamp_sample) / 1e6,
            position_ned=np.array(msg.position, dtype=np.float32),
            velocity_ned=np.array(msg.velocity, dtype=np.float32),
            orientation_quat=np.array(msg.q, dtype=np.float32),
            angular_velocity_body=np.array(msg.angular_velocity, dtype=np.float32),
            target_position_ned=self.target_position,
            target_yaw=self.target_yaw,
            position_variance=self._get_field(msg, "position_variance", default=None),
            orientation_variance=self._get_field(msg, "orientation_variance", default=None),
            quality=self._get_field(msg, "quality", default=None),
        )

    @staticmethod
    def _get_field(msg, field_name: str, default=None):
        """Safely get a field from a message with a default value.

        Args:
            msg: ROS message
            field_name: Name of the field to get
            default: Default value if field doesn't exist

        Returns:
            Field value as numpy array (for array fields), the value itself (for scalars), or default
        """
        if hasattr(msg, field_name):
            val = getattr(msg, field_name)
            if val is not None:
                # Check if it's a sequence/list (has len) but not a string
                if hasattr(val, "__len__") and not isinstance(val, (str, bytes)):
                    if len(val) > 0:
                        return np.array(val, dtype=np.float32)
                else:
                    # Scalar value (like quality)
                    return val
        return default

    def from_dict(self, data: dict) -> RobotState:
        """Create RobotState from a dictionary (useful for testing/simulation).

        Args:
            data: Dictionary with keys matching VehicleOdometry fields

        Returns:
            RobotState instance
        """
        return RobotState(
            timestamp=float(data.get("timestamp", 0)) / 1e6,
            timestamp_sample=float(data.get("timestamp_sample", 0)) / 1e6,
            position_ned=np.array(data.get("position", [0, 0, 0]), dtype=np.float32),
            velocity_ned=np.array(data.get("velocity", [0, 0, 0]), dtype=np.float32),
            orientation_quat=np.array(data.get("q", [1, 0, 0, 0]), dtype=np.float32),
            angular_velocity_body=np.array(data.get("angular_velocity", [0, 0, 0]), dtype=np.float32),
            target_position_ned=self.target_position,
            target_yaw=self.target_yaw,
        )
