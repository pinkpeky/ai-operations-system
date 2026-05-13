"""Browser worker capacity tests."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.remote.services import BrowserWorkerRepository, BrowserWorkerService


@pytest.mark.asyncio
async def test_worker_capacity_increments_and_blocks_full_worker(session: AsyncSession) -> None:
    """Worker should stop being available after reaching max_sessions."""

    service = BrowserWorkerService(session)
    worker = await service.register_worker(
        workspace_id="workspace-capacity",
        worker_name="capacity-worker",
        worker_type="playwright",
        base_url="http://worker",
        capabilities={"browser": "chromium"},
        metadata={},
        max_sessions=1,
    )
    repository = BrowserWorkerRepository(session)

    worker_session = await repository.create_worker_session(
        workspace_id="workspace-capacity",
        worker_id=worker.id,
        remote_session_id="remote-1",
        local_browser_session_id=None,
    )
    available_when_full = await repository.list_available_workers(workspace_id="workspace-capacity")
    await repository.close_worker_session(worker_session)
    available_after_close = await repository.list_available_workers(workspace_id="workspace-capacity")

    assert worker.active_sessions == 0
    assert available_when_full == []
    assert [item.id for item in available_after_close] == [worker.id]
