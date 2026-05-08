"""任务数据访问模块。

该模块封装 tasks 表的常用读写操作，避免业务代码直接散落 SQLAlchemy 查询。
"""

import logging
from datetime import datetime
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

    async def get_task(self, task_id: UUID) -> Task | None:
        """按 ID 查询任务。"""

        try:
            task = await self.session.get(Task, task_id)
            logger.debug("Task loaded", extra={"task_id": str(task_id), "found": task is not None})
            return task
        except Exception as exc:
            logger.exception("Failed to get task", extra={"task_id": str(task_id)})
            raise RuntimeError("Failed to get task") from exc

    async def list_tasks_by_status(self, status: TaskStatus, limit: int = 50) -> list[Task]:
        """按状态查询任务列表。"""

        try:
            statement = (
                select(Task)
                .where(Task.status == status.value)
                .order_by(Task.created_at.desc())
                .limit(limit)
            )
            result = await self.session.execute(statement)
            tasks = list(result.scalars().all())
            logger.debug("Tasks listed by status", extra={"status": status.value, "count": len(tasks)})
            return tasks
        except Exception as exc:
            logger.exception("Failed to list tasks by status", extra={"status": status.value})
            raise RuntimeError("Failed to list tasks by status") from exc
