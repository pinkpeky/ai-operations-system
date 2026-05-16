from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.task_orchestration.service import TaskOrchestratorService


@pytest.mark.asyncio
async def test_task_start_assigns_and_completion_clears_lease(session) -> None:  # type: ignore[no-untyped-def]
    service = TaskOrchestratorService(session, lease_owner="lease-test", lease_seconds=60)
    task = await service.enqueue_task(
        workspace_id="workspace-lease",
        task_type="conversation",
        source_type="conversation",
        source_id="00000000-0000-4000-8000-000000000001",
        input_payload={"thread_id": "00000000-0000-4000-8000-000000000001"},
    )

    await service.start_task(task=task)
    assert task.lease_owner == "lease-test"
    assert task.lease_token
    assert task.heartbeat_at is not None
    assert task.lease_expires_at is not None
    lease_expires_at = task.lease_expires_at
    if lease_expires_at.tzinfo is None:
        lease_expires_at = lease_expires_at.replace(tzinfo=UTC)
    assert lease_expires_at > datetime.now(UTC)

    await service.complete_task(task=task, output_payload={"summary": "done"})
    assert task.status == "completed"
    assert task.lease_owner is None
    assert task.lease_token is None
    assert task.lease_expires_at is None
