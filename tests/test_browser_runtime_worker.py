"""Customer-machine browser runtime route tests."""

from __future__ import annotations

import httpx
import pytest

from worker_client.config import WorkerClientConfig
from worker_client.runtime import create_worker_client_app


@pytest.mark.asyncio
async def test_worker_client_browser_runtime_routes(fake_playwright, tmp_path) -> None:  # type: ignore[no-untyped-def]
    config = WorkerClientConfig(
        server_url="http://api.test",
        worker_name="runtime-worker",
        worker_type="playwright",
        workspace_id="workspace-browser-runtime-worker",
        state_path=tmp_path / "worker_state.json",
        screenshot_dir=str(tmp_path / "screenshots"),
        profile_dir=str(tmp_path / "profiles"),
        capabilities={"browser": "chromium", "browser_runtime": True, "headless": True},
        auth_enabled=False,
    )
    app = create_worker_client_app(config)

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://worker") as client:
        created = await client.post(
            "/browser/session/create",
            json={"workspace_id": "workspace-browser-runtime-worker", "browser": "chromium", "metadata": {}},
        )
        session_id = created.json()["remote_session_id"]
        navigate = await client.post(f"/browser/session/{session_id}/navigate", json={"url": "https://example.com"})
        screenshot = await client.post(f"/browser/session/{session_id}/screenshot", json={"full_page": True})
        page = await client.get(f"/browser/session/{session_id}/page")
        closed = await client.post(f"/browser/session/{session_id}/close")

    assert created.status_code == 201
    assert created.json()["success"] is True
    assert navigate.json()["data"]["page_title"] == "Example Domain"
    assert screenshot.json()["data"]["screenshot_base64"]
    assert "Example Domain" in page.json()["content"]
    assert closed.json()["success"] is True
