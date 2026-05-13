"""Browser worker selector tests."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.remote.services import BrowserWorkerRepository, BrowserWorkerSelector, BrowserWorkerService


@pytest.mark.asyncio
async def test_selector_picks_least_loaded_worker(session: AsyncSession) -> None:
    """Selector should choose the online worker with the lowest load."""

    service = BrowserWorkerService(session)
    busy = await service.register_worker(
        workspace_id="workspace-selector",
        worker_name="busy-worker",
        worker_type="playwright",
        base_url="http://busy",
        capabilities={"browser": "chromium", "screenshot": True},
        metadata={},
        max_sessions=3,
    )
    idle = await service.register_worker(
        workspace_id="workspace-selector",
        worker_name="idle-worker",
        worker_type="playwright",
        base_url="http://idle",
        capabilities={"browser": "chromium", "screenshot": True},
        metadata={},
        max_sessions=3,
    )
    repository = BrowserWorkerRepository(session)
    await repository.create_worker_session(
        workspace_id="workspace-selector",
        worker_id=busy.id,
        remote_session_id="busy-session",
        local_browser_session_id=None,
    )

    selector = BrowserWorkerSelector(session)
    selected = await selector.select_worker(workspace_id="workspace-selector", capability="screenshot")

    assert selected is not None
    assert selected.id == idle.id
