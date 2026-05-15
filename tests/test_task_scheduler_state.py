from __future__ import annotations

import pytest

from app.task_orchestration.recovery_service import TaskRecoveryService


@pytest.mark.asyncio
async def test_task_scheduler_state_created_and_heartbeat(session) -> None:  # type: ignore[no-untyped-def]
    service = TaskRecoveryService(session, scheduler_name="test-scheduler")

    state = await service.heartbeat_scheduler(workspace_id="workspace-scheduler")
    await session.commit()
    await session.refresh(state)

    assert state.workspace_id == "workspace-scheduler"
    assert state.scheduler_name == "test-scheduler"
    assert state.status == "active"
    assert state.heartbeat_at is not None
    assert state.active_task_count == 0
