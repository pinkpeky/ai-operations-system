"""In-process background executor for task_runs.

This is intentionally lightweight. It polls task_runs from PostgreSQL and runs
them in-process; it is not Celery, RabbitMQ, Kubernetes, or a production HA
distributed queue.
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Callable

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.task_orchestration.recovery_service import TaskRecoveryService
from app.task_orchestration.service import TaskOrchestratorService

logger = logging.getLogger(__name__)


class BackgroundTaskExecutor:
    """Simple polling executor for pending task runs."""

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        *,
        poll_interval_seconds: float = 2.0,
        batch_size: int = 5,
        scheduler_name: str = "api-in-process-task-scheduler",
        lease_seconds: int = 120,
        stuck_timeout_seconds: int = 300,
        recovery_interval_seconds: float = 10.0,
    ) -> None:
        self.session_factory = session_factory
        self.poll_interval_seconds = poll_interval_seconds
        self.batch_size = batch_size
        self.scheduler_name = scheduler_name
        self.lease_seconds = lease_seconds
        self.stuck_timeout_seconds = stuck_timeout_seconds
        self.recovery_interval_seconds = recovery_interval_seconds
        self._last_recovery_at = 0.0
        self._running = False

    @property
    def running(self) -> bool:
        return self._running

    async def run_once(self) -> int:
        """Poll and execute a batch of task runs."""

        async with self.session_factory() as session:
            recovery = TaskRecoveryService(
                session,
                scheduler_name=self.scheduler_name,
                lease_seconds=self.lease_seconds,
                stuck_timeout_seconds=self.stuck_timeout_seconds,
            )
            if time.monotonic() - self._last_recovery_at >= self.recovery_interval_seconds:
                await recovery.scan_once()
                self._last_recovery_at = time.monotonic()
            service = TaskOrchestratorService(session, lease_owner=self.scheduler_name, lease_seconds=self.lease_seconds)
            tasks = await service.poll_pending_tasks(limit=self.batch_size)
            count = 0
            for task in tasks:
                await service.execute_task(task=task)
                count += 1
            return count

    async def run_forever(self) -> None:
        """Run the polling loop until cancelled."""

        self._running = True
        logger.info("Background task executor loop started", extra={"interval_seconds": self.poll_interval_seconds})
        try:
            async with self.session_factory() as session:
                await TaskRecoveryService(
                    session,
                    scheduler_name=self.scheduler_name,
                    lease_seconds=self.lease_seconds,
                    stuck_timeout_seconds=self.stuck_timeout_seconds,
                ).scan_once()
                self._last_recovery_at = time.monotonic()
            while True:
                try:
                    await self.run_once()
                except Exception:
                    logger.exception("Background task executor loop iteration failed")
                await asyncio.sleep(self.poll_interval_seconds)
        except asyncio.CancelledError:
            logger.info("Background task executor loop cancelled")
            raise
        finally:
            try:
                async with self.session_factory() as session:
                    await TaskRecoveryService(
                        session,
                        scheduler_name=self.scheduler_name,
                        lease_seconds=self.lease_seconds,
                        stuck_timeout_seconds=self.stuck_timeout_seconds,
                    ).release_executor_leases()
            except Exception:
                logger.exception("Background task executor lease release failed")
            self._running = False


async def run_background_task_executor_loop(
    session_factory: async_sessionmaker[AsyncSession],
    *,
    poll_interval_seconds: float = 2.0,
    batch_size: int = 5,
    scheduler_name: str = "api-in-process-task-scheduler",
    lease_seconds: int = 120,
    stuck_timeout_seconds: int = 300,
    recovery_interval_seconds: float = 10.0,
    executor_factory: Callable[..., BackgroundTaskExecutor] = BackgroundTaskExecutor,
) -> None:
    """Entry point used by FastAPI lifespan."""

    executor = executor_factory(
        session_factory,
        poll_interval_seconds=poll_interval_seconds,
        batch_size=batch_size,
        scheduler_name=scheduler_name,
        lease_seconds=lease_seconds,
        stuck_timeout_seconds=stuck_timeout_seconds,
        recovery_interval_seconds=recovery_interval_seconds,
    )
    await executor.run_forever()
