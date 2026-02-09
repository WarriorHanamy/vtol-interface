/****************************************************************************
 * Copyright (c) 2025 PX4 Development Team.
 * SPDX-License-Identifier: BSD-3-Clause
 ****************************************************************************/
#pragma once

#include <px4_ros2/components/mode.hpp>
#include <px4_ros2/control/setpoint_types/experimental/acc_rates.hpp>
#include <px4_ros2/odometry/attitude.hpp>
#include <px4_msgs/msg/vehicle_thrust_acc_setpoint.hpp>
#include <rclcpp/rclcpp.hpp>
#include <yaml-cpp/yaml.h>
#include <Eigen/Core>

/**
 * @class NeuralManualMode
 * @brief Manual flight mode with tilt-prioritizing attitude control and configurable parameters
 *
 * This mode converts RC stick inputs into acceleration and rate setpoints using
 * a tilt-prioritizing attitude control algorithm.
 *
 * Coordinate Frames:
 * - World Frame: NED (North-East-Down)
 * - Baselist Frame: FRD (Forward-Right-Down)
 * - Quaternion: Hamilton convention [w, x, y, z]
 *
 * Control Mode:
 * - Input: ManualControlInput (roll, pitch, yaw, throttle sticks)
 * - Output: AccRatesSetpoint (thrust acceleration + body rates)
 * - Yaw Control: Rate-based (direct stick input)
 */
class NeuralManualMode : public px4_ros2::ModeBase
{
public:
  explicit NeuralManualMode(rclcpp::Node & node)
      : ModeBase(node, Settings{"NeuralManual"})
  {
    loadConfigFromYaml();

    _manual_control_input = std::make_shared<px4_ros2::ManualControlInput>(*this);
    _attitude = std::make_shared<px4_ros2::OdometryAttitude>(*this);
    _acc_rates_setpoint = std::make_shared<px4_ros2::AccRatesSetpointType>(*this);

    RCLCPP_INFO(_node.get_logger(),
      "NeuralManualMode initialized: max_tilt=%.1f deg, max_acc=%.1f m/s^2, yaw_weight=%.2f",
      radToDeg(_config.max_tilt_angle), _config.max_acc, _config.yaw_weight);
  }

  ~NeuralManualMode() override = default;

  // Disable copy, enable move for efficiency
  NeuralManualMode(const NeuralManualMode&) = delete;
  NeuralManualMode& operator=(const NeuralManualMode&) = delete;
  NeuralManualMode(NeuralManualMode&&) noexcept = default;
  NeuralManualMode& operator=(NeuralManualMode&&) noexcept = default;

protected:
  void onActivate() override
  {
    RCLCPP_INFO(_node.get_logger(), "NeuralManualMode activated");
  }

  void onDeactivate() override
  {
    RCLCPP_INFO(_node.get_logger(), "NeuralManualMode deactivated");
  }

  void updateSetpoint(float dt_s) override
  {
    // Check if manual control is valid
    if (!_manual_control_input->isValid()) {
      RCLCPP_WARN_THROTTLE(_node.get_logger(), *_node.get_clock(), 1000,
        "NeuralManual: Waiting for valid manual control input...");
      return;
    }

    // Check if attitude is valid
    if (!_attitude->lastValid(500ms)) {
      RCLCPP_WARN_THROTTLE(_node.get_logger(), *_node.get_clock(), 1000,
        "NeuralManual: Waiting for attitude data...");
      return;
    }

    // Read stick inputs
    const float stick_roll = _manual_control_input->roll();     // [-1, 1], right positive
    const float stick_pitch = _manual_control_input->pitch();    // [-1, 1], forward negative
    const float stick_yaw = _manual_control_input->yaw();       // [-1, 1], clockwise positive
    const float stick_throttle = _manual_control_input->throttle(); // [-1, 1], up positive

    // Get current attitude
    const Eigen::Quaternionf q_current = _attitude->attitude();

    // Step 1: Generate tilt setpoint from roll/pitch sticks
    const Eigen::Quaternionf q_tilt = generateTiltSetpoint(stick_roll, stick_pitch);

    // Step 2: Compute acceleration setpoint from throttle
    const float acc_sp = computeAccSetpoint(stick_throttle);

    // Step 3: Compute rate setpoint with tilt-prioritizing control
    const Eigen::Vector3f rates_sp = computeRateSetpoint(q_current, q_tilt, stick_yaw);

    // Apply setpoint
    _acc_rates_setpoint->update(acc_sp, rates_sp);

    // Debug logging (throttled)
    RCLCPP_DEBUG_THROTTLE(_node.get_logger(), *_node.get_clock(), 500,
      "NeuralManual: sticks[%.2f,%.2f,%.2f,%.2f] -> acc=%.2f, rates[%.2f,%.2f,%.2f]",
      stick_roll, stick_pitch, stick_yaw, stick_throttle,
      acc_sp, rates_sp[0], rates_sp[1], rates_sp[2]);
  }

private:
  // Configuration parameters
  struct Config
  {
    float max_tilt_angle{0.785f};      // 45 degrees in radians
    float max_acc{19.6f};              // 2g in m/s^2
    float yaw_weight{0.5f};
    Eigen::Vector3f p_gains{5.0f, 5.0f, 3.0f}; // [roll, pitch, yaw]
    float max_rate{3.0f};              // rad/s for rate limiting
  };

