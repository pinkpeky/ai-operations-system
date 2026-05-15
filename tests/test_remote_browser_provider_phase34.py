"""Phase 34 RemoteBrowserProvider tests."""

from __future__ import annotations

import base64

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.providers.remote_provider import RemoteBrowserProvider
from app.browser.remote.client import BrowserWorkerClientResult
from app.browser.remote.services import BrowserWorkerService
from app.core.config import Settings
from app.models.browser_runtime import BrowserRuntimeSession


class FakeRuntimeClient:
    async def create_runtime_session(self, *, payload):  # type: ignore[no-untyped-def]
        return BrowserWorkerClientResult(
            success=True,
            message="created",
            data={"remote_session_id": "runtime-session-1", "browser": payload["browser"]},
        )

    async def runtime_navigate(self, *, remote_session_id: str, payload):  # type: ignore[no-untyped-def]
        return BrowserWorkerClientResult(
            success=True,
            message="navigated",
            data={"remote_session_id": remote_session_id, "current_url": payload["url"], "page_title": "Example Domain"},
        )

    async def runtime_screenshot(self, *, remote_session_id: str, payload):  # type: ignore[no-untyped-def]
        return BrowserWorkerClientResult(
            success=True,
            message="screenshot",
            data={
                "remote_session_id": remote_session_id,
                "screenshot_base64": base64.b64encode(b"\x89PNG\r\n\x1a\n").decode("ascii"),
                "page_title": "Example Domain",
            },
        )

    async def runtime_page(self, *, remote_session_id: str):  # type: ignore[no-untyped-def]
        return BrowserWorkerClientResult(
            success=True,
            message="page",
            data={"remote_session_id": remote_session_id, "page_title": "Example Domain", "content": "<h1>Example Domain</h1>"},
        )

    async def runtime_close(self, *, remote_session_id: str):  # type: ignore[no-untyped-def]
        return BrowserWorkerClientResult(success=True, message="closed", data={"remote_session_id": remote_session_id})


@pytest.mark.asyncio
async def test_phase34_remote_provider_selects_worker_and_stores_screenshot(session: AsyncSession, tmp_path) -> None:
    worker = await BrowserWorkerService(session).register_worker(
        workspace_id="workspace-runtime-provider",
        worker_name="runtime-worker",
        worker_type="playwright",
        base_url="http://worker",
        capabilities={"browser_runtime": True, "browser": "chromium"},
        metadata={},
    )
    provider = RemoteBrowserProvider(
        session=session,
        settings=Settings(BROWSER_RUNTIME_SCREENSHOT_DIR=str(tmp_path)),
        client_factory=lambda _: FakeRuntimeClient(),
    )

    created = await provider.create_session(workspace_id="workspace-runtime-provider", browser="chromium")
    runtime_session = BrowserRuntimeSession(
        workspace_id="workspace-runtime-provider",
        worker_id=worker.id,
        provider="remote",
        browser="chromium",
        runtime_metadata={"remote_session_id": created.data["remote_session_id"]},
    )
    session.add(runtime_session)
    await session.flush()
    shot = await provider.screenshot(runtime_session=runtime_session, screenshot_name="example")

    assert created.success is True
    assert created.data["worker_id"] == str(worker.id)
    assert shot.success is True
    assert shot.data["screenshot_path"].endswith("example.png")
