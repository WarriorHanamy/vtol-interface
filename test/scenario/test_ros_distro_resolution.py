"""
Test suite for ROS_DISTRO resolution scenario.
"""

import os
import subprocess
import tempfile
from pathlib import Path

import pytest


def get_wrapper_script_path() -> Path:
  """Get the path to the wrapper script."""
  project_root = Path(__file__).parent.parent.parent
  return project_root / "scripts" / "ros_wrapper.sh"


def test_ros_distro_set():
  """Case 1: ROS_DISTRO environment variable is set to 'foxy'."""
  wrapper_path = get_wrapper_script_path()

  # Create a minimal Python script to echo ROS_DISTRO
  with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
    f.write('import os; import sys; print(os.environ.get("ROS_DISTRO", "NOT_SET")); sys.exit(0)\n')
    test_script = f.name

  try:
    # Run wrapper with ROS_DISTRO=foxy
    env = os.environ.copy()
    env["ROS_DISTRO"] = "foxy"

    result = subprocess.run(
      [str(wrapper_path), test_script],
      env=env,
      capture_output=True,
      text=True,
    )

    # Verify the Python script received ROS_DISTRO=foxy
    # Note: This test will fail initially because wrapper doesn't exist
    assert "foxy" in result.stdout or "foxy" in result.stderr, (
      f"Expected 'foxy' in output, got: stdout={result.stdout}, stderr={result.stderr}"
    )
  finally:
    os.unlink(test_script)


def test_ros_distro_unset():
  """Case 2: ROS_DISTRO environment variable is not set."""
  wrapper_path = get_wrapper_script_path()

  # Create a minimal Python script to echo ROS_DISTRO
  with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
    f.write('import os; import sys; print(os.environ.get("ROS_DISTRO", "NOT_SET")); sys.exit(0)\n')
    test_script = f.name

  try:
    # Run wrapper without ROS_DISTRO
    env = os.environ.copy()
    env.pop("ROS_DISTRO", None)

    result = subprocess.run(
      [str(wrapper_path), test_script],
      env=env,
      capture_output=True,
      text=True,
    )

    # Verify the Python script received ROS_DISTRO=humble (default)
    # Note: This test will fail initially because wrapper doesn't exist
    assert "humble" in result.stdout or "humble" in result.stderr, (
      f"Expected 'humble' in output, got: stdout={result.stdout}, stderr={result.stderr}"
    )
  finally:
    os.unlink(test_script)


def test_ros_distro_empty():
  """Case 3: ROS_DISTRO environment variable is set but empty."""
  wrapper_path = get_wrapper_script_path()

  # Create a minimal Python script to echo ROS_DISTRO
  with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
    f.write('import os; import sys; print(os.environ.get("ROS_DISTRO", "NOT_SET")); sys.exit(0)\n')
    test_script = f.name

  try:
    # Run wrapper with ROS_DISTRO=""
    env = os.environ.copy()
    env["ROS_DISTRO"] = ""

    result = subprocess.run(
      [str(wrapper_path), test_script],
      env=env,
      capture_output=True,
      text=True,
    )

    # Verify the Python script received ROS_DISTRO=humble (default for empty)
    # Note: This test will fail initially because wrapper doesn't exist
    assert "humble" in result.stdout or "humble" in result.stderr, (
      f"Expected 'humble' in output, got: stdout={result.stdout}, stderr={result.stderr}"
    )
  finally:
    os.unlink(test_script)
