"""固定 Multi-Agent Chain 测试。"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.memory.services import MemoryService
from app.multi_agent.services import MultiAgentService


@pytest.mark.asyncio
async def test_content_planning_chain_completes_with_messages_and_handoffs(session: AsyncSession) -> None:
    """固定链路应完成 run，并记录 messages / handoffs / memory trace 兼容信息。"""

    memory_service = MemoryService(session)
    conversation = await memory_service.create_session(
        workspace_id="workspace-chain",
        user_id="user-chain",
        title="Chain Session",
    )
    await memory_service.append_message(
        workspace_id="workspace-chain",
        session_id=conversation.id,
        role="user",
        content="我关注 multi-agent memory integration。",
    )
    await memory_service.save_memory(
        workspace_id="workspace-chain",
        agent_name="ContentAgent",
        memory_type="long_term",
        content="用户关注 multi-agent content chain。",
    )

    service = MultiAgentService(session)
    run = await service.create_run(
        workspace_id="workspace-chain",
        user_id="user-chain",
        session_id=conversation.id,
        root_agent="content_planner",
        run_input={
            "topic": "AI 自动化运营",
            "platform": "tiktok",
            "style": "专业简洁",
            "query": "ping",
            "collection_name": "phase15_chain_test",
        },
    )

    completed_run, agents_involved = await service.execute_agent_chain(run=run)
    messages = await service.list_messages(run_id=run.id, workspace_id="workspace-chain")
    handoffs = await service.list_handoffs(run_id=run.id, workspace_id="workspace-chain")

    assert completed_run.status == "completed"
    assert agents_involved == ["content_planner", "rag_agent", "content_agent", "review_agent"]
    assert completed_run.run_output is not None
    assert completed_run.run_output["review"]["review_status"] == "approved"
    assert len(handoffs) == 3
    assert any(message.from_agent == "content_agent" for message in messages)
    assert completed_run.duration_ms is not None

