"""Browser session persistent profile integration tests."""

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.browser.services import BrowserProfileService, BrowserService
from app.core.config import Settings
from app.db.base import Base


@pytest.mark.asyncio
async def test_browser_session_locks_and_releases_persistent_profile() -> None:
    """创建 persistent session 时锁定 profile，关闭 session 时释放。"""

    engine = create_async_engine("sqlite+aiosqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    try:
        async with session_factory() as session:
            settings = Settings(BROWSER_PROVIDER="mock", BROWSER_PROFILE_ROOT="worker/profiles")
            profile_service = BrowserProfileService(session, settings=settings)
            profile = await profile_service.create_profile(
                workspace_id="workspace-session-profile",
                user_id="user-session-profile",
                profile_name="session-profile",
            )

            browser_service = BrowserService(session, settings=settings)
            browser_session = await browser_service.create_browser_session(
                workspace_id="workspace-session-profile",
                user_id="user-session-profile",
                metadata={"test": "profile-session"},
                profile_id=profile.id,
                use_persistent_profile=True,
            )
            locked = await profile_service.get_profile(workspace_id="workspace-session-profile", profile_id=profile.id)
            assert locked is not None
            assert locked.status == "locked"
            assert locked.locked_by_session_id == browser_session.id

            closed = await browser_service.close_browser_session(
                workspace_id="workspace-session-profile",
                session_id=browser_session.id,
            )
            released = await profile_service.get_profile(workspace_id="workspace-session-profile", profile_id=profile.id)

            assert browser_session.profile_id == profile.id
            assert browser_session.persistent_context_enabled is True
            assert closed.status == "closed"
            assert released is not None
            assert released.status == "available"
            assert released.locked_by_session_id is None
    finally:
        await engine.dispose()
