"""UI access token tests."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.services import BrowserService, BrowserUIAccessService


@pytest.mark.asyncio
async def test_ui_access_token_is_hashed_and_validated(session: AsyncSession) -> None:
    """UI access token 明文只返回一次，数据库只保存 hash。"""

    browser_service = BrowserService(session)
    browser_session = await browser_service.create_browser_session(workspace_id="workspace-ui-token", user_id="user-a")
    service = BrowserUIAccessService(session)
    created = await service.create_access_session(
        workspace_id="workspace-ui-token",
        browser_session_id=browser_session.id,
    )

    access_token = created.access_token
    access_session_id = created.access_session.id
    fetched = await service.get_access_session(workspace_id="workspace-ui-token", access_session_id=access_session_id)
    valid = await service.validate_access_token(
        workspace_id="workspace-ui-token",
        access_session_id=access_session_id,
        token=access_token,
    )
    invalid = await service.validate_access_token(
        workspace_id="workspace-ui-token",
        access_session_id=access_session_id,
        token="wrong-token",
    )

    assert fetched is not None
    assert fetched.access_token_hash != access_token
    assert len(fetched.access_token_hash) == 64
    assert valid.valid is True
    assert valid.reason is None
    assert invalid.valid is False
    assert invalid.reason == "token_mismatch"
