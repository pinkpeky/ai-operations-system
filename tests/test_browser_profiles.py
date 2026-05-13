"""Browser profile lifecycle tests."""

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.browser.services import BrowserProfileService
from app.core.config import Settings
from app.db.base import Base


@pytest.mark.asyncio
async def test_browser_profile_create_list_get_delete() -> None:
    """Profile service should manage workspace-scoped lifecycle records."""

    engine = create_async_engine("sqlite+aiosqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    try:
        async with session_factory() as session:
            service = BrowserProfileService(session, settings=Settings(BROWSER_PROFILE_ROOT="worker/profiles"))
            profile = await service.create_profile(
                workspace_id="workspace-profile",
                user_id="user-profile",
                profile_name="main-profile",
                profile_type="persistent",
                provider="remote",
                metadata={"purpose": "test"},
            )

            profiles = await service.list_profiles(workspace_id="workspace-profile")
            loaded = await service.get_profile(workspace_id="workspace-profile", profile_id=profile.id)
            deleted = await service.delete_profile(workspace_id="workspace-profile", profile_id=profile.id)

            assert profile.profile_path.endswith(f"workspace-profile/{profile.id}")
            assert len(profiles) == 1
            assert loaded is not None
            assert loaded.profile_name == "main-profile"
            assert deleted.status == "deleted"
            assert await service.get_profile(workspace_id="workspace-profile", profile_id=profile.id) is None
    finally:
        await engine.dispose()
