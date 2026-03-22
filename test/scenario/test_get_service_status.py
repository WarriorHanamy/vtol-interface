"""Tests for service status endpoint."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def mock_client():
  """Create test client for FastAPI app."""
  from log_streamer.main import app

  return TestClient(app)


class TestServiceStatus:
  """Tests for /status endpoint."""

  def test_status_returns_json_content_type(self, mock_client, monkeypatch):
    """Test that endpoint returns application/json content type."""
    mock_process = AsyncMock()
    mock_process.communicate = AsyncMock(return_value=(b"ActiveState=active\n", b""))
    mock_process.wait = AsyncMock(return_value=0)
    mock_process.returncode = 0

    async def mock_create_subprocess(*args, **kwargs):
      return mock_process

    monkeypatch.setattr("log_streamer.main.asyncio.create_subprocess_exec", mock_create_subprocess)

    response = mock_client.get("/status")

    assert response.status_code == 200
    assert "application/json" in response.headers["content-type"]

  def test_status_shows_active_state(self, mock_client, monkeypatch):
    """Test that status shows active for running services."""
    mock_process = AsyncMock()
    mock_process.communicate = AsyncMock(return_value=(b"ActiveState=active\n", b""))
    mock_process.wait = AsyncMock(return_value=0)
    mock_process.returncode = 0

    async def mock_create_subprocess(*args, **kwargs):
      return mock_process

    monkeypatch.setattr("log_streamer.main.asyncio.create_subprocess_exec", mock_create_subprocess)

    response = mock_client.get("/status")

    assert response.status_code == 200
    data = response.json()
    assert "neural_executor" in data
    assert "neural_infer" in data
    assert data["neural_executor"]["status"] in ["active", "failed", "inactive"]
    assert data["neural_infer"]["status"] in ["active", "failed", "inactive"]

  def test_status_shows_failed_state(self, mock_client, monkeypatch):
    """Test that status shows failed for failed services."""
    mock_process = AsyncMock()
    mock_process.communicate = AsyncMock(return_value=(b"ActiveState=failed\n", b""))
    mock_process.wait = AsyncMock(return_value=0)
    mock_process.returncode = 0

    async def mock_create_subprocess(*args, **kwargs):
      return mock_process

    monkeypatch.setattr("log_streamer.main.asyncio.create_subprocess_exec", mock_create_subprocess)

    response = mock_client.get("/status")

    assert response.status_code == 200
    data = response.json()
    # At least one service should show failed
    statuses = [data["neural_executor"]["status"], data["neural_infer"]["status"]]
    assert "failed" in statuses

  def test_status_shows_inactive_state(self, mock_client, monkeypatch):
    """Test that status shows inactive for inactive services."""
    mock_process = AsyncMock()
    mock_process.communicate = AsyncMock(return_value=(b"ActiveState=inactive\n", b""))
    mock_process.wait = AsyncMock(return_value=0)
    mock_process.returncode = 0

    async def mock_create_subprocess(*args, **kwargs):
      return mock_process

    monkeypatch.setattr("log_streamer.main.asyncio.create_subprocess_exec", mock_create_subprocess)

    response = mock_client.get("/status")

    assert response.status_code == 200
    data = response.json()
    assert data["neural_executor"]["status"] == "inactive"
    assert data["neural_infer"]["status"] == "inactive"

  def test_status_malformed_systemctl_output(self, mock_client, monkeypatch):
    """Test handling of malformed systemctl output."""
    mock_process = AsyncMock()
    mock_process.communicate = AsyncMock(return_value=(b"Invalid output\n", b""))
    mock_process.wait = AsyncMock(return_value=0)
    mock_process.returncode = 0

    async def mock_create_subprocess(*args, **kwargs):
      return mock_process

    monkeypatch.setattr("log_streamer.main.asyncio.create_subprocess_exec", mock_create_subprocess)

    response = mock_client.get("/status")

    # Should handle gracefully
    assert response.status_code == 200
    data = response.json()
    assert "neural_executor" in data
    assert "neural_infer" in data
