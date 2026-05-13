"""BrowserWorkerClient tests."""

import httpx
import pytest

from app.browser.remote.client import BrowserWorkerClient


@pytest.mark.asyncio
async def test_browser_worker_client_create_session_and_action() -> None:
    """Client 应规范化 mock worker runtime 响应。"""

    async def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/sessions":
            return httpx.Response(201, json={"success": True, "remote_session_id": "remote-1", "message": "created"})
        if request.url.path == "/actions":
            return httpx.Response(
                200,
                json={
                    "success": True,
                    "remote_action_id": "action-1",
                    "message": "done",
                    "data": {"page_title": "Mock"},
                },
            )
        return httpx.Response(404, json={"success": False, "message": "missing", "error": "missing"})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://worker") as http_client:
        client = BrowserWorkerClient(base_url="http://worker", http_client=http_client)
        session_result = await client.create_session(payload={"workspace_id": "workspace-a"})
        action_result = await client.execute_action(
            payload={"remote_session_id": "remote-1", "action_type": "navigate", "target": "https://example.com"},
        )

    assert session_result.success is True
    assert session_result.data["remote_session_id"] == "remote-1"
    assert action_result.success is True
    assert action_result.data["remote_action_id"] == "action-1"
    assert action_result.data["page_title"] == "Mock"


@pytest.mark.asyncio
async def test_browser_worker_client_reports_errors() -> None:
    """Client 应返回结构化错误而不是抛出未处理异常。"""

    async def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"success": False, "message": "boom", "error": "worker error"})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://worker") as http_client:
        client = BrowserWorkerClient(base_url="http://worker", retry_count=0, http_client=http_client)
        result = await client.health_check()

    assert result.success is False
    assert result.error == "worker error"
    assert result.status_code == 500
