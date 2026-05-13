"""Human control + UI access integration tests."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.services import BrowserHumanControlService, BrowserService, BrowserUIAccessService


@pytest.mark.asyncio
async def test_ui_access_requires_active_human_control_when_control_session_is_provided(session: AsyncSession) -> None:
    """绑定 human control 时，UI access 只能在 active control 下创建。"""

    browser_service = BrowserService(session)
    browser_session = await browser_service.create_browser_session(workspace_id="workspace-human-ui", user_id="user-a")
    human_service = BrowserHumanControlService(session)
    ui_service = BrowserUIAccessService(session)
    control = await human_service.request_control(
        workspace_id="workspace-human-ui",
        browser_session_id=browser_session.id,
        reason="manual check",
        requested_by="user-a",
    )

    with pytest.raises(ValueError, match="active human control"):
        await ui_service.create_access_session(
            workspace_id="workspace-human-ui",
            browser_session_id=browser_session.id,
            human_control_session_id=control.id,
        )

    await human_service.start_control(workspace_id="workspace-human-ui", control_session_id=control.id)
    created = await ui_service.create_access_session(
        workspace_id="workspace-human-ui",
        browser_session_id=browser_session.id,
        human_control_session_id=control.id,
        metadata={"phase": "25"},
    )
    events = await human_service.list_control_events(
        workspace_id="workspace-human-ui",
        control_session_id=control.id,
    )

    assert created.access_session.human_control_session_id == control.id
    assert created.access_session.status == "active"
    assert events[-1].event_type == "note"
    assert events[-1].payload["access_session_id"] == str(created.access_session.id)
