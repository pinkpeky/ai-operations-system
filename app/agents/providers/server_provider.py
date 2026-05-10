"""远端 LLM Provider 预留模块。

该 Provider 暂不调用真实模型服务，只保留 OpenAI-compatible server 的配置入口。
"""

import logging

from app.agents.providers.base import BaseLLMProvider, LLMPrompt
from app.schemas.llm import LLMHealthResponse, LLMRequest, LLMResponse

logger = logging.getLogger(__name__)


class ServerProvider(BaseLLMProvider):
    """远端模型服务 Provider 预留实现。"""

    provider_name = "server"

    def __init__(self, base_url: str, model: str, timeout_seconds: float) -> None:
        super().__init__(model=model)
        self.base_url = base_url
        self.timeout_seconds = timeout_seconds

    async def generate(self, request: LLMRequest, prompt: LLMPrompt) -> LLMResponse:
        """预留真实远端模型调用接口。"""

        logger.warning(
            "Server LLM provider is not implemented",
            extra={
                "provider": self.provider_name,
                "base_url": self.base_url,
                "model": self.model,
                "timeout_seconds": self.timeout_seconds,
            },
        )
        raise NotImplementedError("ServerProvider is reserved for future server LLM integration")

    async def health_check(self) -> LLMHealthResponse:
        """预留 Provider 当前不做真实连通性检查，避免误报可用。"""

        return LLMHealthResponse(
            provider=self.provider_name,
            model=self.model,
            reachable=False,
            error="ServerProvider is reserved for future server LLM integration",
        )