  // Member variables
  std::shared_ptr<px4_ros2::ManualControlInput> _manual_control_input;
  std::shared_ptr<px4_ros2::OdometryAttitude> _attitude;
  std::shared_ptr<px4_ros2::AccRatesSetpointType> _acc_rates_setpoint;
  Config _config;

  // ========================================================================
  // Configuration Loading
  // ========================================================================

  void loadConfigFromYaml()
  {
    // Default configuration
    _config = Config{};

    // Try to load from config file
    std::string config_file;
    if (_node.get_parameter("config_file", config_file) && !config_file.empty()) {
      try {
        YAML::Node config = YAML::LoadFile(config_file);

        if (config["neural_manual"]) {
          auto node = config["neural_manual"];

          if (node["max_tilt_angle"]) {
            _config.max_tilt_angle = node["max_tilt_angle"].as<float>();
            // Convert degrees to radians if needed
            if (_config.max_tilt_angle > 2.0f) { // Heuristic: > 114 deg means input is in degrees
              _config.max_tilt_angle = degToRad(_config.max_tilt_angle);
            }
          }

          if (node["max_acc"]) {
            _config.max_acc = node["max_acc"].as<float>();
          }

          if (node["yaw_weight"]) {
            _config.yaw_weight = node["yaw_weight"].as<float>();
          }

          if (node["p_gains"]) {
            auto gains = node["p_gains"];
            if (gains.size() == 3) {
              _config.p_gains = Eigen::Vector3f{
                gains[0].as<float>(),
                gains[1].as<float>(),
                gains[2].as<float>()
              };
            }
          }

          if (node["max_rate"]) {
            _config.max_rate = node["max_rate"].as<float>();
          }

          RCLCPP_INFO(_node.get_logger(),
            "Loaded neural_manual config from: %s", config_file.c_str());
        } else {
          RCLCPP_WARN(_node.get_logger(),
            "No neural_manual section found in config file, using defaults");
        }
      } catch (const YAML::Exception& e) {
        RCLCPP_ERROR(_node.get_logger(),
          "Failed to load config file '%s': %s. Using defaults.",
          config_file.c_str(), e.what());
      }
    } else {
      RCLCPP_WARN(_node.get_logger(),
        "No config_file parameter found, using default configuration");
    }

    // Validate and clamp configuration
    _config.max_tilt_angle = std::clamp(_config.max_tilt_angle, 0.1f, 1.4f); // ~5-80 deg
    _config.max_acc = std::clamp(_config.max_acc, 5.0f, 30.0f); // Reasonable range
    _config.yaw_weight = std::clamp(_config.yaw_weight, 0.0f, 1.0f);
    _config.p_gains = _config.p_gains.cwiseMax(0.1f).cwiseMin(20.0f);
    _config.max_rate = std::clamp(_config.max_rate, 0.5f, 10.0f);
  }

  // ========================================================================
  // Core Control Algorithms
  // ========================================================================

