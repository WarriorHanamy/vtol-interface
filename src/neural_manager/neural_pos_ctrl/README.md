# Isaac Position Control Neural Network for PX4

这是一个将Isaac Lab训练的无人机位置控制模型部署到PX4-Gazebo的ROS2功能包。

## 功能特性

- ✅ **ONNX模型推理**: 使用ONNX Runtime进行高效神经网络推理
- ✅ **PX4集成**: 完全兼容PX4现有的`mode_neural_ctrl`接口
- ✅ **实时控制**: 支持50Hz控制频率，满足无人机实时控制需求
- ✅ **坐标系转换**: 正确处理Isaac ENU与PX4 NED坐标系转换
- ✅ **目标位置管理**: 支持固定目标和动态目标位置设置
- ✅ **安全保护**: 输出限制、通信超时检测、紧急停止机制

## 模型架构

基于`drone_pos_ctrl_env_cfg.py`训练的PPO模型：

### Policy网络输入 (20维观测)
```
1. lin_vel (3维): 机体线速度 [vx, vy, vz]
2. projected_gravity_b (3维): 机体重力投影 [gx, gy, gz]
3. ang_vel (3维): 机体角速度 [wx, wy, wz]
4. current_yaw_direction (2维): 当前偏航方向 [cos(yaw), sin(yaw)]
5. target_pos_b (3维): 目标位置(机体) [dx, dy, dz]
6. target_yaw (2维): 目标偏航方向 [cos(target_yaw), sin(target_yaw)]
7. actions (4维): 上一时刻动作 [throttle, roll_rate, pitch_rate, yaw_rate]
```

### Policy网络输出 (4维动作)
```
[throttle, roll_rate, pitch_rate, yaw_rate] ∈ [-1, 1]
```

### 动作映射到PX4控制
```
- throttle: [-1, 1] → [0, 1] (油门指令)
- roll_rate: [-1, 1] → [-10, 10] rad/s (滚转角速度)
- pitch_rate: [-1, 1] → [-10, 10] rad/s (俯仰角速度)
- yaw_rate: [-1, 1] → [-5, 5] rad/s (偏航角速度)
```

## 文件结构

```
neural_pos_ctrl/
├── package.xml              # ROS2功能包配置
├── CMakeLists.txt           # 构建配置
├── setup.py                # Python包设置
├── neural_pos_ctrl/      # Python模块
│   ├── __init__.py
│   ├── pos_ctrl_node.py   # 主推理节点
│   └── set_target_pos.py       # 目标位置设置工具
├── launch/
│   └── isaac_pos_ctrl_launch.py # 启动文件
├── config/
│   └── pos_ctrl_params.yaml     # 参数配置
└── models/                     # ONNX模型目录
    └── isaac_pos_ctrl.onnx     # 导出的ONNX模型
```

## 使用方法

### 1. 导出ONNX模型

```bash
# 进入Isaac项目目录
cd /home/arc/framework/isaac/isaac_drone_ctrl

# 导出训练好的模型为ONNX格式
python3 scripts/export_pos_ctrl_onnx.py \
    --model logs/skrl/drone_racer/2025-11-27_04-11-11_ppo_torch/best_agent.pt \
    --output /home/arc/framework/isaac/ros2_ws/src/neural_pos_ctrl/models
    --name isaac_pos_ctrl
```

### 2. 构建ROS2功能包

```bash
# 进入ROS2工作空间
cd /home/arc/framework/isaac/ros2_ws

# 构建功能包
colcon build --packages-select neural_pos_ctrl

# 源工作空间
source install/setup.bash
```

### 3. 启动推理节点

```bash
# 使用默认参数启动
ros2 launch neural_pos_ctrl isaac_pos_ctrl_launch.py

# 启用调试模式
ros2 launch neural_pos_ctrl isaac_pos_ctrl_launch.py debug_mode:=true

# 设置自定义目标位置
ros2 launch neural_pos_ctrl isaac_pos_ctrl_launch.py target_position:="[2.0, 1.0, 2.5]" target_yaw:=1.57

# 使用命令行工具设置目标
python3 neural_pos_ctrl/set_target_pos.py --position "2.0, 1.0, 2.5" --yaw 1.57 --verbose
```

## 话题接口

### 订阅话题

| 话题名称 | 消息类型 | 描述 |
|-----------|----------|------|
| `/fmu/out/vehicle_odometry` | `px4_msgs/VehicleOdometry` | 无人机状态(位置、速度、姿态) |
| `/neural/mode_neural_ctrl` | `std_msgs/Bool` | 神经控制模式触发信号 |

### 发布话题

