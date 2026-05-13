"""Tool Calling API 数据模型。"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.tool_call import ToolCallLog


class ToolInfoResponse(BaseModel):
    """工具信息响应。"""

    name: str
    description: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    enabled: bool
    permission_scopes: list[str]


class ToolListResponse(BaseModel):
    """工具列表响应。"""

    items: list[ToolInfoResponse]


class ToolExecuteRequest(BaseModel):
    """工具执行请求。"""

    input: dict[str, Any] = Field(default_factory=dict, description="工具输入")


class ToolExecuteResponse(BaseModel):
    """工具执行响应。"""

    tool_name: str
    success: bool
    output: dict[str, Any]
    error: str | None
    latency_ms: int


class ToolCallLogResponse(BaseModel):
    """工具调用日志响应。"""

    id: UUID
    workspace_id: str
    agent_name: str | None
    tool_name: str
    tool_input: dict[str, Any]
    tool_output: dict[str, Any]
    success: bool
    error: str | None
    latency_ms: int
    created_at: datetime

    @classmethod
    def from_model(cls, log: ToolCallLog) -> "ToolCallLogResponse":
        """从 ORM 模型构造响应。"""

        return cls(
            id=log.id,
            workspace_id=log.workspace_id,
            agent_name=log.agent_name,
            tool_name=log.tool_name,
            tool_input=log.tool_input,
            tool_output=log.tool_output,
            success=log.success,
            error=log.error,
            latency_ms=log.latency_ms,
            created_at=log.created_at,
        )


class ToolCallLogListResponse(BaseModel):
    """工具调用日志列表响应。"""

    items: list[ToolCallLogResponse]
