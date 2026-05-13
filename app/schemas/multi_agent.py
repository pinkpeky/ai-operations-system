"""Multi-Agent API Schema。"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.multi_agent import AgentHandoff, AgentMessage, AgentRun
from app.multi_agent.services.agent_registry import AgentRole


class AgentInfoResponse(BaseModel):
    """Agent Registry 单项响应。"""

    name: str
    display_name: str
    agent_type: str
    description: str
    capabilities: list[str]
    enabled: bool
    metadata: dict[str, Any]

    @classmethod
    def from_role(cls, role: AgentRole) -> "AgentInfoResponse":
        """从 AgentRole 构造响应。"""

        return cls(
            name=role.name,
            display_name=role.display_name,
            agent_type=role.agent_type,
            description=role.description,
            capabilities=role.capabilities,
            enabled=role.enabled,
            metadata=role.metadata,
        )


class AgentRegistryResponse(BaseModel):
    """Agent Registry 列表响应。"""

    items: list[AgentInfoResponse]


class MultiAgentRunCreateRequest(BaseModel):
    """创建 Multi-Agent run 请求。"""

    root_agent: str = Field(default="content_planner", min_length=1, max_length=128)
    session_id: UUID | None = Field(default=None, description="可选 Memory session ID")
    input: dict[str, Any] = Field(default_factory=dict, description="run 输入")


class ExecuteAgentChainRequest(BaseModel):
    """执行固定 Agent Chain 请求。"""

    chain_name: str = Field(default="content_planning", description="当前仅支持 content_planning")
    input: dict[str, Any] | None = Field(default=None, description="可覆盖 run.input 的链路输入")


class AgentRunResponse(BaseModel):
    """Agent run 响应。"""

    id: UUID
    workspace_id: str
    user_id: str | None
    session_id: UUID | None
    root_agent: str
    status: str
    input: dict[str, Any]
    output: dict[str, Any] | None
    error: str | None
    started_at: datetime | None
    completed_at: datetime | None
    duration_ms: int | None
    created_at: datetime

    @classmethod
    def from_model(cls, run: AgentRun) -> "AgentRunResponse":
        """从 ORM 构造响应。"""

        return cls(
            id=run.id,
            workspace_id=run.workspace_id,
            user_id=run.user_id,
            session_id=run.session_id,
            root_agent=run.root_agent,
            status=run.status,
            input=run.run_input,
            output=run.run_output,
            error=run.error,
            started_at=run.started_at,
            completed_at=run.completed_at,
            duration_ms=run.duration_ms,
            created_at=run.created_at,
        )


class AgentRunListResponse(BaseModel):
    """Agent run 列表响应。"""

    items: list[AgentRunResponse]


class AgentMessageResponse(BaseModel):
    """Agent message 响应。"""

    id: UUID
    workspace_id: str
    run_id: UUID
    from_agent: str | None
    to_agent: str | None
    role: str
    content: str
    metadata: dict[str, Any]
    created_at: datetime

    @classmethod
    def from_model(cls, message: AgentMessage) -> "AgentMessageResponse":
        """从 ORM 构造响应。"""

        return cls(
            id=message.id,
            workspace_id=message.workspace_id,
            run_id=message.run_id,
            from_agent=message.from_agent,
            to_agent=message.to_agent,
            role=message.role,
            content=message.content,
            metadata=message.message_metadata,
            created_at=message.created_at,
        )


class AgentMessageListResponse(BaseModel):
    """Agent message 列表响应。"""

    run_id: UUID
    items: list[AgentMessageResponse]


class AgentHandoffResponse(BaseModel):
    """Agent handoff 响应。"""

    id: UUID
    workspace_id: str
    run_id: UUID
    from_agent: str
    to_agent: str
    reason: str
    payload: dict[str, Any]
    status: str
    created_at: datetime

    @classmethod
    def from_model(cls, handoff: AgentHandoff) -> "AgentHandoffResponse":
        """从 ORM 构造响应。"""

        return cls(
            id=handoff.id,
            workspace_id=handoff.workspace_id,
            run_id=handoff.run_id,
            from_agent=handoff.from_agent,
            to_agent=handoff.to_agent,
            reason=handoff.reason,
            payload=handoff.payload,
            status=handoff.status,
            created_at=handoff.created_at,
        )


class AgentHandoffListResponse(BaseModel):
    """Agent handoff 列表响应。"""

    run_id: UUID
    items: list[AgentHandoffResponse]


class ExecuteAgentChainResponse(BaseModel):
    """固定 Agent Chain 执行响应。"""

    run: AgentRunResponse
    agents_involved: list[str]
    success: bool
    error: str | None = None
    duration_ms: int
    messages: list[AgentMessageResponse]
    handoffs: list[AgentHandoffResponse]
