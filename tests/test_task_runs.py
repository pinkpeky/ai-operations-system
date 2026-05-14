"""Phase 42 task run model/service tests."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from app.models.enums import TaskRunStatus
from app.task_orchestration.service import TaskOrchestratorService


@pytest.mark.asyncio
async def test_task_run_enqueue_schedule_and_workspace_filter(session) -> None:  # type: ignore[no-untyped-def]
    service = TaskOrchestratorService(session)
    queued = await service.enqueue_task(
        workspace_id="workspace-task-runs",
        task_type="conversation",
        source_type="conversation",
        source_id="thread-a",
        input_payload={"thread_id": "11111111-1111-1111-1111-111111111111", "input": {"message": "hello"}},
    )
    scheduled = await service.enqueue_task(
        workspace_id="workspace-task-runs",
        task_type="conversation",
        source_type="conversation",
        source_id="thread-b",
        input_payload={"thread_id": "22222222-2222-2222-2222-222222222222", "input": {"message": "later"}},
        scheduled_at=datetime.now(UTC) + timedelta(hours=1),
    )

    assert queued.status == TaskRunStatus.QUEUED.value
    assert scheduled.status == TaskRunStatus.PENDING.value
    listed = await service.list_tasks(workspace_id="workspace-task-runs")
    other = await service.list_tasks(workspace_id="workspace-other")
    assert {item.id for item in listed} == {queued.id, scheduled.id}
    assert other == []
