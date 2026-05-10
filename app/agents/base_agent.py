"""中央 Agent 基类模块。

BaseAgent 统一定义输入校验、Prompt 构建、LLM 调用、输出格式化和错误处理流程。
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, ClassVar, Protocol

from app.agents.llm_client import LLMClient
from app.schemas.llm import LLMRequest, LLMResponse

logger = logging.getLogger(__name__)


class AgentLLMClient(Protocol):
    """Agent 依赖的 LLM Client 协议，便于测试替换。"""

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """执行一次 LLM 生成。"""


class BaseAgent(ABC):
    """中央 Agent 基类。"""

    agent_name: ClassVar[str]
    agent_type: ClassVar[str]

    def __init__(self, llm_client: AgentLLMClient | None = None) -> None:
        self.llm_client = llm_client or LLMClient()

    async def run(self, agent_input: dict[str, Any]) -> dict[str, Any]:
        """执行 Agent 标准流程。"""

        try:
            logger.info(
                "Agent run started",
                extra={"agent_name": self.agent_name, "agent_type": self.agent_type},
            )
            validated_input = self.validate_input(agent_input)
            prompt = self.build_prompt(validated_input)
            llm_response = await self.call_llm(prompt=prompt, validated_input=validated_input)
            output = self.format_output(validated_input=validated_input, llm_response=llm_response)
            logger.info(
                "Agent run completed",
                extra={
                    "agent_name": self.agent_name,
                    "agent_type": self.agent_type,
                    "provider": llm_response.provider,
                    "model": llm_response.model,
                },
            )
            return output
        except ValueError:
            logger.exception(
                "Agent input validation failed",
                extra={"agent_name": self.agent_name, "agent_type": self.agent_type},
            )
            raise
        except Exception as exc:
            logger.exception(
                "Agent run failed",
                extra={"agent_name": self.agent_name, "agent_type": self.agent_type},
            )
            raise RuntimeError(str(exc) or f"{self.agent_name} failed") from exc

    @abstractmethod
    def validate_input(self, agent_input: dict[str, Any]) -> dict[str, Any]:
        """校验并标准化 Agent 输入。"""

    @abstractmethod
    def build_prompt(self, validated_input: dict[str, Any]) -> str:
        """根据输入构建 Prompt。"""

    async def call_llm(self, prompt: str, validated_input: dict[str, Any]) -> LLMResponse:
        """调用 LLM Client。"""

        try:
            return await self.llm_client.generate(
                LLMRequest(
                    system_prompt=self.get_system_prompt(),
                    user_prompt=prompt,
                )
            )
        except Exception as exc:
            logger.exception("Agent LLM call failed", extra={"agent_name": self.agent_name})
            raise RuntimeError(f"Agent LLM call failed: {exc}") from exc

    @abstractmethod
    def format_output(self, validated_input: dict[str, Any], llm_response: LLMResponse) -> dict[str, Any]:
        """格式化 Agent 输出。"""

    def get_system_prompt(self) -> str:
        """返回 Agent 默认 system prompt。"""

        return "你是 AI Operations System 的中央 Agent，请按当前 Agent 职责输出结构化结果。"
