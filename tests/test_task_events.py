"""任务事件测试。"""

from collections import deque
from typing import Any
from uuid import UUID

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import TaskStatus
from app.models.task import Task
from app.models.task_observability import TaskEvent
from app.services.queue import QueuedTask
from app.workers.handlers.agentic_rag_handler import AGENTIC_RAG_TASK_TYPE
from app.workers.handlers.base import BaseTaskHandler, TaskExecutionResult
from app.workers.task_executor import TaskExecutor


class InMemoryQueue:
    """TaskExecutor 测试用内存队列。"""

    def __init__(self, items: list[QueuedTask] | None = None) -> None:
        self.items = deque(items or [])

    async def enqueue_task(self, task_id: UUID, payload: dict[str, Any] | None = None) -> None:
        self.items.append(QueuedTask(task_id=task_id, payload=payload or {}))

    async def dequeue_task(self, timeout_seconds: int = 5) -> QueuedTask | None:
        if not self.items:
            return None
        return self.items.popleft()


class SuccessfulHandler(BaseTaskHandler):
    """成功 handler。"""

    task_type = AGENTIC_RAG_TASK_TYPE

    async def handle(self, payload: dict[str, Any]) -> TaskExecutionResult:
        return TaskExecutionResult(success=True, data={"provider": "mock", "model": "mock-llm", "latency_ms": 7})


@pytest.mark.asyncio
async def test_task_executor_writes_started_and_completed_events(session: AsyncSession) -> None:
    """TaskExecutor 执行成功时应写入 started/completed 事件。"""

    task = Task(
        title="agentic rag",
        task_type=AGENTIC_RAG_TASK_TYPE,
        payload={"query": "hello"},
        status=TaskStatus.RUNNING.value,
        workspace_id="workspace-events",
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)

    executor = TaskExecutor(
        queue=InMemoryQueue([QueuedTask(task_id=task.id, payload={})]),
        handlers=[SuccessfulHandler()],
        dequeue_timeout_seconds=0,
    )
    await executor.run_once(session)

    result = await session.execute(select(TaskEvent).where(TaskEvent.task_id == task.id).order_by(TaskEvent.created_at))
    event_types = [event.event_type for event in result.scalars().all()]

    assert event_types == ["started", "completed"]
