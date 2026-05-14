"""Conversation runtime run tests."""

import pytest

from app.conversation.services import ConversationService


@pytest.mark.asyncio
async def test_conversation_run_routes_content_agent(session, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """包含“生成/内容”的消息应走 ContentAgent，并记录事件时间线。"""

    async def fake_run(self, agent_input):  # type: ignore[no-untyped-def]
        return {
            "title": "测试标题",
            "description": f"测试内容：{agent_input['topic']}",
            "tags": ["phase33"],
            "cta": "继续执行",
            "raw_response": "mock",
        }

    monkeypatch.setattr("app.conversation.services.conversation_service.ContentAgent.run", fake_run)

    service = ConversationService(session)
    thread = await service.create_thread(
        workspace_id="workspace-run",
        user_id="user-run",
        title="Run Thread",
    )

    result = await service.run_conversation_turn(
        workspace_id="workspace-run",
        user_id="user-run",
        thread_id=thread.id,
        run_input={"input": {"message": "请生成一条 AI 自动化运营内容。"}},
    )

    assert result.route == "content"
    assert result.route_name == "content"
    assert result.selected_tool is None
    assert result.success is True
    assert "测试标题" in result.assistant_message.content
    event_types = {event.event_type for event in result.events}
    assert {
        "message_received",
        "route_selected",
        "agent_execution_started",
        "agent_execution_completed",
        "assistant_response",
    } <= event_types
