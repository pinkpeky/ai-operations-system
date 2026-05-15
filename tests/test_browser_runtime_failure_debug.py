"""Browser runtime failure debug tests."""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.providers.base import BrowserProviderResult
from app.browser.remote.services import BrowserWorkerService
from app.browser.services.browser_runtime_observability_service import BrowserRuntimeObservabilityService
from app.browser.services.browser_runtime_session_service import BrowserRuntimeSessionService
from app.core.config import Settings


class FailingNavigateProvider:
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
                "remote_session_id": "remote-failure",
                "current_url": "about:blank",
                "page_title": "Blank",
            },
        )

    async def navigate(self, **_: object) -> BrowserProviderResult:
        return BrowserProviderResult(
            success=False,
            message="navigate failed",
            error="remote runtime unreachable",
            data={"last_known_url": "about:blank"},
        )


@pytest.mark.asyncio
async def test_failed_browser_runtime_action_records_debug_artifacts(session: AsyncSession, tmp_path) -> None:  # type: ignore[no-untyped-def]
    """Failed actions should create action_failed events and error snapshots."""

    worker = await BrowserWorkerService(session).register_worker(
        workspace_id="workspace-runtime-failure",
        worker_name="runtime-worker",
        worker_type="playwright",
        base_url="http://worker",
        capabilities={"browser_runtime": True, "browser": "chromium"},
        metadata={},
    )
    settings = Settings(BROWSER_RUNTIME_SNAPSHOT_DIR=str(tmp_path))
    service = BrowserRuntimeSessionService(session, provider=FailingNavigateProvider(str(worker.id)), settings=settings)  # type: ignore[arg-type]

    runtime_session = await service.create_session(workspace_id="workspace-runtime-failure", metadata={"phase": "35A"})
    with pytest.raises(ValueError, match="remote runtime unreachable"):
        await service.navigate(
            workspace_id="workspace-runtime-failure",
            session_id=runtime_session.id,
            url="https://example.com",
        )

    observability = BrowserRuntimeObservabilityService(session, settings=settings)
    events = await observability.list_events(
        workspace_id="workspace-runtime-failure",
        runtime_session_id=runtime_session.id,
        limit=100,
    )
    snapshots = await observability.list_snapshots(
        workspace_id="workspace-runtime-failure",
        runtime_session_id=runtime_session.id,
        limit=100,
    )

    assert any(event.event_type == "action_failed" and event.error == "remote runtime unreachable" for event in events)
    assert any(snapshot.snapshot_type == "error" and snapshot.snapshot_metadata["action_type"] == "navigate" for snapshot in snapshots)
