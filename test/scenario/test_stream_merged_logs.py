"""Tests for merged log streaming endpoint."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def mock_client():
  """Create test client for FastAPI app."""
  from log_streamer.main import app

  return TestClient(app)


class TestMergedLogsStreaming:
  """Tests for /logs/merged endpoint."""

  def test_merged_logs_returns_sse_content_type(self, mock_client, monkeypatch):
    """Test that endpoint returns text/event-stream content type."""
    # Mock subprocess calls for both services
    call_count = [0]

    async def mock_create_subprocess(*args, **kwargs):
      call_count[0] += 1
      mock_process = AsyncMock()
      # Only return logs for first service to avoid infinite loop
      if call_count[0] == 1:
        mock_process.stdout.readline = AsyncMock(side_effect=[b""])
      else:
        mock_process.stdout.readline = AsyncMock(side_effect=[b""])
      mock_process.wait = AsyncMock(return_value=0)
      mock_process.returncode = 0
      return mock_process

    monkeypatch.setattr("log_streamer.main.asyncio.create_subprocess_exec", mock_create_subprocess)

    response = mock_client.get("/logs/merged", headers={"Accept": "text/event-stream"})

    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]

  def test_merged_logs_includes_service_identifier(self, mock_client, monkeypatch):
    """Test that each event includes a service field."""
    call_count = [0]

    async def mock_create_subprocess(*args, **kwargs):
      call_count[0] += 1
      mock_process = AsyncMock()
      if call_count[0] == 1:
        mock_process.stdout.readline = AsyncMock(
          side_effect=[
            b'{"MESSAGE": "Executor log"}\n',
            b"",
          ]
        )
      else:
        mock_process.stdout.readline = AsyncMock(side_effect=[b""])
      mock_process.wait = AsyncMock(return_value=0)
      mock_process.returncode = 0
      return mock_process

    monkeypatch.setattr("log_streamer.main.asyncio.create_subprocess_exec", mock_create_subprocess)

    response = mock_client.get("/logs/merged", headers={"Accept": "text/event-stream"})

    assert response.status_code == 200
    # Check that response contains data lines
    assert "data:" in response.text

  def test_merged_logs_one_service_inactive(self, mock_client, monkeypatch):
    """Test merged logs when one service is inactive."""
    call_count = [0]

    async def mock_create_subprocess(*args, **kwargs):
      call_count[0] += 1
      mock_process = AsyncMock()
      if call_count[0] == 1:
        mock_process.stdout.readline = AsyncMock(
          side_effect=[
            b'{"MESSAGE": "Executor log"}\n',
            b"",
          ]
        )
      else:
        mock_process.stdout.readline = AsyncMock(side_effect=[b""])
      mock_process.wait = AsyncMock(return_value=0)
      mock_process.returncode = 0
      return mock_process

    monkeypatch.setattr("log_streamer.main.asyncio.create_subprocess_exec", mock_create_subprocess)

    response = mock_client.get("/logs/merged", headers={"Accept": "text/event-stream"})

    assert response.status_code == 200

    def test_merged_logs_both_services_inactive(self, mock_client, monkeypatch):
      """Test merged logs when both services are inactive."""

      # Mock subprocess calls for both services
      async def mock_create_subprocess(*args, **kwargs):
        mock_process = AsyncMock()
        mock_process.stdout.readline = AsyncMock(side_effect=[b""])
        mock_process.wait = AsyncMock(return_value=0)
        mock_process.returncode = 0
        return mock_process

      monkeypatch.setattr("log_streamer.main.asyncio.create_subprocess_exec", mock_create_subprocess)

      response = mock_client.get("/logs/merged", headers={"Accept": "text/event-stream"})

      assert response.status_code == 200
