"""BrowserWorkerClient to standalone worker app flow tests."""

from pathlib import Path

import httpx
import pytest

from app.browser.remote.client import BrowserWorkerClient
from worker.browser_worker.config import WorkerSettings
from worker.browser_worker.playwright_runtime import PlaywrightBrowserWorkerRuntime
from worker.main import create_app, get_runtime


@pytest.mark.asyncio
async def test_browser_worker_client_talks_to_real_worker_app(fake_playwright, tmp_path: Path) -> None:  # type: ignore[no-untyped-def]
    """Client should use the Phase 20 worker protocol without mock runtime routes."""

    settings = WorkerSettings(
        WORKER_SCREENSHOT_DIR=str(tmp_path),
        browser_worker_auth_enabled=False,
        browser_worker_auth_strict=False,
    )
    runtime = PlaywrightBrowserWorkerRuntime(settings=settings)
    app = create_app(settings=settings)
    app.dependency_overrides[get_runtime] = lambda: runtime

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://browser-worker:9100") as http_client:
        client = BrowserWorkerClient(base_url="http://browser-worker:9100", retry_count=0, http_client=http_client)
        health = await client.health_check()
        session_result = await client.create_session(
            payload={
                "workspace_id": "workspace-client-flow",
                "local_browser_session_id": "local-session-client",
                "metadata": {"source": "unit-test"},
            }
        )
        remote_session_id = str(session_result.data["remote_session_id"])
        navigate = await client.execute_action(
            payload={
                "remote_session_id": remote_session_id,
                "action_type": "navigate",
                "target": "https://example.com",
                "input_payload": {},
            }
        )
        screenshot = await client.execute_action(
            payload={
                "remote_session_id": remote_session_id,
                "action_type": "screenshot",
                "input_payload": {"screenshot_name": "client-flow"},
            }
        )
        page_content = await client.execute_action(
            payload={
                "remote_session_id": remote_session_id,
                "action_type": "get_page_content",
                "input_payload": {},
            }
        )
        closed = await client.close_session(remote_session_id=remote_session_id)

    app.dependency_overrides.clear()
    await runtime.close_all()

    screenshot_path = Path(str(screenshot.data["screenshot_path"]))
    assert health.success is True
    assert session_result.success is True
    assert navigate.success is True
    assert navigate.data["page_title"] == "Example Domain"
    assert screenshot.success is True
    assert screenshot_path.exists()
    assert "Example Domain" in str(page_content.data["content"])
    assert closed.success is True
