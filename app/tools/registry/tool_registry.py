"""Tool Registry。

Registry 负责工具注册、启停、输入校验和统一执行。执行时会强制检查 workspace_id，
并在具备数据库 session 时写入 tool_call_logs。
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from app.repositories.tool_call_repository import ToolCallLogRepository
from app.tools.base import BaseTool, ToolExecutionContext, ToolExecutionRecord

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class ToolRegistration:
    """工具注册信息。"""

    tool: BaseTool
    enabled: bool = True
    allowed_workspaces: set[str] | None = None
    permission_scopes: list[str] = field(default_factory=list)


class ToolRegistry:
    """内部工具注册中心。"""

    def __init__(self) -> None:
        self._tools: dict[str, ToolRegistration] = {}

    def register_tool(
        self,
        tool: BaseTool,
        *,
        enabled: bool = True,
        allowed_workspaces: set[str] | None = None,
        permission_scopes: list[str] | None = None,
    ) -> None:
        """注册工具。"""

        if tool.name in self._tools:
            raise ValueError(f"Tool already registered: {tool.name}")
        self._tools[tool.name] = ToolRegistration(
            tool=tool,
            enabled=enabled,
            allowed_workspaces=allowed_workspaces,
            permission_scopes=permission_scopes or list(tool.permission_scopes),
        )
        logger.info("Tool registered", extra={"tool_name": tool.name, "enabled": enabled})

    def get_tool(self, tool_name: str, workspace_id: str | None = None) -> BaseTool:
        """获取可用工具。"""

        registration = self._tools.get(tool_name)
        if registration is None:
            raise KeyError(f"Tool not found: {tool_name}")
        self._ensure_tool_available(tool_name=tool_name, registration=registration, workspace_id=workspace_id)
        return registration.tool

    def list_tools(self, *, workspace_id: str | None = None, include_disabled: bool = False) -> list[ToolRegistration]:
        """列出当前 workspace 可见的工具。"""

        visible: list[ToolRegistration] = []
        for name, registration in self._tools.items():
            if not include_disabled and not registration.enabled:
                continue
            try:
                self._ensure_workspace_allowed(registration=registration, workspace_id=workspace_id)
            except PermissionError:
                continue
            logger.debug("Tool visible in registry", extra={"tool_name": name, "workspace_id": workspace_id})
            visible.append(registration)
        return visible

    def validate_tool_input(self, tool_name: str, tool_input: dict[str, Any]) -> BaseModel:
        """校验工具输入。"""

        tool = self.get_tool(tool_name)
        return tool.validate_input(tool_input)

    def set_tool_enabled(self, tool_name: str, enabled: bool) -> None:
        """启用或禁用工具，预留给未来管理 API 使用。"""

        registration = self._tools.get(tool_name)
        if registration is None:
            raise KeyError(f"Tool not found: {tool_name}")
        registration.enabled = enabled
        logger.info("Tool enabled flag changed", extra={"tool_name": tool_name, "enabled": enabled})

    async def execute_tool(
        self,
        *,
        tool_name: str,
        tool_input: dict[str, Any],
        context: ToolExecutionContext,
        agent_name: str | None = None,
    ) -> ToolExecutionRecord:
        """执行工具并记录 tool_call_logs。"""

        workspace_id = context.require_workspace()
        started_at = time.perf_counter()
        output: dict[str, Any] = {}
        error: str | None = None
        success = False

        try:
            registration = self._tools.get(tool_name)
            if registration is None:
                raise KeyError(f"Tool not found: {tool_name}")
            self._ensure_tool_available(tool_name=tool_name, registration=registration, workspace_id=workspace_id)
            validated_input = registration.tool.validate_input(tool_input)
            raw_output = await registration.tool.execute(validated_input, context)
            output = registration.tool.validate_output(raw_output).model_dump(mode="json")
            success = True
            logger.info(
                "Tool executed successfully",
                extra={"tool_name": tool_name, "workspace_id": workspace_id},
            )
        except Exception as exc:
            error = str(exc) or f"Tool execution failed: {tool_name}"
            logger.exception(
                "Tool execution failed",
                extra={"tool_name": tool_name, "workspace_id": workspace_id, "error": error},
            )

        latency_ms = int((time.perf_counter() - started_at) * 1000)
        record = ToolExecutionRecord(
            tool_name=tool_name,
            tool_input=tool_input,
            tool_output=output,
            success=success,
            error=error,
            latency_ms=latency_ms,
        )
        await self._write_call_log(record=record, context=context, agent_name=agent_name)
        return record

    async def _write_call_log(
        self,
        *,
        record: ToolExecutionRecord,
        context: ToolExecutionContext,
        agent_name: str | None,
    ) -> None:
        """写入工具调用日志，日志失败时不吞掉业务结果。"""

        if context.session is None:
            return
        repository = ToolCallLogRepository(context.session)
        await repository.create_log(
            workspace_id=context.require_workspace(),
            agent_name=agent_name or context.agent_name,
            tool_name=record.tool_name,
            tool_input=jsonable_encoder(record.tool_input),
            tool_output=jsonable_encoder(record.tool_output),
            success=record.success,
            error=record.error,
            latency_ms=record.latency_ms,
        )
        await context.session.commit()

    def _ensure_tool_available(
        self,
        *,
        tool_name: str,
        registration: ToolRegistration,
        workspace_id: str | None,
    ) -> None:
        """检查工具是否可用。"""

        if not registration.enabled:
            raise PermissionError(f"Tool disabled: {tool_name}")
        self._ensure_workspace_allowed(registration=registration, workspace_id=workspace_id)

    def _ensure_workspace_allowed(self, *, registration: ToolRegistration, workspace_id: str | None) -> None:
        """检查 workspace 是否有权看到工具。"""

        if registration.allowed_workspaces is None:
            return
        if not workspace_id or workspace_id not in registration.allowed_workspaces:
            raise PermissionError("Tool is not available in this workspace")
