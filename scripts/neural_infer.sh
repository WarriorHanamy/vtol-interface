#!/bin/bash
# Neural inference runner

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Source ROS2 setup
source "/opt/ros/${ROS_DISTRO}/setup.bash"
source "${PROJECT_DIR}/install/setup.sh"

cd "${PROJECT_DIR}"

# Run neural inference
./agent_bins/python "${PROJECT_DIR}/src/neural_manager/neural_pos_ctrl/neural_infer.py"
