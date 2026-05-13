"""Task Executor 模块。

TaskExecutor 负责消费 Redis Queue 中的任务，根据 task_type 分发 handler，并回写任务状态、
执行结果、生命周期事件和结构化日志。它不参与 Scheduler 的任务扫描与入队逻辑。
"""

import asyncio
import logging
from collections.abc import Iterable
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models.enums import TaskStatus
from app.models.task import Task
from app.repositories.task_observability_repository import TaskObservabilityRepository
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
        execution_timeout_seconds: int = 300,
    ) -> None:
        self.queue = queue
        self.handlers = {handler.task_type: handler for handler in handlers}
        self.dequeue_timeout_seconds = dequeue_timeout_seconds
        self.execution_timeout_seconds = execution_timeout_seconds

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
            if task.status == TaskStatus.CANCELLED.value:
                await self._record_cancelled_skip(session=session, task=task)
                await session.commit()
                return True
            if task.status in {
                TaskStatus.COMPLETED.value,
                TaskStatus.FAILED.value,
                TaskStatus.CANCELLED.value,
                TaskStatus.TIMEOUT.value,
            }:
                logger.info(
                    "Queued task skipped because it is already terminal",
                    extra={"task_id": str(task.id), "status": task.status},
                )
                return True

            task.status = TaskStatus.RUNNING.value
            task.started_at = datetime.now(UTC)
            task.completed_at = None
            task.duration_ms = None
            observability = TaskObservabilityRepository(session)
            await observability.create_event(
                task_id=task.id,
                workspace_id=task.workspace_id,
                event_type="started",
                message="Task execution started",
                payload={"task_type": task.task_type, "retry_count": task.retry_count},
            )
            await observability.create_log(
                task_id=task.id,
                workspace_id=task.workspace_id,
                level="info",
                message="Task execution started",
                metadata={"task_type": task.task_type, "retry_count": task.retry_count},
            )

            handler = self.handlers.get(task.task_type)
            if handler is None:
                raise RuntimeError(f"Unsupported task type: {task.task_type}")

            result = await asyncio.wait_for(
                handler.handle(self._build_handler_payload(task)),
                timeout=self.execution_timeout_seconds,
            )
            if not result.success:
                raise RuntimeError(result.error or "Task handler failed")

            await self._mark_completed(session=session, task=task, result=result)
            await session.commit()
            logger.info("Task executed successfully", extra={"task_id": str(task.id), "task_type": task.task_type})
            return True
        except TimeoutError:
            await self._handle_timeout(session=session, task_id=queued_task.task_id)
            logger.exception("Task execution timed out", extra={"task_id": str(queued_task.task_id)})
            return True
        except Exception as exc:
            await self._handle_failure(session=session, task_id=queued_task.task_id, error=str(exc))
            logger.exception("Task execution failed", extra={"task_id": str(queued_task.task_id)})
            return True

    def _build_handler_payload(self, task: Task) -> dict[str, Any]:
        """构建传给 handler 的 payload，并注入任务上下文供下游记录 provider/model/latency。"""

        payload = dict(task.payload or {})
        payload.setdefault("workspace_id", task.workspace_id)
        payload.setdefault("task_id", str(task.id))
        return payload

    async def _mark_completed(self, session: AsyncSession, task: Task, result: TaskExecutionResult) -> None:
        """将任务标记为 completed 并保存执行结果。"""

        payload = dict(task.payload or {})
        payload["execution_result"] = result.data
        payload.pop("execution_error", None)
        task.payload = payload
        task.status = TaskStatus.COMPLETED.value
        task.completed_at = datetime.now(UTC)
        task.duration_ms = self._calculate_duration_ms(task.started_at, task.completed_at)
        task.last_error = None

        observability = TaskObservabilityRepository(session)
        await observability.create_event(
            task_id=task.id,
            workspace_id=task.workspace_id,
            event_type="completed",
            message="Task execution completed",
            payload={"duration_ms": task.duration_ms},
        )
        await observability.create_log(
            task_id=task.id,
            workspace_id=task.workspace_id,
            level="info",
            message="Task execution completed",
            metadata={
                "provider": self._extract_provider(result.data),
                "model": self._extract_model(result.data),
                "latency_ms": self._extract_latency_ms(result.data),
                "error": None,
                "workspace_id": task.workspace_id,
                "task_id": str(task.id),
                "duration_ms": task.duration_ms,
            },
        )

    async def _handle_failure(self, session: AsyncSession, task_id, error: str) -> None:  # type: ignore[no-untyped-def]
        """根据重试次数将任务标记为 retry 或 failed，并记录事件/日志。"""

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
            task.duration_ms = self._calculate_duration_ms(task.started_at, datetime.now(UTC))

            observability = TaskObservabilityRepository(session)
            await observability.create_event(
                task_id=task.id,
                workspace_id=task.workspace_id,
                event_type="failed",
                message="Task execution failed",
                payload={"error": error, "retry_count": task.retry_count},
            )
            await observability.create_log(
                task_id=task.id,
                workspace_id=task.workspace_id,
                level="error",
                message="Task execution failed",
                metadata={
                    "error": error,
                    "workspace_id": task.workspace_id,
                    "task_id": str(task.id),
                    "duration_ms": task.duration_ms,
                },
            )
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.RETRY.value
                await observability.create_event(
                    task_id=task.id,
                    workspace_id=task.workspace_id,
                    event_type="retry_scheduled",
                    message="Task scheduled for retry",
                    payload={"retry_count": task.retry_count, "max_retries": task.max_retries},
                )
            else:
                task.status = TaskStatus.FAILED.value
                task.completed_at = datetime.now(UTC)
                task.duration_ms = self._calculate_duration_ms(task.started_at, task.completed_at)
            await session.commit()
        except Exception as exc:
            await session.rollback()
            logger.exception("Failed to persist task execution failure", extra={"task_id": str(task_id)})
            raise RuntimeError("Failed to persist task execution failure") from exc

    async def _handle_timeout(self, session: AsyncSession, task_id) -> None:  # type: ignore[no-untyped-def]
        """将执行超时任务标记为 timeout 并记录日志。"""

        try:
            task = await session.get(Task, task_id)
            if task is None:
                await session.rollback()
                return
            timeout_message = f"Task execution timed out after {self.execution_timeout_seconds} seconds"
            payload: dict[str, Any] = dict(task.payload or {})
            payload["execution_error"] = timeout_message
            task.payload = payload
            task.status = TaskStatus.TIMEOUT.value
            task.completed_at = datetime.now(UTC)
            task.duration_ms = self._calculate_duration_ms(task.started_at, task.completed_at)
            task.last_error = timeout_message

            observability = TaskObservabilityRepository(session)
            await observability.create_event(
                task_id=task.id,
                workspace_id=task.workspace_id,
                event_type="timeout",
                message=timeout_message,
                payload={"duration_ms": task.duration_ms},
            )
            await observability.create_log(
                task_id=task.id,
                workspace_id=task.workspace_id,
                level="error",
                message=timeout_message,
                metadata={
                    "error": timeout_message,
                    "workspace_id": task.workspace_id,
                    "task_id": str(task.id),
                    "duration_ms": task.duration_ms,
                },
            )
            await session.commit()
        except Exception as exc:
            await session.rollback()
            logger.exception("Failed to persist task timeout", extra={"task_id": str(task_id)})
            raise RuntimeError("Failed to persist task timeout") from exc

    async def _record_cancelled_skip(self, session: AsyncSession, task: Task) -> None:
        """记录 cancelled 任务被执行器跳过。"""

        observability = TaskObservabilityRepository(session)
        await observability.create_event(
            task_id=task.id,
            workspace_id=task.workspace_id,
            event_type="cancelled_skipped",
            message="Cancelled task skipped by executor",
            payload={"status": task.status},
        )
        await observability.create_log(
            task_id=task.id,
            workspace_id=task.workspace_id,
            level="warning",
            message="Cancelled task skipped by executor",
            metadata={"workspace_id": task.workspace_id, "task_id": str(task.id)},
        )

    def _calculate_duration_ms(self, started_at: datetime | None, completed_at: datetime | None) -> int | None:
        """计算任务执行耗时。"""

        if started_at is None or completed_at is None:
            return None
        if started_at.tzinfo is None and completed_at.tzinfo is not None:
            started_at = started_at.replace(tzinfo=completed_at.tzinfo)
        if completed_at.tzinfo is None and started_at.tzinfo is not None:
            completed_at = completed_at.replace(tzinfo=started_at.tzinfo)
        return max(0, int((completed_at - started_at).total_seconds() * 1000))

    def _extract_provider(self, data: dict[str, Any]) -> str | None:
        """从执行结果中提取 provider。"""

        return str(data.get("provider")) if data.get("provider") is not None else None

    def _extract_model(self, data: dict[str, Any]) -> str | None:
        """从执行结果中提取 model。"""

        return str(data.get("model")) if data.get("model") is not None else None

    def _extract_latency_ms(self, data: dict[str, Any]) -> int | None:
        """从执行结果或 debug 字段中提取 latency_ms。"""

        latency = data.get("latency_ms")
        if latency is None and isinstance(data.get("debug"), dict):
            latency = data["debug"].get("latency_ms")
        return int(latency) if latency is not None else None


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
