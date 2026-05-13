"""Browser Profile 生命周期服务。"""

from __future__ import annotations

from datetime import UTC, datetime
import logging
import re
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.repositories import BrowserRepository
from app.core.config import Settings, get_settings
from app.models.browser import BrowserProfile, BrowserProfileUsageLog, BrowserSession
from app.models.enums import BrowserProfileHealthStatus, BrowserProfileStatus

logger = logging.getLogger(__name__)


class BrowserProfileService:
    """管理持久化 Browser Profile 的创建、锁定、释放和删除。"""

    def __init__(self, session: AsyncSession, *, settings: Settings | None = None) -> None:
        self.session = session
        self.settings = settings or get_settings()
        self.browser_repository = BrowserRepository(session)

    async def create_profile(
        self,
        *,
        workspace_id: str,
        user_id: str | None,
        profile_name: str,
        profile_type: str = "persistent",
        provider: str = "remote",
        metadata: dict[str, object] | None = None,
    ) -> BrowserProfile:
        """创建 profile，并生成 worker/profiles 下的稳定 profile_path。"""

        profile = BrowserProfile(
            workspace_id=workspace_id,
            user_id=user_id,
            profile_name=profile_name,
            profile_type=profile_type,
            provider=provider,
            profile_path="",
            status=BrowserProfileStatus.AVAILABLE.value,
            health_status=BrowserProfileHealthStatus.HEALTHY.value,
            profile_metadata=metadata or {},
        )
        self.session.add(profile)
        await self.session.flush()
        profile.profile_path = self._profile_path(workspace_id=workspace_id, profile_id=profile.id)
        await self._log_usage(
            workspace_id=workspace_id,
            profile_id=profile.id,
            session_id=None,
            action="create",
            success=True,
            metadata={"profile_name": profile.profile_name, "profile_path": profile.profile_path},
        )
        await self.session.commit()
        await self.session.refresh(profile)
        logger.info(
            "Browser profile created",
            extra={"workspace_id": workspace_id, "profile_id": str(profile.id), "profile_name": profile.profile_name},
        )
        return profile

    async def list_profiles(
        self,
        *,
        workspace_id: str,
        status: str | None = None,
        limit: int = 100,
    ) -> list[BrowserProfile]:
        """列出当前 workspace 的 profiles，默认不返回 deleted。"""

        statement = select(BrowserProfile).where(BrowserProfile.workspace_id == workspace_id)
        if status is not None:
            statement = statement.where(BrowserProfile.status == status)
        else:
            statement = statement.where(BrowserProfile.status != BrowserProfileStatus.DELETED.value)
        statement = statement.order_by(BrowserProfile.created_at.desc()).limit(limit)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_profile(self, *, workspace_id: str, profile_id: UUID, include_deleted: bool = False) -> BrowserProfile | None:
        """按 workspace 加载单个 profile。"""

        statement = select(BrowserProfile).where(
            BrowserProfile.workspace_id == workspace_id,
            BrowserProfile.id == profile_id,
        )
        if not include_deleted:
            statement = statement.where(BrowserProfile.status != BrowserProfileStatus.DELETED.value)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_available_profile(
        self,
        *,
        workspace_id: str,
        provider: str | None = None,
        profile_type: str | None = None,
    ) -> BrowserProfile | None:
        """返回一个可用 profile，供后续自动分配使用。"""

        statement = select(BrowserProfile).where(
            BrowserProfile.workspace_id == workspace_id,
            BrowserProfile.status == BrowserProfileStatus.AVAILABLE.value,
        )
        if provider is not None:
            statement = statement.where(BrowserProfile.provider == provider)
        if profile_type is not None:
            statement = statement.where(BrowserProfile.profile_type == profile_type)
        statement = statement.order_by(BrowserProfile.last_used_at.asc().nullsfirst(), BrowserProfile.created_at.asc()).limit(1)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def lock_profile(
        self,
        *,
        workspace_id: str,
        profile_id: UUID,
        session_id: UUID,
    ) -> BrowserProfile:
        """为指定 browser session 锁定 profile，同一时间只允许一个 session 使用。"""

        profile = await self.get_profile(workspace_id=workspace_id, profile_id=profile_id)
        if profile is None:
            raise ValueError("Browser profile not found")
        browser_session = await self.browser_repository.get_session(session_id=session_id, workspace_id=workspace_id)
        if browser_session is None:
            raise ValueError("Browser session not found")
        if profile.status == BrowserProfileStatus.LOCKED.value and profile.locked_by_session_id != session_id:
            logger.warning(
                "Browser profile lock conflict",
                extra={
                    "workspace_id": workspace_id,
                    "profile_id": str(profile_id),
                    "locked_by_session_id": str(profile.locked_by_session_id),
                    "requested_session_id": str(session_id),
                },
            )
            if profile.locked_by_session_id is not None:
                await self._log_profile_event(
                    workspace_id=workspace_id,
                    session_id=profile.locked_by_session_id,
                    message="Browser profile lock conflict",
                    level="warning",
                    metadata={"requested_session_id": str(session_id), "profile_id": str(profile_id)},
                )
                await self.session.commit()
            raise ValueError("Browser profile is already locked")
        if profile.status not in {BrowserProfileStatus.AVAILABLE.value, BrowserProfileStatus.LOCKED.value}:
            raise ValueError(f"Browser profile is not available: {profile.status}")

        now = datetime.now(UTC)
        profile.status = BrowserProfileStatus.LOCKED.value
        profile.locked_by_session_id = session_id
        profile.locked_at = now
        profile.last_used_at = now
        profile.last_error = None
        await self._log_profile_event(
            workspace_id=workspace_id,
            session_id=session_id,
            message="Browser profile locked",
            metadata={"profile_id": str(profile.id), "profile_path": profile.profile_path},
        )
        await self._log_usage(
            workspace_id=workspace_id,
            profile_id=profile.id,
            session_id=session_id,
            action="lock",
            success=True,
            metadata={"profile_path": profile.profile_path},
        )
        await self.session.commit()
        await self.session.refresh(profile)
        logger.info("Browser profile locked", extra={"workspace_id": workspace_id, "profile_id": str(profile.id)})
        return profile

    async def release_profile(
        self,
        *,
        workspace_id: str,
        profile_id: UUID,
        session_id: UUID | None = None,
    ) -> BrowserProfile:
        """释放 profile lock，并更新 last_used_at。"""

        profile = await self.get_profile(workspace_id=workspace_id, profile_id=profile_id, include_deleted=True)
        if profile is None:
            raise ValueError("Browser profile not found")
        if profile.status == BrowserProfileStatus.LOCKED.value and session_id is not None and profile.locked_by_session_id != session_id:
            raise ValueError("Browser profile is locked by another session")

        previous_session_id = profile.locked_by_session_id
        profile.status = BrowserProfileStatus.AVAILABLE.value if profile.status != BrowserProfileStatus.DELETED.value else profile.status
        profile.locked_by_session_id = None
        profile.locked_at = None
        profile.last_used_at = datetime.now(UTC)
        if profile.health_status == BrowserProfileHealthStatus.STALE.value:
            profile.health_status = BrowserProfileHealthStatus.HEALTHY.value
            profile.last_error = None
        if previous_session_id is not None:
            await self._log_profile_event(
                workspace_id=workspace_id,
                session_id=previous_session_id,
                message="Browser profile released",
                metadata={"profile_id": str(profile.id), "profile_path": profile.profile_path},
            )
        await self._log_usage(
            workspace_id=workspace_id,
            profile_id=profile.id,
            session_id=previous_session_id,
            action="release",
            success=True,
            metadata={"profile_path": profile.profile_path},
        )
        await self.session.commit()
        await self.session.refresh(profile)
        logger.info("Browser profile released", extra={"workspace_id": workspace_id, "profile_id": str(profile.id)})
        return profile

    async def mark_corrupted(
        self,
        *,
        workspace_id: str,
        profile_id: UUID,
        error_message: str | None = None,
    ) -> BrowserProfile:
        """标记 profile 损坏，后续不再分配。"""

        profile = await self.get_profile(workspace_id=workspace_id, profile_id=profile_id, include_deleted=True)
        if profile is None:
            raise ValueError("Browser profile not found")
        profile.status = BrowserProfileStatus.CORRUPTED.value
        profile.health_status = BrowserProfileHealthStatus.CORRUPTED.value
        profile.last_error = error_message
        profile.corrupted_at = datetime.now(UTC)
        profile.profile_metadata = {**(profile.profile_metadata or {}), "error_message": error_message}
        await self._log_usage(
            workspace_id=workspace_id,
            profile_id=profile.id,
            session_id=profile.locked_by_session_id,
            action="corrupted",
            success=False,
            error=error_message,
        )
        await self.session.commit()
        await self.session.refresh(profile)
        logger.error("Browser profile corrupted", extra={"workspace_id": workspace_id, "profile_id": str(profile.id)})
        return profile

    async def delete_profile(self, *, workspace_id: str, profile_id: UUID) -> BrowserProfile:
        """逻辑删除 profile，不物理删除 worker/profiles 文件。"""

        profile = await self.get_profile(workspace_id=workspace_id, profile_id=profile_id, include_deleted=True)
        if profile is None:
            raise ValueError("Browser profile not found")
        if profile.status == BrowserProfileStatus.LOCKED.value:
            raise ValueError("Browser profile is locked")
        profile.status = BrowserProfileStatus.DELETED.value
        profile.health_status = BrowserProfileHealthStatus.DELETED.value
        profile.locked_by_session_id = None
        profile.locked_at = None
        await self._log_usage(
            workspace_id=workspace_id,
            profile_id=profile.id,
            session_id=None,
            action="delete",
            success=True,
            metadata={"profile_path": profile.profile_path},
        )
        await self.session.commit()
        await self.session.refresh(profile)
        logger.info("Browser profile deleted", extra={"workspace_id": workspace_id, "profile_id": str(profile.id)})
        return profile

    async def _log_profile_event(
        self,
        *,
        workspace_id: str,
        session_id: UUID,
        message: str,
        level: str = "info",
        metadata: dict[str, object] | None = None,
    ) -> None:
        """把 profile lock/release 写入 browser_action_logs。"""

        session = await self.browser_repository.get_session(session_id=session_id, workspace_id=workspace_id)
        if session is None:
            return
        await self.browser_repository.create_log(
            workspace_id=workspace_id,
            session_id=session_id,
            action_id=None,
            level=level,
            message=message,
            metadata=metadata or {},
        )

    async def _log_usage(
        self,
        *,
        workspace_id: str,
        profile_id: UUID,
        session_id: UUID | None,
        action: str,
        success: bool,
        error: str | None = None,
        metadata: dict[str, object] | None = None,
    ) -> None:
        """写入 browser_profile_usage_logs，便于后续审计和恢复。"""

        self.session.add(
            BrowserProfileUsageLog(
                workspace_id=workspace_id,
                profile_id=profile_id,
                session_id=session_id,
                action=action,
                success=success,
                error=error,
                log_metadata=metadata or {},
            )
        )
        await self.session.flush()

    def _profile_path(self, *, workspace_id: str, profile_id: UUID) -> str:
        """生成 worker 侧 profile path。"""

        safe_workspace_id = self._safe_name(workspace_id)
        return f"{self.settings.browser_profile_root.rstrip('/')}/{safe_workspace_id}/{profile_id}"

    def _safe_name(self, value: str) -> str:
        """生成安全路径片段，避免跨目录写入。"""

        return re.sub(r"[^a-zA-Z0-9_.-]", "-", value).strip("-") or "item"
