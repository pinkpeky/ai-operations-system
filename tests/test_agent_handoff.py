"""Agent handoff 测试。"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.multi_agent.services import MultiAgentService


@pytest.mark.asyncio
async def test_agent_handoff_records_message_and_payload(session: AsyncSession) -> None:
    """handoff 应同时写入 agent_handoffs 和消息流。"""

    service = MultiAgentService(session)
    run = await service.create_run(
        workspace_id="workspace-handoff",
        user_id=None,
        session_id=None,
        root_agent="content_planner",
        run_input={"topic": "handoff"},
    )
    handoff = await service.handoff(
        run=run,
        from_agent="content_planner",
        to_agent="rag_agent",
        reason="Need RAG grounding",
        payload={"query": "handoff query"},
    )
    await session.commit()

    handoffs = await service.list_handoffs(run_id=run.id, workspace_id="workspace-handoff")
    messages = await service.list_messages(run_id=run.id, workspace_id="workspace-handoff")

    assert handoffs[0].id == handoff.id
    assert handoffs[0].status == "completed"
    assert handoffs[0].payload == {"query": "handoff query"}
    assert any(message.role == "handoff" and message.to_agent == "rag_agent" for message in messages)

