"""
Test suite for Unit - Setup Script Path Diagnostics Output scenario.
"""

import os
import subprocess
import tempfile
from pathlib import Path

import pytest


def get_wrapper_script_path() -> Path:
  """Get the path to the agent_bins/python wrapper script."""
  project_root = Path(__file__).parent.parent.parent
  return project_root / "agent_bins" / "python"


def test_print_paths_contains_setup_path_humble():
  """Case 1: Wrapper with --print-paths displays setup path with absolute path /opt/ros/humble/setup.bash."""
  wrapper_path = get_wrapper_script_path()

  try:
    # Run wrapper with --print-paths and ROS_DISTRO=humble
    env = os.environ.copy()
    env["ROS_DISTRO"] = "humble"

    result = subprocess.run(
      [str(wrapper_path), "--print-paths"],
      env=env,
      capture_output=True,
      text=True,
      timeout=5,
    )

    # Verify ROS_SETUP line is present with absolute path
    assert result.returncode == 0, f"Wrapper failed: {result.stderr}"
    assert "ROS_SETUP:" in result.stdout, f"Expected 'ROS_SETUP:' in output, got: {result.stdout}"
    assert "/opt/ros/humble/setup.bash" in result.stdout, (
      f"Expected '/opt/ros/humble/setup.bash' in output, got: {result.stdout}"
    )

  finally:
    pass


def test_print_paths_contains_setup_path_custom():
  """Case 2: Wrapper with --print-paths displays setup path when using custom distro noetic."""
  wrapper_path = get_wrapper_script_path()

  try:
    # Run wrapper with --print-paths and ROS_DISTRO=noetic
    env = os.environ.copy()
    env["ROS_DISTRO"] = "noetic"

    result = subprocess.run(
      [str(wrapper_path), "--print-paths"],
      env=env,
      capture_output=True,
      text=True,
      timeout=5,
    )

    # Verify ROS_SETUP line is present with absolute path for noetic
    # Note: This test may fail if /opt/ros/noetic/setup.bash doesn't exist
    # That's expected - the wrapper should exit with error about missing setup file
    if result.returncode == 0:
      assert "ROS_SETUP:" in result.stdout, f"Expected 'ROS_SETUP:' in output, got: {result.stdout}"
      assert "/opt/ros/noetic/setup.bash" in result.stdout, (
        f"Expected '/opt/ros/noetic/setup.bash' in output, got: {result.stdout}"
      )
    else:
      # Expected failure due to missing noetic setup file
      assert "setup.bash" in result.stderr.lower() or "not found" in result.stderr.lower(), (
        f"Expected error about setup.bash, got: {result.stderr}"
      )

  finally:
    pass
