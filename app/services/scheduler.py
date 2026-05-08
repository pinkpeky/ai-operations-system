"""中央任务调度器模块。

该模块负责扫描 pending/retry 任务、推入 Redis Queue，并处理 running 任务超时重试或失败。
"""

import asyncio
import logging
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models.enums import TaskStatus
from app.models.task import Task
from app.services.queue import TaskQueue

logger = logging.getLogger(__name__)


class TaskScheduler:
    """AI 中央任务调度器。"""

    def __init__(
        self,
        queue: TaskQueue,
        batch_size: int = 20,
        running_timeout_seconds: int = 300,
    ) -> None:
        # queue 使用协议类型，真实运行可接 Redis，单测可接内存假队列。
        self.queue = queue
        self.batch_size = batch_size
        self.running_timeout_seconds = running_timeout_seconds

    async def enqueue_due_tasks(self, session: AsyncSession) -> int:
        """扫描 pending/retry 任务并推入队列。"""

        try:
            now = datetime.now(UTC)
            statement = (
                select(Task)
                .where(
                    Task.status.in_([TaskStatus.PENDING.value, TaskStatus.RETRY.value]),
                    or_(Task.scheduled_at.is_(None), Task.scheduled_at <= now),
                )
                .order_by(Task.created_at.asc())
                .limit(self.batch_size)
            )
            result = await session.execute(statement)
            tasks = list(result.scalars().all())

            for task in tasks:
                # 入队前先标记 running，避免同一任务被多轮调度重复扫描。
                task.status = TaskStatus.RUNNING.value
                task.started_at = now
                await self.queue.enqueue_task(
                    task.id,
                    {
                        "task_type": task.task_type,
                        "account_id": str(task.account_id) if task.account_id else None,
                    },
                )

            await session.commit()
            logger.info("Due tasks enqueued", extra={"count": len(tasks)})
            return len(tasks)
        except Exception as exc:
            await session.rollback()
            logger.exception("Failed to enqueue due tasks")
            raise RuntimeError("Failed to enqueue due tasks") from exc

    async def retry_stale_running_tasks(self, session: AsyncSession) -> int:
        """将超时 running 任务转为 retry 或 failed。"""

        try:
            cutoff = datetime.now(UTC) - timedelta(seconds=self.running_timeout_seconds)
            statement = (
                select(Task)
                .where(
                    Task.status == TaskStatus.RUNNING.value,
                    Task.updated_at <= cutoff,
                )
                .order_by(Task.updated_at.asc())
                .limit(self.batch_size)
            )
            result = await session.execute(statement)
            stale_tasks = list(result.scalars().all())

            for task in stale_tasks:
                if task.retry_count < task.max_retries:
                    task.retry_count += 1
                    task.status = TaskStatus.RETRY.value
                    task.last_error = "Task running timeout, scheduled for retry"
                else:
                    task.status = TaskStatus.FAILED.value
                    task.last_error = "Task running timeout, max retries reached"

            await session.commit()
            logger.info("Stale running tasks processed", extra={"count": len(stale_tasks)})
            return len(stale_tasks)
        except Exception as exc:
            await session.rollback()
            logger.exception("Failed to process stale running tasks")
            raise RuntimeError("Failed to process stale running tasks") from exc

    async def mark_task_completed(self, session: AsyncSession, task_id: UUID) -> None:
        """将任务标记为 completed。"""

        try:
            task = await session.get(Task, task_id)
            if task is None:
                raise RuntimeError(f"Task not found: {task_id}")
            task.status = TaskStatus.COMPLETED.value
            task.completed_at = datetime.now(UTC)
            await session.commit()
            logger.info("Task marked completed", extra={"task_id": str(task_id)})
        except Exception as exc:
            await session.rollback()
            logger.exception("Failed to mark task completed", extra={"task_id": str(task_id)})
            raise RuntimeError("Failed to mark task completed") from exc

    async def mark_task_failed(self, session: AsyncSession, task_id: UUID, reason: str) -> None:
        """将任务标记为 failed。"""

        try:
            task = await session.get(Task, task_id)
            if task is None:
                raise RuntimeError(f"Task not found: {task_id}")
            task.status = TaskStatus.FAILED.value
            task.last_error = reason
            await session.commit()
            logger.info("Task marked failed", extra={"task_id": str(task_id)})
        except Exception as exc:
            await session.rollback()
            logger.exception("Failed to mark task failed", extra={"task_id": str(task_id)})
            raise RuntimeError("Failed to mark task failed") from exc

    async def run_once(self, session: AsyncSession) -> dict[str, int]:
        """执行一轮调度，便于 API 启动循环和单元测试复用。"""

        try:
            retried_or_failed = await self.retry_stale_running_tasks(session)
            enqueued = await self.enqueue_due_tasks(session)
            result = {
                "processed_stale_running": retried_or_failed,
                "enqueued": enqueued,
            }
            logger.info("Scheduler run completed", extra=result)
            return result
        except Exception as exc:
            logger.exception("Scheduler run failed")
            raise RuntimeError("Scheduler run failed") from exc


async def run_scheduler_loop(
    session_factory: async_sessionmaker[AsyncSession],
    scheduler: TaskScheduler,
    interval_seconds: float,
) -> None:
    """持续运行调度器循环。"""

    try:
        logger.info("Scheduler loop started", extra={"interval_seconds": interval_seconds})
        while True:
            try:
                async with session_factory() as session:
                    await scheduler.run_once(session)
            except Exception:
                # 单轮失败只记录日志，不让后台调度循环退出。
                logger.exception("Scheduler loop iteration failed")
            await asyncio.sleep(interval_seconds)
    except asyncio.CancelledError:
        logger.info("Scheduler loop cancelled")
        raise
    except Exception as exc:
        logger.exception("Scheduler loop failed")
        raise RuntimeError("Scheduler loop failed") from exc
