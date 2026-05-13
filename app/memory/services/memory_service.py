"""Agent Memory 服务层。

MemoryService 负责编排会话、消息、Memory 检索和操作日志。
当前 Memory Retrieval 使用数据库文本检索，不做 vector memory / graph memory。
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.memory.repositories import AgentMemoryRepository, ConversationRepository
from app.models.memory import AgentMemory, ConversationMessage, ConversationSession

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class MemoryExecutionContext:
    """Agent 使用 Memory 时的执行上下文。"""

    service: "MemoryService"
    workspace_id: str
    user_id: str | None = None
    session_id: UUID | None = None
    agent_name: str | None = None
    recent_limit: int = 10
    memory_limit: int = 5


class MemoryService:
    """Memory 基础服务。"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.conversations = ConversationRepository(session)
        self.memories = AgentMemoryRepository(session)

    async def create_session(
        self,
        *,
        workspace_id: str,
        user_id: str | None,
        title: str,
        metadata: dict[str, Any] | None = None,
    ) -> ConversationSession:
        """创建会话。"""

        started_at = time.perf_counter()
        try:
            session = await self.conversations.create_session(
                workspace_id=workspace_id,
                user_id=user_id,
                title=title,
                metadata=metadata,
            )
            await self._log_operation(
                workspace_id=workspace_id,
                session_id=session.id,
                operation="create_session",
                success=True,
                latency_ms=self._latency_ms(started_at),
            )
            await self.session.commit()
            await self.session.refresh(session)
            logger.info("Memory session created", extra={"workspace_id": workspace_id, "session_id": str(session.id)})
            return session
        except Exception as exc:
            await self.session.rollback()
            await self._safe_log_failure(
                workspace_id=workspace_id,
                operation="create_session",
                error=str(exc),
                latency_ms=self._latency_ms(started_at),
            )
            raise

    async def append_message(
        self,
        *,
        workspace_id: str,
        session_id: UUID,
        role: str,
        content: str,
        token_count: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ConversationMessage:
        """追加消息。"""

        started_at = time.perf_counter()
        try:
            conversation = await self.conversations.get_session(session_id=session_id, workspace_id=workspace_id)
            if conversation is None:
                raise ValueError("Conversation session not found in workspace")
            message = await self.conversations.append_message(
                session_id=session_id,
                workspace_id=workspace_id,
                role=role,
                content=content,
                token_count=token_count if token_count is not None else self._estimate_token_count(content),
                metadata=metadata,
            )
            await self._log_operation(
                workspace_id=workspace_id,
                session_id=session_id,
                operation="append_message",
                success=True,
                latency_ms=self._latency_ms(started_at),
                metadata={"role": role},
            )
            await self.session.commit()
            await self.session.refresh(message)
            return message
        except Exception as exc:
            await self.session.rollback()
            await self._safe_log_failure(
                workspace_id=workspace_id,
                session_id=session_id,
                operation="append_message",
                error=str(exc),
                latency_ms=self._latency_ms(started_at),
                metadata={"role": role},
            )
            raise

    async def list_sessions(
        self,
        *,
        workspace_id: str,
        status: str | None = None,
        limit: int = 100,
    ) -> list[ConversationSession]:
        """列出当前 workspace 的会话并记录操作。"""

        started_at = time.perf_counter()
        try:
            sessions = await self.conversations.list_sessions(workspace_id=workspace_id, status=status, limit=limit)
            await self._log_operation(
                workspace_id=workspace_id,
                operation="list_sessions",
                success=True,
                latency_ms=self._latency_ms(started_at),
                metadata={"count": len(sessions), "status": status},
            )
            await self.session.commit()
            return sessions
        except Exception as exc:
            await self.session.rollback()
            await self._safe_log_failure(
                workspace_id=workspace_id,
                operation="list_sessions",
                error=str(exc),
                latency_ms=self._latency_ms(started_at),
            )
            raise

    async def get_session(self, *, workspace_id: str, session_id: UUID) -> ConversationSession | None:
        """查询会话并记录操作。"""

        started_at = time.perf_counter()
        try:
            conversation = await self.conversations.get_session(session_id=session_id, workspace_id=workspace_id)
            await self._log_operation(
                workspace_id=workspace_id,
                session_id=session_id,
                operation="get_session",
                success=True,
                latency_ms=self._latency_ms(started_at),
                metadata={"found": conversation is not None},
            )
            await self.session.commit()
            return conversation
        except Exception as exc:
            await self.session.rollback()
            await self._safe_log_failure(
                workspace_id=workspace_id,
                session_id=session_id,
                operation="get_session",
                error=str(exc),
                latency_ms=self._latency_ms(started_at),
            )
            raise

    async def list_messages(
        self,
        *,
        workspace_id: str,
        session_id: UUID,
        limit: int = 50,
    ) -> list[ConversationMessage]:
        """查询会话消息并记录操作。"""

        started_at = time.perf_counter()
        try:
            messages = await self.conversations.list_messages(
                session_id=session_id,
                workspace_id=workspace_id,
                limit=limit,
            )
            await self._log_operation(
                workspace_id=workspace_id,
                session_id=session_id,
                operation="list_messages",
                success=True,
                latency_ms=self._latency_ms(started_at),
                metadata={"count": len(messages)},
            )
            await self.session.commit()
            return messages
        except Exception as exc:
            await self.session.rollback()
            await self._safe_log_failure(
                workspace_id=workspace_id,
                session_id=session_id,
                operation="list_messages",
                error=str(exc),
                latency_ms=self._latency_ms(started_at),
            )
            raise

    async def get_recent_messages(
        self,
        *,
        workspace_id: str,
        session_id: UUID,
        limit: int = 10,
    ) -> list[ConversationMessage]:
        """获取最近消息，返回按时间正序排列。"""

        started_at = time.perf_counter()
        try:
            messages = await self.conversations.list_messages(
                session_id=session_id,
                workspace_id=workspace_id,
                limit=limit,
                recent_only=True,
            )
            await self._log_operation(
                workspace_id=workspace_id,
                session_id=session_id,
                operation="get_recent_messages",
                success=True,
                latency_ms=self._latency_ms(started_at),
                metadata={"count": len(messages)},
            )
            await self.session.commit()
            return messages
        except Exception as exc:
            await self.session.rollback()
            await self._safe_log_failure(
                workspace_id=workspace_id,
                session_id=session_id,
                operation="get_recent_messages",
                error=str(exc),
                latency_ms=self._latency_ms(started_at),
            )
            raise

    async def summarize_session(self, *, workspace_id: str, session_id: UUID, limit: int = 20) -> str:
        """生成轻量会话摘要，不调用 LLM。"""

        started_at = time.perf_counter()
        try:
            messages = await self.conversations.list_messages(
                session_id=session_id,
                workspace_id=workspace_id,
                limit=limit,
                recent_only=True,
            )
            summary = " | ".join(f"{message.role}: {message.content[:120]}" for message in messages)
            summary = summary[:2000]
            await self._log_operation(
                workspace_id=workspace_id,
                session_id=session_id,
                operation="summarize_session",
                success=True,
                latency_ms=self._latency_ms(started_at),
                metadata={"message_count": len(messages)},
            )
            await self.session.commit()
            return summary
        except Exception as exc:
            await self.session.rollback()
            await self._safe_log_failure(
                workspace_id=workspace_id,
                session_id=session_id,
                operation="summarize_session",
                error=str(exc),
                latency_ms=self._latency_ms(started_at),
            )
            raise

    async def save_memory(
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

        started_at = time.perf_counter()
        try:
            memory = await self.memories.create_memory(
                workspace_id=workspace_id,
                agent_name=agent_name,
                memory_type=memory_type,
                content=content,
                metadata=metadata,
                importance_score=max(0.0, min(1.0, importance_score)),
            )
            await self._log_operation(
                workspace_id=workspace_id,
                agent_name=agent_name,
                memory_type=memory_type,
                operation="save_memory",
                success=True,
                latency_ms=self._latency_ms(started_at),
            )
            await self.session.commit()
            await self.session.refresh(memory)
            return memory
        except Exception as exc:
            await self.session.rollback()
            await self._safe_log_failure(
                workspace_id=workspace_id,
                agent_name=agent_name,
                memory_type=memory_type,
                operation="save_memory",
                error=str(exc),
                latency_ms=self._latency_ms(started_at),
            )
            raise

    async def search_memory(
        self,
        *,
        workspace_id: str,
        query: str | None = None,
        agent_name: str | None = None,
        memory_type: str | None = None,
        limit: int = 10,
    ) -> list[AgentMemory]:
        """检索 Agent Memory。"""

        started_at = time.perf_counter()
        try:
            memories = await self.memories.search_memories(
                workspace_id=workspace_id,
                query=query,
                agent_name=agent_name,
                memory_type=memory_type,
                limit=limit,
            )
            await self._log_operation(
                workspace_id=workspace_id,
                agent_name=agent_name,
                memory_type=memory_type,
                operation="search_memory",
                success=True,
                latency_ms=self._latency_ms(started_at),
                metadata={"count": len(memories), "query": query},
            )
            await self.session.commit()
            return memories
        except Exception as exc:
            await self.session.rollback()
            await self._safe_log_failure(
                workspace_id=workspace_id,
                agent_name=agent_name,
                memory_type=memory_type,
                operation="search_memory",
                error=str(exc),
                latency_ms=self._latency_ms(started_at),
            )
            raise

    async def delete_memory(self, *, workspace_id: str, memory_id: UUID) -> bool:
        """删除一条 Agent Memory。"""

        started_at = time.perf_counter()
        try:
            deleted = await self.memories.delete_memory(memory_id=memory_id, workspace_id=workspace_id)
            await self._log_operation(
                workspace_id=workspace_id,
                operation="delete_memory",
                success=True,
                latency_ms=self._latency_ms(started_at),
                metadata={"memory_id": str(memory_id), "deleted": deleted},
            )
            await self.session.commit()
            return deleted
        except Exception as exc:
            await self.session.rollback()
            await self._safe_log_failure(
                workspace_id=workspace_id,
                operation="delete_memory",
                error=str(exc),
                latency_ms=self._latency_ms(started_at),
                metadata={"memory_id": str(memory_id)},
            )
            raise

    async def _log_operation(
        self,
        *,
        workspace_id: str,
        operation: str,
        success: bool,
        latency_ms: int,
        session_id: UUID | None = None,
        agent_name: str | None = None,
        memory_type: str | None = None,
        error: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """记录 Memory 操作日志。"""

        await self.conversations.create_operation_log(
            workspace_id=workspace_id,
            session_id=session_id,
            agent_name=agent_name,
            memory_type=memory_type,
            operation=operation,
            success=success,
            error=error,
            latency_ms=latency_ms,
            metadata=metadata,
        )
        logger.info(
            "Memory operation recorded",
            extra={
                "workspace_id": workspace_id,
                "session_id": str(session_id) if session_id else None,
                "agent_name": agent_name,
                "memory_type": memory_type,
                "operation": operation,
                "latency_ms": latency_ms,
                "success": success,
                "error": error,
            },
        )

    async def _safe_log_failure(
        self,
        *,
        workspace_id: str,
        operation: str,
        error: str,
        latency_ms: int,
        session_id: UUID | None = None,
        agent_name: str | None = None,
        memory_type: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """尽力记录失败，不让日志失败掩盖原始错误。"""

        try:
            await self._log_operation(
                workspace_id=workspace_id,
                session_id=session_id,
                agent_name=agent_name,
                memory_type=memory_type,
                operation=operation,
                success=False,
                error=error,
                latency_ms=latency_ms,
                metadata=metadata,
            )
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            logger.exception("Failed to record memory operation failure")

    def _estimate_token_count(self, content: str) -> int:
        """粗略估算 token 数，避免引入 tokenizer 依赖。"""

        return max(1, len(content.split()) or len(content) // 4)

    def _latency_ms(self, started_at: float) -> int:
        """计算耗时。"""

        return int((time.perf_counter() - started_at) * 1000)
