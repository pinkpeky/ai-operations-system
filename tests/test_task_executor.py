"""TaskExecutor 测试模块。

验证队列消费、handler 分发、任务完成、retry 和 failed 状态回写。
"""

from collections import deque
from typing import Any
from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import TaskStatus
from app.models.task import Task
from app.services.queue import QueuedTask
from app.workers.handlers.agentic_rag_handler import AGENTIC_RAG_TASK_TYPE
from app.workers.handlers.base import BaseTaskHandler, TaskExecutionResult
from app.workers.task_executor import TaskExecutor


class InMemoryQueue:
    """TaskExecutor 测试用内存队列。"""

    def __init__(self, items: list[QueuedTask] | None = None) -> None:
        self.items = deque(items or [])

    async def enqueue_task(self, task_id: UUID, payload: dict[str, Any] | None = None) -> None:
        """加入内存队列。"""

        self.items.append(QueuedTask(task_id=task_id, payload=payload or {}))

    async def dequeue_task(self, timeout_seconds: int = 5) -> QueuedTask | None:
        """从内存队列取出任务。"""

        if not self.items:
            return None
        return self.items.popleft()


class SuccessfulHandler(BaseTaskHandler):
    """成功 handler。"""

    task_type = AGENTIC_RAG_TASK_TYPE

    async def handle(self, payload: dict[str, Any]) -> TaskExecutionResult:
        """返回成功执行结果。"""

        return TaskExecutionResult(
            success=True,
            data={"answer": "ok", "input_query": payload["query"]},
        )


class FailingHandler(BaseTaskHandler):
    """失败 handler。"""

    task_type = AGENTIC_RAG_TASK_TYPE

    async def handle(self, payload: dict[str, Any]) -> TaskExecutionResult:
        """返回失败执行结果。"""

        return TaskExecutionResult(success=False, error="handler failed")


@pytest.mark.asyncio
async def test_task_executor_marks_task_completed(session: AsyncSession) -> None:
    """TaskExecutor 应消费队列任务并写回 completed 与 execution_result。"""

    task = Task(
        title="agentic rag",
        task_type=AGENTIC_RAG_TASK_TYPE,
        payload={"query": "hello"},
        status=TaskStatus.RUNNING.value,
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)

    queue = InMemoryQueue([QueuedTask(task_id=task.id, payload={})])
    executor = TaskExecutor(queue=queue, handlers=[SuccessfulHandler()], dequeue_timeout_seconds=0)

    executed = await executor.run_once(session)
    await session.refresh(task)

    assert executed is True
    assert task.status == TaskStatus.COMPLETED.value
    assert task.completed_at is not None
    assert task.last_error is None
    assert task.payload["execution_result"]["answer"] == "ok"


@pytest.mark.asyncio
async def test_task_executor_marks_task_retry_on_failure(session: AsyncSession) -> None:
    """失败但未超过重试次数时应进入 retry。"""

    task = Task(
        title="agentic rag",
        task_type=AGENTIC_RAG_TASK_TYPE,
        payload={"query": "hello"},
        status=TaskStatus.RUNNING.value,
        retry_count=0,
        max_retries=2,
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)

    queue = InMemoryQueue([QueuedTask(task_id=task.id, payload={})])
    executor = TaskExecutor(queue=queue, handlers=[FailingHandler()], dequeue_timeout_seconds=0)

    executed = await executor.run_once(session)
    await session.refresh(task)

    assert executed is True
    assert task.status == TaskStatus.RETRY.value
    assert task.retry_count == 1
    assert task.last_error == "handler failed"
    assert task.payload["execution_error"] == "handler failed"


@pytest.mark.asyncio
async def test_task_executor_marks_task_failed_when_retries_exhausted(session: AsyncSession) -> None:
    """超过最大重试次数时应进入 failed。"""

    task = Task(
        title="agentic rag",
        task_type=AGENTIC_RAG_TASK_TYPE,
        payload={"query": "hello"},
        status=TaskStatus.RUNNING.value,
        retry_count=1,
        max_retries=1,
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)

    queue = InMemoryQueue([QueuedTask(task_id=task.id, payload={})])
    executor = TaskExecutor(queue=queue, handlers=[FailingHandler()], dequeue_timeout_seconds=0)

    executed = await executor.run_once(session)
    await session.refresh(task)

    assert executed is True
    assert task.status == TaskStatus.FAILED.value
    assert task.retry_count == 1
    assert task.last_error == "handler failed"
