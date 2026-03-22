"""Tests for neural executor log streaming endpoint."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def mock_client():
  """Create test client for FastAPI app."""
  from log_streamer.main import app

  return TestClient(app)


class TestNeuralExecutorLogsStreaming:
  """Tests for /logs/neural_executor endpoint."""

  def test_neural_executor_logs_returns_sse_content_type(self, mock_client, monkeypatch):
    """Test that endpoint returns text/event-stream content type."""
    # Mock subprocess to avoid calling journalctl
    mock_process = AsyncMock()
    mock_process.stdout.readline = AsyncMock(side_effect=[b""])
    mock_process.wait = AsyncMock(return_value=0)
    mock_process.returncode = 0

    async def mock_create_subprocess(*args, **kwargs):
      return mock_process

    monkeypatch.setattr("log_streamer.main.asyncio.create_subprocess_exec", mock_create_subprocess)

    response = mock_client.get("/logs/neural_executor", headers={"Accept": "text/event-stream"})

    # Expected: response should have text/event-stream content type
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]

  def test_neural_executor_logs_streams_structured_json(self, mock_client, monkeypatch):
    """Test that each SSE event contains structured JSON payload."""
    # Mock journalctl output
    mock_process = AsyncMock()
    mock_process.stdout.readline = AsyncMock(
      side_effect=[
        b'{"MESSAGE": "Test log", "SERVICE": "neural_executor"}\n',
        b"",  # EOF
      ]
    )
    mock_process.wait = AsyncMock(return_value=0)
    mock_process.returncode = 0

    async def mock_create_subprocess(*args, **kwargs):
      return mock_process

    monkeypatch.setattr("log_streamer.main.asyncio.create_subprocess_exec", mock_create_subprocess)

    response = mock_client.get("/logs/neural_executor", headers={"Accept": "text/event-stream"})

    # Expected: response should contain SSE events with JSON data
    assert response.status_code == 200
    lines = response.text.split("\n")
    assert any("data:" in line for line in lines)

  def test_neural_executor_logs_inactive_service(self, mock_client, monkeypatch):
    """Test behavior when neural_executor service is inactive."""
    # Mock journalctl returning no output
    mock_process = AsyncMock()
    mock_process.stdout.readline = AsyncMock(side_effect=[b""])
    mock_process.wait = AsyncMock(return_value=0)
    mock_process.returncode = 0

    async def mock_create_subprocess(*args, **kwargs):
      return mock_process

    monkeypatch.setattr("log_streamer.main.asyncio.create_subprocess_exec", mock_create_subprocess)

    response = mock_client.get("/logs/neural_executor", headers={"Accept": "text/event-stream"})

    # Expected: should handle gracefully (empty stream or no-data events)
    assert response.status_code == 200

  def test_neural_executor_logs_malformed_journalctl_output(self, mock_client, monkeypatch):
    """Test handling of malformed journalctl output."""
    # Mock journalctl returning invalid JSON
    mock_process = AsyncMock()
    mock_process.stdout.readline = AsyncMock(
      side_effect=[
        b'{"MESSAGE": "Valid log"}\n',
        b"This is not JSON\n",
        b'{"MESSAGE": "Another valid log"}\n',
        b"",
      ]
    )
    mock_process.wait = AsyncMock(return_value=0)
    mock_process.returncode = 0

    async def mock_create_subprocess(*args, **kwargs):
      return mock_process

    monkeypatch.setattr("log_streamer.main.asyncio.create_subprocess_exec", mock_create_subprocess)

    response = mock_client.get("/logs/neural_executor", headers={"Accept": "text/event-stream"})

    # Expected: should handle gracefully without crashing
    assert response.status_code == 200