  /**
   * @brief Generate tilt setpoint quaternion from roll/pitch stick inputs
   *
   * Input: stick_roll, stick_pitch in [-1, 1]
   * Output: Quaternion representing the desired tilt
   *
   * Coordinate Frame: FRD (Forward-Right-Down)
   * - Roll stick right (+) → positive rotation around X (right side down)
   * - Pitch stick forward (+) → negative rotation around Y (nose down)
   *
   * The negative sign on pitch is CRITICAL for correct behavior in NED frame.
   */
  Eigen::Quaternionf generateTiltSetpoint(float stick_roll, float stick_pitch) const
  {
    // Build tilt vector in FRD frame
    Eigen::Vector3f tilt_vector;
    tilt_vector.x() = stick_roll * _config.max_tilt_angle;     // Right positive
    tilt_vector.y() = -stick_pitch * _config.max_tilt_angle;   // Forward negative (nose down)
    tilt_vector.z() = 0.0f;  // No tilt around Z axis

    // Limit magnitude to max_tilt_angle
    const float tilt_magnitude = tilt_vector.norm();
    if (tilt_magnitude > _config.max_tilt_angle) {
      tilt_vector = tilt_vector / tilt_magnitude * _config.max_tilt_angle;
    }

    // Create quaternion from rotation vector (axis-angle representation)
    return axisAngleToQuaternion(tilt_vector);
  }

  /**
   * @brief Compute acceleration setpoint from throttle stick input
   *
   * Input: stick_throttle in [-1, 1]
   * Output: acceleration in m/s^2
   *
   * Mapping:
   * - Mid-throttle (0.0) = 1g = hovering
   * - Full up (+1.0) = max_acc (typically 2g)
   * - Full down (-1.0) = reduced thrust but still positive
   *
   * Formula: acc = 1g + throttle * (max_acc - 1g)
   */
  float computeAccSetpoint(float stick_throttle) const
  {
    constexpr float gravity = 9.81f;  // m/s^2
    const float acc_sp = gravity + stick_throttle * (_config.max_acc - gravity);

    // Ensure minimum thrust (don't fall out of sky)
    return std::max(acc_sp, 0.5f);  // Minimum 0.5g upward
  }

  /**
   * @brief Compute rate setpoint using tilt-prioritizing attitude control
   *
   * This algorithm prioritizes tilt (roll/pitch) over yaw for smoother control.
   *
   * Input:
   * - q_current: Current attitude quaternion
   * - q_target: Target tilt quaternion (from generateTiltSetpoint)
   * - stick_yaw: Yaw stick input [-1, 1] for manual yaw rate control
   *
   * Output: Rate setpoint [roll_rate, pitch_rate, yaw_rate] in rad/s
   *
   * Algorithm steps:
   * 1. Extract Z axes from current and target quaternions
   * 2. Compute tilt correction quaternion to align Z axes
   * 3. Create q_reduced (perfect tilt, current yaw)
   * 4. Extract pure yaw error
   * 5. Apply yaw_weight to yaw_error_angle
   * 6. Add yaw stick input for manual yaw control
   * 7. Create final target quaternion
   * 8. Compute error quaternion
   * 9. Convert to rate setpoint using P-gains
   * 10. Apply rate limiting
   */
  Eigen::Vector3f computeRateSetpoint(
    const Eigen::Quaternionf& q_current,
    const Eigen::Quaternionf& q_target,
    float stick_yaw) const
  {
    using namespace px4_ros2;

    // Step 1: Extract Z axes from current and target quaternions
    const Eigen::Vector3f z_current = extractZAxis(q_current);
    const Eigen::Vector3f z_target = extractZAxis(q_target);

    // Step 2: Compute tilt correction quaternion to align Z axes
    const Eigen::Quaternionf q_tilt_correction = tiltCorrectionQuaternion(z_current, z_target);

    // Step 3: Create q_reduced (perfect tilt, current yaw)
    const Eigen::Quaternionf q_reduced = q_tilt_correction * q_current;

    // Step 4: Extract pure yaw error
    const Eigen::Quaternionf q_reduced_inv = q_reduced.inverse();
    const Eigen::Quaternionf q_yaw_diff = q_reduced_inv * q_target;
    const float yaw_error_angle = extractYawAngle(q_yaw_diff);

    // Step 5: Apply yaw weight (reduce yaw authority for smoother control)
    const float weighted_yaw_error = yaw_error_angle * _config.yaw_weight;

    // Step 6: Add yaw stick input for manual yaw control (1 rad/s max manual yaw)
    const float yaw_setpoint = weighted_yaw_error + stick_yaw * 1.0f;

    // Step 7: Create final target quaternion
    const Eigen::Quaternionf q_yaw_rotation = yawRotationQuaternion(yaw_setpoint);
    const Eigen::Quaternionf q_final_target = q_reduced * q_yaw_rotation;

    // Step 8: Compute error quaternion
    const Eigen::Quaternionf q_error = q_current.inverse() * q_final_target;

    // Step 9: Convert to rate setpoint using P-gains
    // Formula: rate = 2 * q_error.xyz * p_gains
    // Small angle approximation: for small angles, rate ≈ 2 * angle_vector * gains
    Eigen::Vector3f rate_setpoint;
    rate_setpoint.x() = 2.0f * q_error.x() * _config.p_gains.x();  // roll rate
    rate_setpoint.y() = 2.0f * q_error.y() * _config.p_gains.y();  // pitch rate
    rate_setpoint.z() = 2.0f * q_error.z() * _config.p_gains.z();  // yaw rate

    // Handle double cover: if w < 0, negate the error vector
    // This ensures we take the shortest rotation path
    if (q_error.w() < 0.0f) {
      rate_setpoint = -rate_setpoint;
    }

    // Step 10: Apply rate limiting
    rate_setpoint = rate_setpoint.cwiseMin(_config.max_rate).cwiseMax(-_config.max_rate);

    return rate_setpoint;
  }

