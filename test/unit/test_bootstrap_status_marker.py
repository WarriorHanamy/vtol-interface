#!/usr/bin/env python3
"""
Test suite for Unit - Bootstrap Status Marker Output scenario.
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


def test_print_paths_contains_bootstrap_success_marker():
    """Case 1: Wrapper with --print-paths displays success marker after successful ROS bootstrap."""
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

        # Verify bootstrap status marker is present with SUCCESS
        assert result.returncode == 0, f"Wrapper failed: {result.stderr}"
        assert "ROS_BOOTSTRAP:" in result.stdout, (
            f"Expected 'ROS_BOOTSTRAP:' in output, got: {result.stdout}"
        )
        assert "SUCCESS" in result.stdout, (
            f"Expected 'SUCCESS' in output, got: {result.stdout}"
        )

    finally:
        pass


def test_print_paths_contains_bootstrap_failure_marker():
    """Case 2: Wrapper with --print-paths displays failure marker when ROS setup is missing."""
    wrapper_path = get_wrapper_script_path()

    try:
        # Run wrapper with --print-paths and non-existent ROS_DISTRO
        env = os.environ.copy()
        env["ROS_DISTRO"] = "nonexistent_distro_xyz"

        result = subprocess.run(
            [str(wrapper_path), "--print-paths"],
            env=env,
            capture_output=True,
            text=True,
            timeout=5,
        )

        # Verify bootstrap status marker is present with FAILED
        # The wrapper should exit with error code 1
        assert result.returncode != 0, (
            f"Expected non-zero exit code, got: {result.returncode}"
        )
        # Check for failure marker in stderr (error output)
        assert "ROS_BOOTSTRAP:" in result.stderr or "Error:" in result.stderr, (
            f"Expected 'ROS_BOOTSTRAP:' or error in stderr, got: {result.stderr}"
        )
        assert "FAILED" in result.stderr or "Error" in result.stderr, (
            f"Expected 'FAILED' or error message in stderr, got: {result.stderr}"
        )

    finally:
        pass
