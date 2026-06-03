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
    monkeypatch.setenv("WORKER_CLIENT_CONFIG", str(tmp_path / "missing-worker_config.yaml"))
    monkeypatch.setenv("WORKER_CLIENT_STATE_PATH", str(tmp_path / "missing-worker_state.json"))
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
        unsigned_human_control = await http_client.get("/human-control/status/remote-session")
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
    assert unsigned_human_control.status_code == 401
    assert signed.success is True
    assert signed.data["remote_session_id"]


@pytest.mark.asyncio
async def test_worker_runtime_prefers_registered_worker_state_secret(
    fake_playwright,  # type: ignore[no-untyped-def]
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """worker_state.json must be the signing source after API registration."""

    state_secret = "registered-state-worker-secret"
    env_secret = "env-fallback-worker-secret"
    config_path = tmp_path / "worker_config.yaml"
    state_path = tmp_path / "worker_state.json"
    config_path.write_text(
        "\n".join(
            [
                "server_url: http://ai-server.test",
                "worker_name: registered-worker",
                "worker_type: playwright",
                "workspace_id: production-workspace",
                "worker_secret: null",
                "worker_base_url: http://127.0.0.1:9100",
                f"state_path: {state_path.as_posix()}",
                "runtime_port: 9100",
            ]
        ),
        encoding="utf-8",
    )
    state_path.write_text(
        (
            '{"worker_id":"worker-state-1","worker_secret":"%s","server_url":"http://ai-server.test",'
            '"worker_name":"registered-worker","workspace_id":"production-workspace",'
            '"worker_base_url":"http://127.0.0.1:9100"}'
        )
        % state_secret,
        encoding="utf-8",
    )

    monkeypatch.setenv("WORKER_CLIENT_CONFIG", str(config_path))
    monkeypatch.setenv("BROWSER_WORKER_AUTH_ENABLED", "true")
    monkeypatch.setenv("BROWSER_WORKER_AUTH_STRICT", "true")
    monkeypatch.setenv("BROWSER_WORKER_SECRET", env_secret)
    get_worker_settings.cache_clear()

    runtime = PlaywrightBrowserWorkerRuntime(settings=WorkerSettings(WORKER_SCREENSHOT_DIR=str(tmp_path / "screenshots")))
    app = create_app()
    app.dependency_overrides[get_runtime] = lambda: runtime
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://browser-worker:9100") as http_client:
        stale_env_client = BrowserWorkerClient(
            base_url="http://browser-worker:9100",
            retry_count=0,
            http_client=http_client,
            worker_id="worker-state-1",
            worker_secret=env_secret,
        )
        state_client = BrowserWorkerClient(
            base_url="http://browser-worker:9100",
            retry_count=0,
            http_client=http_client,
            worker_id="worker-state-1",
            worker_secret=state_secret,
        )
        stale_env = await stale_env_client.create_session(payload={"workspace_id": "production-workspace", "metadata": {}})
        signed = await state_client.create_session(payload={"workspace_id": "production-workspace", "metadata": {}})

    app.dependency_overrides.clear()
    await runtime.close_all()
    get_worker_settings.cache_clear()

    assert stale_env.success is False
    assert stale_env.status_code == 401
    assert signed.success is True
    assert signed.data["remote_session_id"]
