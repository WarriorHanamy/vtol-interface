# Fake Network Node

一个用于神经控制演示的仿真网络节点，生成目标航点轨迹。

## 功能特性

- ✅ **航点导航**: 支持多个目标航点的序列化导航
- ✅ **RC触发控制**: 通过遥控器按钮(1024)触发导航任务
- ✅ **配置文件支持**: 支持YAML格式的航点配置文件
- ✅ **实时监控**: 监听无人机位置状态，判断航点到达
- ✅ **自动完成**: 航点完成后自动停止神经控制

## 节点描述

### fake_network_node
- **功能**: 生成目标位置信息，模拟基于网络的导航系统
- **发布话题**:
  - `/neural/target_pose` - 目标位置 (geometry_msgs/PoseStamped)
  - `/neural/stop_control` - 停止控制信号 (std_msgs/Bool)
- **订阅话题**:
  - `/fmu/out/manual_control_setpoint` - 遥控器输入 (px4_msgs/ManualControlSetpoint)
  - `/fmu/out/vehicle_local_position` - 无人机位置 (px4_msgs/VehicleLocalPosition)

## 使用方法

### 启动节点
```bash
# 使用默认航点启动
ros2 launch fake_network fake_network_node.launch.py

# 使用自定义配置文件
ros2 launch fake_network fake_network_node.launch.py config_file:=/path/to/config.yaml

# 启用调试模式
ros2 launch fake_network fake_network_node.launch.py debug:=true

# 设置发布频率
ros2 launch fake_network fake_network_node.launch.py publish_rate:=20.0
```

### 配置文件格式

```yaml
demo_targets:
  waypoints:
    - [5.0, 0.0, -2.0]   # 航点1: 前进5m，高度2m
    - [5.0, 3.0, -2.0]   # 航点2: 右移3m
    - [0.0, 3.0, -2.0]   # 航点3: 回到原X坐标
    - [0.0, 0.0, -2.0]   # 航点4: 回到起始位置

failsafe_config:
  target_tolerance: 0.5   # 航点到达容差(m)
  max_velocity: 8.0       # 最大速度(m/s)
```

## 参数配置

### 节点参数
- `config_file` - 配置文件路径
- `publish_rate` - 目标位置发布频率 (Hz，默认10.0)
- `fake_target_tolerance` - 航点到达容差 (m，默认0.5)
- `fake_max_velocity` - 最大速度 (m/s，默认8.0)
- `use_sim_time` - 是否使用仿真时间 (默认false)

### RC触发条件
- **按钮ID**: 1024 (AUX1通道)
- **触发条件**: 按钮值 == 1024
- **激活行为**: 开始航点导航任务

## 工作流程

1. **初始化阶段**:
   - 加载配置文件或使用默认航点
   - 设置发布者和订阅者
   - 等待RC触发信号

2. **导航阶段**:
   - 监听当前无人机位置
   - 发布当前目标航点
   - 判断航点是否到达

3. **完成阶段**:
   - 所有航点完成后
   - 发布停止控制信号
   - 停止目标位置发布

## 依赖项

### ROS2依赖
- `rclcpp` - C++ ROS2客户端库
- `px4_msgs` - PX4消息定义
- `geometry_msgs` - 几何消息类型
- `std_msgs` - 标准消息类型
- `px4_ros2` - PX4 ROS2工具

### 系统依赖
- `yaml-cpp` - YAML解析库
- `Eigen3` - 线性代数库

## 构建说明

```bash
# 构建包
colcon build --packages-select fake_network

# 源工作空间
source install/setup.bash
```

## 故障排除

### 常见问题

1. **航点文件加载失败**
   - 检查YAML文件格式是否正确
   - 确认文件路径存在且可读

2. **RC触发无效**
   - 确认遥控器配置正确
   - 检查ManualControlSetpoint话题是否正常发布

3. **位置订阅失败**
   - 确认PX4正在发布VehicleLocalPosition话题
   - 检查QoS设置是否匹配

### 调试技巧

启用调试模式查看详细信息：
```bash
ros2 launch fake_network fake_network_node.launch.py debug:=true
```

## 许可证

Copyright (c) 2025, Differential Robotics
SPDX-License-Identifier: BSD-3-Clause