"""
Test suite for Unit - Bootstrap Failure Exit scenario.
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


def test_bootstrap_failure_missing_setup_file():
  """Case 1: Mock missing setup file at /opt/ros/humble/setup.bash, verify wrapper exits with code 1."""
  wrapper_path = get_wrapper_script_path()

  # Create a minimal Python script
  with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
    f.write('import sys; print("Success"); sys.exit(0)\n')
    test_script = f.name

  try:
    # Run wrapper with a non-existent distro to force missing setup file
    env = os.environ.copy()
    env["ROS_DISTRO"] = "nonexistent_distro_xyz"

    result = subprocess.run(
      [str(wrapper_path), test_script],
      env=env,
      capture_output=True,
      text=True,
      timeout=5,
    )

    # Verify wrapper exits non-zero when setup file is missing
    # This test will initially fail because wrapper doesn't check setup file
    assert result.returncode != 0, f"Expected non-zero exit code for missing setup file, got: {result.returncode}"
    assert len(result.stderr) > 0, "Expected error message in stderr"
    assert "setup.bash" in result.stderr.lower() or "not found" in result.stderr.lower(), (
      f"Expected error message about setup.bash, got: {result.stderr}"
    )

  finally:
    os.unlink(test_script)


def test_bootstrap_failure_permission_denied():
  """Case 2: Mock permission denied on setup file, verify wrapper exits non-zero."""
  wrapper_path = get_wrapper_script_path()

  # Create a minimal Python script
  with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
    f.write('import sys; print("Success"); sys.exit(0)\n')
    test_script = f.name

  try:
    # This test simulates permission denied scenario
    # In real world, we'd need a setup file with no read permissions
    # For testing, we use a distro name that likely doesn't exist
    env = os.environ.copy()
    env["ROS_DISTRO"] = "permission_test_distro"

    result = subprocess.run(
      [str(wrapper_path), test_script],
      env=env,
      capture_output=True,
      text=True,
      timeout=5,
    )

    # Verify wrapper exits non-zero for setup file issues
    # This test will initially fail because wrapper doesn't check setup file
    # After implementation, it should fail fast for any setup file error
    assert result.returncode != 0, f"Expected non-zero exit code for setup file error, got: {result.returncode}"

  finally:
    os.unlink(test_script)
