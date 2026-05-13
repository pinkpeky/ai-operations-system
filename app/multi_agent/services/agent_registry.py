"""Agent Registry。

Registry 只负责登记 Agent 能力与启停状态，不做 autonomous planning。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class AgentRole:
    """一个可被 Multi-Agent 服务调用的 Agent 元数据。"""

    name: str
    display_name: str
    agent_type: str
    description: str
    capabilities: list[str] = field(default_factory=list)
    enabled: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


class AgentRegistry:
    """多 Agent 注册表。"""

    def __init__(self) -> None:
        self._agents: dict[str, AgentRole] = {}

    def register_agent(self, role: AgentRole) -> None:
        """注册 Agent。"""

        if role.name in self._agents:
            raise ValueError(f"Agent already registered: {role.name}")
        self._agents[role.name] = role
        logger.info("Agent registered", extra={"agent_name": role.name, "enabled": role.enabled})

    def get_agent(self, name: str) -> AgentRole:
        """获取已启用 Agent。"""

        role = self._agents.get(name)
        if role is None:
            raise KeyError(f"Agent not found: {name}")
        if not role.enabled:
            raise PermissionError(f"Agent disabled: {name}")
        return role

    def list_agents(self, *, include_disabled: bool = False) -> list[AgentRole]:
        """列出 Agent 元数据。"""

        return [
            role
            for role in self._agents.values()
            if include_disabled or role.enabled
        ]

    def set_agent_enabled(self, name: str, enabled: bool) -> None:
        """启用或禁用 Agent。"""

        role = self._agents.get(name)
        if role is None:
            raise KeyError(f"Agent not found: {name}")
        role.enabled = enabled
        logger.info("Agent enabled flag changed", extra={"agent_name": name, "enabled": enabled})


def build_default_agent_registry() -> AgentRegistry:
    """构建当前默认 Agent 注册表。"""

    registry = AgentRegistry()
    registry.register_agent(
        AgentRole(
            name="content_planner",
            display_name="Content Planner",
            agent_type="mock_planner",
            description="轻量内容规划 Agent，当前使用确定性 mock 规划。",
            capabilities=["content:plan"],
            metadata={"phase": "15", "planning_mode": "fixed_chain"},
        )
    )
    registry.register_agent(
        AgentRole(
            name="rag_agent",
            display_name="RAG Agent",
            agent_type="agentic_rag",
            description="AgenticRAGOrchestrator 的 Multi-Agent 包装。",
            capabilities=["rag:query", "memory:read"],
            metadata={"orchestrator": "AgenticRAGOrchestrator"},
        )
    )
    registry.register_agent(
        AgentRole(
            name="content_agent",
            display_name="Content Agent",
            agent_type="content_generation",
            description="ContentAgent 内容生成能力。",
            capabilities=["content:generate"],
            metadata={"class": "ContentAgent"},
        )
    )
    registry.register_agent(
        AgentRole(
            name="review_agent",
            display_name="Review Agent",
            agent_type="mock_review",
            description="轻量 mock review Agent，用于固定链路输出检查。",
            capabilities=["content:review"],
            metadata={"phase": "15", "review_mode": "mock"},
        )
    )
    registry.register_agent(
        AgentRole(
            name="runtime_agent",
            display_name="Runtime Agent",
            agent_type="runtime_reader",
            description="读取 CURRENT_RUNTIME 的轻量 Agent。",
            capabilities=["runtime:read"],
        )
    )
    registry.register_agent(
        AgentRole(
            name="tool_agent",
            display_name="Tool Agent",
            agent_type="tool_executor",
            description="调用现有 ToolRegistry 中的 builtin tools。",
            capabilities=["tool:execute"],
            metadata={"tools": ["rag_search_tool", "file_search_tool", "create_task_tool", "get_task_status_tool", "current_runtime_tool"]},
        )
    )
    return registry
