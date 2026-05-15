"""Workflow diagnostics service tests."""

from __future__ import annotations

import pytest

from app.workflow.observability import WorkflowDiagnosticsService
from app.workflow.services import WorkflowStateService


@pytest.mark.asyncio
async def test_failed_workflow_generates_diagnostics(session) -> None:  # type: ignore[no-untyped-def]
    state = WorkflowStateService(session)
    workflow = await state.create_workflow_run(workspace_id="diag-ws", source_type="test")
    step = await state.start_step(
        workspace_id="diag-ws",
        workflow_run_id=workflow.id,
        step_index=0,
        step_name="Broken node",
        step_type="tool_call",
        node_key="broken",
    )
    await state.fail_step(workspace_id="diag-ws", workflow_step_id=step.id, error="temporary runtime error")
    await state.fail_workflow(workspace_id="diag-ws", workflow_run_id=workflow.id, error="temporary runtime error")

    diagnostics = await WorkflowDiagnosticsService(session).analyze_failed_workflow(
        workspace_id="diag-ws",
        workflow_run_id=workflow.id,
    )

    assert any(item.diagnostic_type == "workflow_failure" for item in diagnostics)
    assert any(item.diagnostic_type == "checkpoint_gap" for item in diagnostics)
