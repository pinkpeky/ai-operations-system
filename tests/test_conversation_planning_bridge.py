"""Phase 38 planning bridge tests."""

from __future__ import annotations

from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.conversation.services import ConversationService


@pytest.mark.asyncio
async def test_conversation_planning_bridge_creates_plan(session, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    plan_id = uuid4()

    async def fake_create_plan(self, **kwargs):  # type: ignore[no-untyped-def]
        return SimpleNamespace(id=plan_id, status="pending")

    async def fake_list_steps(self, **kwargs):  # type: ignore[no-untyped-def]
        return [
            SimpleNamespace(id=uuid4(), step_order=1, agent_name="rag_agent", tool_name=None, title="Collect context", status="pending"),
            SimpleNamespace(id=uuid4(), step_order=2, agent_name="content_agent", tool_name=None, title="Draft content", status="pending"),
        ]

    monkeypatch.setattr("app.conversation.services.conversation_service.PlanningService.create_plan", fake_create_plan)
    monkeypatch.setattr("app.conversation.services.conversation_service.PlanningService.list_steps", fake_list_steps)
    service = ConversationService(session)
    thread = await service.create_thread(workspace_id="workspace-plan", user_id="user-plan", title="Plan")

    result = await service.run_conversation_turn(
        workspace_id="workspace-plan",
        user_id="user-plan",
        thread_id=thread.id,
        run_input={"input": {"message": "请帮我拆解一个浏览器搜索热门视频并生成文案的计划。"}},
    )

    assert result.success is True
    assert result.route_name == "planning"
    assert result.result_metadata["plan_id"] == str(plan_id)
    assert len(result.result_metadata["steps"]) == 2
