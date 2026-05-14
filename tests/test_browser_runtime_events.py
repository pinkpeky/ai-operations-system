"""Browser runtime timeline event tests."""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.providers.base import BrowserProviderResult
from app.browser.remote.services import BrowserWorkerService
from app.browser.services.browser_runtime_observability_service import BrowserRuntimeObservabilityService
from app.browser.services.browser_runtime_session_service import BrowserRuntimeSessionService
from app.core.config import Settings


class FakeRuntimeProvider:
    provider_name = "remote"

    def __init__(self, worker_id: str) -> None:
        self.worker_id = worker_id

    async def create_session(self, **_: object) -> BrowserProviderResult:
        return BrowserProviderResult(
            success=True,
            message="created",
            data={"worker_id": self.worker_id, "worker_name": "runtime-worker", "remote_session_id": "remote-events"},
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
        return BrowserProviderResult(success=True, message="closed", data={"latency_ms": 1})


@pytest.mark.asyncio
async def test_browser_runtime_events_are_recorded(session: AsyncSession, tmp_path) -> None:  # type: ignore[no-untyped-def]
    """Session lifecycle should produce a readable timeline."""

    worker = await BrowserWorkerService(session).register_worker(
        workspace_id="workspace-runtime-events",
        worker_name="runtime-worker",
        worker_type="playwright",
        base_url="http://worker",
        capabilities={"browser_runtime": True, "browser": "chromium"},
        metadata={},
    )
    settings = Settings(BROWSER_RUNTIME_SNAPSHOT_DIR=str(tmp_path))
    service = BrowserRuntimeSessionService(session, provider=FakeRuntimeProvider(str(worker.id)), settings=settings)  # type: ignore[arg-type]

    runtime_session = await service.create_session(workspace_id="workspace-runtime-events", metadata={"phase": "35A"})
    await service.navigate(workspace_id="workspace-runtime-events", session_id=runtime_session.id, url="https://example.com")
    await service.screenshot(workspace_id="workspace-runtime-events", session_id=runtime_session.id)
    await service.get_page(workspace_id="workspace-runtime-events", session_id=runtime_session.id)
    await service.close_session(workspace_id="workspace-runtime-events", session_id=runtime_session.id)

    events = await BrowserRuntimeObservabilityService(session, settings=settings).list_events(
        workspace_id="workspace-runtime-events",
        runtime_session_id=runtime_session.id,
        limit=100,
    )
    event_types = [event.event_type for event in events]

    assert "session_created" in event_types
    assert "navigate_started" in event_types
    assert "navigate_completed" in event_types
    assert "screenshot_completed" in event_types
    assert "page_snapshot_captured" in event_types
    assert "session_closed" in event_types
