"""browser_tool with Playwright Local Provider tests."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.repositories.tool_call_repository import ToolCallLogRepository
from app.tools.base import ToolExecutionContext
from app.tools.registry import build_default_tool_registry


@pytest.mark.asyncio
async def test_browser_tool_executes_playwright_page_content(fake_playwright, tmp_path, session: AsyncSession) -> None:  # type: ignore[no-untyped-def]
    """browser_tool 应能在 playwright_local 模式下执行并记录 tool trace。"""

    settings = Settings(BROWSER_PROVIDER="playwright_local", BROWSER_SCREENSHOT_DIR=str(tmp_path))
    registry = build_default_tool_registry()
    context = ToolExecutionContext(workspace_id="workspace-tool-playwright", user_id="user-a", session=session, settings=settings)

    navigate = await registry.execute_tool(
        tool_name="browser_tool",
        tool_input={"action_type": "navigate", "target": "https://example.com"},
        context=context,
        agent_name="tool_agent",
    )
    session_id = navigate.tool_output["session"]["id"]
    content = await registry.execute_tool(
        tool_name="browser_tool",
        tool_input={"session_id": session_id, "action_type": "get_page_content"},
        context=context,
        agent_name="tool_agent",
    )
    logs = await ToolCallLogRepository(session).list_logs(workspace_id="workspace-tool-playwright", tool_name="browser_tool")

    assert navigate.success is True
    assert content.success is True
    assert "Example Domain" in content.tool_output["action"]["output_payload"]["data"]["content"]
    assert len(logs) == 2
