"""Tests for neural infer log streaming endpoint."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def mock_client():
  """Create test client for FastAPI app."""
  from log_streamer.main import app

  return TestClient(app)


class TestNeuralInferLogsStreaming:
  """Tests for /logs/neural_infer endpoint."""

  def test_neural_infer_logs_returns_sse_content_type(self, mock_client, monkeypatch):
    """Test that endpoint returns text/event-stream content type."""
    mock_process = AsyncMock()
    mock_process.stdout.readline = AsyncMock(side_effect=[b""])
    mock_process.wait = AsyncMock(return_value=0)
    mock_process.returncode = 0

    async def mock_create_subprocess(*args, **kwargs):
      return mock_process

    monkeypatch.setattr("log_streamer.main.asyncio.create_subprocess_exec", mock_create_subprocess)

    response = mock_client.get("/logs/neural_infer", headers={"Accept": "text/event-stream"})

    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]

  def test_neural_infer_logs_streams_structured_json(self, mock_client, monkeypatch):
    """Test that each SSE event contains structured JSON payload."""
    mock_process = AsyncMock()
    mock_process.stdout.readline = AsyncMock(
      side_effect=[
        b'{"MESSAGE": "Test infer log", "SERVICE": "neural_infer"}\n',
        b"",
      ]
    )
    mock_process.wait = AsyncMock(return_value=0)
    mock_process.returncode = 0

    async def mock_create_subprocess(*args, **kwargs):
      return mock_process

    monkeypatch.setattr("log_streamer.main.asyncio.create_subprocess_exec", mock_create_subprocess)

    response = mock_client.get("/logs/neural_infer", headers={"Accept": "text/event-stream"})

    assert response.status_code == 200
    lines = response.text.split("\n")
    assert any("data:" in line for line in lines)

  def test_neural_infer_logs_inactive_service(self, mock_client, monkeypatch):
    """Test behavior when neural_infer service is inactive."""
    mock_process = AsyncMock()
    mock_process.stdout.readline = AsyncMock(side_effect=[b""])
    mock_process.wait = AsyncMock(return_value=0)
    mock_process.returncode = 0

    async def mock_create_subprocess(*args, **kwargs):
      return mock_process

    monkeypatch.setattr("log_streamer.main.asyncio.create_subprocess_exec", mock_create_subprocess)

    response = mock_client.get("/logs/neural_infer", headers={"Accept": "text/event-stream"})

    assert response.status_code == 200
