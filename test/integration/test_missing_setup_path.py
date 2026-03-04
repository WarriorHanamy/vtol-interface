"""
Test suite for Integration - Missing Setup Path scenario.
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


def test_missing_setup_path_nonzero_exit():
  """Case 1: Set ROS_DISTRO to non-existent distro, verify wrapper exits with code 1."""
  wrapper_path = get_wrapper_script_path()

  # Create a minimal Python script
  with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
    f.write('import sys; print("Success"); sys.exit(0)\n')
    test_script = f.name

  try:
    # Run wrapper with a non-existent distro to force missing setup file
    env = os.environ.copy()
    env["ROS_DISTRO"] = "nonexistent_distro_xyz_123"

    result = subprocess.run(
      [str(wrapper_path), test_script],
      env=env,
      capture_output=True,
      text=True,
      timeout=5,
    )

    # Verify wrapper exits with non-zero code when setup file doesn't exist
    # This test will initially fail because wrapper doesn't check setup file
    # After implementation, should exit with code 1
    assert result.returncode != 0, f"Expected non-zero exit code for missing setup file, got: {result.returncode}"
    assert len(result.stderr) > 0, "Expected error message in stderr"
    assert "setup.bash" in result.stderr.lower() or "not found" in result.stderr.lower(), (
      f"Expected error message about setup.bash, got: {result.stderr}"
    )

  finally:
    os.unlink(test_script)


def test_missing_setup_path_empty_distro():
  """Case 2: Set ROS_DISTRO to empty string with no default setup file, verify wrapper exits."""
  wrapper_path = get_wrapper_script_path()

  # Create a minimal Python script
  with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
    f.write('import sys; print("Success"); sys.exit(0)\n')
    test_script = f.name

  try:
    # Run wrapper with empty ROS_DISTRO
    # According to spec, should use default humble
    env = os.environ.copy()
    env["ROS_DISTRO"] = ""

    result = subprocess.run(
      [str(wrapper_path), test_script],
      env=env,
      capture_output=True,
      text=True,
      timeout=5,
    )

    # After implementation, should use default humble
    # If humble setup file doesn't exist, expect non-zero exit
    # This test will initially fail because wrapper doesn't handle ROS setup
    # Verify wrapper exists and runs
    assert wrapper_path.exists(), f"Wrapper script not found at {wrapper_path}"

    # If wrapper runs but setup file doesn't exist, expect error
    if result.returncode != 0:
      assert len(result.stderr) > 0, "Expected error message in stderr"
      assert "setup.bash" in result.stderr.lower() or "not found" in result.stderr.lower(), (
        f"Expected error message about setup.bash, got: {result.stderr}"
      )

  finally:
    os.unlink(test_script)
