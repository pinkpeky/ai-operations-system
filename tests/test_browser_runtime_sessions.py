"""Browser runtime session service tests."""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.providers.base import BrowserProviderResult
from app.browser.remote.services import BrowserWorkerService
from app.browser.services.browser_runtime_session_service import BrowserRuntimeSessionService
from app.models.enums import BrowserRuntimeSessionStatus


class FakeRemoteRuntimeProvider:
    provider_name = "remote"

    def __init__(self, worker_id: str) -> None:
        self.worker_id = worker_id

    async def create_session(self, **_: object) -> BrowserProviderResult:
        return BrowserProviderResult(
            success=True,
            message="created",
            data={
                "worker_id": self.worker_id,
                "worker_name": "runtime-worker",
                "remote_session_id": "remote-runtime-1",
                "current_url": None,
                "page_title": None,
            },
        )

    async def navigate(self, **_: object) -> BrowserProviderResult:
        return BrowserProviderResult(
            success=True,
            message="navigated",
            data={"current_url": "https://example.com", "page_title": "Example Domain"},
        )

    async def screenshot(self, **_: object) -> BrowserProviderResult:
        return BrowserProviderResult(
            success=True,
            message="screenshot",
            data={"screenshot_path": "storage/browser_screenshots/ws/session/example.png", "page_title": "Example Domain"},
        )

    async def get_page(self, **_: object) -> BrowserProviderResult:
        return BrowserProviderResult(
            success=True,
            message="page",
            data={"current_url": "https://example.com", "page_title": "Example Domain", "content": "<h1>Example Domain</h1>"},
        )

    async def close_session(self, **_: object) -> BrowserProviderResult:
        return BrowserProviderResult(success=True, message="closed", data={})


@pytest.mark.asyncio
async def test_browser_runtime_session_lifecycle(session: AsyncSession) -> None:
    worker = await BrowserWorkerService(session).register_worker(
        workspace_id="workspace-runtime-session",
        worker_name="runtime-worker",
        worker_type="playwright",
        base_url="http://worker",
        capabilities={"browser_runtime": True, "browser": "chromium"},
        metadata={},
    )
    service = BrowserRuntimeSessionService(session, provider=FakeRemoteRuntimeProvider(str(worker.id)))  # type: ignore[arg-type]

    runtime_session = await service.create_session(workspace_id="workspace-runtime-session", metadata={"phase": "34"})
    navigated = await service.navigate(
        workspace_id="workspace-runtime-session",
        session_id=runtime_session.id,
        url="https://example.com",
    )
    page = await service.get_page(workspace_id="workspace-runtime-session", session_id=runtime_session.id)
    closed = await service.close_session(workspace_id="workspace-runtime-session", session_id=runtime_session.id)

    assert runtime_session.worker_id == worker.id
    assert navigated.runtime_metadata["current_url"] == "https://example.com"
    assert "Example Domain" in page["content"]
    assert closed.session_status == BrowserRuntimeSessionStatus.CLOSED.value
