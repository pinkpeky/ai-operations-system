"""LLM Client 测试模块。

验证默认 Mock Provider 链路，不依赖真实模型服务。
"""

import pytest

from app.agents.llm_client import LLMClient
from app.agents.providers.mock_provider import MockProvider
from app.schemas.llm import LLMRequest


@pytest.mark.asyncio
async def test_llm_client_mock_provider_returns_fixed_content() -> None:
    """MockProvider 应返回固定测试内容。"""

    client = LLMClient(provider=MockProvider())
    request = LLMRequest(
        system_prompt="你是一个测试助手。",
        user_prompt="ping",
    )

    response = await client.generate(request)

    assert response.provider == "mock"
    assert response.model == "mock-llm"
    assert response.content == "MockProvider 测试响应：LLM Client Layer 已就绪。"
    assert response.metadata["mock"] is True
    assert response.metadata["has_system_prompt"] is True
    assert response.usage["prompt_chars"] > 0


@pytest.mark.asyncio
async def test_llm_client_renders_template_before_provider_call() -> None:
    """LLMClient 应先渲染模板再交给 Provider。"""

    client = LLMClient(provider=MockProvider())
    request = LLMRequest(
        user_prompt="内容运营",
        template="请为 {topic} 生成摘要，主题：{user_prompt}",
        variables={"topic": "AI 工具"},
    )

    response = await client.generate(request)

    assert response.provider == "mock"
    assert response.usage["prompt_chars"] == len("请为 AI 工具 生成摘要，主题：内容运营")
