# Scripts Directory

## 脚本映射

### ROS2 工作区

| 脚本 | 功能 |
|------|------|
| `build.sh` | 构建 ROS2 工作区|
| `clean.sh` | 清理构建产物 |
| `neural_mode.sh` | 启动 neural executor |
| `neural_infer.sh` | 运行 neural inference |

### Docker - ROS2

| 脚本 | 功能 |
|------|------|
| `exec_ros2.sh` | 在 ROS2 容器中执行命令 |

### Docker Compose

| 脚本 | 功能 |
|------|------|
| `docker_up.sh` | 启动 compose 服务 |
| `docker_down.sh` | 停止 compose 服务 |

## 环境变量

- `ROS_DISTRO`: ROS2 发行版（如 `humble`, `foxy`）

## 特点

- ✅ 无硬编码路径，使用 `SCRIPT_DIR` 和 `PROJECT_DIR` 动态获取
- ✅ 每个脚本独立可执行
- ✅ 遵循 bash 最佳实践（`set -e`）
