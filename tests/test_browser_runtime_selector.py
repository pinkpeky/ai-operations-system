"""Browser runtime worker selection tests."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.remote.services import BrowserWorkerSelector, BrowserWorkerService


@pytest.mark.asyncio
async def test_browser_runtime_selector_requires_runtime_capability(session: AsyncSession) -> None:
    service = BrowserWorkerService(session)
    await service.register_worker(
        workspace_id="workspace-runtime-selector",
        worker_name="plain-worker",
        worker_type="playwright",
        base_url="http://plain",
        capabilities={"browser": "chromium", "screenshot": True},
        metadata={},
    )
    runtime_worker = await service.register_worker(
        workspace_id="workspace-runtime-selector",
        worker_name="runtime-worker",
        worker_type="playwright",
        base_url="http://runtime",
        capabilities={"browser": "chromium", "browser_runtime": True, "screenshot": True},
        metadata={},
    )

    selected = await BrowserWorkerSelector(session).select_worker(
        workspace_id="workspace-runtime-selector",
        capabilities={"browser_runtime": True, "browser": "chromium"},
    )

    assert selected is not None
    assert selected.id == runtime_worker.id
