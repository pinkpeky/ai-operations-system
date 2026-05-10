"""内容生成任务测试模块。

验证 content_generation handler 和任务 API 能创建可被 TaskExecutor 消费的任务。
"""

from collections import deque
from typing import Any
from uuid import UUID

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes.tasks import router as tasks_router
from app.db.postgres import get_session
from app.models.enums import TaskStatus
from app.services.queue import QueuedTask
from app.workers.handlers.content_generation_handler import CONTENT_GENERATION_TASK_TYPE, ContentGenerationHandler
from app.workers.task_executor import TaskExecutor


class FakeContentAgent:
    """内容生成 Agent 替身。"""

    async def run(self, agent_input: dict[str, Any]) -> dict[str, Any]:
        """返回固定内容生成结果。"""

        return {
            "title": f"{agent_input['topic']} title",
            "description": "fake description",
            "tags": [agent_input["platform"]],
            "cta": "fake cta",
            "raw_response": "fake raw",
        }


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


@pytest.mark.asyncio
async def test_content_generation_handler_returns_execution_result() -> None:
    """ContentGenerationHandler 应返回标准任务执行结果。"""

    handler = ContentGenerationHandler(agent_factory=FakeContentAgent)  # type: ignore[arg-type]

    result = await handler.handle(
        {
            "topic": "AI 自动化运营",
            "platform": "tiktok",
            "style": "专业简洁",
        }
    )

    assert handler.task_type == CONTENT_GENERATION_TASK_TYPE
    assert result.success is True
    assert result.data["title"] == "AI 自动化运营 title"
    assert result.data["raw_response"] == "fake raw"


@pytest.mark.asyncio
async def test_content_generation_task_executor_flow(session: AsyncSession) -> None:
    """TaskExecutor 应能消费 content_generation 任务并保存 execution_result。"""

    from app.models.task import Task

    task = Task(
        title="content generation",
        task_type=CONTENT_GENERATION_TASK_TYPE,
        payload={
            "topic": "AI 自动化运营",
            "platform": "tiktok",
            "style": "专业简洁",
        },
        status=TaskStatus.RUNNING.value,
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)

    queue = InMemoryQueue([QueuedTask(task_id=task.id, payload={})])
    executor = TaskExecutor(
        queue=queue,
        handlers=[ContentGenerationHandler(agent_factory=FakeContentAgent)],  # type: ignore[arg-type]
        dequeue_timeout_seconds=0,
    )

    executed = await executor.run_once(session)
    await session.refresh(task)

    assert executed is True
    assert task.status == TaskStatus.COMPLETED.value
    assert task.payload["execution_result"]["title"] == "AI 自动化运营 title"


@pytest.mark.asyncio
async def test_create_content_generation_task_api(session: AsyncSession) -> None:
    """任务 API 应能创建 content_generation 类型任务。"""

    app = FastAPI()

    async def override_get_session():  # type: ignore[no-untyped-def]
        yield session

    app.dependency_overrides[get_session] = override_get_session
    app.include_router(tasks_router, prefix="/api/v1")
    client = TestClient(app)

    response = client.post(
        "/api/v1/tasks/content-generation",
        json={
            "topic": "AI 自动化运营",
            "platform": "tiktok",
            "style": "专业简洁",
            "title": "Content task",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["task_type"] == CONTENT_GENERATION_TASK_TYPE
    assert body["payload"]["topic"] == "AI 自动化运营"
    assert body["status"] == TaskStatus.PENDING.value
