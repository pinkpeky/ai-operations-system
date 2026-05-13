"""任务数据访问模块。

该模块封装 tasks 表的常用读写操作，避免业务代码直接散落 SQLAlchemy 查询。
"""

import logging
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import TaskStatus
from app.models.task import Task

logger = logging.getLogger(__name__)


class TaskRepository:
    """任务 Repository。"""

    def __init__(self, session: AsyncSession) -> None:
        # session 由外部注入，便于在 API 请求和单测中控制事务边界。
        self.session = session

    async def create_task(
        self,
        title: str,
        task_type: str,
        payload: dict[str, Any] | None = None,
        account_id: UUID | None = None,
        workspace_id: str | None = None,
        user_id: str | None = None,
        scheduled_at: datetime | None = None,
        max_retries: int = 3,
    ) -> Task:
        """创建 pending 任务。"""

        try:
            task = Task(
                title=title,
                task_type=task_type,
                payload=payload or {},
                account_id=account_id,
                workspace_id=workspace_id,
                user_id=user_id,
                scheduled_at=scheduled_at,
                max_retries=max_retries,
                status=TaskStatus.PENDING.value,
            )
            self.session.add(task)
            await self.session.commit()
            await self.session.refresh(task)
            logger.info("Task created", extra={"task_id": str(task.id), "task_type": task_type})
            return task
        except Exception as exc:
            await self.session.rollback()
            logger.exception("Failed to create task", extra={"task_type": task_type})
            raise RuntimeError("Failed to create task") from exc

    async def get_task(self, task_id: UUID, workspace_id: str | None = None) -> Task | None:
        """按 ID 查询任务。"""

        try:
            if workspace_id is None:
                task = await self.session.get(Task, task_id)
            else:
                statement = select(Task).where(Task.id == task_id, Task.workspace_id == workspace_id)
                result = await self.session.execute(statement)
                task = result.scalar_one_or_none()
            logger.debug("Task loaded", extra={"task_id": str(task_id), "found": task is not None})
            return task
        except Exception as exc:
            logger.exception("Failed to get task", extra={"task_id": str(task_id)})
            raise RuntimeError("Failed to get task") from exc

    async def list_tasks_by_status(
        self,
        status: TaskStatus,
        limit: int = 50,
        workspace_id: str | None = None,
    ) -> list[Task]:
        """按状态查询任务列表。"""

        try:
            statement = (
                select(Task)
                .where(Task.status == status.value)
                .order_by(Task.created_at.desc())
                .limit(limit)
            )
            if workspace_id is not None:
                statement = statement.where(Task.workspace_id == workspace_id)
            result = await self.session.execute(statement)
            tasks = list(result.scalars().all())
            logger.debug("Tasks listed by status", extra={"status": status.value, "count": len(tasks)})
            return tasks
        except Exception as exc:
            logger.exception("Failed to list tasks by status", extra={"status": status.value})
            raise RuntimeError("Failed to list tasks by status") from exc

    async def cancel_task(self, task_id: UUID, workspace_id: str) -> Task | None:
        """取消尚未终止的任务。"""

        task = await self.get_task(task_id=task_id, workspace_id=workspace_id)
        if task is None:
            return None
        terminal_statuses = {
            TaskStatus.COMPLETED.value,
            TaskStatus.FAILED.value,
            TaskStatus.CANCELLED.value,
            TaskStatus.TIMEOUT.value,
        }
        if task.status in terminal_statuses and task.status != TaskStatus.CANCELLED.value:
            raise ValueError(f"Cannot cancel terminal task with status: {task.status}")
        task.status = TaskStatus.CANCELLED.value
        now = datetime.now(UTC)
        task.completed_at = now
        task.duration_ms = self._calculate_duration_ms(task.started_at, task.completed_at)
        task.last_error = "Task cancelled by user"
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def retry_task(self, task_id: UUID, workspace_id: str) -> Task | None:
        """手动重试 failed/cancelled/timeout 任务。"""

        task = await self.get_task(task_id=task_id, workspace_id=workspace_id)
        if task is None:
            return None
        if task.status not in {
            TaskStatus.FAILED.value,
            TaskStatus.CANCELLED.value,
            TaskStatus.TIMEOUT.value,
        }:
            raise ValueError(f"Task with status {task.status} cannot be retried manually")
        payload = dict(task.payload or {})
        payload.pop("execution_error", None)
        task.payload = payload
        task.status = TaskStatus.RETRY.value
        task.retry_count = 0
        task.started_at = None
        task.completed_at = None
        task.duration_ms = None
        task.last_error = None
        await self.session.commit()
        await self.session.refresh(task)
        return task

    def _calculate_duration_ms(self, started_at: datetime | None, completed_at: datetime | None) -> int | None:
        """计算任务耗时，缺少开始或结束时间时返回 None。"""

        if started_at is None or completed_at is None:
            return None
        if started_at.tzinfo is None and completed_at.tzinfo is not None:
            started_at = started_at.replace(tzinfo=completed_at.tzinfo)
        if completed_at.tzinfo is None and started_at.tzinfo is not None:
            completed_at = completed_at.replace(tzinfo=started_at.tzinfo)
        return max(0, int((completed_at - started_at).total_seconds() * 1000))
