"""BrowserWorkerClient Phase 34 runtime method tests."""

import httpx
import pytest

from app.browser.remote.client import BrowserWorkerClient


@pytest.mark.asyncio
async def test_browser_worker_client_runtime_methods() -> None:
    paths: list[str] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        paths.append(request.url.path)
        if request.url.path.endswith("/page"):
            return httpx.Response(
                200,
                json={"success": True, "message": "page", "data": {"content": "<h1>Example Domain</h1>"}},
            )
        return httpx.Response(200, json={"success": True, "message": "ok", "data": {"remote_session_id": "runtime-1"}})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://worker") as http_client:
        client = BrowserWorkerClient(base_url="http://worker", http_client=http_client, retry_count=0)
        created = await client.create_runtime_session(payload={"browser": "chromium"})
        navigated = await client.runtime_navigate(remote_session_id="runtime-1", payload={"url": "https://example.com"})
        page = await client.runtime_page(remote_session_id="runtime-1")

    assert created.success is True
    assert navigated.success is True
    assert "Example Domain" in page.data["content"]
    assert paths == [
        "/browser/session/create",
        "/browser/session/runtime-1/navigate",
        "/browser/session/runtime-1/page",
    ]
