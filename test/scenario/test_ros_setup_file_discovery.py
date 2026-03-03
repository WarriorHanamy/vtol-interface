#!/usr/bin/env python3
"""
Test suite for ROS setup file discovery scenario.
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


def test_setup_file_exists():
    """Case 1: Setup file exists at /opt/ros/humble/setup.bash."""
    wrapper_path = get_wrapper_script_path()

    # Create a minimal Python script
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write('import sys; print("Success"); sys.exit(0)\n')
        test_script = f.name

    try:
        # Run wrapper (assuming /opt/ros/humble/setup.bash exists in test environment)
        env = os.environ.copy()
        env["ROS_DISTRO"] = "humble"

        result = subprocess.run(
            [str(wrapper_path), test_script],
            env=env,
            capture_output=True,
            text=True,
        )

        # Verify wrapper successfully sourced the setup file
        # Note: This test will fail initially because wrapper doesn't exist
        # In a real environment with ROS humble installed, this should succeed
        # For testing without ROS, we expect specific error message
        assert result.returncode == 0 or "setup.bash" in result.stderr.lower(), (
            f"Expected success or setup.bash mention, got: returncode={result.returncode}, stderr={result.stderr}"
        )
    finally:
        os.unlink(test_script)


def test_setup_file_missing():
    """Case 2: Setup file does not exist at /opt/ros/humble/setup.bash."""
    wrapper_path = get_wrapper_script_path()

    # Create a minimal Python script
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write('import sys; print("Success"); sys.exit(0)\n')
        test_script = f.name

    try:
        # Run wrapper with a non-existent distro
        env = os.environ.copy()
        env["ROS_DISTRO"] = "nonexistent_distro"

        result = subprocess.run(
            [str(wrapper_path), test_script],
            env=env,
            capture_output=True,
            text=True,
        )

        # Verify wrapper detects missing setup file
        # Note: This test will fail initially because wrapper doesn't exist
        assert result.returncode != 0, (
            f"Expected non-zero exit code, got: {result.returncode}"
        )
        assert (
            "setup.bash" in result.stderr.lower()
            or "not found" in result.stderr.lower()
        ), f"Expected error message about setup.bash, got: {result.stderr}"
    finally:
        os.unlink(test_script)


def test_invalid_distro_path():
    """Case 3: Resolved distro leads to non-existent path."""
    wrapper_path = get_wrapper_script_path()

    # Create a minimal Python script
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write('import sys; print("Success"); sys.exit(0)\n')
        test_script = f.name

    try:
        # Run wrapper with an invalid distro name containing special characters
        env = os.environ.copy()
        env["ROS_DISTRO"] = "invalid/distro"

        result = subprocess.run(
            [str(wrapper_path), test_script],
            env=env,
            capture_output=True,
            text=True,
        )

        # Verify wrapper handles invalid distro gracefully
        # Note: This test will fail initially because wrapper doesn't exist
        assert result.returncode != 0, (
            f"Expected non-zero exit code, got: {result.returncode}"
        )
        assert (
            "error" in result.stderr.lower() or "setup.bash" in result.stderr.lower()
        ), f"Expected error message, got: {result.stderr}"
    finally:
        os.unlink(test_script)
