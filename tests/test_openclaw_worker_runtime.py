"""worker_client OpenClaw runtime API tests."""

import pytest
from httpx import ASGITransport, AsyncClient

from worker_client.config import WorkerClientConfig
from worker_client.runtime import create_worker_client_app


@pytest.mark.asyncio
async def test_worker_client_runtime_openclaw_routes() -> None:
    """worker_client serve app 应暴露 /openclaw/* mock routes。"""

    config = WorkerClientConfig(
        server_url="http://localhost:8000",
        worker_name="test-worker",
        worker_type="playwright",
        workspace_id="workspace-openclaw-runtime",
        capabilities={"browser": "chromium", "openclaw": True},
    )
    app = create_worker_client_app(config)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://worker") as client:
        health = await client.get("/openclaw/health")
        capabilities = await client.get("/openclaw/capabilities")
        action = await client.post(
            "/openclaw/actions",
            json={"action_type": "mock_inspect", "target": "https://example.com", "input_payload": {"x": 1}},
        )

    assert health.status_code == 200
    assert health.json()["provider"] == "mock"
    assert capabilities.json()["capabilities"]["real_openclaw"] is False
    assert action.json()["success"] is True
    assert action.json()["output_payload"]["real_openclaw_called"] is False
