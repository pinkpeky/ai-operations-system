"""browser_tool remote provider tests."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.remote.client import BrowserWorkerClientResult
from app.browser.remote.services import BrowserWorkerService
from app.core.config import Settings
from app.repositories.tool_call_repository import ToolCallLogRepository
from app.tools.base import ToolExecutionContext
from app.tools.registry import build_default_tool_registry


class FakeBrowserWorkerClient:
    """测试用 fake remote worker client。"""

    def __init__(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        pass

    async def create_session(self, *, payload):  # type: ignore[no-untyped-def]
        return BrowserWorkerClientResult(success=True, message="created", data={"remote_session_id": "tool-remote-session"})

    async def execute_action(self, *, payload):  # type: ignore[no-untyped-def]
        return BrowserWorkerClientResult(
            success=True,
            message="remote action ok",
            data={
                "remote_action_id": "tool-remote-action",
                "target_url": payload.get("target"),
                "page_title": "Remote Tool",
            },
        )


@pytest.mark.asyncio
async def test_browser_tool_executes_remote_provider(monkeypatch, session: AsyncSession) -> None:  # type: ignore[no-untyped-def]
    """browser_tool 应通过 BrowserService 使用 remote provider，并记录 tool logs。"""

    monkeypatch.setattr("app.browser.providers.remote_browser_provider.BrowserWorkerClient", FakeBrowserWorkerClient)
    await BrowserWorkerService(session).register_worker(
        workspace_id="workspace-tool-remote",
        worker_name="remote-worker",
        worker_type="playwright",
        base_url="http://worker",
        capabilities={"browser": "chromium"},
        metadata={},
    )
    registry = build_default_tool_registry()
    context = ToolExecutionContext(
        workspace_id="workspace-tool-remote",
        user_id="user-a",
        session=session,
        settings=Settings(BROWSER_PROVIDER="remote"),
    )

    record = await registry.execute_tool(
        tool_name="browser_tool",
        tool_input={"action_type": "navigate", "target": "https://example.com"},
        context=context,
        agent_name="tool_agent",
    )
    logs = await ToolCallLogRepository(session).list_logs(workspace_id="workspace-tool-remote", tool_name="browser_tool")

    assert record.success is True
    assert record.tool_output["session"]["provider"] == "remote"
    assert record.tool_output["action"]["output_payload"]["data"]["remote_action_id"] == "tool-remote-action"
    assert len(logs) == 1
