"""任务可观测性数据访问层。

集中封装 task_events、task_logs 和任务概览统计，避免 API/worker 直接拼写 SQL。
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import TaskStatus
from app.models.task import Task
from app.models.task_observability import TaskEvent, TaskLog


class TaskObservabilityRepository:
    """任务事件、日志和统计 Repository。"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_event(
        self,
        *,
        task_id: UUID,
        workspace_id: str | None,
        event_type: str,
        message: str,
        payload: dict[str, Any] | None = None,
    ) -> TaskEvent:
        """写入一条任务生命周期事件。"""

        event = TaskEvent(
            task_id=task_id,
            workspace_id=workspace_id,
            event_type=event_type,
            message=message,
            payload=payload or {},
        )
        self.session.add(event)
        await self.session.flush()
        return event

    async def create_log(
        self,
        *,
        task_id: UUID,
        workspace_id: str | None,
        level: str,
        message: str,
        metadata: dict[str, Any] | None = None,
    ) -> TaskLog:
        """写入一条任务结构化日志。"""

        log = TaskLog(
            task_id=task_id,
            workspace_id=workspace_id,
            level=level.lower(),
            message=message,
            log_metadata=metadata or {},
        )
        self.session.add(log)
        await self.session.flush()
        return log

    async def list_events(
        self,
        *,
        task_id: UUID,
        workspace_id: str,
        limit: int = 100,
    ) -> list[TaskEvent]:
        """按任务查询事件，强制 workspace 过滤。"""

        statement = (
            select(TaskEvent)
            .where(TaskEvent.task_id == task_id, TaskEvent.workspace_id == workspace_id)
            .order_by(TaskEvent.created_at.asc())
            .limit(limit)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def list_logs(
        self,
        *,
        task_id: UUID,
        workspace_id: str,
        limit: int = 200,
    ) -> list[TaskLog]:
        """按任务查询日志，强制 workspace 过滤。"""

        statement = (
            select(TaskLog)
            .where(TaskLog.task_id == task_id, TaskLog.workspace_id == workspace_id)
            .order_by(TaskLog.created_at.asc())
            .limit(limit)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_summary(self, *, workspace_id: str) -> dict[str, int | float | None]:
        """返回当前工作区任务状态概览。"""

        counts: dict[str, int | float | None] = {}
        for status in (
            TaskStatus.PENDING,
            TaskStatus.RUNNING,
            TaskStatus.FAILED,
            TaskStatus.COMPLETED,
            TaskStatus.CANCELLED,
            TaskStatus.TIMEOUT,
        ):
            statement = select(func.count()).select_from(Task).where(
                Task.workspace_id == workspace_id,
                Task.status == status.value,
            )
            result = await self.session.execute(statement)
            counts[f"{status.value}_count"] = int(result.scalar_one())

        avg_statement = select(func.avg(Task.duration_ms)).where(
            Task.workspace_id == workspace_id,
            Task.duration_ms.is_not(None),
        )
        avg_result = await self.session.execute(avg_statement)
        avg_duration = avg_result.scalar_one()
        counts["avg_duration_ms"] = float(avg_duration) if avg_duration is not None else None
        return counts
