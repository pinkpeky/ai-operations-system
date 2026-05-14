"""Phase 38 content bridge tests."""

from __future__ import annotations

import pytest

from app.conversation.services import ConversationService


@pytest.mark.asyncio
async def test_conversation_content_bridge_runs_content_agent(session, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    async def fake_run(self, agent_input):  # type: ignore[no-untyped-def]
        return {
            "title": "AI 自动化运营标题",
            "description": f"围绕 {agent_input['topic']} 生成短视频文案",
            "tags": ["ai", "ops"],
            "cta": "关注获取下一步",
            "raw_response": "mock",
        }

    monkeypatch.setattr("app.conversation.services.conversation_service.ContentAgent.run", fake_run)
    service = ConversationService(session)
    thread = await service.create_thread(workspace_id="workspace-content", user_id="user-content", title="Content")

    result = await service.run_conversation_turn(
        workspace_id="workspace-content",
        user_id="user-content",
        thread_id=thread.id,
        run_input={"input": {"message": "请帮我生成一条关于 AI 自动化运营的短视频文案。"}},
    )

    assert result.success is True
    assert result.route_name == "content"
    assert "AI 自动化运营标题" in result.summary
    event_types = {event.event_type for event in result.events}
    assert {"agent_execution_started", "agent_execution_completed"} <= event_types
