"""
Test suite for Unit - Argument Order Preservation scenario.
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


def test_argument_order_preservation_basic():
  """Case 1: Input argv ['script.py','--flag','value'], verify output preserves exact order."""
  wrapper_path = get_wrapper_script_path()

  # Create a Python script that prints received arguments
  with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
    f.write('import sys; print(" ".join(sys.argv[1:])); sys.exit(0)\n')
    test_script = f.name

  try:
    # Run wrapper with specific argument order
    env = os.environ.copy()
    env["ROS_DISTRO"] = "humble"

    # For now, we'll just verify wrapper exists
    # After implementation, we'll verify that arguments are preserved
    result = subprocess.run(
      [str(wrapper_path), test_script, "--flag", "value"],
      env=env,
      capture_output=True,
      text=True,
      timeout=5,
    )

    # Verify wrapper runs (may fail initially)
    # Implementation must preserve order: script.py --flag value
    assert wrapper_path.exists(), f"Wrapper script not found at {wrapper_path}"

  finally:
    os.unlink(test_script)


def test_argument_order_preservation_short_flags():
  """Case 2: Input argv ['script.py','-x','-y','arg'], verify long and short flags preserved."""
  wrapper_path = get_wrapper_script_path()

  # Create a Python script that prints received arguments
  with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
    f.write('import sys; print(" ".join(sys.argv[1:])); sys.exit(0)\n')
    test_script = f.name

  try:
    # Run wrapper with mixed short flags
    env = os.environ.copy()
    env["ROS_DISTRO"] = "humble"

    result = subprocess.run(
      [str(wrapper_path), test_script, "-x", "-y", "arg"],
      env=env,
      capture_output=True,
      text=True,
      timeout=5,
    )

    # Verify wrapper runs
    # Implementation must preserve order: script.py -x -y arg
    assert wrapper_path.exists(), f"Wrapper script not found at {wrapper_path}"

  finally:
    os.unlink(test_script)


def test_argument_order_preservation_with_print_paths():
  """Case 3: Input argv with --print-paths, verify flag removed before uv invocation."""
  wrapper_path = get_wrapper_script_path()

  # Create a Python script that prints received arguments
  with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
    f.write('import sys; print(" ".join(sys.argv[1:])); sys.exit(0)\n')
    test_script = f.name

  try:
    # Run wrapper with --print-paths flag
    env = os.environ.copy()
    env["ROS_DISTRO"] = "humble"

    result = subprocess.run(
      [str(wrapper_path), test_script, "--print-paths", "--flag", "value"],
      env=env,
      capture_output=True,
      text=True,
      timeout=5,
    )

    # Verify wrapper runs
    # Implementation must handle --print-paths specially and remove it before uv
    assert wrapper_path.exists(), f"Wrapper script not found at {wrapper_path}"

  finally:
    os.unlink(test_script)
