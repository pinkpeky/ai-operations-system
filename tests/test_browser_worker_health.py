"""Browser worker health service tests."""

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.remote.services import BrowserWorkerHealthService, BrowserWorkerService
from app.core.config import Settings


@pytest.mark.asyncio
async def test_browser_worker_health_marks_stale_worker_offline(session: AsyncSession) -> None:
    """Health service should mark stale heartbeat workers offline."""

    service = BrowserWorkerService(session)
    worker = await service.register_worker(
        workspace_id="workspace-health",
        worker_name="stale-worker",
        worker_type="playwright",
        base_url="http://worker",
        capabilities={"browser": "chromium"},
        metadata={},
    )
    worker.last_heartbeat_at = datetime.now(UTC) - timedelta(seconds=120)
    await session.commit()

    health = BrowserWorkerHealthService(session, settings=Settings(BROWSER_WORKER_HEARTBEAT_TIMEOUT_SECONDS=60))
    stale_workers = await health.mark_stale_workers_offline(workspace_id="workspace-health")
    summary = await health.health_summary(workspace_id="workspace-health")

    assert [item.id for item in stale_workers] == [worker.id]
    assert summary["offline_workers"] == 1
    assert summary["online_workers"] == 0
    assert summary["stale_workers"] == 1
    assert stale_workers[0].error_message == "heartbeat stale for 60s"
