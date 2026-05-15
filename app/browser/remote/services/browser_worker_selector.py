"""Browser Worker selection service."""

from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.remote.services.browser_worker_repository import BrowserWorkerRepository
from app.models.browser_worker import BrowserWorker

logger = logging.getLogger(__name__)


class BrowserWorkerSelector:
    """Select the least-loaded online worker inside one workspace."""

    def __init__(self, session: AsyncSession) -> None:
        self.repository = BrowserWorkerRepository(session)

    async def list_available_workers(
        self,
        *,
        workspace_id: str,
        capability: str | None = None,
        capabilities: dict[str, object] | None = None,
        limit: int = 100,
    ) -> list[BrowserWorker]:
        """Return online workers that still have capacity and match capabilities."""

        workers = await self.repository.list_available_workers(
            workspace_id=workspace_id,
            capability=capability,
            limit=limit,
        )
        if capabilities:
            workers = [worker for worker in workers if self._matches_capabilities(worker, capabilities)]
        return workers

    async def select_worker(
        self,
        *,
        workspace_id: str,
        worker_id: UUID | None = None,
        capability: str | None = None,
        capabilities: dict[str, object] | None = None,
    ) -> BrowserWorker | None:
        """Prefer an explicit worker; otherwise choose the least-loaded worker."""

        if worker_id is not None:
            worker = await self.repository.get_worker(workspace_id=workspace_id, worker_id=worker_id)
            if worker is None or worker.status != "online" or worker.active_sessions >= worker.max_sessions:
                return None
            if capability is not None and not bool((worker.capabilities or {}).get(capability)):
                return None
            if capabilities and not self._matches_capabilities(worker, capabilities):
                return None
            return worker

        workers = await self.list_available_workers(
            workspace_id=workspace_id,
            capability=capability,
            capabilities=capabilities,
            limit=100,
        )
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
                    "capabilities": worker.capabilities,
                },
            )
        return worker

    def _matches_capabilities(self, worker: BrowserWorker, expected: dict[str, object]) -> bool:
        """Check exact capability requirements such as browser_runtime/chromium."""

        capabilities = worker.capabilities or {}
        for key, expected_value in expected.items():
            actual = capabilities.get(key)
            if isinstance(expected_value, bool):
                if bool(actual) is not expected_value:
                    return False
                continue
            if expected_value is not None and str(actual).lower() != str(expected_value).lower():
                return False
        return True
