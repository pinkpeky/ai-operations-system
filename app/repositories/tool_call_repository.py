"""工具调用日志 Repository。

集中封装 tool_call_logs 的写入与查询，确保所有查询都默认带 workspace_id，
避免多人环境下工具调用日志串库。
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tool_call import ToolCallLog


class ToolCallLogRepository:
    """工具调用日志数据访问层。"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_log(
        self,
        *,
        workspace_id: str,
        tool_name: str,
        tool_input: dict[str, Any],
        tool_output: dict[str, Any] | None,
        success: bool,
        latency_ms: int,
        agent_name: str | None = None,
        error: str | None = None,
    ) -> ToolCallLog:
        """写入一条工具调用日志。"""

        log = ToolCallLog(
            workspace_id=workspace_id,
            agent_name=agent_name,
            tool_name=tool_name,
            tool_input=tool_input,
            tool_output=tool_output or {},
            success=success,
            error=error,
            latency_ms=latency_ms,
        )
        self.session.add(log)
        await self.session.flush()
        return log

    async def list_logs(
        self,
        *,
        workspace_id: str,
        tool_name: str | None = None,
        agent_name: str | None = None,
        success: bool | None = None,
        limit: int = 100,
    ) -> list[ToolCallLog]:
        """按 workspace 查询工具调用日志。"""

        statement = select(ToolCallLog).where(ToolCallLog.workspace_id == workspace_id)
        if tool_name is not None:
            statement = statement.where(ToolCallLog.tool_name == tool_name)
        if agent_name is not None:
            statement = statement.where(ToolCallLog.agent_name == agent_name)
        if success is not None:
            statement = statement.where(ToolCallLog.success.is_(success))
        statement = statement.order_by(ToolCallLog.created_at.desc()).limit(limit)
        result = await self.session.execute(statement)
        return list(result.scalars().all())
