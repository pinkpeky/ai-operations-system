"""默认工具注册表工厂。"""

from app.tools.builtin import (
    BrowserTool,
    CreateTaskTool,
    CurrentRuntimeTool,
    FileSearchTool,
    GetTaskStatusTool,
    RagSearchTool,
)
from app.tools.registry.tool_registry import ToolRegistry


def build_default_tool_registry() -> ToolRegistry:
    """构建当前系统默认内置工具注册表。"""

    registry = ToolRegistry()
    registry.register_tool(RagSearchTool())
    registry.register_tool(FileSearchTool())
    registry.register_tool(CreateTaskTool())
    registry.register_tool(GetTaskStatusTool())
    registry.register_tool(CurrentRuntimeTool())
    registry.register_tool(BrowserTool())
    return registry
