"""Multi-Agent service 聚合。"""

from app.multi_agent.services.agent_registry import AgentRegistry, AgentRole, build_default_agent_registry
from app.multi_agent.services.multi_agent_service import MultiAgentService

__all__ = ["AgentRegistry", "AgentRole", "MultiAgentService", "build_default_agent_registry"]
