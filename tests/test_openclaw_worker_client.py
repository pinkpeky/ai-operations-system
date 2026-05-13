"""OpenClawWorkerClient tests."""

import httpx
import pytest

from app.openclaw.client import OpenClawWorkerClient


@pytest.mark.asyncio
async def test_openclaw_worker_client_calls_runtime_routes() -> None:
    """Client 应规范化 worker runtime 的 mock 响应。"""

    async def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/openclaw/health":
            return httpx.Response(200, json={"success": True, "provider": "mock", "enabled": True, "reachable": True, "mock": True})
        if request.url.path == "/openclaw/capabilities":
            return httpx.Response(
                200,
                json={"success": True, "provider": "mock", "mock": True, "capabilities": {"openclaw": True}, "actions": ["execute_action"]},
            )
        if request.url.path == "/openclaw/actions":
            return httpx.Response(
                200,
                json={
                    "success": True,
                    "action_type": "mock_action",
                    "output_payload": {"real_openclaw_called": False},
                    "duration_ms": 1,
                    "provider": "mock",
                    "mock": True,
                },
            )
        return httpx.Response(404, json={"success": False, "error": "missing"})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://worker") as http_client:
        client = OpenClawWorkerClient(base_url="http://worker", http_client=http_client)
        health = await client.health_check()
        capabilities = await client.capabilities()
        action = await client.execute_action(payload={"action_type": "mock_action"})

    assert health.success is True
    assert capabilities.data["capabilities"]["openclaw"] is True
    assert action.success is True
    assert action.data["output_payload"]["real_openclaw_called"] is False
