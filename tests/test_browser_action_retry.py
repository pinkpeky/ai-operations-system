"""Browser Worker action retry tests."""

import httpx
import pytest

from app.browser.remote.client import BrowserWorkerClient


@pytest.mark.asyncio
async def test_browser_worker_client_retries_action_and_records_logs() -> None:
    """远程动作失败后应按配置重试，并保留结构化 retry 日志。"""

    call_count = 0

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return httpx.Response(
                status_code=500,
                json={"success": False, "message": "temporary failure", "error": "worker busy"},
            )
        return httpx.Response(
            status_code=200,
            json={
                "success": True,
                "message": "action completed",
                "remote_action_id": "remote-action-1",
                "data": {"page_title": "Example Domain"},
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://worker") as http_client:
        client = BrowserWorkerClient(
            base_url="http://worker",
            retry_count=2,
            retry_backoff_seconds=0,
            action_timeout_seconds=1,
            http_client=http_client,
        )
        result = await client.execute_action(
            payload={
                "remote_session_id": "remote-session-1",
                "action_type": "navigate",
                "target": "https://example.com",
            }
        )

    assert call_count == 2
    assert result.success is True
    assert result.retry_count == 1
    assert result.retry_logs[0]["attempt"] == 1
    assert result.data["retry_count"] == 1
    assert result.data["retry_logs"][0]["error"] == "worker busy"


@pytest.mark.asyncio
async def test_browser_worker_client_returns_clear_error_after_retry_exhausted() -> None:
    """重试耗尽后不抛出到上层，而是返回清晰错误结果。"""

    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=503,
            json={"success": False, "message": "still unavailable", "error": "service unavailable"},
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://worker") as http_client:
        client = BrowserWorkerClient(
            base_url="http://worker",
            retry_count=1,
            retry_backoff_seconds=0,
            action_timeout_seconds=1,
            http_client=http_client,
        )
        result = await client.execute_action(
            payload={
                "remote_session_id": "remote-session-1",
                "action_type": "screenshot",
                "screenshot_name": "failed-shot",
            }
        )

    assert result.success is False
    assert result.retry_count == 1
    assert result.error == "service unavailable"
