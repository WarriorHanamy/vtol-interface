"""RobotState dataclass for decoupling from ROS/PX4 messages."""

from dataclasses import dataclass
import numpy as np
from typing import Optional


@dataclass(frozen=True)
class RobotState:
    """Standardized robot state snapshot, decoupled from ROS/PX4 messages.

    Uses NED world frame and FRD body frame convention (PX4 standard).
    Observation features are computed in FLU (Forward-Left-Up) frame for
    compatibility with neural network training.

    Attributes:
        timestamp: Message timestamp in seconds (converted from PX4 microseconds)
        timestamp_sample: Sample timestamp in seconds
        position_ned: Position in NED frame [x, y, z] in meters
        velocity_ned: Velocity in NED frame [vx, vy, vz] in m/s
        orientation_quat: Orientation as Hamilton quaternion [w, x, y, z]
        angular_velocity_body: Angular velocity in FRD body frame [wx, wy, wz] in rad/s
        target_position_ned: Target position in NED frame [x, y, z] in meters
        target_yaw: Target yaw angle in radians
        position_variance: Optional position error variance
        orientation_variance: Optional orientation error variance
        quality: Optional quality metric from PX4
    """
    # Core state
    timestamp: float
    timestamp_sample: float

    # Position and velocity (NED frame)
    position_ned: np.ndarray      # [x, y, z] in meters
    velocity_ned: np.ndarray      # [vx, vy, vz] in m/s

    # Orientation (Hamilton quaternion [w, x, y, z])
    orientation_quat: np.ndarray  # [w, x, y, z]

    # Angular velocity (body frame FRD)
    angular_velocity_body: np.ndarray  # [wx, wy, wz] in rad/s

    # Target/goal state
    target_position_ned: np.ndarray
    target_yaw: float

    # Optional metadata
    position_variance: Optional[np.ndarray] = None
    orientation_variance: Optional[np.ndarray] = None
    quality: Optional[int] = None

    @property
    def rotation_matrix(self) -> np.ndarray:
        """Compute rotation matrix from quaternion (lazy evaluation).

        Returns:
            3x3 rotation matrix from body to NED frame
        """
        from ..math_utils import quaternion_to_rotation_matrix
        return quaternion_to_rotation_matrix(self.orientation_quat)

    @property
    def yaw(self) -> float:
        """Extract current yaw angle from quaternion.

        Returns:
            Yaw angle in radians
        """
        from ..math_utils import quaternion_to_yaw
        return quaternion_to_yaw(self.orientation_quat)

    def __post_init__(self):
        """Validate array shapes after initialization."""
        # Validate position_ned shape
        if isinstance(self.position_ned, np.ndarray) and self.position_ned.shape != (3,):
            raise ValueError(f"position_ned must be shape (3,), got {self.position_ned.shape}")

        # Validate velocity_ned shape
        if isinstance(self.velocity_ned, np.ndarray) and self.velocity_ned.shape != (3,):
            raise ValueError(f"velocity_ned must be shape (3,), got {self.velocity_ned.shape}")

        # Validate orientation_quat shape
        if isinstance(self.orientation_quat, np.ndarray) and self.orientation_quat.shape != (4,):
            raise ValueError(f"orientation_quat must be shape (4,), got {self.orientation_quat.shape}")

        # Validate angular_velocity_body shape
        if isinstance(self.angular_velocity_body, np.ndarray) and self.angular_velocity_body.shape != (3,):
            raise ValueError(f"angular_velocity_body must be shape (3,), got {self.angular_velocity_body.shape}")

        # Validate target_position_ned shape
        if isinstance(self.target_position_ned, np.ndarray) and self.target_position_ned.shape != (3,):
            raise ValueError(f"target_position_ned must be shape (3,), got {self.target_position_ned.shape}")
