"""Task Executor 模块。

TaskExecutor 负责消费 Redis Queue 中的任务，根据 task_type 分发 handler，并回写 PostgreSQL 任务状态和执行结果。
"""

import asyncio
import logging
from collections.abc import Iterable
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models.enums import TaskStatus
from app.models.task import Task
from app.services.queue import TaskQueue
from app.workers.handlers.base import BaseTaskHandler, TaskExecutionResult

logger = logging.getLogger(__name__)


class TaskExecutor:
    """中央任务执行器。"""

    def __init__(
        self,
        queue: TaskQueue,
        handlers: Iterable[BaseTaskHandler],
        dequeue_timeout_seconds: int = 5,
    ) -> None:
        self.queue = queue
        self.handlers = {handler.task_type: handler for handler in handlers}
        self.dequeue_timeout_seconds = dequeue_timeout_seconds

    async def run_once(self, session: AsyncSession) -> bool:
        """从队列拉取并执行一个任务；没有任务时返回 False。"""

        queued_task = await self.queue.dequeue_task(timeout_seconds=self.dequeue_timeout_seconds)
        if queued_task is None:
            return False

        try:
            task = await session.get(Task, queued_task.task_id)
            if task is None:
                logger.warning("Queued task not found in database", extra={"task_id": str(queued_task.task_id)})
                return True
            if task.status in {TaskStatus.COMPLETED.value, TaskStatus.FAILED.value}:
                logger.info(
                    "Queued task skipped because it is already terminal",
                    extra={"task_id": str(task.id), "status": task.status},
                )
                return True

            task.status = TaskStatus.RUNNING.value
            task.started_at = task.started_at or datetime.now(UTC)
            handler = self.handlers.get(task.task_type)
            if handler is None:
                raise RuntimeError(f"Unsupported task type: {task.task_type}")

            result = await handler.handle(dict(task.payload or {}))
            if not result.success:
                raise RuntimeError(result.error or "Task handler failed")

            self._mark_completed(task, result)
            await session.commit()
            logger.info("Task executed successfully", extra={"task_id": str(task.id), "task_type": task.task_type})
            return True
        except Exception as exc:
            await self._handle_failure(session=session, task_id=queued_task.task_id, error=str(exc))
            logger.exception("Task execution failed", extra={"task_id": str(queued_task.task_id)})
            return True

    def _mark_completed(self, task: Task, result: TaskExecutionResult) -> None:
        """将任务标记为 completed 并保存执行结果。"""

        payload = dict(task.payload or {})
        payload["execution_result"] = result.data
        payload.pop("execution_error", None)
        task.payload = payload
        task.status = TaskStatus.COMPLETED.value
        task.completed_at = datetime.now(UTC)
        task.last_error = None

    async def _handle_failure(self, session: AsyncSession, task_id, error: str) -> None:  # type: ignore[no-untyped-def]
        """根据重试次数将任务标记为 retry 或 failed。"""

        try:
            task = await session.get(Task, task_id)
            if task is None:
                await session.rollback()
                return

            payload: dict[str, Any] = dict(task.payload or {})
            payload["execution_error"] = error
            task.payload = payload
            task.last_error = error
            task.completed_at = None
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.RETRY.value
            else:
                task.status = TaskStatus.FAILED.value
            await session.commit()
        except Exception as exc:
            await session.rollback()
            logger.exception("Failed to persist task execution failure", extra={"task_id": str(task_id)})
            raise RuntimeError("Failed to persist task execution failure") from exc


async def run_task_executor_loop(
    session_factory: async_sessionmaker[AsyncSession],
    executor: TaskExecutor,
) -> None:
    """持续运行 TaskExecutor 消费队列。"""

    try:
        logger.info("Task executor loop started")
        while True:
            try:
                async with session_factory() as session:
                    await executor.run_once(session)
            except Exception:
                # 单次执行异常只记录日志，避免整个 worker 循环退出。
                logger.exception("Task executor loop iteration failed")
            await asyncio.sleep(0)
    except asyncio.CancelledError:
        logger.info("Task executor loop cancelled")
        raise
    except Exception as exc:
        logger.exception("Task executor loop failed")
        raise RuntimeError("Task executor loop failed") from exc
