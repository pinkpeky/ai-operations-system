"""Browser profile locking tests."""

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.browser.repositories import BrowserRepository
from app.browser.services import BrowserProfileService
from app.core.config import Settings
from app.db.base import Base


@pytest.mark.asyncio
async def test_profile_lock_release_and_conflict_logging() -> None:
    """同一个 profile 同时只能被一个 browser session 锁定。"""

    engine = create_async_engine("sqlite+aiosqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    try:
        async with session_factory() as session:
            profile_service = BrowserProfileService(session, settings=Settings())
            repository = BrowserRepository(session)
            profile = await profile_service.create_profile(
                workspace_id="workspace-lock",
                user_id="user-lock",
                profile_name="locked-profile",
            )
            first_session = await repository.create_session(
                workspace_id="workspace-lock",
                user_id="user-lock",
                provider="mock",
            )
            second_session = await repository.create_session(
                workspace_id="workspace-lock",
                user_id="user-lock",
                provider="mock",
            )
            await session.commit()

            locked = await profile_service.lock_profile(
                workspace_id="workspace-lock",
                profile_id=profile.id,
                session_id=first_session.id,
            )
            assert locked.status == "locked"
            assert locked.locked_by_session_id == first_session.id

            with pytest.raises(ValueError, match="already locked"):
                await profile_service.lock_profile(
                    workspace_id="workspace-lock",
                    profile_id=profile.id,
                    session_id=second_session.id,
                )
            released = await profile_service.release_profile(
                workspace_id="workspace-lock",
                profile_id=profile.id,
                session_id=first_session.id,
            )
            logs = await repository.list_logs(workspace_id="workspace-lock", session_id=first_session.id)

            assert released.status == "available"
            assert released.locked_by_session_id is None
            assert any("profile locked" in log.message.lower() for log in logs)
            assert any("profile released" in log.message.lower() for log in logs)
    finally:
        await engine.dispose()
