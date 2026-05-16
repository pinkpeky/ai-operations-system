"""Workflow integration with conversation playbooks."""

from __future__ import annotations

import pytest

from app.conversation.services import ConversationPlaybookService, ConversationService
from app.workflow.services import WorkflowStateService


@pytest.mark.asyncio
async def test_playbook_run_creates_workflow_steps_checkpoint_and_memory(session, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    async def fake_run(self, agent_input):  # type: ignore[no-untyped-def]
        return {
            "title": "Workflow title",
            "description": agent_input["topic"],
            "tags": ["workflow"],
            "cta": "Review.",
            "raw_response": "mock",
        }

    monkeypatch.setattr("app.conversation.services.conversation_service.ContentAgent.run", fake_run)
    conversation = ConversationService(session)
    thread = await conversation.create_thread(workspace_id="workspace-playbook-workflow", user_id="user", title="Workflow")
    result = await ConversationPlaybookService(session).run_playbook_by_name(
        workspace_id="workspace-playbook-workflow",
        user_id="user",
        thread=thread,
        playbook_name="content_generation",
        input_payload={"topic": "AI ops"},
        mode="auto_safe",
        message_id=None,
        source_message="Generate content",
    )

    workflow_id = result.workflow_run_id
    assert workflow_id is not None
    service = WorkflowStateService(session)
    workflow = await service.require_workflow_run(workspace_id="workspace-playbook-workflow", workflow_run_id=workflow_id)
    assert workflow.status == "completed"
    assert await service.list_steps(workspace_id="workspace-playbook-workflow", workflow_run_id=workflow_id)
    assert await service.list_checkpoints(workspace_id="workspace-playbook-workflow", workflow_run_id=workflow_id)
    assert await service.list_memory_snapshots(workspace_id="workspace-playbook-workflow", workflow_run_id=workflow_id)
