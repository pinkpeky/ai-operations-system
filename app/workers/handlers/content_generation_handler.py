"""内容生成任务 Handler 模块。

该 Handler 接收 content_generation 任务 payload，调用 ContentAgent 并返回标准执行结果。
"""

import logging
from collections.abc import Callable
from typing import Any

from app.agents.content_agent import ContentAgent
from app.schemas.agent import ContentAgentRequest
from app.workers.handlers.base import BaseTaskHandler, TaskExecutionResult

logger = logging.getLogger(__name__)

CONTENT_GENERATION_TASK_TYPE = "content_generation"
ContentAgentFactory = Callable[[], ContentAgent]


class ContentGenerationHandler(BaseTaskHandler):
    """内容生成任务 Handler。"""

    task_type = CONTENT_GENERATION_TASK_TYPE

    def __init__(self, agent_factory: ContentAgentFactory | None = None) -> None:
        self.agent_factory = agent_factory or ContentAgent

    async def handle(self, payload: dict[str, Any]) -> TaskExecutionResult:
        """执行 content_generation 任务。"""

        try:
            request = ContentAgentRequest.model_validate(payload)
            agent = self.agent_factory()
            agent_input = {
                **request.model_dump(),
                "workspace_id": payload.get("workspace_id"),
                "task_id": payload.get("task_id"),
            }
            result = await agent.run(agent_input)
            logger.info(
                "Content generation task handled",
                extra={
                    "topic": request.topic,
                    "platform": request.platform,
                    "workspace_id": payload.get("workspace_id"),
                    "task_id": payload.get("task_id"),
                    "error": None,
                },
            )
            return TaskExecutionResult(success=True, data=result)
        except Exception as exc:
            logger.exception(
                "Content generation task handler failed",
                extra={"workspace_id": payload.get("workspace_id"), "task_id": payload.get("task_id"), "error": str(exc)},
            )
            return TaskExecutionResult(success=False, error=str(exc))
