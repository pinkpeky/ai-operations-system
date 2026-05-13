"""Browser session cleanup service tests."""

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.remote.services import BrowserSessionCleanupService, BrowserWorkerRepository, BrowserWorkerService
from app.browser.repositories import BrowserRepository
from app.core.config import Settings
from app.models.enums import BrowserSessionStatus


@pytest.mark.asyncio
async def test_cleanup_closes_stale_sessions_and_decrements_worker_load(session: AsyncSession) -> None:
    """Cleanup should close stale sessions and decrement active worker load."""

    browser_repo = BrowserRepository(session)
    browser_session = await browser_repo.create_session(
        workspace_id="workspace-cleanup",
        user_id="user-cleanup",
        provider="remote",
        metadata={},
    )
    browser_session.created_at = datetime.now(UTC) - timedelta(seconds=120)
    service = BrowserWorkerService(session)
    worker = await service.register_worker(
        workspace_id="workspace-cleanup",
        worker_name="cleanup-worker",
        worker_type="playwright",
        base_url="http://worker",
        capabilities={"browser": "chromium"},
        metadata={},
        max_sessions=2,
    )
    worker_repo = BrowserWorkerRepository(session)
    await worker_repo.create_worker_session(
        workspace_id="workspace-cleanup",
        worker_id=worker.id,
        remote_session_id="remote-cleanup",
        local_browser_session_id=browser_session.id,
    )
    await session.commit()

    cleanup = BrowserSessionCleanupService(session, settings=Settings(BROWSER_SESSION_TIMEOUT_SECONDS=60))
    result = await cleanup.cleanup_stale_sessions(workspace_id="workspace-cleanup")

    assert result.stale_sessions == 1
    assert result.closed_sessions == 1
    assert worker.active_sessions == 0
    assert browser_session.status == BrowserSessionStatus.CLOSED.value
