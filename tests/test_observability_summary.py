"""可观测性概览测试。"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import TaskStatus
from app.models.task import Task
from app.repositories.task_observability_repository import TaskObservabilityRepository


@pytest.mark.asyncio
async def test_observability_summary_counts_workspace_tasks(session: AsyncSession) -> None:
    """summary 应只统计当前 workspace，并计算平均耗时。"""

    session.add_all(
        [
            Task(title="pending", task_type="custom", payload={}, status=TaskStatus.PENDING.value, workspace_id="workspace-summary"),
            Task(title="running", task_type="custom", payload={}, status=TaskStatus.RUNNING.value, workspace_id="workspace-summary"),
            Task(title="failed", task_type="custom", payload={}, status=TaskStatus.FAILED.value, workspace_id="workspace-summary", duration_ms=100),
            Task(title="completed", task_type="custom", payload={}, status=TaskStatus.COMPLETED.value, workspace_id="workspace-summary", duration_ms=300),
            Task(title="cancelled", task_type="custom", payload={}, status=TaskStatus.CANCELLED.value, workspace_id="workspace-summary"),
            Task(title="timeout", task_type="custom", payload={}, status=TaskStatus.TIMEOUT.value, workspace_id="workspace-summary"),
            Task(title="other", task_type="custom", payload={}, status=TaskStatus.FAILED.value, workspace_id="other-workspace"),
        ]
    )
    await session.commit()

    summary = await TaskObservabilityRepository(session).get_summary(workspace_id="workspace-summary")

    assert summary["pending_count"] == 1
    assert summary["running_count"] == 1
    assert summary["failed_count"] == 1
    assert summary["completed_count"] == 1
    assert summary["cancelled_count"] == 1
    assert summary["timeout_count"] == 1
    assert summary["avg_duration_ms"] == 200.0
