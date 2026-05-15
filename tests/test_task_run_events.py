"""Phase 42 task run event timeline tests."""

from __future__ import annotations

import pytest

from app.task_orchestration.service import TaskOrchestratorService


@pytest.mark.asyncio
async def test_task_run_events_record_queue_start_cancel(session) -> None:  # type: ignore[no-untyped-def]
    service = TaskOrchestratorService(session)
    task = await service.enqueue_task(
        workspace_id="workspace-task-events",
        task_type="conversation",
        source_type="conversation",
        source_id="thread-events",
        input_payload={"thread_id": "11111111-1111-1111-1111-111111111111", "input": {"message": "hello"}},
    )
    await service.start_task(task=task)
    await service.cancel_task(workspace_id="workspace-task-events", task_run_id=task.id, reason="test cancel")

    events = await service.list_events(workspace_id="workspace-task-events", task_run_id=task.id)
    event_types = [event.event_type for event in events]
    assert "task_created" in event_types
    assert "task_queued" in event_types
    assert "task_started" in event_types
    assert "task_cancelled" in event_types
