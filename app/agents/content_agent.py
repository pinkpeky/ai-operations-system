"""内容生成 Agent 模块。

ContentAgent 是中央 Agent 基础层的第一个示例 Agent，当前继续使用 MockProvider。
"""

import logging
from typing import Any

from pydantic import ValidationError

from app.agents.base_agent import AgentLLMClient, BaseAgent
from app.schemas.agent import ContentAgentRequest, ContentAgentResponse
from app.schemas.llm import LLMResponse

logger = logging.getLogger(__name__)


class ContentAgent(BaseAgent):
    """内容生成 Agent。"""

    agent_name = "ContentAgent"
    agent_type = "content_generation"

    def __init__(self, llm_client: AgentLLMClient | None = None) -> None:
        super().__init__(llm_client=llm_client)

    def validate_input(self, agent_input: dict[str, Any]) -> dict[str, Any]:
        """校验内容生成输入。"""

        try:
            request = ContentAgentRequest.model_validate(agent_input)
            return request.model_dump()
        except ValidationError as exc:
            logger.exception("ContentAgent input validation failed")
            raise ValueError(str(exc)) from exc

    def build_prompt(self, validated_input: dict[str, Any]) -> str:
        """构建内容生成 Prompt。"""

        return (
            "请为以下主题生成一条适合社交平台发布的内容方案。\n\n"
            f"主题：{validated_input['topic']}\n"
            f"平台：{validated_input['platform']}\n"
            f"风格：{validated_input['style']}\n\n"
            "请包含标题、描述、标签和行动召唤。"
        )

    def format_output(self, validated_input: dict[str, Any], llm_response: LLMResponse) -> dict[str, Any]:
        """将 LLM 响应格式化为 ContentAgentResponse。"""

        try:
            topic = str(validated_input["topic"])
            platform = str(validated_input["platform"])
            style = str(validated_input["style"])
            response = ContentAgentResponse(
                title=f"{topic} | {platform} 内容方案",
                description=f"围绕「{topic}」生成一条{style}风格的 {platform} 内容。{llm_response.content}",
                tags=self._build_tags(topic=topic, platform=platform, style=style),
                cta=f"关注我们，获取更多关于{topic}的自动化运营实践。",
                raw_response=llm_response.content,
            )
            return response.model_dump()
        except Exception as exc:
            logger.exception("ContentAgent output formatting failed")
            raise RuntimeError("ContentAgent output formatting failed") from exc

    def get_system_prompt(self) -> str:
        """返回 ContentAgent system prompt。"""

        return "你是专业内容运营 Agent，擅长为不同平台生成结构化内容方案。"

    def _build_tags(self, topic: str, platform: str, style: str) -> list[str]:
        """构建稳定标签列表。"""

        return [
            topic.replace(" ", ""),
            platform.lower().replace(" ", "-"),
            style.replace(" ", ""),
        ]
