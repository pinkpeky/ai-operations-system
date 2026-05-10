"""LLM Client Layer 入口模块。

该模块负责选择 Provider、渲染 Prompt 并执行生成调用；它不参与 Scheduler 的任务扫描、入队或状态流转。
"""

import logging

from app.agents.providers.base import BaseLLMProvider
from app.agents.providers.local_provider import LocalProvider
from app.agents.providers.mock_provider import MockProvider
from app.agents.providers.server_provider import ServerProvider
from app.core.config import Settings, get_settings
from app.schemas.llm import LLMHealthResponse, LLMRequest, LLMResponse
from app.services.prompt_manager import PromptManager

logger = logging.getLogger(__name__)


class LLMClient:
    """统一 LLM 客户端。"""

    def __init__(
        self,
        settings: Settings | None = None,
        provider: BaseLLMProvider | None = None,
        prompt_manager: PromptManager | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.prompt_manager = prompt_manager or PromptManager()
        self.provider = provider or self._create_provider(self.settings)

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """执行一次 LLM 调用。"""

        try:
            prompt = self.prompt_manager.build_prompt(
                system_prompt=request.system_prompt,
                user_prompt=request.user_prompt,
                template=request.template,
                variables=request.variables,
            )
            logger.info(
                "LLM generation started",
                extra={"provider": self.provider.provider_name, "model": self.provider.model},
            )
            response = await self.provider.generate(request=request, prompt=prompt)
            logger.info(
                "LLM generation completed",
                extra={"provider": response.provider, "model": response.model},
            )
            return response
        except ValueError:
            logger.exception("LLM request validation failed")
            raise
        except NotImplementedError as exc:
            logger.exception("LLM provider is not implemented")
            raise RuntimeError(str(exc)) from exc
        except Exception as exc:
            logger.exception("LLM generation failed")
            raise RuntimeError(str(exc) or "LLM generation failed") from exc

    async def health_check(self) -> LLMHealthResponse:
        """检查当前 Provider 健康状态。"""

        try:
            return await self.provider.health_check()
        except Exception as exc:
            logger.exception("LLM health check failed")
            return LLMHealthResponse(
                provider=self.provider.provider_name,
                model=self.provider.model,
                reachable=False,
                error=str(exc),
            )

    def _create_provider(self, settings: Settings) -> BaseLLMProvider:
        """根据配置创建 Provider。"""

        provider_name = settings.llm_provider.strip().lower()
        try:
            if provider_name == "mock":
                return MockProvider()
            if provider_name == "local":
                return LocalProvider(
                    base_url=settings.local_llm_base_url,
                    model=settings.local_llm_model,
                    timeout_seconds=settings.llm_timeout_seconds,
                )
            if provider_name == "server":
                return ServerProvider(
                    base_url=settings.server_llm_base_url,
                    model=settings.server_llm_model,
                    timeout_seconds=settings.llm_timeout_seconds,
                )
            raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")
        except ValueError:
            logger.exception("Invalid LLM provider configuration")
            raise
        except Exception as exc:
            logger.exception("Failed to create LLM provider", extra={"provider": provider_name})
            raise RuntimeError("Failed to create LLM provider") from exc
