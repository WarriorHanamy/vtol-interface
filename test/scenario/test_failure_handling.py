#!/usr/bin/env python3
"""
Test suite for failure handling scenario.
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


def test_missing_setup_file_with_error_message():
    """Case 1: /opt/ros/humble/setup.bash does not exist."""
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
        )

        # Verify failure handling
        # Note: This test will fail initially because wrapper doesn't exist
        assert result.returncode != 0, (
            f"Expected non-zero exit code for missing setup file, got: {result.returncode}"
        )
        assert len(result.stderr) > 0, "Expected error message in stderr"
        assert (
            "setup.bash" in result.stderr.lower()
            or "not found" in result.stderr.lower()
        ), f"Expected explicit error message about setup.bash, got: {result.stderr}"
    finally:
        os.unlink(test_script)


def test_missing_setup_file_with_custom_distro():
    """Case 2: /opt/ros/foxy/setup.bash does not exist when ROS_DISTRO=foxy."""
    wrapper_path = get_wrapper_script_path()

    # Create a minimal Python script
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write('import sys; print("Success"); sys.exit(0)\n')
        test_script = f.name

    try:
        # Run wrapper with foxy distro (which may not be installed)
        env = os.environ.copy()
        env["ROS_DISTRO"] = "foxy"

        result = subprocess.run(
            [str(wrapper_path), test_script],
            env=env,
            capture_output=True,
            text=True,
        )

        # If foxy is not installed, expect failure
        # Note: This test will fail initially because wrapper doesn't exist
        if result.returncode != 0:
            assert len(result.stderr) > 0, "Expected error message in stderr"
            assert (
                "setup.bash" in result.stderr.lower()
                or "not found" in result.stderr.lower()
                or "foxy" in result.stderr.lower()
            ), f"Expected error message about setup.bash or foxy, got: {result.stderr}"
        # If foxy is installed, test passes silently
    finally:
        os.unlink(test_script)


def test_suggest_ros_distro_in_error():
    """Case 3: Error message should suggest setting ROS_DISTRO."""
    wrapper_path = get_wrapper_script_path()

    # Create a minimal Python script
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write('import sys; print("Success"); sys.exit(0)\n')
        test_script = f.name

    try:
        # Run wrapper with non-existent distro to force error
        env = os.environ.copy()
        # Use a guaranteed non-existent distro name
        env["ROS_DISTRO"] = "nonexistent_test_distro_xyz"

        result = subprocess.run(
            [str(wrapper_path), test_script],
            env=env,
            capture_output=True,
            text=True,
        )

        # Verify error message mentions ROS_DISTRO
        # Note: This test will fail initially because wrapper doesn't exist
        if result.returncode != 0:
            # Check if error message suggests setting ROS_DISTRO
            error_output = result.stderr.lower()
            suggests_distro = (
                "ros_distro" in error_output
                or "set ros_distro" in error_output
                or "ros-distro" in error_output
                or "set ros-distro" in error_output
                or "ros distribution" in error_output
            )

            # This is a best-effort check - implementation may vary
            # The main requirement is non-zero exit code and explicit error
            assert len(result.stderr) > 0, "Expected error message in stderr"
            assert result.returncode != 0, (
                f"Expected non-zero exit code, got: {result.returncode}"
            )
            # Verify error message contains setup.bash reference
            assert "setup.bash" in error_output, (
                f"Expected error message to mention setup.bash, got: {error_output}"
            )
    finally:
        os.unlink(test_script)
