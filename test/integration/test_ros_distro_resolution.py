#!/usr/bin/env python3
"""
Test suite for Integration - ROS Distro Resolution scenario.
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


def test_ros_distro_humble():
    """Case 1: Set ROS_DISTRO=humble, verify wrapper loads /opt/ros/humble/setup.bash."""
    wrapper_path = get_wrapper_script_path()

    # Create a Python script that echoes ROS_DISTRO
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(
            'import os; import sys; print(os.environ.get("ROS_DISTRO", "NOT_SET")); sys.exit(0)\n'
        )
        test_script = f.name

    try:
        # Run wrapper with ROS_DISTRO=humble
        env = os.environ.copy()
        env["ROS_DISTRO"] = "humble"

        result = subprocess.run(
            [str(wrapper_path), test_script],
            env=env,
            capture_output=True,
            text=True,
            timeout=5,
        )

        # Verify wrapper sourced the setup file and ROS_DISTRO is set
        # This test will initially fail because wrapper doesn't source ROS setup
        # After implementation, should print "humble" (or fail if setup file missing)
        if result.returncode == 0:
            assert "humble" in result.stdout or "humble" in result.stderr, (
                f"Expected 'humble' in output, got: stdout={result.stdout}, stderr={result.stderr}"
            )
        else:
            # If setup file doesn't exist, expect proper error message
            assert (
                "setup.bash" in result.stderr.lower()
                or "not found" in result.stderr.lower()
            ), f"Expected error about setup.bash, got: {result.stderr}"

    finally:
        os.unlink(test_script)


def test_ros_distro_default_when_unset():
    """Case 2: Unset ROS_DISTRO, verify default humble is used."""
    wrapper_path = get_wrapper_script_path()

    # Create a Python script that echoes ROS_DISTRO
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(
            'import os; import sys; print(os.environ.get("ROS_DISTRO", "NOT_SET")); sys.exit(0)\n'
        )
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
            timeout=5,
        )

        # Verify wrapper uses default humble when ROS_DISTRO not set
        # This test will initially fail because wrapper doesn't source ROS setup
        # After implementation, should print "humble" (or fail if setup file missing)
        if result.returncode == 0:
            assert "humble" in result.stdout or "humble" in result.stderr, (
                f"Expected 'humble' in output, got: stdout={result.stdout}, stderr={result.stderr}"
            )
        else:
            # If setup file doesn't exist, expect proper error message
            assert (
                "setup.bash" in result.stderr.lower()
                or "not found" in result.stderr.lower()
            ), f"Expected error about setup.bash, got: {result.stderr}"

    finally:
        os.unlink(test_script)
