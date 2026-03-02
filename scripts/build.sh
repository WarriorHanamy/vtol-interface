#!/bin/bash
# Full build: config px4msgs + build workspace

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# First config px4msgs
"${SCRIPT_DIR}/config_px4msgs.sh"

# Source ROS2 setup
source "/opt/ros/${ROS_DISTRO}/setup.bash"

# Build with symlink install and compile commands export
colcon build --symlink-install \
    --cmake-args -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
