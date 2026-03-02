#!/bin/bash
# Neural executor demo launcher

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Source ROS2 and workspace setup
source "/opt/ros/${ROS_DISTRO}/setup.bash"
source "${PROJECT_DIR}/install/setup.sh"
# Launch neural demo
ros2 launch neural_executor neural_executor.launch.py