  // ========================================================================
  // Quaternion Utility Functions
  // ========================================================================

  /**
   * @brief Convert axis-angle rotation vector to quaternion
   *
   * The input is a rotation vector where the direction is the rotation axis
   * and the magnitude is the rotation angle (in radians).
   *
   * Uses Eigen's AngleAxis for robust conversion.
   */
  static Eigen::Quaternionf axisAngleToQuaternion(const Eigen::Vector3f& axis_angle)
  {
    const float angle = axis_angle.norm();

    if (angle < 1e-6f) {
      return Eigen::Quaternionf::Identity();  // Small angle, return identity
    }

    const Eigen::Vector3f axis = axis_angle / angle;
    return Eigen::Quaternionf(Eigen::AngleAxisf(angle, axis)).normalized();
  }

  /**
   * @brief Extract the Z axis (body-down direction) from a quaternion
   *
   * For a quaternion representing the body-to-world rotation,
   * the Z axis of the body frame in world coordinates is the third column
   * of the rotation matrix.
   *
   * Mathematically: z_world = R * [0, 0, 1]^T = R.col(2)
   */
  static Eigen::Vector3f extractZAxis(const Eigen::Quaternionf& q)
  {
    // Rotate the Z axis [0, 0, 1] by quaternion q
    const Eigen::Matrix3f R = q.toRotationMatrix();
    return R.col(2);  // Third column is the rotated Z axis
  }

  /**
   * @brief Compute the rotation quaternion that aligns two vectors
   *
   * This computes the shortest arc rotation from z_current to z_target.
   * Uses Eigen's FromTwoVectors method which is numerically stable.
   */
  static Eigen::Quaternionf tiltCorrectionQuaternion(
    const Eigen::Vector3f& z_current,
    const Eigen::Vector3f& z_target)
  {
    return Eigen::Quaternionf::FromTwoVectors(z_current, z_target).normalized();
  }

  /**
   * @brief Extract the yaw angle from a quaternion
   *
   * For quaternion [w, x, y, z] (Hamilton convention), the yaw angle is:
   * yaw = atan2(2*(w*z + x*y), 1 - 2*(y*y + z*z))
   *
   * This extracts the pure rotation around the Z axis.
   */
  static float extractYawAngle(const Eigen::Quaternionf& q)
  {
    const float w = q.w(), x = q.x(), y = q.y(), z = q.z();
    return std::atan2(2.0f * (w*z + x*y), 1.0f - 2.0f * (y*y + z*z));
  }

  /**
   * @brief Create a pure Z-axis rotation quaternion
   *
   * This creates a quaternion representing rotation around the Z axis only.
   */
  static Eigen::Quaternionf yawRotationQuaternion(float yaw_angle)
  {
    return Eigen::Quaternionf(
      Eigen::AngleAxisf(yaw_angle, Eigen::Vector3f::UnitZ())
    ).normalized();
  }
};
