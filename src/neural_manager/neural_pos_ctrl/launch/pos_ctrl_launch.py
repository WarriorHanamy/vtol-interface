"""
Copyright (c) 2025, Differential Robotics
All rights reserved.

SPDX-License-Identifier: BSD-3-Clause

Isaac Position Control Neural Network Launch File

启动Isaac位置控制神经网络推理节点，用于PX4-Gazebo仿真。

使用方法:
  # 使用默认参数启动
  ros2 launch neural_pos_ctrl isaac_pos_ctrl_launch.py

  # 启用调试模式
  ros2 launch neural_pos_ctrl isaac_pos_ctrl_launch.py debug_mode:=true

  # 设置自定义目标位置
  ros2 launch neural_pos_ctrl isaac_pos_ctrl_launch.py target_position:="[2.0, -1.0, 2.0]"
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node


def generate_launch_description():
    """生成launch描述"""
    package_name = "neural_pos_ctrl"

    # 获取包共享目录
    package_share_dir = get_package_share_directory(package_name)

    return LaunchDescription(
        [
            # Launch参数声明
            DeclareLaunchArgument(
                "model_path",
                default_value=PathJoinSubstitution(
                    [package_share_dir, "models", "isaac_pos_ctrl_noyaw.onnx"]
                ),
                description="ONNX模型文件路径",
            ),
            DeclareLaunchArgument(
                "target_position",
                default_value="[0.0, 0.0, 2.5]",
                description="固定目标位置 [北向, 东向, 地下] (NED坐标系，单位：米)",
            ),
            DeclareLaunchArgument(
                "target_yaw", default_value="0.0", description="固定目标偏航角 (弧度)"
            ),
            DeclareLaunchArgument(
                "control_rate", default_value="100.0", description="控制发布频率 (Hz)"
            ),
            DeclareLaunchArgument(
                "enable_input_saturation",
                default_value="true",
                description="是否启用输入饱和限制",
            ),
            DeclareLaunchArgument(
                "debug_mode", default_value="false", description="是否启用调试模式"
            ),
            DeclareLaunchArgument(
                "log_level",
                default_value="info",
                description="日志级别 (debug, info, warn, error)",
            ),
            DeclareLaunchArgument(
                "use_sim_time",
                default_value="false",
                description="是否使用仿真时间 (仅在Gazebo中有效)",
            ),
            DeclareLaunchArgument(
                "namespace", default_value="", description="节点命名空间"
            ),
            # 主推理节点
            Node(
                package=package_name,
                executable="pos_ctrl_node.py",
                name="pos_ctrl_node",
                namespace=LaunchConfiguration("namespace"),
                output="screen",
                emulate_tty=True,
                parameters=[
                    {
                        "model_path": LaunchConfiguration("model_path"),
                        "target_position": LaunchConfiguration("target_position"),
                        "target_yaw": LaunchConfiguration("target_yaw"),
                        "control_rate": LaunchConfiguration("control_rate"),
                        "enable_input_saturation": LaunchConfiguration(
                            "enable_input_saturation"
                        ),
                        "debug_mode": LaunchConfiguration("debug_mode"),
                        "use_sim_time": LaunchConfiguration("use_sim_time"),
                    }
                ],
                remappings=[
                    # VehicleOdometry话题重映射 (支持不同版本)
                    ("/fmu/out/vehicle_odometry", "/fmu/out/vehicle_odometry"),
                    ("/neural/mode_neural_ctrl", "/neural/mode_neural_ctrl"),
                    ("/neural/rates_sp", "/neural/rates_sp"),
                ],
            ),
            # 命令行工具 - 设置目标位置 (暂时禁用，因为xterm未安装)
            # Node(
            #     package=package_name,
            #     executable='set_target_pos.py',
            #     name='set_target_pos_tool',
            #     namespace=LaunchConfiguration('namespace'),
            #     prefix=['xterm', '-e'],
            #     emulate_tty=True,
            #     parameters=[{
            #         'position': LaunchConfiguration('target_position'),
            #         'yaw': LaunchConfiguration('target_yaw')
            #     }],
            #     # 注释掉这个条件，因为它会导致 'bool' object is not iterable 错误
            #     # condition=IfCondition(False)  # 默认禁用，作为工具使用
            # )
        ]
    )
