"""Agent Memory Repository。"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import delete, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import AgentMemoryType
from app.models.memory import AgentMemory


class AgentMemoryRepository:
    """Agent Memory 数据访问层。"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_memory(
        self,
        *,
        workspace_id: str,
        agent_name: str,
        memory_type: str,
        content: str,
        metadata: dict[str, Any] | None = None,
        importance_score: float = 0.5,
    ) -> AgentMemory:
        """保存一条 Agent Memory。"""

        if memory_type not in {item.value for item in AgentMemoryType}:
            raise ValueError("memory_type must be short_term, long_term, task_memory, or retrieval_memory")
        memory = AgentMemory(
            workspace_id=workspace_id,
            agent_name=agent_name,
            memory_type=memory_type,
            content=content,
            memory_metadata=metadata or {},
            importance_score=importance_score,
        )
        self.session.add(memory)
        await self.session.flush()
        return memory

    async def get_memory(self, *, memory_id: UUID, workspace_id: str) -> AgentMemory | None:
        """按 workspace 查询单条 memory。"""

        statement = select(AgentMemory).where(AgentMemory.id == memory_id, AgentMemory.workspace_id == workspace_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def search_memories(
        self,
        *,
        workspace_id: str,
        query: str | None = None,
        agent_name: str | None = None,
        memory_type: str | None = None,
        limit: int = 20,
    ) -> list[AgentMemory]:
        """使用 PostgreSQL/SQLite 文本匹配检索 memory。"""

        statement = select(AgentMemory).where(AgentMemory.workspace_id == workspace_id)
        if agent_name is not None:
            statement = statement.where(AgentMemory.agent_name == agent_name)
        if memory_type is not None:
            statement = statement.where(AgentMemory.memory_type == memory_type)
        tokens = self._tokenize(query or "")
        if tokens:
            statement = statement.where(or_(*[AgentMemory.content.ilike(f"%{token}%") for token in tokens]))
        statement = statement.order_by(AgentMemory.importance_score.desc(), AgentMemory.created_at.desc()).limit(limit)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def delete_memory(self, *, memory_id: UUID, workspace_id: str) -> bool:
        """物理删除一条 memory。"""

        statement = delete(AgentMemory).where(AgentMemory.id == memory_id, AgentMemory.workspace_id == workspace_id)
        result = await self.session.execute(statement)
        return bool(result.rowcount)

    def _tokenize(self, text: str) -> list[str]:
        """简单分词：英文按空格，中文按字符，保证稳定测试。"""

        lowered = text.lower().strip()
        if not lowered:
            return []
        latin_tokens = [part for part in lowered.replace(",", " ").replace(".", " ").split() if part]
        cjk_tokens = [char for char in lowered if "\u4e00" <= char <= "\u9fff"]
        seen: set[str] = set()
        tokens: list[str] = []
        for token in [*latin_tokens, *cjk_tokens]:
            if token not in seen:
                seen.add(token)
                tokens.append(token)
        return tokens
