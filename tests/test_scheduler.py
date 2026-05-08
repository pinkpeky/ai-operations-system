"""Scheduler 测试模块。

该模块验证 pending/retry/running/failed 状态流转，确保调度器可以独立测试。
"""

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import TaskStatus
from app.models.task import Task
from app.services.queue import QueuedTask
from app.services.scheduler import TaskScheduler


class InMemoryQueue:
    """用于测试 Scheduler 的内存队列。"""

    def __init__(self) -> None:
        self.items: list[QueuedTask] = []

    async def enqueue_task(self, task_id: UUID, payload: dict[str, Any] | None = None) -> None:
        """模拟任务入队。"""

        self.items.append(QueuedTask(task_id=task_id, payload=payload or {}))

    async def dequeue_task(self, timeout_seconds: int = 5) -> QueuedTask | None:
        """模拟任务出队。"""

        if not self.items:
            return None
        return self.items.pop(0)


@pytest.mark.asyncio
async def test_scheduler_enqueues_pending_and_retry_tasks(session: AsyncSession) -> None:
    """调度器应扫描 pending/retry 任务并改为 running。"""

    pending_task = Task(title="pending", task_type="publish", payload={}, status=TaskStatus.PENDING.value)
    retry_task = Task(title="retry", task_type="publish", payload={}, status=TaskStatus.RETRY.value)
    failed_task = Task(title="failed", task_type="publish", payload={}, status=TaskStatus.FAILED.value)
    session.add_all([pending_task, retry_task, failed_task])
    await session.commit()

    queue = InMemoryQueue()
    scheduler = TaskScheduler(queue=queue, batch_size=10)
    count = await scheduler.enqueue_due_tasks(session)

    assert count == 2
    assert len(queue.items) == 2
    assert pending_task.status == TaskStatus.RUNNING.value
    assert retry_task.status == TaskStatus.RUNNING.value
    assert failed_task.status == TaskStatus.FAILED.value


@pytest.mark.asyncio
async def test_scheduler_retries_or_fails_stale_running_tasks(session: AsyncSession) -> None:
    """超时 running 任务应进入 retry，超过重试次数后进入 failed。"""

    stale_time = datetime.now(UTC) - timedelta(minutes=10)
    retryable_task = Task(
        title="retryable",
        task_type="publish",
        payload={},
        status=TaskStatus.RUNNING.value,
        retry_count=0,
        max_retries=1,
        updated_at=stale_time,
    )
    exhausted_task = Task(
        title="exhausted",
        task_type="publish",
        payload={},
        status=TaskStatus.RUNNING.value,
        retry_count=1,
        max_retries=1,
        updated_at=stale_time,
    )
    session.add_all([retryable_task, exhausted_task])
    await session.commit()

    scheduler = TaskScheduler(queue=InMemoryQueue(), batch_size=10, running_timeout_seconds=1)
    count = await scheduler.retry_stale_running_tasks(session)

    result = await session.execute(select(Task).order_by(Task.title.asc()))
    tasks = {task.title: task for task in result.scalars().all()}

    assert count == 2
    assert tasks["retryable"].status == TaskStatus.RETRY.value
    assert tasks["retryable"].retry_count == 1
    assert tasks["exhausted"].status == TaskStatus.FAILED.value
