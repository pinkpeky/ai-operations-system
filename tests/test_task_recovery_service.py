from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from app.models.enums import TaskRunStatus
from app.task_orchestration.recovery_service import TaskRecoveryService
from app.task_orchestration.service import TaskOrchestratorService


@pytest.mark.asyncio
async def test_recovery_scan_queues_due_scheduled_and_retrying_tasks(session) -> None:  # type: ignore[no-untyped-def]
    orchestrator = TaskOrchestratorService(session)
    due = datetime.now(UTC) - timedelta(seconds=1)
    scheduled = await orchestrator.enqueue_task(
        workspace_id="workspace-recovery",
        task_type="conversation",
        source_type="conversation",
        source_id="00000000-0000-4000-8000-000000000002",
        input_payload={"thread_id": "00000000-0000-4000-8000-000000000002"},
        scheduled_at=datetime.now(UTC) + timedelta(minutes=5),
    )
    scheduled.status = TaskRunStatus.PENDING.value
    scheduled.scheduled_at = due
    retrying = await orchestrator.enqueue_task(
        workspace_id="workspace-recovery",
        task_type="conversation",
        source_type="conversation",
        source_id="00000000-0000-4000-8000-000000000003",
        input_payload={"thread_id": "00000000-0000-4000-8000-000000000003"},
    )
    retrying.status = TaskRunStatus.RETRYING.value
    retrying.scheduled_at = due
    await session.commit()

    details = await TaskRecoveryService(session).scan_once(workspace_id="workspace-recovery")
    await session.refresh(scheduled)
    await session.refresh(retrying)

    assert details["scheduled_recovered"] == 1
    assert details["retrying_recovered"] == 1
    assert scheduled.status == "queued"
    assert retrying.status == "queued"


@pytest.mark.asyncio
async def test_recovery_scan_recovers_expired_running_lease(session) -> None:  # type: ignore[no-untyped-def]
    orchestrator = TaskOrchestratorService(session, lease_owner="old-executor", lease_seconds=1)
    task = await orchestrator.enqueue_task(
        workspace_id="workspace-expired-lease",
        task_type="conversation",
        source_type="conversation",
        source_id="00000000-0000-4000-8000-000000000004",
        input_payload={"thread_id": "00000000-0000-4000-8000-000000000004"},
    )
    await orchestrator.start_task(task=task)
    task.lease_expires_at = datetime.now(UTC) - timedelta(seconds=1)
    await session.commit()

    details = await TaskRecoveryService(session).scan_once(workspace_id="workspace-expired-lease")
    await session.refresh(task)

    assert details["expired_leases_recovered"] == 1
    assert task.status == "retrying"
    assert task.recovery_count == 1
    assert task.lease_owner is None
