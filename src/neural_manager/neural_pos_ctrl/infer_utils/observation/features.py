"""Atomic feature extraction functions.

Each function is a pure function that takes a RobotState and returns
a numpy array feature vector. These functions are stateless and
have no side effects.
"""

import numpy as np
from typing import Callable

from .robot_state import RobotState

# Feature function type alias
FeatureFn = Callable[[RobotState], np.ndarray]


def get_body_linear_velocity(state: RobotState) -> np.ndarray:
    """Body frame linear velocity in FLU coordinates.

    Transforms velocity from NED world frame to FLU body frame.

    Args:
        state: RobotState containing velocity and orientation

    Returns:
        np.ndarray: [vx, vy, vz] velocity in FLU body frame (m/s)
    """
    from ..math_utils import frd_flu_rotate, quat_pas_rot

    # NED -> FRD body frame
    vel_frd = quat_pas_rot(state.orientation_quat, state.velocity_ned)
    # FRD -> FLU
    return frd_flu_rotate(vel_frd).astype(np.float32)


def get_gravity_projection(state: RobotState) -> np.ndarray:
    """Gravity direction vector in body frame (FLU).

    Computes the projection of the gravity vector (pointing down in NED)
    onto the body frame.

    Args:
        state: RobotState containing orientation

    Returns:
        np.ndarray: [gx, gy, gz] gravity direction in FLU frame
    """
    from ..math_utils import frd_flu_rotate, quat_pas_rot

    # Gravity vector in NED: [0, 0, 1] (Z-down)
    gravity_ned = np.array([0.0, 0.0, 1.0], dtype=np.float32)

    # NED -> FRD body frame
    gravity_frd = quat_pas_rot(state.orientation_quat, gravity_ned)
    # FRD -> FLU
    return frd_flu_rotate(gravity_frd).astype(np.float32)


def get_angular_velocity(state: RobotState) -> np.ndarray:
    """Angular velocity in FLU body frame.

    Converts angular velocity from FRD to FLU frame.

    Args:
        state: RobotState containing angular velocity

    Returns:
        np.ndarray: [wx, wy, wz] angular velocity in FLU frame (rad/s)
    """
    from ..math_utils import frd_flu_rotate

    # FRD -> FLU (Y and Z components flip sign)
    return frd_flu_rotate(state.angular_velocity_body).astype(np.float32)


def get_target_position_error(state: RobotState) -> np.ndarray:
    """Target position error in body frame (FLU).

    Computes the vector from current position to target position,
    expressed in the FLU body frame.

    Args:
        state: RobotState containing position and target

    Returns:
        np.ndarray: [dx, dy, dz] position error in FLU frame (m)
    """
    from ..math_utils import frd_flu_rotate, quat_pas_rot

    # Position error in NED
    error_ned = state.target_position_ned - state.position_ned

    # NED -> FRD body frame
    error_frd = quat_pas_rot(state.orientation_quat, error_ned)
    # FRD -> FLU
    return frd_flu_rotate(error_frd).astype(np.float32)


def get_yaw_encoding(state: RobotState) -> np.ndarray:
    """Current yaw direction as [cos(yaw), sin(yaw)].

    Encodes yaw angle using sine and cosine for continuity.

    Args:
        state: RobotState containing orientation

    Returns:
        np.ndarray: [cos(yaw), sin(yaw)]
    """
    yaw = state.yaw
    return np.array([np.cos(yaw), np.sin(yaw)], dtype=np.float32)


def get_target_yaw_encoding(state: RobotState) -> np.ndarray:
    """Target yaw direction as [cos(target_yaw), sin(target_yaw)].

    Encodes target yaw angle using sine and cosine for continuity.

    Args:
        state: RobotState containing target_yaw

    Returns:
        np.ndarray: [cos(target_yaw), sin(target_yaw)]
    """
    return np.array([np.cos(state.target_yaw), np.sin(state.target_yaw)], dtype=np.float32)
