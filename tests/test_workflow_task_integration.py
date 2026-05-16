"""Workflow integration with task orchestration."""

from __future__ import annotations

from uuid import UUID

import pytest

from app.conversation.services import ConversationService
from app.task_orchestration.service import TaskOrchestratorService
from app.workflow.services import WorkflowStateService


@pytest.mark.asyncio
async def test_task_enqueue_creates_linked_workflow(session) -> None:  # type: ignore[no-untyped-def]
    conversation = ConversationService(session)
    thread = await conversation.create_thread(workspace_id="workspace-task-workflow", user_id="user", title="Task workflow")
    task = await TaskOrchestratorService(session).enqueue_task(
        workspace_id="workspace-task-workflow",
        task_type="conversation",
        source_type="conversation",
        source_id=str(thread.id),
        input_payload={"thread_id": str(thread.id), "input": {"message": "generate content"}},
        created_by="user",
    )

    workflow_id = task.task_metadata.get("workflow_run_id")
    assert workflow_id
    workflow = await WorkflowStateService(session).get_workflow_run(
        workspace_id="workspace-task-workflow",
        workflow_run_id=UUID(str(workflow_id)),
    )
    assert workflow is not None
    assert workflow.task_run_id == task.id
