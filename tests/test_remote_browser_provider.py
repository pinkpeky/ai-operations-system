"""RemoteBrowserProvider tests."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.providers.remote_browser_provider import RemoteBrowserProvider
from app.browser.remote.client import BrowserWorkerClientResult
from app.browser.remote.services import BrowserWorkerService
from app.core.config import Settings


class FakeBrowserWorkerClient:
    """测试用 fake worker client。"""

    async def create_session(self, *, payload):  # type: ignore[no-untyped-def]
        return BrowserWorkerClientResult(
            success=True,
            message="created",
            data={"remote_session_id": "remote-session-1", "payload": payload},
        )

    async def execute_action(self, *, payload):  # type: ignore[no-untyped-def]
        return BrowserWorkerClientResult(
            success=True,
            message="remote action ok",
            data={
                "remote_action_id": "remote-action-1",
                "page_title": "Remote Example",
                "target_url": payload.get("target"),
            },
        )

    async def close_session(self, *, remote_session_id: str):  # type: ignore[no-untyped-def]
        return BrowserWorkerClientResult(success=True, message="closed", data={"remote_session_id": remote_session_id})


@pytest.mark.asyncio
async def test_remote_browser_provider_dispatches_action(session: AsyncSession) -> None:
    """RemoteBrowserProvider 应创建 worker session 并调度 action。"""

    worker = await BrowserWorkerService(session).register_worker(
        workspace_id="workspace-remote-provider",
        worker_name="remote-worker",
        worker_type="playwright",
        base_url="http://worker",
        capabilities={"browser": "chromium"},
        metadata={},
    )
    provider = RemoteBrowserProvider(
        session=session,
        settings=Settings(),
        client_factory=lambda _: FakeBrowserWorkerClient(),
    )

    created = await provider.create_session(metadata={"workspace_id": "workspace-remote-provider"})
    action = await provider.navigate(
        target="https://example.com",
        input_payload={"_workspace_id": "workspace-remote-provider"},
        session_metadata=created.data["provider_session_metadata"],
    )

    assert created.success is True
    assert created.data["worker_id"] == str(worker.id)
    assert action.success is True
    assert action.data["remote_action_id"] == "remote-action-1"
    assert action.data["worker_name"] == "remote-worker"


@pytest.mark.asyncio
async def test_remote_browser_provider_requires_worker(session: AsyncSession) -> None:
    """没有可用 worker 时应返回清晰错误。"""

    provider = RemoteBrowserProvider(session=session, settings=Settings())

    result = await provider.create_session(metadata={"workspace_id": "workspace-no-worker"})

    assert result.success is False
    assert "No available browser worker" in result.message
