"""任务取消测试。"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import TaskStatus
from app.models.task import Task
from app.repositories.task_repository import TaskRepository


@pytest.mark.asyncio
async def test_cancel_task_marks_cancelled_with_workspace_filter(session: AsyncSession) -> None:
    """取消任务时必须按 workspace 过滤，并写入 cancelled 状态。"""

    task = Task(
        title="cancel me",
        task_type="custom",
        payload={},
        status=TaskStatus.PENDING.value,
        workspace_id="workspace-cancel",
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)

    repository = TaskRepository(session)
    missing = await repository.cancel_task(task_id=task.id, workspace_id="other-workspace")
    cancelled = await repository.cancel_task(task_id=task.id, workspace_id="workspace-cancel")

    assert missing is None
    assert cancelled is not None
    assert cancelled.status == TaskStatus.CANCELLED.value
    assert cancelled.completed_at is not None
    assert cancelled.last_error == "Task cancelled by user"
