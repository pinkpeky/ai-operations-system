"""ToolRegistry 测试。"""

from typing import Any

import pytest
from pydantic import BaseModel, Field

from app.tools.base import BaseTool, ToolExecutionContext
from app.tools.registry import ToolRegistry


class EchoInput(BaseModel):
    """测试工具输入。"""

    text: str = Field(min_length=1)


class EchoOutput(BaseModel):
    """测试工具输出。"""

    echoed: str


class EchoTool(BaseTool):
    """测试用 Echo 工具。"""

    name = "echo_tool"
    description = "Echo test tool"
    input_schema = EchoInput
    output_schema = EchoOutput

    async def execute(self, tool_input: BaseModel, context: ToolExecutionContext) -> BaseModel:
        """返回输入文本。"""

        request = EchoInput.model_validate(tool_input.model_dump())
        return EchoOutput(echoed=f"{context.require_workspace()}:{request.text}")


def test_tool_registry_registers_and_lists_tools() -> None:
    """Registry 应能注册和列出工具。"""

    registry = ToolRegistry()
    registry.register_tool(EchoTool(), permission_scopes=["demo:read"])

    tools = registry.list_tools(workspace_id="workspace-a")

    assert len(tools) == 1
    assert tools[0].tool.name == "echo_tool"
    assert tools[0].permission_scopes == ["demo:read"]


def test_tool_registry_validates_tool_input() -> None:
    """Registry 应委托工具 schema 校验输入。"""

    registry = ToolRegistry()
    registry.register_tool(EchoTool())

    validated = registry.validate_tool_input("echo_tool", {"text": "hello"})

    assert isinstance(validated, EchoInput)
    assert validated.text == "hello"


@pytest.mark.asyncio
async def test_tool_registry_executes_tool_with_workspace() -> None:
    """Registry 执行工具时必须携带 workspace。"""

    registry = ToolRegistry()
    registry.register_tool(EchoTool())

    result = await registry.execute_tool(
        tool_name="echo_tool",
        tool_input={"text": "hello"},
        context=ToolExecutionContext(workspace_id="workspace-a"),
    )

    assert result.success is True
    assert result.tool_output["echoed"] == "workspace-a:hello"


@pytest.mark.asyncio
async def test_tool_registry_records_disabled_tool_failure() -> None:
    """禁用工具不应执行，并应返回失败结果。"""

    registry = ToolRegistry()
    registry.register_tool(EchoTool(), enabled=False)

    result = await registry.execute_tool(
        tool_name="echo_tool",
        tool_input={"text": "hello"},
        context=ToolExecutionContext(workspace_id="workspace-a"),
    )

    assert result.success is False
    assert "disabled" in str(result.error)


@pytest.mark.asyncio
async def test_tool_registry_rejects_invalid_input() -> None:
    """非法输入应返回失败结果。"""

    registry = ToolRegistry()
    registry.register_tool(EchoTool())

    result = await registry.execute_tool(
        tool_name="echo_tool",
        tool_input={"text": ""},
        context=ToolExecutionContext(workspace_id="workspace-a"),
    )

    assert result.success is False
    assert result.tool_output == {}
    assert result.error
