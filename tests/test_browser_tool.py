"""Browser tool tests."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.services import BrowserService
from app.planning.services import PlanningService
from app.planning.services.simple_planner_agent import PlannedStep
from app.repositories.tool_call_repository import ToolCallLogRepository
from app.tools.base import ToolExecutionContext
from app.tools.registry import build_default_tool_registry


@pytest.mark.asyncio
async def test_browser_tool_registered_and_executable(session: AsyncSession) -> None:
    """Default ToolRegistry should expose and execute browser_tool."""

    registry = build_default_tool_registry()

    record = await registry.execute_tool(
        tool_name="browser_tool",
        tool_input={"action_type": "navigate", "target": "https://example.com"},
        context=ToolExecutionContext(workspace_id="workspace-browser-tool", user_id="user-a", session=session),
        agent_name="test_agent",
    )
    logs = await ToolCallLogRepository(session).list_logs(
        workspace_id="workspace-browser-tool",
        tool_name="browser_tool",
        limit=10,
    )

    assert record.success is True
    assert record.tool_output["success"] is True
    assert record.tool_output["action"]["status"] == "completed"
    assert logs[0].tool_name == "browser_tool"


@pytest.mark.asyncio
async def test_browser_tool_can_use_existing_session(session: AsyncSession) -> None:
    """browser_tool should accept an existing mock browser session."""

    service = BrowserService(session)
    browser_session = await service.create_browser_session(workspace_id="workspace-browser-tool-existing", user_id=None)
    registry = build_default_tool_registry()

    record = await registry.execute_tool(
        tool_name="browser_tool",
        tool_input={
            "session_id": str(browser_session.id),
            "action_type": "screenshot",
            "target": "body",
        },
        context=ToolExecutionContext(workspace_id="workspace-browser-tool-existing", session=session),
    )

    assert record.success is True
    assert record.tool_output["session"]["id"] == str(browser_session.id)
    assert record.tool_output["action"]["output_payload"]["data"]["screenshot"] == "mock://browser/screenshot.png"


@pytest.mark.asyncio
async def test_planning_step_supports_browser_tool(session: AsyncSession) -> None:
    """PlanningService should execute a step whose target is browser_tool."""

    service = PlanningService(session)
    plan = await service.create_plan(
        workspace_id="workspace-browser-plan",
        session_id=None,
        root_goal="Open a mock page",
        auto_create_steps=False,
    )
    await service.create_steps(
        plan=plan,
        steps=[
            PlannedStep(
                step_order=1,
                tool_name="browser_tool",
                title="Mock browser navigate",
                description="Navigate through the mock browser provider.",
                input_payload={"action_type": "navigate", "target": "https://example.com"},
            )
        ],
    )
    await session.commit()

    result = await service.execute_plan(plan=plan, user_id="user-plan")
    steps = await service.list_steps(plan_id=plan.id, workspace_id="workspace-browser-plan")

    assert result["status"] == "completed"
    assert steps[0].status == "completed"
    assert steps[0].output_payload["tool_name"] == "browser_tool"
