"""UI access scope and one-time token tests."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.services import BrowserService, BrowserUIAccessService


@pytest.mark.asyncio
async def test_ui_access_scope_validation(session: AsyncSession) -> None:
    """validate token 时必须检查请求 scope。"""

    browser_session = await BrowserService(session).create_browser_session(
        workspace_id="workspace-ui-scope",
        user_id="user-a",
    )
    service = BrowserUIAccessService(session)
    created = await service.create_access_session(
        workspace_id="workspace-ui-scope",
        browser_session_id=browser_session.id,
        scopes=["view"],
    )

    view = await service.validate_access_token(
        workspace_id="workspace-ui-scope",
        access_session_id=created.access_session.id,
        token=created.access_token,
        scope="view",
    )
    control = await service.validate_access_token(
        workspace_id="workspace-ui-scope",
        access_session_id=created.access_session.id,
        token=created.access_token,
        scope="control",
    )

    assert view.valid is True
    assert control.valid is False
    assert control.reason == "scope_denied:control"


@pytest.mark.asyncio
async def test_ui_access_one_time_token_is_invalid_after_first_use(session: AsyncSession) -> None:
    """one_time=true 的 token 第一次验证成功后再次验证失败。"""

    browser_session = await BrowserService(session).create_browser_session(
        workspace_id="workspace-ui-onetime",
        user_id="user-a",
    )
    service = BrowserUIAccessService(session)
    created = await service.create_access_session(
        workspace_id="workspace-ui-onetime",
        browser_session_id=browser_session.id,
        scopes=["view", "control"],
        one_time=True,
    )

    first = await service.validate_access_token(
        workspace_id="workspace-ui-onetime",
        access_session_id=created.access_session.id,
        token=created.access_token,
        scope="view",
    )
    second = await service.validate_access_token(
        workspace_id="workspace-ui-onetime",
        access_session_id=created.access_session.id,
        token=created.access_token,
        scope="view",
    )

    assert first.valid is True
    assert first.access_session is not None
    assert first.access_session.used_at is not None
    assert second.valid is False
    assert second.reason == "one_time_used"
