"""本地 LLM Provider 模块。

该 Provider 兼容 Ollama API，使用 /api/generate 非流式接口调用本地模型。
"""

import logging
from typing import Any, Protocol

import httpx

from app.agents.providers.base import BaseLLMProvider, LLMPrompt
from app.schemas.llm import LLMHealthResponse, LLMRequest, LLMResponse

logger = logging.getLogger(__name__)


class AsyncHTTPClient(Protocol):
    """LocalProvider 依赖的最小异步 HTTP Client 协议，便于单元测试替换。"""

    async def get(self, url: str) -> Any:
        """发送 GET 请求。"""

    async def post(self, url: str, json: dict[str, Any]) -> Any:
        """发送 POST 请求。"""


class LocalProvider(BaseLLMProvider):
    """Ollama 本地模型服务 Provider。"""

    provider_name = "local"

    def __init__(
        self,
        base_url: str,
        model: str,
        timeout_seconds: float,
        num_ctx: int | None = None,
        http_client: AsyncHTTPClient | None = None,
    ) -> None:
        super().__init__(model=model)
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.num_ctx = num_ctx
        self._http_client = http_client

    async def generate(self, request: LLMRequest, prompt: LLMPrompt) -> LLMResponse:
        """调用 Ollama /api/generate 生成文本。"""

        try:
            payload: dict[str, Any] = {
                "model": self.model,
                "prompt": prompt.full_prompt,
                "stream": False,
            }
            options: dict[str, Any] = {}
            if request.temperature is not None:
                options["temperature"] = request.temperature
            if request.max_tokens is not None:
                options["num_predict"] = request.max_tokens
            if self.num_ctx is not None:
                options["num_ctx"] = self.num_ctx
            runtime_options = request.variables.get("ollama_options") if isinstance(request.variables, dict) else None
            if isinstance(runtime_options, dict):
                for key in ("num_gpu", "main_gpu", "num_thread", "num_batch"):
                    value = runtime_options.get(key)
                    if isinstance(value, int):
                        options[key] = value
            if options:
                payload["options"] = options

            data = await self._post_json("/api/generate", payload)
            content = str(data.get("response") or "")
            if not content:
                raise RuntimeError("Ollama response is empty")

            logger.info("Local Ollama response generated", extra={"provider": self.provider_name, "model": self.model})
            return LLMResponse(
                provider=self.provider_name,
                model=self.model,
                content=content,
                usage={
                    "prompt_tokens": int(data.get("prompt_eval_count") or 0),
                    "completion_tokens": int(data.get("eval_count") or 0),
                },
                metadata={
                    "base_url": self.base_url,
                    "done": data.get("done"),
                    "total_duration": data.get("total_duration"),
                    "runtime_options": {
                        key: options[key]
                        for key in ("num_gpu", "main_gpu", "num_thread", "num_batch")
                        if key in options
                    },
                },
            )
        except Exception as exc:
            logger.exception("Local Ollama provider failed")
            raise RuntimeError(f"Local Ollama provider failed: {exc}") from exc

    async def health_check(self) -> LLMHealthResponse:
        """通过 Ollama /api/tags 检查服务和模型是否可用。"""

        try:
            data = await self._get_json("/api/tags")
            models = data.get("models") or []
            model_names = {str(item.get("name", "")) for item in models}
            model_aliases = {name.split(":")[0] for name in model_names}
            reachable = self.model in model_names or self.model in model_aliases
            return LLMHealthResponse(
                provider=self.provider_name,
                model=self.model,
                reachable=reachable,
                error=None if reachable else f"Model not found in Ollama tags: {self.model}",
            )
        except Exception as exc:
            logger.warning("Local Ollama health check failed", extra={"error": str(exc)})
            return LLMHealthResponse(
                provider=self.provider_name,
                model=self.model,
                reachable=False,
                error=str(exc),
            )

    async def _get_json(self, path: str) -> dict[str, Any]:
        """发送 GET 请求并解析 JSON。"""

        response = await self._request("GET", path)
        return self._response_json(response)

    async def _post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        """发送 POST 请求并解析 JSON。"""

        response = await self._request("POST", path, payload)
        return self._response_json(response)

    async def _request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
        """发送 HTTP 请求，支持注入测试 client。"""

        url = f"{self.base_url}{path}"
        if self._http_client is not None:
            if method == "GET":
                return await self._http_client.get(url)
            return await self._http_client.post(url, json=payload or {})

        timeout = httpx.Timeout(self.timeout_seconds)
        async with httpx.AsyncClient(timeout=timeout, trust_env=False) as client:
            if method == "GET":
                return await client.get(url)
            return await client.post(url, json=payload or {})

    def _response_json(self, response: Any) -> dict[str, Any]:
        """统一处理 HTTP 响应。"""

        if hasattr(response, "raise_for_status"):
            response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict):
            raise RuntimeError("Ollama response JSON must be an object")
        return data
