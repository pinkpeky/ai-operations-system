"""Phase 42 task-to-artifact linkage tests."""

from __future__ import annotations

import pytest
from uuid import UUID

from app.services.output_artifact_service import OutputArtifactService
from app.task_orchestration.service import TaskOrchestratorService


@pytest.mark.asyncio
async def test_task_completion_links_existing_thread_artifacts(session) -> None:  # type: ignore[no-untyped-def]
    service = TaskOrchestratorService(session)
    task = await service.enqueue_task(
        workspace_id="workspace-task-artifact",
        task_type="conversation",
        source_type="conversation",
        source_id="11111111-1111-1111-1111-111111111111",
        input_payload={"thread_id": "11111111-1111-1111-1111-111111111111", "input": {"message": "done"}},
    )
    artifact = await OutputArtifactService(session).create_artifact(
        workspace_id="workspace-task-artifact",
        thread_id=UUID(str(task.source_id)),
        source_type="conversation",
        artifact_type="content_draft",
        title="Draft",
        summary="Task linked",
        content="hello",
    )

    completed = await service.complete_task(
        task=task,
        output_payload={"thread_id": task.source_id, "summary": "done"},
    )

    refreshed = await OutputArtifactService(session).get_artifact(
        workspace_id="workspace-task-artifact",
        artifact_id=artifact.id,
    )
    assert completed.status == "completed"
    assert refreshed.task_run_id == task.id
