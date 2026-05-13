"""Tool Calling 可观测性 ORM 模型。

该模块记录 Agent 或 API 触发的内部工具调用，当前只做基础审计与调试，
后续可扩展为权限控制、配额统计和执行回放。
"""

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Integer, JSON, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ToolCallLog(Base):
    """工具调用日志表。"""

    __tablename__ = "tool_call_logs"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4, comment="工具调用日志 ID")
    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="工作区 ID")
    agent_name: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="触发调用的 Agent 名称")
    tool_name: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="工具名称")
    tool_input: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False, comment="工具输入")
    tool_output: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False, comment="工具输出")
    success: Mapped[bool] = mapped_column(Boolean, index=True, nullable=False, comment="是否执行成功")
    error: Mapped[str | None] = mapped_column(Text, nullable=True, comment="错误信息")
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False, comment="工具执行耗时毫秒")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="创建时间",
    )
