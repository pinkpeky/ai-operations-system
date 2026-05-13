"""Browser Worker 选择服务。"""

from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.remote.services.browser_worker_repository import BrowserWorkerRepository
from app.models.browser_worker import BrowserWorker

logger = logging.getLogger(__name__)


class BrowserWorkerSelector:
    """在单个 workspace 内选择负载最低且仍有容量的 worker。"""

    def __init__(self, session: AsyncSession) -> None:
        self.repository = BrowserWorkerRepository(session)

    async def list_available_workers(
        self,
        *,
        workspace_id: str,
        capability: str | None = None,
        limit: int = 100,
    ) -> list[BrowserWorker]:
        """返回在线、能力匹配且未超过容量的 worker。"""

        return await self.repository.list_available_workers(
            workspace_id=workspace_id,
            capability=capability,
            limit=limit,
        )

    async def select_worker(
        self,
        *,
        workspace_id: str,
        worker_id: UUID | None = None,
        capability: str | None = None,
    ) -> BrowserWorker | None:
        """优先使用显式 worker；否则按负载选择 least-loaded worker。"""

        if worker_id is not None:
            worker = await self.repository.get_worker(workspace_id=workspace_id, worker_id=worker_id)
            if worker is None or worker.status != "online" or worker.active_sessions >= worker.max_sessions:
                return None
            if capability is not None and not bool((worker.capabilities or {}).get(capability)):
                return None
            return worker

        workers = await self.list_available_workers(workspace_id=workspace_id, capability=capability, limit=1)
        worker = workers[0] if workers else None
        if worker is not None:
            logger.info(
                "Browser worker selected",
                extra={
                    "workspace_id": workspace_id,
                    "worker_id": str(worker.id),
                    "worker_name": worker.worker_name,
                    "active_sessions": worker.active_sessions,
                    "current_load": worker.current_load,
                },
            )
        return worker
