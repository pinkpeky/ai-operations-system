"""Agent API 路由模块。

当前只暴露 ContentAgent 示例接口，后续业务 Agent 可沿用 BaseAgent 框架扩展。
"""

import logging

from fastapi import APIRouter, Depends

from app.agents.content_agent import ContentAgent
from app.core.errors import AppError
from app.core.workspace_context import WorkspaceContext, get_workspace_context
from app.multi_agent.services import build_default_agent_registry
from app.schemas.agent import ContentAgentRequest, ContentAgentResponse
from app.schemas.multi_agent import AgentInfoResponse, AgentRegistryResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("/registry", response_model=AgentRegistryResponse)
async def list_agent_registry(context: WorkspaceContext = Depends(get_workspace_context)) -> AgentRegistryResponse:
    """列出当前可用 Agent Registry。"""

    try:
        registry = build_default_agent_registry()
        agents = registry.list_agents()
        logger.info("Agent registry listed", extra={"workspace_id": context.workspace_id, "count": len(agents)})
        return AgentRegistryResponse(items=[AgentInfoResponse.from_role(agent) for agent in agents])
    except Exception as exc:
        logger.exception("Agent registry API failed")
        raise AppError("Agent registry failed", status_code=500) from exc


@router.post("/content/generate", response_model=ContentAgentResponse)
async def generate_content(request: ContentAgentRequest) -> ContentAgentResponse:
    """调用 ContentAgent 生成内容方案。"""

    try:
        agent = ContentAgent()
        result = await agent.run(request.model_dump())
        logger.info("ContentAgent API completed", extra={"topic": request.topic, "platform": request.platform})
        return ContentAgentResponse.model_validate(result)
    except ValueError as exc:
        logger.warning("ContentAgent API received invalid request", extra={"error": str(exc)})
        raise AppError(str(exc), status_code=400) from exc
    except Exception as exc:
        logger.exception("ContentAgent API failed")
        raise AppError(str(exc) or "ContentAgent generation failed", status_code=500) from exc
