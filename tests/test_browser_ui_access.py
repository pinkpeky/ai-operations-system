"""Browser UI Access Placeholder service tests."""

from datetime import UTC, datetime, timedelta

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.services import BrowserService, BrowserUIAccessService
from worker.main import create_app


@pytest.mark.asyncio
async def test_ui_access_service_create_get_revoke_and_expire(session: AsyncSession) -> None:
    """UI access service 应创建占位 URL、支持查询、撤销和过期。"""

    browser_service = BrowserService(session)
    browser_session = await browser_service.create_browser_session(workspace_id="workspace-ui-access", user_id="user-a")
    service = BrowserUIAccessService(session)

    created = await service.create_access_session(
        workspace_id="workspace-ui-access",
        browser_session_id=browser_session.id,
        metadata={"phase": "25"},
    )
    fetched = await service.get_access_session(
        workspace_id="workspace-ui-access",
        access_session_id=created.access_session.id,
    )
    revoked = await service.revoke_access_session(
        workspace_id="workspace-ui-access",
        access_session_id=created.access_session.id,
        reason="test revoke",
    )
    second = await service.create_access_session(
        workspace_id="workspace-ui-access",
        browser_session_id=browser_session.id,
    )
    second.access_session.expires_at = datetime.now(UTC) - timedelta(seconds=1)
    await session.commit()
    expired = await service.expire_access_sessions(workspace_id="workspace-ui-access")

    assert created.access_token
    assert fetched is not None
    assert fetched.access_token_hash != created.access_token
    assert fetched.remote_control_url.endswith(str(created.access_session.id))
    assert fetched.live_view_url.endswith(str(created.access_session.id))
    assert fetched.devtools_url is None
    assert fetched.access_metadata["placeholder"] is True
    assert revoked.status == "revoked"
    assert len(expired) == 1
    assert expired[0].status == "expired"


@pytest.mark.asyncio
async def test_worker_ui_access_capabilities_endpoint(fake_playwright) -> None:  # type: ignore[no-untyped-def]
    """browser-worker 应声明 UI access 仍是 placeholder。"""

    _ = fake_playwright
    app = create_app()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://worker") as client:
        response = await client.get("/ui-access/capabilities")

    assert response.status_code == 200
    assert response.json() == {
        "vnc": False,
        "novnc": False,
        "devtools": False,
        "placeholder": True,
    }
