"""
Copyright (c) 2025, Differential Robotics
All rights reserved.

SPDX-License-Identifier: BSD-3-Clause

Inference Logger Module

Centralized logging for neural inference:
1. Raw sensor data before feature transformation
2. Output results (actions and control commands)
"""

from __future__ import annotations

import numpy as np
from rclpy.impl.rcutils_logger import RcutilsLogger


class InferenceLogger:
  """
  Centralized logger for neural inference data.

  Logs:
  - Raw sensor data (before feature transformation)
  - Output results (raw actions, processed control commands)
  """

  def __init__(
    self,
    logger: RcutilsLogger,
    log_interval: int = 100,
    enable_raw_input: bool = True,
    enable_output: bool = True,
  ):
    """
    Initialize the inference logger.

    Args:
        logger: ROS2 logger instance
        log_interval: Log every N steps (default 100)
        enable_raw_input: Whether to log raw input data
        enable_output: Whether to log output results
    """
    self._logger = logger
    self._log_interval = log_interval
    self._enable_raw_input = enable_raw_input
    self._enable_output = enable_output
    self._step_count = 0

  def log_raw_input(
    self,
    position_ned: np.ndarray,
    velocity_ned: np.ndarray,
    quat: np.ndarray,
    ang_vel_frd: np.ndarray,
    target_pos_ned: np.ndarray,
    last_action: np.ndarray,
  ) -> None:
    """
    Log raw sensor data before feature transformation.

    Args:
        position_ned: Position in NED frame [N, E, D] meters
        velocity_ned: Velocity in NED frame [N, E, D] m/s
        quat: Orientation quaternion [w, x, y, z]
        ang_vel_frd: Angular velocity in FRD frame [roll, pitch, yaw] rad/s
        target_pos_ned: Target position in NED frame [N, E, D] meters
        last_action: Last action vector [thrust, roll_rate, pitch_rate, yaw_rate]
    """
    if not self._enable_raw_input:
      return

    self._step_count += 1
    if self._step_count % self._log_interval != 0:
      return

    self._logger.info("=" * 60)
    self._logger.info(f"[RAW INPUT] Step {self._step_count}")
    self._logger.info("-" * 40)
    self._logger.info(f"  position_ned:    [{position_ned[0]:+.3f}, {position_ned[1]:+.3f}, {position_ned[2]:+.3f}] m")
    self._logger.info(
      f"  velocity_ned:    [{velocity_ned[0]:+.3f}, {velocity_ned[1]:+.3f}, {velocity_ned[2]:+.3f}] m/s"
    )
    self._logger.info(f"  quat (wxyz):     [{quat[0]:+.4f}, {quat[1]:+.4f}, {quat[2]:+.4f}, {quat[3]:+.4f}]")
    self._logger.info(f"  ang_vel_frd:     [{ang_vel_frd[0]:+.4f}, {ang_vel_frd[1]:+.4f}, {ang_vel_frd[2]:+.4f}] rad/s")
    self._logger.info(
      f"  target_pos_ned:  [{target_pos_ned[0]:+.3f}, {target_pos_ned[1]:+.3f}, {target_pos_ned[2]:+.3f}] m"
    )
    self._logger.info(
      f"  last_action:     [{last_action[0]:+.4f}, {last_action[1]:+.4f}, {last_action[2]:+.4f}, {last_action[3]:+.4f}]"
    )
    self._logger.info("=" * 60)

  def log_output(
    self,
    raw_action: np.ndarray,
    thrust_acc: float,
    rate_frd: np.ndarray,
  ) -> None:
    """
    Log output results after inference.

    Args:
        raw_action: Raw action from neural network [thrust, roll_rate, pitch_rate, yaw_rate]
        thrust_acc: Processed thrust acceleration in m/s^2
        rate_frd: Processed angular rates in FRD frame [roll, pitch, yaw] rad/s
    """
    if not self._enable_output:
      return

    if self._step_count % self._log_interval != 0:
      return

    self._logger.info("-" * 40)
    self._logger.info(f"[OUTPUT] Step {self._step_count}")
    self._logger.info(
      f"  raw_action:      [{raw_action[0]:+.4f}, {raw_action[1]:+.4f}, {raw_action[2]:+.4f}, {raw_action[3]:+.4f}]"
    )
    self._logger.info(f"  thrust_acc:      {thrust_acc:+.3f} m/s^2")
    self._logger.info(f"  rate_frd:        [{rate_frd[0]:+.4f}, {rate_frd[1]:+.4f}, {rate_frd[2]:+.4f}] rad/s")
    self._logger.info("=" * 60)

  def set_log_interval(self, interval: int) -> None:
    """Set logging interval."""
    self._log_interval = max(1, interval)

  def enable_raw_input(self, enable: bool) -> None:
    """Enable/disable raw input logging."""
    self._enable_raw_input = enable

  def enable_output(self, enable: bool) -> None:
    """Enable/disable output logging."""
    self._enable_output = enable

  def reset(self) -> None:
    """Reset step counter."""
    self._step_count = 0
