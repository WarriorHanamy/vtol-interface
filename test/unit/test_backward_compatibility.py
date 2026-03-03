#!/usr/bin/env python3
"""
Test suite for Unit - Backward Compatibility with Existing Diagnostics scenario.
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


def test_print_paths_preserves_existing_lines():
    """Case 1: --print-paths output contains all original lines (PYTHON_CMD, ROS_DISTRO, ROS_SETUP, package imports)."""
    wrapper_path = get_wrapper_script_path()

    try:
        # Run wrapper with --print-paths
        env = os.environ.copy()
        env["ROS_DISTRO"] = "humble"

        result = subprocess.run(
            [str(wrapper_path), "--print-paths"],
            env=env,
            capture_output=True,
            text=True,
            timeout=5,
        )

        # Verify all original lines are present
        assert result.returncode == 0, f"Wrapper failed: {result.stderr}"

        # Check for header
        assert "=== Python Entry Point Paths ===" in result.stdout, (
            f"Expected header in output, got: {result.stdout}"
        )

        # Check for PYTHON_CMD
        assert "PYTHON_CMD:" in result.stdout, (
            f"Expected 'PYTHON_CMD:' in output, got: {result.stdout}"
        )
        assert "uv run --no-sync python" in result.stdout, (
            f"Expected 'uv run --no-sync python' in output, got: {result.stdout}"
        )

        # Check for ROS_DISTRO (should still be there)
        assert "ROS_DISTRO:" in result.stdout, (
            f"Expected 'ROS_DISTRO:' in output, got: {result.stdout}"
        )

        # Check for ROS_SETUP (should still be there)
        assert "ROS_SETUP:" in result.stdout, (
            f"Expected 'ROS_SETUP:' in output, got: {result.stdout}"
        )

        # Check for footer
        assert "================================" in result.stdout, (
            f"Expected footer in output, got: {result.stdout}"
        )

    finally:
        pass


def test_print_paths_preserves_package_import_checks():
    """Case 2: --print-paths output still contains Python package import verification (onnxruntime, numpy, yaml)."""
    wrapper_path = get_wrapper_script_path()

    try:
        # Run wrapper with --print-paths
        env = os.environ.copy()
        env["ROS_DISTRO"] = "humble"

        result = subprocess.run(
            [str(wrapper_path), "--print-paths"],
            env=env,
            capture_output=True,
            text=True,
            timeout=5,
        )

        # Verify package import checks are still present
        assert result.returncode == 0, f"Wrapper failed: {result.stderr}"

        # Check for package imports (success or failure messages)
        # The exact format may be "✓ onnxruntime imported from:" or "✗ onnxruntime import failed:"
        assert "onnxruntime" in result.stdout, (
            f"Expected 'onnxruntime' in output, got: {result.stdout}"
        )
        assert "numpy" in result.stdout, (
            f"Expected 'numpy' in output, got: {result.stdout}"
        )
        assert "yaml" in result.stdout, (
            f"Expected 'yaml' in output, got: {result.stdout}"
        )

        # Check for import format (either success or failure)
        assert "imported from:" in result.stdout or "import failed:" in result.stdout, (
            f"Expected import format in output, got: {result.stdout}"
        )

    finally:
        pass
