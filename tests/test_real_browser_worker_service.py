"""Standalone browser-worker service tests."""

from pathlib import Path

import httpx
import pytest

from worker.browser_worker.config import WorkerSettings
from worker.browser_worker.playwright_runtime import PlaywrightBrowserWorkerRuntime
from worker.main import create_app, get_runtime


@pytest.mark.asyncio
async def test_browser_worker_service_executes_basic_flow(fake_playwright, tmp_path: Path) -> None:  # type: ignore[no-untyped-def]
    """Worker service should create a real runtime session and execute safe actions."""

    settings = WorkerSettings(WORKER_SCREENSHOT_DIR=str(tmp_path))
    runtime = PlaywrightBrowserWorkerRuntime(settings=settings)
    app = create_app()
    app.dependency_overrides[get_runtime] = lambda: runtime

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://worker") as client:
        health = await client.get("/health")
        session_response = await client.post(
            "/sessions",
            json={
                "workspace_id": "workspace-phase20",
                "local_browser_session_id": "local-session-1",
                "metadata": {"test": "phase20"},
            },
        )
        remote_session_id = session_response.json()["remote_session_id"]
        navigate = await client.post(
            "/actions",
            json={
                "remote_session_id": remote_session_id,
                "action_type": "navigate",
                "target": "https://example.com",
                "input_payload": {},
            },
        )
        screenshot = await client.post(
            "/actions",
            json={
                "remote_session_id": remote_session_id,
                "action_type": "screenshot",
                "input_payload": {"screenshot_name": "phase20-example"},
            },
        )
        content = await client.post(
            "/actions",
            json={
                "remote_session_id": remote_session_id,
                "action_type": "get_page_content",
                "input_payload": {},
            },
        )
        closed = await client.post(f"/sessions/{remote_session_id}/close")

    app.dependency_overrides.clear()
    await runtime.close_all()

    screenshot_path = Path(screenshot.json()["data"]["screenshot_path"])
    assert health.status_code == 200
    assert health.json()["reachable"] is True
    assert session_response.status_code == 201
    assert remote_session_id.startswith("worker-session-")
    assert navigate.json()["success"] is True
    assert navigate.json()["data"]["page_title"] == "Example Domain"
    assert screenshot.json()["success"] is True
    assert screenshot_path.exists()
    assert screenshot_path.read_bytes().startswith(b"\x89PNG")
    assert "Example Domain" in content.json()["data"]["content"]
    assert closed.json()["success"] is True


@pytest.mark.asyncio
async def test_browser_worker_rejects_unsafe_navigation(fake_playwright, tmp_path: Path) -> None:  # type: ignore[no-untyped-def]
    """Worker safety boundary should reject unsupported external domains."""

    runtime = PlaywrightBrowserWorkerRuntime(settings=WorkerSettings(WORKER_SCREENSHOT_DIR=str(tmp_path)))
    app = create_app()
    app.dependency_overrides[get_runtime] = lambda: runtime

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://worker") as client:
        session_response = await client.post("/sessions", json={"workspace_id": "workspace-phase20"})
        remote_session_id = session_response.json()["remote_session_id"]
        blocked = await client.post(
            "/actions",
            json={
                "remote_session_id": remote_session_id,
                "action_type": "navigate",
                "target": "https://not-allowed.example.org",
                "input_payload": {},
            },
        )

    app.dependency_overrides.clear()
    await runtime.close_all()

    assert blocked.status_code == 200
    assert blocked.json()["success"] is False
    assert "only allows example.com" in blocked.json()["error"]
