"""Phase 42 background executor tests."""

from __future__ import annotations

import pytest

from app.conversation.services import ConversationService
from app.models.enums import TaskRunStatus
from app.task_orchestration.background_executor import BackgroundTaskExecutor
from app.task_orchestration.service import TaskOrchestratorService


@pytest.mark.asyncio
async def test_background_task_executor_runs_one_queued_task(session, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    async def fake_run(self, agent_input):  # type: ignore[no-untyped-def]
        return {
            "title": "Background title",
            "description": agent_input["topic"],
            "tags": ["background"],
            "cta": "Continue.",
            "raw_response": "mock",
        }

    monkeypatch.setattr("app.conversation.services.conversation_service.ContentAgent.run", fake_run)
    conversation = ConversationService(session)
    thread = await conversation.create_thread(workspace_id="workspace-bg", user_id="user", title="BG")
    await TaskOrchestratorService(session).enqueue_task(
        workspace_id="workspace-bg",
        task_type="conversation",
        source_type="conversation",
        source_id=str(thread.id),
        input_payload={"thread_id": str(thread.id), "run_input": {"input": {"message": "请生成内容"}}},
        created_by="user",
    )

    class StaticSessionFactory:
        def __call__(self):  # type: ignore[no-untyped-def]
            return self

        async def __aenter__(self):  # type: ignore[no-untyped-def]
            return session

        async def __aexit__(self, exc_type, exc, tb):  # type: ignore[no-untyped-def]
            return False

    executor = BackgroundTaskExecutor(session_factory=StaticSessionFactory(), batch_size=5)  # type: ignore[arg-type]
    assert await executor.run_once() == 1

    tasks = await TaskOrchestratorService(session).list_tasks(workspace_id="workspace-bg")
    assert tasks[0].status == TaskRunStatus.COMPLETED.value
