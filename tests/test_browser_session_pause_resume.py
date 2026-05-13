"""Browser session pause/resume tests."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.services import BrowserHumanControlService, BrowserService


@pytest.mark.asyncio
async def test_paused_session_rejects_actions_until_human_control_completed(session: AsyncSession) -> None:
    """进入 human control 后 action 应被阻止，complete 后可继续执行。"""

    browser_service = BrowserService(session)
    browser_session = await browser_service.create_browser_session(workspace_id="workspace-pause-resume", user_id=None)
    human_service = BrowserHumanControlService(session)
    control = await human_service.request_control(
        workspace_id="workspace-pause-resume",
        browser_session_id=browser_session.id,
        reason="manual step",
        requested_by="tester",
    )

    with pytest.raises(ValueError, match="not active"):
        await browser_service.execute_action(
            workspace_id="workspace-pause-resume",
            session_id=browser_session.id,
            action_type="navigate",
            target="https://example.com",
        )

    await human_service.complete_control(
        workspace_id="workspace-pause-resume",
        control_session_id=control.id,
        note="done",
    )
    action = await browser_service.execute_action(
        workspace_id="workspace-pause-resume",
        session_id=browser_session.id,
        action_type="navigate",
        target="https://example.com",
    )

    assert action.status == "completed"