| 话题名称 | 消息类型 | 描述 |
|-----------|----------|------|
| `/neural/rates_sp` | `px4_msgs/VehicleRatesSetpoint` | 角速度和推力控制指令 |
| `/neural/target_pose` | `geometry_msgs/PoseStamped` | 目标位置(用于设置工具) |

## 配置参数

主要配置文件：`config/pos_ctrl_params.yaml`

### 关键参数

- `model.onnx_path`: ONNX模型文件路径
- `control.update_rate`: 控制发布频率 (Hz)
- `target.fixed_position`: 固定目标位置 [北向, 东向, 地下]
- `target.fixed_yaw`: 固定目标偏航角 (弧度)
- `action_mapping`: 动作映射参数 (神经网络输出 → PX4控制)

### 安全参数

- `control.timeout_ms`: 通信超时阈值 (毫秒)
- `safety.throttle_limits`: 油门限制 [0.0, 1.0]
- `safety.angular_rate_limits`: 角速度限制 (rad/s)

## 坐标系转换

### Isaac → PX4
- **位置**: Isaac ENU (东-北-天) → PX4 NED (北-东-地)
- **姿态**: 四元数格式一致，注意handedness
- **速度**: 机体坐标系保持一致，世界坐标系需转换
- **重力**: Isaac [0,0,-1] → PX4 [0,0,1] (Z轴反向)

### 数据预处理
1. **VehicleOdometry提取**: 获取位置、速度、角速度、四元数
2. **坐标系统一**: 确保与Isaac训练时数据格式一致
3. **观测向量组装**: 严格按训练时的20维顺序
4. **数据归一化**: 匹配训练时的数据分布
5. **输入饱和限制**: 防止数值不稳定

## 测试验证

### 单元测试
```bash
# 测试导入
python3 -c "import neural_pos_ctrl; print('导入成功')"

# 测试模型加载
python3 -c "from neural_pos_ctrl.pos_ctrl_node import IsaacPositionControlNode; print('节点类加载成功')"
```

### 集成测试
```bash
# 启动PX4 Gazebo仿真
# 在另一个终端启动控制节点
ros2 launch neural_pos_ctrl isaac_pos_ctrl_launch.py

# 测试目标位置设置
ros2 topic pub /neural/target_pose geometry_msgs/PoseStamped '{header: {frame_id: "world"}, pose: {position: {x: 2.0, y: 1.0, z: 2.0}, orientation: {w: 1.0, x: 0.0, y: 0.0, z: 0.0}}}'

# 启用神经网络控制
ros2 topic pub /neural/mode_neural_ctrl std_msgs/Bool "data: true"
```

## 性能指标

- **推理延迟**: < 2ms (ONNX Runtime, 20维输入)
- **控制频率**: 50Hz (可配置1-200Hz)
- **内存占用**: 轻量级 (适合嵌入式部署)
- **CPU使用**: 低 (优化后的ONNX模型)

## 故障排除

### 常见问题

1. **模型加载失败**
   - 检查ONNX模型文件路径
   - 确认onnxruntime已安装: `pip install onnxruntime`

2. **数据订阅失败**
   - 检查PX4话题是否正确发布
   - 验证QoS设置是否匹配

3. **控制指令无效**
   - 检查坐标系转换是否正确
   - 验证动作映射参数

4. **性能问题**
   - 调整控制发布频率
   - 启用输入饱和限制
   - 检查数据预处理流程

### 调试模式

启用调试模式获得详细的状态信息：
```bash
ros2 launch neural_pos_ctrl isaac_pos_ctrl_launch.py debug_mode:=true
```

输出示例：
```
🔍 调试状态:
  神经网络控制: 激活
  数据延迟: 12.3 ms
  目标位置(NED): 0.0, 0.0, 1.5
  当前动作: [0.5, 0.1, -0.2, 0.0]
```

## 依赖项

### ROS2依赖
- `rclpy`
- `rclcpp`
- `px4_msgs`
- `geometry_msgs`
- `std_msgs`
- `sensor_msgs`
- `ament_cmake_python`

### Python依赖
- `numpy`
- `onnxruntime`
- `pyyaml`
- `scipy`

### 系统要求
- Ubuntu 20.04+ / ROS2 Humble+
- Python 3.8+
- ONNX Runtime CPU/GPU支持

## 许可证

Copyright (c) 2025, Differential Robotics
SPDX-License-Identifier: BSD-3-Clause

## 贡献者

- Differential Robotics (原始Isaac模型和训练)
- Isaac Neural Control Implementation (ROS2集成和部署)

## 引用

1. Isaac Lab Documentation: https://github.com/isaac-sim/IsaacLab
2. PX4 Autopilot: https://docs.px4.io/
3. ONNX Runtime: https://onnxruntime.ai/