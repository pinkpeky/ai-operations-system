"""Agent Memory retrieval 测试模块。

当前 memory retrieval 使用数据库文本检索，不引入向量 memory 或 graph memory。
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.memory.services import MemoryService


@pytest.mark.asyncio
async def test_memory_retrieval_is_workspace_and_agent_scoped(session: AsyncSession) -> None:
    """Memory 搜索必须同时支持 workspace 隔离、agent 过滤和文本查询。"""

    service = MemoryService(session)
    memory = await service.save_memory(
        workspace_id="workspace-memory-search-a",
        agent_name="AgenticRAGOrchestrator",
        memory_type="long_term",
        content="用户关注 memory trace 与 hybrid search debug。",
        metadata={"topic": "trace"},
        importance_score=0.9,
    )
    await service.save_memory(
        workspace_id="workspace-memory-search-a",
        agent_name="ContentAgent",
        memory_type="short_term",
        content="ContentAgent 只关注内容生成。",
        importance_score=0.7,
    )
    await service.save_memory(
        workspace_id="workspace-memory-search-b",
        agent_name="AgenticRAGOrchestrator",
        memory_type="long_term",
        content="另一个 workspace 的 memory trace 不应被查到。",
        importance_score=1.0,
    )

    results = await service.search_memory(
        workspace_id="workspace-memory-search-a",
        query="memory trace",
        agent_name="AgenticRAGOrchestrator",
        limit=10,
    )
    other_workspace = await service.search_memory(
        workspace_id="workspace-memory-search-b",
        query="hybrid",
        agent_name="AgenticRAGOrchestrator",
        limit=10,
    )
    deleted = await service.delete_memory(workspace_id="workspace-memory-search-a", memory_id=memory.id)
    after_delete = await service.search_memory(
        workspace_id="workspace-memory-search-a",
        query="memory trace",
        agent_name="AgenticRAGOrchestrator",
        limit=10,
    )

    assert [item.id for item in results] == [memory.id]
    assert other_workspace == []
    assert deleted is True
    assert after_delete == []


@pytest.mark.asyncio
async def test_memory_retrieval_rejects_invalid_memory_type(session: AsyncSession) -> None:
    """memory_type 必须限定在 short_term/long_term/task_memory/retrieval_memory。"""

    service = MemoryService(session)

    with pytest.raises(ValueError, match="memory_type must be"):
        await service.save_memory(
            workspace_id="workspace-memory-type",
            agent_name="DemoAgent",
            memory_type="unknown",
            content="bad memory",
        )

