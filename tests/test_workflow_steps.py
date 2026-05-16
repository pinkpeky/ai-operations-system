"""Workflow step tests."""

from __future__ import annotations

import pytest

from app.workflow.services import WorkflowStateService


@pytest.mark.asyncio
async def test_workflow_step_failure_records_error(session) -> None:  # type: ignore[no-untyped-def]
    service = WorkflowStateService(session)
    workflow = await service.create_workflow_run(workspace_id="workspace-step", source_type="playbook")
    step = await service.start_step(
        workspace_id="workspace-step",
        workflow_run_id=workflow.id,
        step_index=2,
        step_name="Browser action",
        step_type="tool",
    )

    failed = await service.fail_step(workspace_id="workspace-step", workflow_step_id=step.id, error="network timeout")

    assert failed.status == "failed"
    assert failed.error == "network timeout"
    assert failed.duration_ms is not None
