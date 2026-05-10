"""Mock LLM Provider 模块。

默认 Provider，不调用真实模型服务，用于验证 LLM Client Layer 的请求链路和 Swagger 测试接口。
"""

import logging

from app.agents.providers.base import BaseLLMProvider, LLMPrompt
from app.schemas.llm import LLMRequest, LLMResponse

logger = logging.getLogger(__name__)


class MockProvider(BaseLLMProvider):
    """固定响应的 Mock Provider。"""

    provider_name = "mock"

    def __init__(self, model: str = "mock-llm") -> None:
        super().__init__(model=model)

    async def generate(self, request: LLMRequest, prompt: LLMPrompt) -> LLMResponse:
        """返回固定测试内容，避免默认环境依赖真实模型。"""

        try:
            content = "MockProvider 测试响应：LLM Client Layer 已就绪。"
            logger.info(
                "Mock LLM response generated",
                extra={"provider": self.provider_name, "model": self.model},
            )
            return LLMResponse(
                provider=self.provider_name,
                model=self.model,
                content=content,
                usage={
                    "prompt_chars": len(prompt.full_prompt),
                    "completion_chars": len(content),
                },
                metadata={
                    "mock": True,
                    "has_system_prompt": prompt.system_prompt is not None,
                    "temperature": request.temperature,
                    "max_tokens": request.max_tokens,
                },
            )
        except Exception as exc:
            logger.exception("Mock LLM provider failed")
            raise RuntimeError("Mock LLM provider failed") from exc
