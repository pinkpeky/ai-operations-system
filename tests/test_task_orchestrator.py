"""Phase 42 task orchestrator execution tests."""

from __future__ import annotations

import pytest
from uuid import UUID

from app.conversation.services import ConversationService
from app.conversation.services import ConversationApprovalService
from app.models.enums import TaskRunStatus
from app.task_orchestration.service import TaskOrchestratorService


@pytest.mark.asyncio
async def test_task_orchestrator_executes_content_conversation(session, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    async def fake_run(self, agent_input):  # type: ignore[no-untyped-def]
        return {
            "title": "Task content title",
            "description": agent_input["topic"],
            "tags": ["task"],
            "cta": "Review before publishing.",
            "raw_response": "mock",
        }

    monkeypatch.setattr("app.conversation.services.conversation_service.ContentAgent.run", fake_run)
    conversation = ConversationService(session)
    thread = await conversation.create_thread(workspace_id="workspace-orchestrator", user_id="user", title="Task")
    task = await TaskOrchestratorService(session).enqueue_task(
        workspace_id="workspace-orchestrator",
        task_type="conversation",
        source_type="conversation",
        source_id=str(thread.id),
        input_payload={"thread_id": str(thread.id), "run_input": {"input": {"message": "请生成 AI 内容"}}},
        created_by="user",
    )

    executed = await TaskOrchestratorService(session).execute_task(task=task)

    assert executed.status == TaskRunStatus.COMPLETED.value
    assert executed.output_payload["route_name"] == "content"
    events = await TaskOrchestratorService(session).list_events(
        workspace_id="workspace-orchestrator",
        task_run_id=task.id,
    )
    assert {"task_started", "task_step_completed", "task_completed"} <= {event.event_type for event in events}


@pytest.mark.asyncio
async def test_task_orchestrator_resume_updates_nested_run_input(session, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    async def fake_run(self, agent_input):  # type: ignore[no-untyped-def]
        return {
            "title": "Approved content",
            "description": agent_input["topic"],
            "tags": ["approved"],
            "cta": "Continue.",
            "raw_response": "mock",
        }

    monkeypatch.setattr("app.conversation.services.conversation_service.ContentAgent.run", fake_run)
    conversation = ConversationService(session)
    thread = await conversation.create_thread(workspace_id="workspace-resume", user_id="user", title="Resume")
    task = await TaskOrchestratorService(session).enqueue_task(
        workspace_id="workspace-resume",
        task_type="conversation",
        source_type="conversation",
        source_id=str(thread.id),
        input_payload={
            "thread_id": str(thread.id),
            "run_input": {
                "input": {"message": "请生成一条内容"},
                "playbook_name": "content_generation",
                "mode": "review_first",
            },
        },
        created_by="user",
    )

    waiting = await TaskOrchestratorService(session).execute_task(task=task)
    assert waiting.status == TaskRunStatus.WAITING_APPROVAL.value
    approval_id = UUID(str(waiting.output_payload["approval_id"]))
    await ConversationApprovalService(session).approve(
        workspace_id="workspace-resume",
        approval_id=approval_id,
        approved_by="user",
    )
    resumed = await TaskOrchestratorService(session).resume_waiting_approval_task(
        workspace_id="workspace-resume",
        task_run_id=task.id,
    )

    assert resumed.input_payload["run_input"]["mode"] == "execute_after_approval"
    completed = await TaskOrchestratorService(session).execute_task(task=resumed)
    assert completed.status == TaskRunStatus.COMPLETED.value
