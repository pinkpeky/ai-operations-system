"""Human control state flow tests."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.services import BrowserHumanControlService, BrowserService


@pytest.mark.asyncio
async def test_human_control_cancel_resumes_session(session: AsyncSession) -> None:
    """cancel_control 应恢复 session，避免自动化永久暂停。"""

    browser_service = BrowserService(session)
    browser_session = await browser_service.create_browser_session(workspace_id="workspace-human-cancel", user_id="user-a")
    service = BrowserHumanControlService(session)
    control = await service.request_control(
        workspace_id="workspace-human-cancel",
        browser_session_id=browser_session.id,
        reason="operator cancelled test",
        requested_by="user-a",
    )

    cancelled = await service.cancel_control(
        workspace_id="workspace-human-cancel",
        control_session_id=control.id,
        reason="not needed",
    )
    resumed = await browser_service.repository.get_session(
        session_id=browser_session.id,
        workspace_id="workspace-human-cancel",
    )

    assert cancelled.status == "cancelled"
    assert resumed is not None
    assert resumed.status == "active"
    assert resumed.human_control_status == "cancelled"


@pytest.mark.asyncio
async def test_human_control_expire_resumes_session(session: AsyncSession) -> None:
    """expire_control 应写入 expired 状态并恢复 session。"""

    browser_service = BrowserService(session)
    browser_session = await browser_service.create_browser_session(workspace_id="workspace-human-expire", user_id="user-a")
    service = BrowserHumanControlService(session)
    control = await service.request_control(
        workspace_id="workspace-human-expire",
        browser_session_id=browser_session.id,
        reason="timeout test",
        requested_by="user-a",
    )

    expired = await service.expire_control(
        workspace_id="workspace-human-expire",
        control_session_id=control.id,
        reason="timeout",
    )
    resumed = await browser_service.repository.get_session(
        session_id=browser_session.id,
        workspace_id="workspace-human-expire",
    )

    assert expired.status == "expired"
    assert resumed is not None
    assert resumed.status == "active"
    assert resumed.human_control_status == "expired"
