"""Agent API 路由模块。

当前只暴露 ContentAgent 示例接口，后续业务 Agent 可沿用 BaseAgent 框架扩展。
"""

import logging

from fastapi import APIRouter

from app.agents.content_agent import ContentAgent
from app.core.errors import AppError
from app.schemas.agent import ContentAgentRequest, ContentAgentResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agents", tags=["agents"])


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
