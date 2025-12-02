<div align="center">

# PX4-ROS2-Bridge

**Bridge between PX4-Autopilot and ROS 2**

[![ROS 2](https://img.shields.io/badge/ROS%202-Humble-blue)](https://docs.ros.org/en/humble/)
[![PX4](https://img.shields.io/badge/PX4-Autopilot-orange)](https://px4.io/)
[![License](https://img.shields.io/badge/License-BSD--3-green.svg)](LICENSE)

</div>

---

## 📋 目录

- [项目简介](#项目简介)
- [功能特性](#功能特性)
- [系统要求](#系统要求)
- [快速开始](#快速开始)
  - [Docker 部署](#docker-部署)
  - [本地构建](#本地构建)
- [包结构](#包结构)
- [使用说明](#使用说明)
- [开发计划](#开发计划)
- [更新日志](#更新日志)
- [贡献指南](#贡献指南)
- [作者信息](#作者信息)
- [许可证](#许可证)

---

## 🚀 项目简介

PX4-ROS2-Bridge 是一个连接 PX4 自动驾驶仪与 ROS 2 生态系统的桥接项目，提供了一系列工具和接口，用于：

- 实现 PX4 自定义飞行模式
- 神经网络控制集成


本项目基于 [px4-ros2-interface-lib](https://github.com/PX4/px4-ros2-interface-lib) 进行扩展开发。

---

## ✨ 功能特性

- ✅ **神经网络控制模式**：支持基于神经网络的飞行器控制
- ✅ **执行器支持**：多模式执行器框架
- ✅ **Docker 容器化**：开箱即用的开发环境
- ✅ **PX4 消息转换**：完整的 PX4 消息类型支持
- 🔄 **实时控制**：低延迟的控制指令传输

---

## 💻 系统要求

### 软件依赖

- **操作系统**: Ubuntu 22.04 (推荐)
- **ROS 2**: Humble Hawksbill
- **PX4-Autopilot**: v1.16 或更高版本
- **Docker**: 20.10 或更高版本
- **Just**: 命令运行工具

---

## 🎯 快速开始

### Docker 部署

#### 1. 构建 Docker 镜像

```bash
just build-image
```

或使用 Docker 命令：

```bash
docker build -t px4-ros2-bridge .
```

#### 2. 运行容器

```bash
just run-container
```

### 本地构建

#### 1. 安装依赖

```bash
# 安装 ROS 2 Humble (如果尚未安装)
# 参考: https://docs.ros.org/en/humble/Installation.html

# 安装项目依赖
sudo apt update
sudo apt install -y \
  ros-humble-px4-msgs \
  ros-humble-eigen3-cmake-module \
  libeigen3-dev
```

#### 2. 克隆仓库

```bash
cd ~/
mkdir -p ros2_ws/src
cd ros2_ws/src
git clone --recursive https://github.com/Arclunar/px4-ros2-interface.git .
```

#### 3. 构建工作空间

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install
```

#### 4. 启动环境

```bash
source install/setup.bash
```

---

## 📦 包结构

```
ros2_ws/
├── src/
│   ├── px4-ros2-interface-lib/      # PX4-ROS2 接口库
│   │   ├── neural_demo/             # 神经网络控制演示
│   │   ├── example_mode_*/          # 各种飞行模式示例
│   │   └── px4_ros2_cpp/            # 核心 C++ 库
│   ├── isaac_pos_ctrl_neural/       # Isaac 位置控制（神经网络）
│   ├── translation_node/            # 数据转换节点
│   ├── super_interface/             # 超级接口
│   └── time_test_example/           # 时间测试示例
├── build/                           # 构建输出
├── install/                         # 安装文件
└── log/                             # 日志文件
```

---

## 📖 使用说明

### 启动神经网络控制模式

```bash
# 终端 1: 启动 PX4 SITL 仿真
cd ~/PX4-Autopilot
make px4_sitl gz_x500

# 终端 2: 启动控制节点
source ~/ros2_ws/install/setup.bash
ros2 run neural_demo neural_demo_node

# 终端 3: 发送目标位置
ros2 run isaac_pos_ctrl_neural set_target_pos.py
```

### 查看话题

```bash
# 查看所有话题
ros2 topic list

# 监听神经网络输出
ros2 topic echo /neural/rates_sp

# 监听位置信息
ros2 topic echo /fmu/out/vehicle_local_position
```

---

## 📅 开发计划

### 当前版本 (v0.1.0)

- [x] 基础框架搭建
- [x] 神经网络控制模式
- [x] Docker 环境配置
- [x] PX4 消息转换

### 下一版本 (v0.2.0)

- [ ] 完善神经网络训练流程
- [ ] 增加碰撞检测模块
- [ ] 优化控制性能
- [ ] 添加仿真测试用例
- [ ] 编写完整的 API 文档

### 未来计划

- [ ] 多机协同控制
- [ ] 视觉 SLAM 集成
- [ ] 强化学习训练框架
- [ ] Web 监控界面
- [ ] 硬件在环测试支持

---

## 📝 更新日志

### [Unreleased]

#### 新增
- 添加 `USE_SCOPED_HEADER_INSTALL_DIR` 选项以符合 ROS 2 未来版本规范
- 完善 README 文档结构

#### 修复
- 修复头文件安装路径警告

---

### [0.1.0] - 2025-12-02

#### 新增
- 初始项目结构
- 神经网络控制模式 (`neural_demo`)
- Isaac 位置控制节点
- Docker 构建支持
- PX4-ROS2 基础接口

#### 已知问题
- 神经网络模型尚未完全训练
- 部分模式缺少详细文档

---

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

### 贡献流程

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 代码规范

- 遵循 [ROS 2 编码规范](https://docs.ros.org/en/humble/The-ROS2-Project/Contributing/Code-Style-Language-Versions.html)
- 使用有意义的提交信息
- 添加必要的注释和文档
- 确保代码通过编译和测试

---

## 👥 作者信息

**项目维护者**: Arclunar  
**组织**: [Arclunar](https://github.com/Arclunar)  
**仓库**: [px4-ros2-interface](https://github.com/Arclunar/px4-ros2-interface)

**贡献者**:
- WarriorHanamy - 原始仓库贡献者

**联系方式**:
- Issues: [GitHub Issues](https://github.com/Arclunar/px4-ros2-interface/issues)
- Discussions: [GitHub Discussions](https://github.com/Arclunar/px4-ros2-interface/discussions)

---

## 📄 许可证

本项目基于 BSD-3-Clause 许可证开源。详见 [LICENSE](LICENSE) 文件。

---

## 🙏 致谢

- [PX4 Autopilot](https://px4.io/) - 开源飞行控制栈
- [ROS 2](https://docs.ros.org/) - 机器人操作系统
- [px4-ros2-interface-lib](https://github.com/PX4/px4-ros2-interface-lib) - 官方 PX4-ROS2 接口库

---

<div align="center">

**如果这个项目对你有帮助，请给一个 ⭐ Star！**

Made with ❤️ by Arclunar

</div>