"""Remote browser worker heartbeat tests."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.remote.services import BrowserWorkerService


@pytest.mark.asyncio
async def test_browser_worker_heartbeat_updates_status(session: AsyncSession) -> None:
    """Heartbeat 应更新 worker 状态、能力和 last_heartbeat_at。"""

    service = BrowserWorkerService(session)
    worker = await service.register_worker(
        workspace_id="workspace-heartbeat",
        worker_name="worker-heartbeat",
        worker_type="playwright",
        base_url="http://worker",
        capabilities={"browser": "chromium"},
        metadata={},
    )

    updated = await service.heartbeat_worker(
        workspace_id="workspace-heartbeat",
        worker_id=worker.id,
        status="busy",
        capabilities={"browser": "chromium", "screenshot": True},
        metadata={"load": 1},
    )

    assert updated.status == "busy"
    assert updated.capabilities["screenshot"] is True
    assert updated.worker_metadata["load"] == 1
    assert updated.last_heartbeat_at is not None


@pytest.mark.asyncio
async def test_browser_worker_heartbeat_rejects_other_workspace(session: AsyncSession) -> None:
    """Heartbeat 不能跨 workspace 更新 worker。"""

    service = BrowserWorkerService(session)
    worker = await service.register_worker(
        workspace_id="workspace-owner",
        worker_name="worker-owner",
        worker_type="playwright",
        base_url="http://worker",
        capabilities={},
        metadata={},
    )

    with pytest.raises(ValueError, match="not found"):
        await service.heartbeat_worker(
            workspace_id="workspace-other",
            worker_id=worker.id,
            status="online",
            capabilities={},
            metadata={},
        )
