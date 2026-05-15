"""Workflow replay metadata tests."""

from __future__ import annotations

import pytest

from app.workflow.services import WorkflowStateService


@pytest.mark.asyncio
async def test_workflow_replay_is_metadata_only(session) -> None:  # type: ignore[no-untyped-def]
    service = WorkflowStateService(session)
    workflow = await service.create_workflow_run(workspace_id="workspace-replay", source_type="test")
    checkpoint = await service.create_checkpoint(
        workspace_id="workspace-replay",
        workflow_run_id=workflow.id,
        checkpoint_name="before-branch",
        state_payload={"node_key": "router"},
    )

    replay = await service.create_replay(
        workspace_id="workspace-replay",
        workflow_run_id=workflow.id,
        replay_source_checkpoint_id=checkpoint.id,
        replay_reason="debug conditional routing",
    )

    assert replay.replay_status == "created"
    assert replay.replay_reason == "debug conditional routing"
    assert replay.replay_metadata["replay_lineage"]["source_checkpoint_id"] == str(checkpoint.id)
