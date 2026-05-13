"""Browser service tests."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.services import BrowserService


@pytest.mark.asyncio
async def test_browser_service_creates_and_closes_session(session: AsyncSession) -> None:
    """BrowserService should persist session lifecycle and logs."""

    service = BrowserService(session)

    browser_session = await service.create_browser_session(
        workspace_id="workspace-browser",
        user_id="user-browser",
        metadata={"case": "service"},
    )
    closed = await service.close_browser_session(workspace_id="workspace-browser", session_id=browser_session.id)
    sessions = await service.list_sessions(workspace_id="workspace-browser")
    logs = await service.list_logs(workspace_id="workspace-browser", session_id=browser_session.id)

    assert browser_session.provider == "mock"
    assert closed.status == "closed"
    assert len(sessions) == 1
    assert any(log.message == "mock browser session closed" for log in logs)


@pytest.mark.asyncio
async def test_browser_service_workspace_isolation(session: AsyncSession) -> None:
    """Browser sessions must not be visible across workspaces."""

    service = BrowserService(session)

    await service.create_browser_session(workspace_id="workspace-a", user_id=None, metadata={})

    assert len(await service.list_sessions(workspace_id="workspace-a")) == 1
    assert len(await service.list_sessions(workspace_id="workspace-b")) == 0
