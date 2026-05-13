"""browser_tool UI access tests."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.services import BrowserHumanControlService, BrowserService
from app.repositories.tool_call_repository import ToolCallLogRepository
from app.tools.base import ToolExecutionContext
from app.tools.registry import build_default_tool_registry


@pytest.mark.asyncio
async def test_browser_tool_can_create_and_revoke_ui_access(session: AsyncSession) -> None:
    """browser_tool 应支持 create_ui_access / revoke_ui_access placeholder 动作。"""

    browser_service = BrowserService(session)
    browser_session = await browser_service.create_browser_session(workspace_id="workspace-tool-ui", user_id="user-a")
    human_service = BrowserHumanControlService(session)
    control = await human_service.request_control(
        workspace_id="workspace-tool-ui",
        browser_session_id=browser_session.id,
        reason="manual check",
        requested_by="user-a",
    )
    await human_service.start_control(workspace_id="workspace-tool-ui", control_session_id=control.id)

    registry = build_default_tool_registry()
    context = ToolExecutionContext(workspace_id="workspace-tool-ui", user_id="user-a", session=session)
    created = await registry.execute_tool(
        tool_name="browser_tool",
        tool_input={
            "session_id": str(browser_session.id),
            "human_control_session_id": str(control.id),
            "action_type": "create_ui_access",
            "metadata": {"phase": "25"},
        },
        context=context,
        agent_name="test_agent",
    )
    access_id = created.tool_output["action"]["ui_access"]["id"]
    revoked = await registry.execute_tool(
        tool_name="browser_tool",
        tool_input={
            "access_session_id": access_id,
            "action_type": "revoke_ui_access",
            "reason": "test done",
        },
        context=context,
        agent_name="test_agent",
    )
    logs = await ToolCallLogRepository(session).list_logs(
        workspace_id="workspace-tool-ui",
        tool_name="browser_tool",
        limit=10,
    )

    assert created.success is True
    assert created.tool_output["action"]["ui_access"]["access_token"]
    assert created.tool_output["action"]["placeholder"] is True
    assert revoked.success is True
    assert revoked.tool_output["action"]["ui_access"]["status"] == "revoked"
    assert len(logs) == 2
