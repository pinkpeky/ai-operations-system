from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.models.task_run import TaskSchedulerState
from app.task_orchestration.background_executor import BackgroundTaskExecutor
from app.task_orchestration.service import TaskOrchestratorService


@pytest.mark.asyncio
async def test_background_executor_runs_recovery_before_polling(session) -> None:  # type: ignore[no-untyped-def]
    factory = async_sessionmaker(session.bind, expire_on_commit=False)
    orchestrator = TaskOrchestratorService(session)
    task = await orchestrator.enqueue_task(
        workspace_id="workspace-loop",
        task_type="conversation",
        source_type="conversation",
        source_id="00000000-0000-4000-8000-000000000005",
        input_payload={"thread_id": "00000000-0000-4000-8000-000000000005"},
        scheduled_at=datetime.now(UTC) - timedelta(seconds=1),
    )
    await session.close()

    executor = BackgroundTaskExecutor(factory, scheduler_name="loop-test", recovery_interval_seconds=0.0)
    await executor.run_once()

    async with factory() as verify:
        refreshed = await verify.get(type(task), task.id)
        states = (await verify.execute(select(TaskSchedulerState).where(TaskSchedulerState.workspace_id == "workspace-loop"))).scalars().all()

    assert refreshed is not None
    assert refreshed.status in {"retrying", "failed", "queued"}
    assert states
    assert states[0].last_scan_at is not None
