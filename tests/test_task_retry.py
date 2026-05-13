"""任务重试控制测试。"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import TaskStatus
from app.models.task import Task
from app.repositories.task_repository import TaskRepository


@pytest.mark.asyncio
async def test_retry_task_resets_failed_task_to_retry(session: AsyncSession) -> None:
    """手动重试 failed 任务时应重置执行字段并进入 retry。"""

    task = Task(
        title="retry me",
        task_type="custom",
        payload={"execution_error": "boom"},
        status=TaskStatus.FAILED.value,
        retry_count=3,
        max_retries=3,
        workspace_id="workspace-retry",
        last_error="boom",
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)

    repository = TaskRepository(session)
    retried = await repository.retry_task(task_id=task.id, workspace_id="workspace-retry")

    assert retried is not None
    assert retried.status == TaskStatus.RETRY.value
    assert retried.retry_count == 0
    assert retried.started_at is None
    assert retried.completed_at is None
    assert retried.duration_ms is None
    assert retried.last_error is None
    assert "execution_error" not in retried.payload
