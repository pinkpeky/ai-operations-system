"""OpenClaw builtin tool.

当前仅通过已注册 Browser Worker 调用 mock OpenClaw runtime，不接真实 OpenClaw 或平台自动化。
"""

from __future__ import annotations

from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.openclaw.schemas import OpenClawActionRequest
from app.openclaw.service import OpenClawService
from app.tools.base import BaseTool, ToolExecutionContext


class OpenClawToolInput(BaseModel):
    """OpenClaw tool 输入。"""

    action_type: Literal["health_check", "list_capabilities", "execute_action"]
    worker_id: UUID | None = None
    openclaw_action_type: str | None = Field(default=None, description="Action type used when action_type=execute_action")
    target: str | None = None
    input_payload: dict[str, Any] = Field(default_factory=dict)
    profile_id: str | None = None
    browser_session_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class OpenClawToolOutput(BaseModel):
    """OpenClaw tool 输出。"""

    success: bool
    operation: str
    worker_id: str | None = None
    result: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


class OpenClawTool(BaseTool):
    """调用 OpenClaw mock worker adapter 的内置工具。"""

    name = "openclaw_tool"
    description = "Call the mock OpenClaw worker adapter through registered browser workers. This is a placeholder, not real OpenClaw automation."
    input_schema = OpenClawToolInput
    output_schema = OpenClawToolOutput
    permission_scopes = ["openclaw:execute"]

    async def execute(self, tool_input: BaseModel, context: ToolExecutionContext) -> BaseModel:
        """执行 OpenClaw tool operation。"""

        request = OpenClawToolInput.model_validate(tool_input.model_dump())
        service = OpenClawService(context.require_session(), settings=context.effective_settings)
        if request.action_type == "health_check":
            result = await service.health_check(
                workspace_id=context.require_workspace(),
                worker_id=request.worker_id,
                actor_type="tool",
                actor_id=self.name,
            )
            return OpenClawToolOutput(
                success=result.reachable,
                operation=request.action_type,
                worker_id=str(result.worker_id) if result.worker_id else None,
                result=result.model_dump(mode="json"),
                error=result.error,
            )
        if request.action_type == "list_capabilities":
            result = await service.capabilities(
                workspace_id=context.require_workspace(),
                worker_id=request.worker_id,
                actor_type="tool",
                actor_id=self.name,
            )
            return OpenClawToolOutput(
                success=result.error is None,
                operation=request.action_type,
                worker_id=str(result.worker_id) if result.worker_id else None,
                result=result.model_dump(mode="json"),
                error=result.error,
            )

        action_result = await service.execute_action(
            workspace_id=context.require_workspace(),
            actor_type="tool",
            actor_id=self.name,
            request=OpenClawActionRequest(
                action_type=request.openclaw_action_type or "mock_action",
                target=request.target,
                input_payload=request.input_payload,
                profile_id=request.profile_id,
                browser_session_id=request.browser_session_id,
                metadata=request.metadata,
                worker_id=request.worker_id,
            ),
        )
        return OpenClawToolOutput(
            success=action_result.success,
            operation=request.action_type,
            worker_id=str(action_result.worker_id) if action_result.worker_id else None,
            result=action_result.model_dump(mode="json"),
            error=action_result.error,
        )
