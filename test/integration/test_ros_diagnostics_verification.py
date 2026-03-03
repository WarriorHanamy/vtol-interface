#!/usr/bin/env python3
"""
Test suite for Integration - ROS Diagnostics Verification with Real Wrapper scenario.
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


def test_print_paths_includes_ros_lines_and_package_imports():
    """Case 1: Verify --print-paths includes ROS lines plus previous package import checks."""
    wrapper_path = get_wrapper_script_path()

    try:
        # Run wrapper with --print-paths using real ROS integration
        env = os.environ.copy()
        env["ROS_DISTRO"] = "humble"

        result = subprocess.run(
            [str(wrapper_path), "--print-paths"],
            env=env,
            capture_output=True,
            text=True,
            timeout=10,
        )

        # Verify all ROS diagnostics lines are present
        assert result.returncode == 0, f"Wrapper failed: {result.stderr}"

        # Check for ROS_DISTRO line
        assert "ROS_DISTRO:" in result.stdout, (
            f"Expected 'ROS_DISTRO:' in output, got: {result.stdout}"
        )
        assert "humble" in result.stdout, (
            f"Expected 'humble' in output, got: {result.stdout}"
        )

        # Check for ROS_SETUP line
        assert "ROS_SETUP:" in result.stdout, (
            f"Expected 'ROS_SETUP:' in output, got: {result.stdout}"
        )
        assert "/opt/ros/humble/setup.bash" in result.stdout, (
            f"Expected '/opt/ros/humble/setup.bash' in output, got: {result.stdout}"
        )

        # Check for ROS_BOOTSTRAP status line
        assert "ROS_BOOTSTRAP:" in result.stdout, (
            f"Expected 'ROS_BOOTSTRAP:' in output, got: {result.stdout}"
        )
        assert "SUCCESS" in result.stdout, (
            f"Expected 'SUCCESS' in output, got: {result.stdout}"
        )

        # Verify package import checks are still present
        assert "onnxruntime" in result.stdout, (
            f"Expected 'onnxruntime' in output, got: {result.stdout}"
        )
        assert "numpy" in result.stdout, (
            f"Expected 'numpy' in output, got: {result.stdout}"
        )
        assert "yaml" in result.stdout, (
            f"Expected 'yaml' in output, got: {result.stdout}"
        )

        # Check for import format
        assert "imported from:" in result.stdout or "import failed:" in result.stdout, (
            f"Expected import format in output, got: {result.stdout}"
        )

    finally:
        pass


def test_print_paths_missing_setup_shows_failure_details():
    """Case 2: Verify missing setup path surfaces non-zero status with ROS failure details."""
    wrapper_path = get_wrapper_script_path()

    try:
        # Run wrapper with --print-paths using non-existent ROS distro
        env = os.environ.copy()
        env["ROS_DISTRO"] = "nonexistent_distro_xyz"

        result = subprocess.run(
            [str(wrapper_path), "--print-paths"],
            env=env,
            capture_output=True,
            text=True,
            timeout=10,
        )

        # Verify non-zero exit status
        assert result.returncode != 0, (
            f"Expected non-zero exit code, got: {result.returncode}"
        )

        # Verify failure details are present
        # Check for error message about missing setup file
        assert (
            "setup.bash" in result.stderr.lower()
            or "not found" in result.stderr.lower()
        ), f"Expected error about setup.bash, got: {result.stderr}"

        # Check for ROS_BOOTSTRAP failure marker
        # Note: This might be in stderr since the wrapper exits before printing --print-paths output
        assert "ROS_BOOTSTRAP:" in result.stderr or "Error:" in result.stderr, (
            f"Expected 'ROS_BOOTSTRAP:' or error in stderr, got: {result.stderr}"
        )
        assert "FAILED" in result.stderr or "Error" in result.stderr, (
            f"Expected 'FAILED' or error message in stderr, got: {result.stderr}"
        )

        # Check for helpful error message suggesting ROS_DISTRO
        assert "ROS_DISTRO" in result.stderr or "ros" in result.stderr.lower(), (
            f"Expected mention of ROS_DISTRO or ros in error, got: {result.stderr}"
        )

    finally:
        pass
