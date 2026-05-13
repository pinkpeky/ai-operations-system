"""Browser Session 清理服务。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.remote.services.browser_worker_repository import BrowserWorkerRepository
from app.browser.repositories import BrowserRepository
from app.browser.services.browser_profile_health_service import BrowserProfileHealthService
from app.core.config import Settings, get_settings
from app.models.browser import BrowserSession
from app.models.browser_worker import BrowserWorker, BrowserWorkerSession
from app.models.enums import BrowserSessionStatus, BrowserWorkerSessionStatus, BrowserWorkerStatus

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class BrowserSessionCleanupResult:
    """结构化 session 清理结果。"""

    workspace_id: str
    stale_sessions: int
    offline_worker_sessions: int
    closed_sessions: int
    failed_sessions: int
    log_count: int


class BrowserSessionCleanupService:
    """清理 stale session，并处理 offline/error worker 关联的 session。"""

    def __init__(self, session: AsyncSession, *, settings: Settings | None = None) -> None:
        self.session = session
        self.settings = settings or get_settings()
        self.browser_repository = BrowserRepository(session)
        self.worker_repository = BrowserWorkerRepository(session)

    async def cleanup_stale_sessions(
        self,
        *,
        workspace_id: str,
        session_timeout_seconds: int | None = None,
        close_stale_sessions: bool = True,
    ) -> BrowserSessionCleanupResult:
        """将超时 session 关闭，并将离线 worker 的 session 标记为 failed。"""

        timeout_seconds = session_timeout_seconds or self.settings.browser_session_timeout_seconds
        threshold = datetime.now(UTC) - timedelta(seconds=timeout_seconds)
        statement = (
            select(BrowserWorkerSession, BrowserSession, BrowserWorker)
            .join(BrowserWorker, BrowserWorker.id == BrowserWorkerSession.worker_id)
            .join(BrowserSession, BrowserSession.id == BrowserWorkerSession.local_browser_session_id)
            .where(
                BrowserWorkerSession.workspace_id == workspace_id,
                BrowserWorkerSession.status == BrowserWorkerSessionStatus.ACTIVE.value,
                BrowserSession.status == BrowserSessionStatus.ACTIVE.value,
            )
        )
        result = await self.session.execute(statement)
        rows = list(result.all())

        stale_sessions = 0
        offline_worker_sessions = 0
        closed_sessions = 0
        failed_sessions = 0
        log_count = 0

        for worker_session, browser_session, worker in rows:
            created_at = browser_session.created_at
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=UTC)
            is_stale = created_at < threshold
            is_worker_offline = worker.status in {BrowserWorkerStatus.OFFLINE.value, BrowserWorkerStatus.ERROR.value}

            if not is_stale and not is_worker_offline:
                continue
            if is_stale:
                stale_sessions += 1
            if is_worker_offline:
                offline_worker_sessions += 1

            if is_worker_offline:
                await self.worker_repository.fail_worker_session(worker_session, error="worker offline during cleanup")
                await self.browser_repository.update_session_status(
                    browser_session=browser_session,
                    status=BrowserSessionStatus.FAILED.value,
                    metadata_patch={"cleanup_reason": "worker_offline"},
                )
                failed_sessions += 1
                level = "error"
                message = "Browser session failed because worker is offline"
            elif close_stale_sessions:
                await self.worker_repository.close_worker_session(worker_session)
                await self.browser_repository.update_session_status(
                    browser_session=browser_session,
                    status=BrowserSessionStatus.CLOSED.value,
                    metadata_patch={"cleanup_reason": "session_stale"},
                )
                closed_sessions += 1
                level = "info"
                message = "Browser session closed by stale session cleanup"
            else:
                continue

            if browser_session.profile_id is not None and browser_session.persistent_context_enabled:
                await BrowserProfileHealthService(self.session, settings=self.settings).recover_stale_lock(
                    workspace_id=workspace_id,
                    profile_id=browser_session.profile_id,
                    reason="session cleanup released profile lock",
                )

            await self.browser_repository.create_log(
                workspace_id=workspace_id,
                session_id=browser_session.id,
                action_id=None,
                level=level,
                message=message,
                metadata={
                    "worker_id": str(worker.id),
                    "worker_name": worker.worker_name,
                    "timeout_seconds": timeout_seconds,
                    "is_stale": is_stale,
                    "is_worker_offline": is_worker_offline,
                },
            )
            log_count += 1

        await self.session.commit()
        logger.info(
            "Browser session cleanup completed",
            extra={
                "workspace_id": workspace_id,
                "stale_sessions": stale_sessions,
                "offline_worker_sessions": offline_worker_sessions,
                "closed_sessions": closed_sessions,
                "failed_sessions": failed_sessions,
            },
        )
        return BrowserSessionCleanupResult(
            workspace_id=workspace_id,
            stale_sessions=stale_sessions,
            offline_worker_sessions=offline_worker_sessions,
            closed_sessions=closed_sessions,
            failed_sessions=failed_sessions,
            log_count=log_count,
        )
