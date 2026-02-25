#!/usr/bin/env python3
"""
Copyright (c) 2025, Differential Robotics
All rights reserved.

SPDX-License-Identifier: BSD-3-Clause

ROS Sensor Bridge Module

This module provides a ROS bridge connecting sensor topics to VtolFeatureProvider
sensor updates, enabling real-time neural inference for VTOL vehicle control.
"""

from __future__ import annotations

import time
from typing import Any, Optional, Tuple

import numpy as np

# Import ControlPublisher for publishing control commands
from control.control_publisher import ControlPublisher

# Handle ROS2 imports gracefully
ROS2_AVAILABLE = False
VehicleOdometry = None
SensorImu = None
VehicleGpsPosition = None

try:
    from px4_msgs.msg import VehicleOdometry, SensorImu, VehicleGpsPosition

    ROS2_AVAILABLE = True
except ImportError:
    # px4_msgs not available - will use mock for testing
    pass


# Constants
INFERENCE_RATE_HZ = 50.0
INFERENCE_PERIOD_SEC = 1.0 / INFERENCE_RATE_HZ


class RosSensorBridge:
    """
    ROS sensor bridge connecting topics to VtolFeatureProvider.

    This bridge:
    1. Subscribes to odometry, IMU, and GPS topics
    2. Parses sensor data from ROS messages
    3. Updates VtolFeatureProvider with sensor data
    4. Runs inference at fixed rate (50 Hz)
    5. Publishes control commands to /neural/control

    Attributes:
        _node: ROS2 node for creating publishers/subscribers/timers
        _inference_node: VtolNeuralInferenceNode for running inference
        _feature_provider: VtolFeatureProvider for sensor data buffering
        _control_publisher: ControlPublisher for publishing control commands
        _odometry_subscription: Subscription to VehicleOdometry topic
        _imu_subscription: Subscription to SensorImu topic
        _gps_subscription: Subscription to VehicleGpsPosition topic
        _inference_timer: Timer for running inference loop
        _odom_sub_topic: Odometry topic name
        _imu_sub_topic: IMU topic name
        _gps_sub_topic: GPS topic name
    """

    def __init__(
        self,
        node: Any,
        inference_node: Any,
        feature_provider: Any,
        odom_topic: str = "/fmu/out/vehicle_odometry",
        imu_topic: str = "/fmu/out/sensor_imu",
        gps_topic: str = "/fmu/out/vehicle_gps_position",
    ):
        """
        Initialize the ROS sensor bridge.

        Args:
            node: ROS2 node for creating publishers/subscribers/timers
            inference_node: VtolNeuralInferenceNode for running inference
            feature_provider: VtolFeatureProvider for sensor data buffering
            odom_topic: Odometry topic name (default: /fmu/out/vehicle_odometry)
            imu_topic: IMU topic name (default: /fmu/out/sensor_imu)
            gps_topic: GPS topic name (default: /fmu/out/vehicle_gps_position)
        """
        self._node = node
        self._inference_node = inference_node
        self._feature_provider = feature_provider

        # Topic names
        self._odom_sub_topic = odom_topic
        self._imu_sub_topic = imu_topic
        self._gps_sub_topic = gps_topic

        # Initialize control publisher
        self._control_publisher = ControlPublisher(node=node)
        self._control_publisher.initialize()

        # Subscriptions and timers
        self._odometry_subscription = None
        self._imu_subscription = None
        self._gps_subscription = None
        self._inference_timer = None

        # Create subscriptions and timer
        self._setup_ros_connections()

        self._get_logger().info("RosSensorBridge initialized")

    def _get_logger(self):
        """
        Get logger from ROS node.

        Returns:
            ROS logger instance
        """
        return self._node.get_logger()

    def _setup_ros_connections(self) -> None:
        """
        Create ROS subscriptions and timer.

        Creates subscriptions to odometry, IMU, and GPS topics,
        and creates a timer for running inference at 50 Hz.
        """
        # Create odometry subscription
        self._odometry_subscription = self._node.create_subscription(
            VehicleOdometry if ROS2_AVAILABLE else object,
            self._odom_sub_topic,
            self._odometry_callback,
            10,  # QoS profile depth
        )

        # Create IMU subscription
        self._imu_subscription = self._node.create_subscription(
            SensorImu if ROS2_AVAILABLE else object,
            self._imu_sub_topic,
            self._imu_callback,
            10,
        )

        # Create GPS subscription
        self._gps_subscription = self._node.create_subscription(
            VehicleGpsPosition if ROS2_AVAILABLE else object,
            self._gps_sub_topic,
            self._gps_callback,
            10,
        )

        # Create inference timer (50 Hz = 0.02 second period)
        self._inference_timer = self._node.create_timer(
            INFERENCE_PERIOD_SEC, self._inference_timer_callback
        )

        self._get_logger().info("ROS connections setup complete")
        self._get_logger().info(f"  Odometry: {self._odom_sub_topic}")
        self._get_logger().info(f"  IMU: {self._imu_sub_topic}")
        self._get_logger().info(f"  GPS: {self._gps_sub_topic}")
        self._get_logger().info(f"  Inference rate: {INFERENCE_RATE_HZ} Hz")

    def _odometry_callback(self, msg: Any) -> None:
        """
        Handle incoming odometry messages.

        Extracts position, velocity, orientation, and angular velocity
        from VehicleOdometry message and updates VtolFeatureProvider.

        Args:
            msg: VehicleOdometry message
        """
        try:
            # Parse odometry message
            position, velocity, quat, ang_vel = self._parse_odometry(msg)

            # Update feature provider
            if (
                position is not None
                and velocity is not None
                and quat is not None
                and ang_vel is not None
            ):
                self._feature_provider.update_vehicle_odom(
                    position=position,
                    velocity=velocity,
                    quat=quat,
                    ang_vel=ang_vel,
                )
        except Exception as e:
            self._get_logger().warning(f"Error in odometry callback: {e}")

    def _imu_callback(self, msg: Any) -> None:
        """
        Handle incoming IMU messages.

        Extracts angular velocity and linear acceleration
        from SensorImu message and updates VtolFeatureProvider.

        Args:
            msg: SensorImu message
        """
        try:
            # Parse IMU message
            ang_vel, linear_accel = self._parse_imu(msg)

            # Update feature provider
            if ang_vel is not None:
                self._feature_provider.update_imu(
                    linear_accel=linear_accel, ang_vel=ang_vel
                )
        except Exception as e:
            self._get_logger().warning(f"Error in IMU callback: {e}")

    def _gps_callback(self, msg: Any) -> None:
        """
        Handle incoming GPS messages.

        Extracts GPS position and converts to NED coordinates,
        then updates VtolFeatureProvider.

        Args:
            msg: VehicleGpsPosition message
        """
        try:
            # Parse GPS message
            ned_pos = self._parse_gps(msg)

            # Update feature provider
            if ned_pos is not None:
                self._feature_provider.update_target(target_pos=ned_pos)
        except Exception as e:
            self._get_logger().warning(f"Error in GPS callback: {e}")

    def _inference_timer_callback(self) -> None:
        """
        Timer callback for running inference loop.

        Runs at 50 Hz (0.02 second period) to:
        1. Call VtolNeuralInferenceNode.infer() to get control commands
        2. Publish control commands via ControlPublisher
        """
        try:
            if self._inference_node is None:
                return

            # Run inference
            control_commands = self._inference_node.infer()

            # Publish control commands
            if control_commands is not None:
                self._publish_control_commands(control_commands)
        except Exception as e:
            self._get_logger().warning(f"Error in inference callback: {e}")

    @staticmethod
    def _safe_convert_to_float32(value) -> Optional[np.ndarray]:
        """
        Safely convert a value to float32 numpy array.

        Args:
            value: Value to convert

        Returns:
            float32 numpy array or None if value is None
        """
        if value is None:
            return None
        return np.array(value, dtype=np.float32)

    @staticmethod
    def _parse_odometry(
        msg: Any,
    ) -> Tuple[
        Optional[np.ndarray],
        Optional[np.ndarray],
        Optional[np.ndarray],
        Optional[np.ndarray],
    ]:
        """
        Parse VehicleOdometry message.

        Extracts position, velocity, orientation quaternion, and angular velocity.

        Args:
            msg: VehicleOdometry message

        Returns:
            Tuple of (position, velocity, quaternion, angular_velocity) as numpy arrays
        """
        # Check if message has required fields
        if msg is None:
            return None, None, None, None

        # Extract position (NED frame)
        position = RosSensorBridge._safe_convert_to_float32(msg.position)

        # Extract velocity (NED frame)
        velocity = RosSensorBridge._safe_convert_to_float32(msg.velocity)

        # Extract orientation quaternion [w, x, y, z]
        quat = RosSensorBridge._safe_convert_to_float32(msg.q)

        # Extract angular velocity (FRD frame)
        ang_vel = RosSensorBridge._safe_convert_to_float32(msg.angular_velocity)

        return position, velocity, quat, ang_vel

    @staticmethod
    def _parse_imu(msg: Any) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """
        Parse SensorImu message.

        Extracts angular velocity and linear acceleration.

        Args:
            msg: SensorImu message

        Returns:
            Tuple of (angular_velocity, linear_acceleration) as numpy arrays
        """
        # Check if message has required fields
        if msg is None:
            return None, None

        # Extract angular velocity (FRD frame)
        ang_vel = RosSensorBridge._safe_convert_to_float32(msg.angular_velocity)

        # Extract linear acceleration
        linear_accel = RosSensorBridge._safe_convert_to_float32(msg.linear_acceleration)

        return ang_vel, linear_accel

    @staticmethod
    def _parse_gps(msg: Any) -> Optional[np.ndarray]:
        """
        Parse VehicleGpsPosition message.

        Converts GPS coordinates (latitude, longitude, altitude) to NED frame.
        Note: This is a simplified conversion. For production, use proper geodetic
        to NED conversion with reference point.

        Args:
            msg: VehicleGpsPosition message

        Returns:
            NED position [North, East, Down] as numpy array, or None if invalid
        """
        # Check if message has required fields
        if msg is None:
            return None

        # Extract GPS coordinates
        lat = msg.latitude
        lon = msg.longitude
        alt = msg.altitude

        # Validate GPS coordinates
        if lat is None or lon is None or alt is None:
            return None

        # Simple conversion (for testing purposes)
        # In production, use proper geodetic to NED conversion
        # This is a placeholder that assumes small local area
        ned_position = np.array([0.0, 0.0, -alt], dtype=np.float32)

        return ned_position

    def _publish_control_commands(self, commands: np.ndarray) -> None:
        """
        Publish control commands to /neural/control topic.

        Converts control commands to the format expected by ControlPublisher:
        - acc_p_z: Z-axis acceleration (m/s^2)
        - bodyrate: Angular velocity [wx, wy, wz] (rad/s)

        Args:
            commands: Control commands array [thrust, roll_rate, pitch_rate, yaw_rate]
        """
        if commands is None:
            return

        try:
            # Parse commands
            thrust = commands[0]
            roll_rate = commands[1]
            pitch_rate = commands[2]
            yaw_rate = commands[3]

            # Extract body rate (angular velocity)
            bodyrate = np.array([roll_rate, pitch_rate, yaw_rate], dtype=np.float32)

            # Thrust to acceleration (simplified: thrust is proportional to acceleration)
            # In production, calibrate thrust to acceleration properly
            acc_p_z = thrust * 9.81

            # Publish control commands
            timestamp = int(time.time() * 1e6)  # microseconds
            self._control_publisher.publish(acc_p_z, bodyrate, timestamp)
        except Exception as e:
            self._get_logger().warning(f"Error publishing control commands: {e}")

    def shutdown(self) -> None:
        """
        Shutdown the sensor bridge.

        Destroys subscriptions and timer.
        """
        if self._odometry_subscription is not None:
            self._node.destroy_subscription(self._odometry_subscription)
        if self._imu_subscription is not None:
            self._node.destroy_subscription(self._imu_subscription)
        if self._gps_subscription is not None:
            self._node.destroy_subscription(self._gps_subscription)
        if self._inference_timer is not None:
            self._node.destroy_timer(self._inference_timer)

        logger = self._node.get_logger()
        logger.info("RosSensorBridge shutdown complete")
