/****************************************************************************
 * Copyright (c) 2023 PX4 Development Team.
 * SPDX-License-Identifier: BSD-3-Clause
 ****************************************************************************/

#include "rclcpp/rclcpp.hpp"

#include <neural_executor/executor.hpp>
#include <neural_executor/neural_ctrl_mode.hpp>
#include <neural_executor/executor_entry_mode.hpp>
#include <px4_ros2/components/node_with_mode.hpp>

using NeuralTaskNodeWithModeExecutor = px4_ros2::NodeWithModeExecutor<NeuralExecutor, ExecutorEntryMode, NeuralCtrlMode>;

static const std::string kNodeName = "neural_executor";
static const bool kEnableDebugOutput = true;

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<NeuralTaskNodeWithModeExecutor>(kNodeName, kEnableDebugOutput));
  rclcpp::shutdown();
  return 0;
}
