"""Memory API 数据模型。"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.memory import AgentMemory, ConversationMessage, ConversationSession


class ConversationSessionCreateRequest(BaseModel):
    """创建会话请求。"""

    title: str = Field(min_length=1, max_length=255, description="会话标题")
    metadata: dict[str, Any] = Field(default_factory=dict, description="会话元数据")


class ConversationSessionResponse(BaseModel):
    """会话响应。"""

    id: UUID
    workspace_id: str
    user_id: str | None
    title: str
    status: str
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, session: ConversationSession) -> "ConversationSessionResponse":
        """从 ORM 构造响应。"""

        return cls(
            id=session.id,
            workspace_id=session.workspace_id,
            user_id=session.user_id,
            title=session.title,
            status=session.status,
            metadata=session.session_metadata,
            created_at=session.created_at,
            updated_at=session.updated_at,
        )


class ConversationSessionListResponse(BaseModel):
    """会话列表响应。"""

    items: list[ConversationSessionResponse]


class ConversationMessageCreateRequest(BaseModel):
    """追加消息请求。"""

    session_id: UUID
    role: str = Field(description="消息角色：system/user/assistant/tool")
    content: str = Field(min_length=1, description="消息内容")
    token_count: int | None = Field(default=None, ge=0, description="可选 token 数")
    metadata: dict[str, Any] = Field(default_factory=dict, description="消息元数据")


class ConversationMessageResponse(BaseModel):
    """会话消息响应。"""

    id: UUID
    session_id: UUID | None
    workspace_id: str
    role: str
    content: str
    token_count: int
    metadata: dict[str, Any]
    created_at: datetime

    @classmethod
    def from_model(cls, message: ConversationMessage) -> "ConversationMessageResponse":
        """从 ORM 构造响应。"""

        return cls(
            id=message.id,
            session_id=message.session_id,
            workspace_id=message.workspace_id,
            role=message.role,
            content=message.content,
            token_count=message.token_count,
            metadata=message.message_metadata,
            created_at=message.created_at,
        )


class ConversationMessageListResponse(BaseModel):
    """会话消息列表响应。"""

    session_id: UUID
    items: list[ConversationMessageResponse]


class AgentMemoryCreateRequest(BaseModel):
    """保存 Agent Memory 请求。"""

    agent_name: str = Field(min_length=1, max_length=128, description="Agent 名称")
    memory_type: str = Field(description="short_term / long_term / task_memory / retrieval_memory")
    content: str = Field(min_length=1, description="Memory 内容")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Memory 元数据")
    importance_score: float = Field(default=0.5, ge=0, le=1, description="重要性分数")


class AgentMemoryResponse(BaseModel):
    """Agent Memory 响应。"""

    id: UUID
    workspace_id: str
    agent_name: str
    memory_type: str
    content: str
    metadata: dict[str, Any]
    importance_score: float
    created_at: datetime

    @classmethod
    def from_model(cls, memory: AgentMemory) -> "AgentMemoryResponse":
        """从 ORM 构造响应。"""

        return cls(
            id=memory.id,
            workspace_id=memory.workspace_id,
            agent_name=memory.agent_name,
            memory_type=memory.memory_type,
            content=memory.content,
            metadata=memory.memory_metadata,
            importance_score=memory.importance_score,
            created_at=memory.created_at,
        )


class AgentMemoryListResponse(BaseModel):
    """Agent Memory 列表响应。"""

    items: list[AgentMemoryResponse]


class AgentMemoryDeleteResponse(BaseModel):
    """删除 Memory 响应。"""

    memory_id: UUID
    deleted: bool


class MemoryTraceItem(BaseModel):
    """Agent / RAG Memory trace 项。"""

    operation: str
    session_id: str | None = None
    recent_messages_count: int = 0
    retrieved_memories_count: int = 0
    latency_ms: int = 0
    success: bool = True
    error: str | None = None
