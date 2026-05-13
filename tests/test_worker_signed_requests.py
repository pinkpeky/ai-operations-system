"""Signed Browser Worker request tests."""

from pathlib import Path

import httpx
import pytest

from app.browser.remote.client import BrowserWorkerClient
from worker.browser_worker.config import WorkerSettings, get_worker_settings
from worker.browser_worker.playwright_runtime import PlaywrightBrowserWorkerRuntime
from worker.main import create_app, get_runtime


@pytest.mark.asyncio
async def test_worker_runtime_accepts_signed_requests_and_rejects_unsigned(
    fake_playwright,  # type: ignore[no-untyped-def]
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """strict=true 时 worker runtime 要求签名 header。"""

    secret = "unit-test-worker-secret"
    monkeypatch.setenv("BROWSER_WORKER_AUTH_ENABLED", "true")
    monkeypatch.setenv("BROWSER_WORKER_AUTH_STRICT", "true")
    monkeypatch.setenv("BROWSER_WORKER_SECRET", secret)
    get_worker_settings.cache_clear()

    runtime = PlaywrightBrowserWorkerRuntime(settings=WorkerSettings(WORKER_SCREENSHOT_DIR=str(tmp_path)))
    app = create_app()
    app.dependency_overrides[get_runtime] = lambda: runtime
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://browser-worker:9100") as http_client:
        unsigned = await http_client.post(
            "/sessions",
            json={"workspace_id": "workspace-signed", "metadata": {}},
        )
        signed_client = BrowserWorkerClient(
            base_url="http://browser-worker:9100",
            retry_count=0,
            http_client=http_client,
            worker_id="worker-1",
            worker_secret=secret,
        )
        signed = await signed_client.create_session(payload={"workspace_id": "workspace-signed", "metadata": {}})

    app.dependency_overrides.clear()
    await runtime.close_all()
    get_worker_settings.cache_clear()

    assert unsigned.status_code == 401
    assert signed.success is True
    assert signed.data["remote_session_id"]
