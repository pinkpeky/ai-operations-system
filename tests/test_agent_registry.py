"""Agent Registry 测试。"""

import pytest

from app.multi_agent.services import AgentRole, build_default_agent_registry


def test_default_agent_registry_lists_phase15_agents() -> None:
    """默认 Registry 应包含 Phase 15 固定链路和工具类 Agent。"""

    registry = build_default_agent_registry()
    names = {agent.name for agent in registry.list_agents()}

    assert {"content_planner", "rag_agent", "content_agent", "review_agent", "runtime_agent", "tool_agent"}.issubset(names)
    assert registry.get_agent("rag_agent").metadata["orchestrator"] == "AgenticRAGOrchestrator"
    assert "current_runtime_tool" in registry.get_agent("tool_agent").metadata["tools"]


def test_agent_registry_enable_disable() -> None:
    """Registry 应支持启停 Agent。"""

    registry = build_default_agent_registry()
    registry.set_agent_enabled("content_agent", False)

    with pytest.raises(PermissionError, match="Agent disabled"):
        registry.get_agent("content_agent")

    assert "content_agent" not in {agent.name for agent in registry.list_agents()}
    assert "content_agent" in {agent.name for agent in registry.list_agents(include_disabled=True)}


def test_agent_registry_rejects_duplicate() -> None:
    """重复注册同名 Agent 应报错。"""

    registry = build_default_agent_registry()

    with pytest.raises(ValueError, match="Agent already registered"):
        registry.register_agent(
            AgentRole(
                name="content_agent",
                display_name="Duplicate",
                agent_type="duplicate",
                description="duplicate",
            )
        )

