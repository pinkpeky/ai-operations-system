"""Conversation session/message Repository。"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import ConversationRole, ConversationSessionStatus
from app.models.memory import ConversationMessage, ConversationSession, MemoryOperationLog


class ConversationRepository:
    """会话与消息数据访问层。"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_session(
        self,
        *,
        workspace_id: str,
        user_id: str | None,
        title: str,
        metadata: dict[str, Any] | None = None,
    ) -> ConversationSession:
        """创建会话。"""

        conversation = ConversationSession(
            workspace_id=workspace_id,
            user_id=user_id,
            title=title,
            status=ConversationSessionStatus.ACTIVE.value,
            session_metadata=metadata or {},
        )
        self.session.add(conversation)
        await self.session.flush()
        return conversation

    async def get_session(self, *, session_id: UUID, workspace_id: str) -> ConversationSession | None:
        """按 workspace 查询会话。"""

        statement = select(ConversationSession).where(
            ConversationSession.id == session_id,
            ConversationSession.workspace_id == workspace_id,
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def list_sessions(
        self,
        *,
        workspace_id: str,
        status: str | None = None,
        limit: int = 100,
    ) -> list[ConversationSession]:
        """列出当前 workspace 会话。"""

        statement = select(ConversationSession).where(ConversationSession.workspace_id == workspace_id)
        if status is not None:
            statement = statement.where(ConversationSession.status == status)
        statement = statement.order_by(ConversationSession.updated_at.desc()).limit(limit)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def append_message(
        self,
        *,
        session_id: UUID,
        workspace_id: str,
        role: str,
        content: str,
        token_count: int,
        metadata: dict[str, Any] | None = None,
    ) -> ConversationMessage:
        """追加会话消息。"""

        if role not in {item.value for item in ConversationRole}:
            raise ValueError("role must be system, user, assistant, tool, or event")
        message = ConversationMessage(
            session_id=session_id,
            workspace_id=workspace_id,
            role=role,
            content=content,
            token_count=token_count,
            message_metadata=metadata or {},
        )
        self.session.add(message)
        await self.session.flush()
        return message

    async def list_messages(
        self,
        *,
        session_id: UUID,
        workspace_id: str,
        limit: int = 50,
        recent_only: bool = False,
    ) -> list[ConversationMessage]:
        """查询消息，recent_only=True 时先按倒序取最近消息再恢复正序。"""

        statement = select(ConversationMessage).where(
            ConversationMessage.session_id == session_id,
            ConversationMessage.workspace_id == workspace_id,
        )
        if recent_only:
            statement = statement.order_by(ConversationMessage.created_at.desc()).limit(limit)
            result = await self.session.execute(statement)
            return list(reversed(list(result.scalars().all())))
        statement = statement.order_by(ConversationMessage.created_at.asc()).limit(limit)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def create_operation_log(
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
    ) -> MemoryOperationLog:
        """写入 Memory 操作日志。"""

        log = MemoryOperationLog(
            workspace_id=workspace_id,
            session_id=session_id,
            agent_name=agent_name,
            memory_type=memory_type,
            operation=operation,
            success=success,
            error=error,
            latency_ms=latency_ms,
            log_metadata=metadata or {},
        )
        self.session.add(log)
        await self.session.flush()
        return log
