"""Phase 43 task diagnostics tests."""

from __future__ import annotations

import pytest

from app.task_orchestration.recovery_service import TaskRecoveryService
from app.task_orchestration.service import TaskOrchestratorService


@pytest.mark.asyncio
async def test_failed_task_diagnostics_classify_non_recoverable_error(session) -> None:  # type: ignore[no-untyped-def]
    service = TaskOrchestratorService(session)
    task = await service.enqueue_task(
        workspace_id="workspace-diagnostics",
        task_type="conversation",
        source_type="conversation",
        source_id="33333333-3333-4333-8333-333333333333",
        input_payload={"thread_id": "33333333-3333-4333-8333-333333333333"},
    )

    await service.fail_task(task=task, error="validation error: missing thread")
    diagnostics = await TaskRecoveryService(session).diagnostics_for_task(task=task)

    assert task.status == "failed"
    assert diagnostics["failure_category"] == "validation"
    assert diagnostics["recoverable"] is False
    assert diagnostics["suggested_action"] == "Fix the task input, source object, or workspace reference before retrying."
    assert diagnostics["last_event_summary"] == "validation error: missing thread"
