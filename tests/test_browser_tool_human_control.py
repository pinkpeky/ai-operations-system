"""browser_tool human control tests."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.services import BrowserService
from app.repositories.tool_call_repository import ToolCallLogRepository
from app.tools.base import ToolExecutionContext
from app.tools.registry import build_default_tool_registry


@pytest.mark.asyncio
async def test_browser_tool_can_request_and_complete_human_control(session: AsyncSession) -> None:
    """browser_tool 应支持 request_human_control / complete_human_control。"""

    browser_service = BrowserService(session)
    browser_session = await browser_service.create_browser_session(workspace_id="workspace-browser-tool-human", user_id="user-a")
    registry = build_default_tool_registry()
    context = ToolExecutionContext(workspace_id="workspace-browser-tool-human", user_id="user-a", session=session)

    requested = await registry.execute_tool(
        tool_name="browser_tool",
        tool_input={
            "session_id": str(browser_session.id),
            "action_type": "request_human_control",
            "reason": "manual step required",
            "metadata": {"phase": "24"},
        },
        context=context,
        agent_name="test_agent",
    )
    control_id = requested.tool_output["action"]["human_control"]["id"]
    completed = await registry.execute_tool(
        tool_name="browser_tool",
        tool_input={
            "action_type": "complete_human_control",
            "control_session_id": control_id,
            "note": "manual step completed",
        },
        context=context,
        agent_name="test_agent",
    )
    logs = await ToolCallLogRepository(session).list_logs(
        workspace_id="workspace-browser-tool-human",
        tool_name="browser_tool",
        limit=10,
    )

    assert requested.success is True
    assert requested.tool_output["session"]["status"] == "paused"
    assert completed.success is True
    assert completed.tool_output["session"]["status"] == "active"
    assert completed.tool_output["action"]["human_control"]["status"] == "completed"
    assert len(logs) == 2
