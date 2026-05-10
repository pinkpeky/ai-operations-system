"""LocalProvider 测试模块。

使用 fake HTTP client 验证 Ollama /api/generate 和 /api/tags 兼容性，不依赖真实 Ollama。
"""

import pytest

from app.agents.providers.base import LLMPrompt
from app.agents.providers.local_provider import LocalProvider
from app.schemas.llm import LLMRequest


class FakeResponse:
    """最小 HTTP 响应替身。"""

    def __init__(self, data: dict, status_error: Exception | None = None) -> None:
        self.data = data
        self.status_error = status_error

    def raise_for_status(self) -> None:
        """模拟 httpx raise_for_status。"""

        if self.status_error is not None:
            raise self.status_error

    def json(self) -> dict:
        """返回 JSON 数据。"""

        return self.data


class FakeHTTPClient:
    """最小异步 HTTP client 替身。"""

    def __init__(self) -> None:
        self.post_url: str | None = None
        self.post_payload: dict | None = None
        self.get_url: str | None = None

    async def post(self, url: str, json: dict) -> FakeResponse:
        """模拟 Ollama /api/generate。"""

        self.post_url = url
        self.post_payload = json
        return FakeResponse(
            {
                "response": "Ollama fake response",
                "done": True,
                "prompt_eval_count": 12,
                "eval_count": 8,
                "total_duration": 100,
            }
        )

    async def get(self, url: str) -> FakeResponse:
        """模拟 Ollama /api/tags。"""

        self.get_url = url
        return FakeResponse(
            {
                "models": [
                    {"name": "mistral:latest"},
                ]
            }
        )


@pytest.mark.asyncio
async def test_local_provider_calls_ollama_generate() -> None:
    """LocalProvider 应调用 Ollama /api/generate 非流式接口。"""

    http_client = FakeHTTPClient()
    provider = LocalProvider(
        base_url="http://localhost:11434/",
        model="mistral",
        timeout_seconds=120,
        http_client=http_client,
    )

    response = await provider.generate(
        request=LLMRequest(user_prompt="hello", temperature=0.2, max_tokens=32),
        prompt=LLMPrompt(system_prompt=None, user_prompt="hello", full_prompt="hello"),
    )

    assert response.provider == "local"
    assert response.model == "mistral"
    assert response.content == "Ollama fake response"
    assert response.usage["prompt_tokens"] == 12
    assert response.usage["completion_tokens"] == 8
    assert http_client.post_url == "http://localhost:11434/api/generate"
    assert http_client.post_payload == {
        "model": "mistral",
        "prompt": "hello",
        "stream": False,
        "options": {
            "temperature": 0.2,
            "num_predict": 32,
        },
    }


@pytest.mark.asyncio
async def test_local_provider_health_check_finds_model_alias() -> None:
    """health check 应能识别 mistral:latest 对应 mistral。"""

    http_client = FakeHTTPClient()
    provider = LocalProvider(
        base_url="http://localhost:11434",
        model="mistral",
        timeout_seconds=120,
        http_client=http_client,
    )

    health = await provider.health_check()

    assert health.provider == "local"
    assert health.model == "mistral"
    assert health.reachable is True
    assert health.error is None
    assert http_client.get_url == "http://localhost:11434/api/tags"


@pytest.mark.asyncio
async def test_local_provider_health_check_reports_missing_model() -> None:
    """health check 找不到模型时应返回清晰错误，不抛出导致系统崩溃。"""

    class MissingModelHTTPClient(FakeHTTPClient):
        async def get(self, url: str) -> FakeResponse:
            return FakeResponse({"models": [{"name": "llama3:latest"}]})

    provider = LocalProvider(
        base_url="http://localhost:11434",
        model="mistral",
        timeout_seconds=120,
        http_client=MissingModelHTTPClient(),
    )

    health = await provider.health_check()

    assert health.reachable is False
    assert health.error == "Model not found in Ollama tags: mistral"


@pytest.mark.asyncio
async def test_local_provider_health_check_handles_connection_error() -> None:
    """health check 连接失败时应返回不可达状态，系统不能崩溃。"""

    class FailingHTTPClient(FakeHTTPClient):
        async def get(self, url: str) -> FakeResponse:
            raise RuntimeError("connection refused")

    provider = LocalProvider(
        base_url="http://localhost:11434",
        model="mistral",
        timeout_seconds=120,
        http_client=FailingHTTPClient(),
    )

    health = await provider.health_check()

    assert health.provider == "local"
    assert health.model == "mistral"
    assert health.reachable is False
    assert health.error == "connection refused"
