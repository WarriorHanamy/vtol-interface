# Step 1 - Understand Intent

## Functional Requirements

### FR-1: VtolFeatureProvider Class Structure
Create VtolFeatureProvider class that inherits from FeatureProviderBase and initializes with observation_metadata.yaml file path.

### FR-2: Sensor Update Methods
Implement update methods for incoming sensor data:
- update_vehicle_odom(position, velocity, quat, ang_vel): Update vehicle odometry data (position NED, velocity NED, orientation quaternion, angular velocity FRD)
- update_imu(linear_accel, ang_vel): Update IMU data (linear acceleration, angular velocity)
- update_target(target_pos_ned): Update target position in NED frame
- update_last_action(action): Buffer the last action vector

### FR-3: get_to_target_b() Feature
Compute target position error vector in FLU body frame:
- Input: Vehicle position (NED), target position (NED), orientation quaternion
- Transform: NED -> FRD -> FLU coordinate conversion
- Output: 3D numpy array representing target error in FLU frame
- Return None if vehicle odometry or target data is missing

### FR-4: get_grav_dir_b() Feature
Compute gravity direction vector in FLU body frame:
- Input: Orientation quaternion
- Computation: Project gravity vector [0, 0, 9.81] from world to body frame and normalize
- Output: 3D normalized numpy array in FLU frame
- Return None if vehicle odometry data is missing

### FR-5: get_ang_vel_b() Feature
Compute angular velocity in FLU body frame:
- Input: Angular velocity in FRD frame
- Transform: FRD -> FLU coordinate conversion (negate Y and Z components)
- Output: 3D numpy array in FLU frame
- Return None if IMU or odometry data is missing

### FR-6: get_last_action() Feature
Return the buffered action vector:
- Input: Buffered action from update_last_action()
- Output: 4D numpy array [thrust, roll_rate, pitch_rate, yaw_rate]
- Return None if no action has been buffered

### FR-7: Coordinate Transformation Helpers
Implement helper methods for coordinate conversions:
- _ned_to_frd(quat, vec): Transform vector from NED to FRD using quaternion
- _frd_to_flu(vec): Transform vector from FRD to FLU (negate Y and Z components)

## Assumptions

### Assumption 1: observation_metadata.yaml Structure
The observation_metadata.yaml file will have the following structure:
```yaml
features:
  - name: to_target_b
    dim: 3
    dtype: float32
    description: "Target error vector in FLU body frame"
  - name: grav_dir_b
    dim: 3
    dtype: float32
    description: "Gravity direction vector in FLU body frame"
  - name: ang_vel_b
    dim: 3
    dtype: float32
    description: "Angular velocity in FLU body frame"
  - name: last_action
    dim: 4
    dtype: float32
    description: "Previous action vector"
```

### Assumption 2: Coordinate Frame Definitions
- NED (North-East-Down): Global reference frame used by PX4
- FRD (Forward-Right-Down): Body frame used by PX4 (aircraft aligned)
- FLU (Forward-Left-Up): Body frame used by neural network training

### Assumption 3: Coordinate Transformation Details
- NED -> FRD: Use quaternion active rotation (quat_act_rot)
- FRD -> FLU: Negate Y (right -> left) and Z (down -> up) components
- FRD -> FLU conversion: [vx, vy, vz] -> [vx, -vy, -vz]

### Assumption 4: Sensor Data Structure
- Vehicle odometry includes: position (NED), velocity (NED), orientation_quat [w,x,y,z], angular_velocity (FRD)
- IMU includes: linear_acceleration, angular_velocity
- Target position: 3D vector in NED frame
- Last action: 4D vector [thrust, roll_rate, pitch_rate, yaw_rate]

### Assumption 5: None Handling
When sensor data is not available, all get_* methods should return None rather than raising exceptions.
