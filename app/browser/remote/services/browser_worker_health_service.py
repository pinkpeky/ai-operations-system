"""Browser Worker 健康监控服务。"""

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.remote.services.browser_worker_repository import BrowserWorkerRepository
from app.core.config import Settings, get_settings
from app.models.browser_worker import BrowserWorker

logger = logging.getLogger(__name__)


class BrowserWorkerHealthService:
    """监控 worker heartbeat，并输出 workspace 维度健康摘要。"""

    def __init__(self, session: AsyncSession, *, settings: Settings | None = None) -> None:
        self.session = session
        self.settings = settings or get_settings()
        self.repository = BrowserWorkerRepository(session)

    async def mark_stale_workers_offline(self, *, workspace_id: str) -> list[BrowserWorker]:
        """当 heartbeat 超时时，将 stale worker 标记为 offline。"""

        stale_workers = await self.repository.mark_stale_workers_offline(
            workspace_id=workspace_id,
            timeout_seconds=self.settings.browser_worker_heartbeat_timeout_seconds,
        )
        await self.session.commit()
        for worker in stale_workers:
            logger.warning(
                "Browser worker marked offline due to stale heartbeat",
                extra={"workspace_id": workspace_id, "worker_id": str(worker.id), "worker_name": worker.worker_name},
            )
        return stale_workers

    async def health_summary(self, *, workspace_id: str) -> dict[str, Any]:
        """返回 worker 健康、容量与可分配数量摘要。"""

        summary = await self.repository.summarize_workers(
            workspace_id=workspace_id,
            timeout_seconds=self.settings.browser_worker_heartbeat_timeout_seconds,
        )
        available = await self.repository.list_available_workers(workspace_id=workspace_id, limit=1000)
        summary["available_workers"] = len(available)
        summary["heartbeat_timeout_seconds"] = self.settings.browser_worker_heartbeat_timeout_seconds
        return summary

    async def mark_worker_offline(
        self,
        *,
        workspace_id: str,
        worker_id: UUID,
        error_message: str | None = None,
    ) -> BrowserWorker:
        """手动将单个 worker 标记为 offline，便于维护和故障隔离。"""

        worker = await self.repository.get_worker(workspace_id=workspace_id, worker_id=worker_id)
        if worker is None:
            raise ValueError("Browser worker not found")
        updated = await self.repository.mark_worker_offline(worker=worker, error_message=error_message or "manual mark offline")
        await self.session.commit()
        await self.session.refresh(updated)
        logger.info(
            "Browser worker manually marked offline",
            extra={"workspace_id": workspace_id, "worker_id": str(worker_id), "error_message": updated.error_message},
        )
        return updated
