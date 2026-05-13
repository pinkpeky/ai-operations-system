"""Browser profile health service tests."""

from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.services import BrowserProfileHealthService, BrowserProfileService
from app.core.config import Settings


async def test_profile_health_marks_missing_path_corrupted(session: AsyncSession, tmp_path: Path) -> None:
    """profile path 缺失时应标记 corrupted，避免继续分配坏 profile。"""

    settings = Settings(BROWSER_PROFILE_ROOT=str(tmp_path / "profiles"))
    profile_service = BrowserProfileService(session, settings=settings)
    profile = await profile_service.create_profile(
        workspace_id="workspace-health",
        user_id="user-health",
        profile_name="health-profile",
    )

    health = await BrowserProfileHealthService(session, settings=settings).check_profile_health(
        workspace_id="workspace-health",
        profile_id=profile.id,
    )

    assert health.healthy is False
    assert health.health_status == "corrupted"
    assert health.profile.status == "corrupted"
    assert health.profile.last_error == "profile path does not exist"


async def test_profile_health_passes_when_profile_path_exists(session: AsyncSession, tmp_path: Path) -> None:
    """profile path 存在时 health check 应稳定返回 healthy。"""

    settings = Settings(BROWSER_PROFILE_ROOT=str(tmp_path / "profiles"))
    profile_service = BrowserProfileService(session, settings=settings)
    profile = await profile_service.create_profile(
        workspace_id="workspace-health-ok",
        user_id="user-health",
        profile_name="health-ok-profile",
    )
    Path(profile.profile_path).mkdir(parents=True, exist_ok=True)

    health = await BrowserProfileHealthService(session, settings=settings).check_profile_health(
        workspace_id="workspace-health-ok",
        profile_id=profile.id,
    )

    assert health.healthy is True
    assert health.health_status == "healthy"
    assert health.profile.last_health_check_at is not None


async def test_profile_health_summary_counts_by_workspace(session: AsyncSession, tmp_path: Path) -> None:
    """health summary 应按 workspace 隔离统计各状态数量。"""

    settings = Settings(BROWSER_PROFILE_ROOT=str(tmp_path / "profiles"))
    profile_service = BrowserProfileService(session, settings=settings)
    healthy_profile = await profile_service.create_profile(
        workspace_id="workspace-summary",
        user_id="user-summary",
        profile_name="summary-healthy",
    )
    corrupted_profile = await profile_service.create_profile(
        workspace_id="workspace-summary",
        user_id="user-summary",
        profile_name="summary-corrupted",
    )
    Path(healthy_profile.profile_path).mkdir(parents=True, exist_ok=True)

    health_service = BrowserProfileHealthService(session, settings=settings)
    await health_service.check_profile_health(workspace_id="workspace-summary", profile_id=healthy_profile.id)
    await health_service.check_profile_health(workspace_id="workspace-summary", profile_id=corrupted_profile.id)

    summary = await health_service.summarize_profiles(workspace_id="workspace-summary")

    assert summary.total_profiles == 2
    assert summary.healthy_count == 1
    assert summary.corrupted_count == 1
