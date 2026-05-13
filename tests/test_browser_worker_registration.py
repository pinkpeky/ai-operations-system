"""Remote browser worker registration tests."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.remote.services import BrowserWorkerService


@pytest.mark.asyncio
async def test_browser_worker_registration_is_workspace_scoped(session: AsyncSession) -> None:
    """同名 worker 在不同 workspace 下应彼此隔离。"""

    service = BrowserWorkerService(session)
    worker_a = await service.register_worker(
        workspace_id="workspace-a",
        worker_name="local-worker-1",
        worker_type="playwright",
        base_url="http://worker-a",
        capabilities={"browser": "chromium"},
        metadata={"region": "local"},
    )
    worker_b = await service.register_worker(
        workspace_id="workspace-b",
        worker_name="local-worker-1",
        worker_type="playwright",
        base_url="http://worker-b",
        capabilities={"browser": "chromium"},
        metadata={},
    )

    workers_a = await service.list_workers(workspace_id="workspace-a")
    workers_b = await service.list_workers(workspace_id="workspace-b")

    assert worker_a.id != worker_b.id
    assert len(workers_a) == 1
    assert workers_a[0].base_url == "http://worker-a"
    assert len(workers_b) == 1
    assert workers_b[0].base_url == "http://worker-b"


@pytest.mark.asyncio
async def test_register_worker_updates_same_workspace_name(session: AsyncSession) -> None:
    """同 workspace + worker_name 重复注册时更新原记录。"""

    service = BrowserWorkerService(session)
    first = await service.register_worker(
        workspace_id="workspace-update",
        worker_name="local-worker-1",
        worker_type="mock",
        base_url="http://old",
        capabilities={},
        metadata={},
    )
    second = await service.register_worker(
        workspace_id="workspace-update",
        worker_name="local-worker-1",
        worker_type="playwright",
        base_url="http://new",
        capabilities={"screenshot": True},
        metadata={"version": "2"},
    )

    workers = await service.list_workers(workspace_id="workspace-update")

    assert first.id == second.id
    assert len(workers) == 1
    assert workers[0].base_url == "http://new"
    assert workers[0].capabilities["screenshot"] is True
