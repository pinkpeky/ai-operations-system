"""Tool Calling 基础接口。

所有内部工具都继承 BaseTool，统一暴露名称、描述、输入输出 schema 和 execute 方法。
当前阶段不做 autonomous planning，只提供可被 Agent 或 API 手动调用的稳定工具协议。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, ClassVar

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings


@dataclass(slots=True)
class ToolExecutionContext:
    """工具执行上下文。

    workspace_id 是隔离边界，所有会访问业务数据的工具都必须使用该字段过滤数据。
    session/settings 由 API 或 Agent 注入，便于测试和后续权限控制扩展。
    """

    workspace_id: str
    user_id: str | None = None
    session: AsyncSession | None = None
    settings: Settings | None = None
    agent_name: str | None = None
    task_id: str | None = None

    def require_workspace(self) -> str:
        """返回 workspace_id，缺失时抛出清晰错误。"""

        if not self.workspace_id:
            raise ValueError("workspace_id is required for tool execution")
        return self.workspace_id

    def require_session(self) -> AsyncSession:
        """返回数据库会话，缺失时抛出清晰错误。"""

        if self.session is None:
            raise ValueError("database session is required for this tool")
        return self.session

    @property
    def effective_settings(self) -> Settings:
        """返回当前配置对象。"""

        return self.settings or get_settings()


@dataclass(frozen=True, slots=True)
class ToolExecutionRecord:
    """一次工具调用的标准结果。"""

    tool_name: str
    tool_input: dict[str, Any]
    tool_output: dict[str, Any]
    success: bool
    error: str | None
    latency_ms: int

    def model_dump(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        """返回可序列化字典，兼容 Agent trace 和 API 响应。"""

        _ = (args, kwargs)
        return jsonable_encoder({
            "tool_name": self.tool_name,
            "tool_input": self.tool_input,
            "tool_output": self.tool_output,
            "success": self.success,
            "error": self.error,
            "latency_ms": self.latency_ms,
        })


class BaseTool(ABC):
    """统一工具基类。"""

    name: ClassVar[str]
    description: ClassVar[str]
    input_schema: ClassVar[type[BaseModel]]
    output_schema: ClassVar[type[BaseModel]]
    permission_scopes: ClassVar[list[str]] = []

    def validate_input(self, tool_input: dict[str, Any]) -> BaseModel:
        """用 Pydantic schema 校验工具输入。"""

        try:
            return self.input_schema.model_validate(tool_input)
        except ValidationError as exc:
            raise ValueError(str(exc)) from exc

    def validate_output(self, tool_output: BaseModel | dict[str, Any]) -> BaseModel:
        """用 Pydantic schema 校验工具输出。"""

        if isinstance(tool_output, BaseModel):
            return self.output_schema.model_validate(tool_output.model_dump())
        return self.output_schema.model_validate(tool_output)

    def input_json_schema(self) -> dict[str, Any]:
        """返回工具输入 JSON Schema。"""

        return self.input_schema.model_json_schema()

    def output_json_schema(self) -> dict[str, Any]:
        """返回工具输出 JSON Schema。"""

        return self.output_schema.model_json_schema()

    @abstractmethod
    async def execute(self, tool_input: BaseModel, context: ToolExecutionContext) -> BaseModel:
        """执行工具逻辑。"""
