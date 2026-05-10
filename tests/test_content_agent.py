"""ContentAgent 测试模块。

验证内容生成 Agent 的输入校验、Prompt 构建和输出结构。
"""

import pytest

from app.agents.content_agent import ContentAgent
from app.schemas.llm import LLMRequest, LLMResponse


class FakeLLMClient:
    """ContentAgent 测试用 LLM Client 替身。"""

    def __init__(self) -> None:
        self.last_request: LLMRequest | None = None

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """返回固定内容。"""

        self.last_request = request
        return LLMResponse(provider="mock", model="mock-llm", content="mock content body")


@pytest.mark.asyncio
async def test_content_agent_generates_structured_output() -> None:
    """ContentAgent 应返回 title、description、tags、cta、raw_response。"""

    llm_client = FakeLLMClient()
    agent = ContentAgent(llm_client=llm_client)

    output = await agent.run(
        {
            "topic": "AI 自动化运营",
            "platform": "tiktok",
            "style": "专业简洁",
        }
    )

    assert output["title"] == "AI 自动化运营 | tiktok 内容方案"
    assert "mock content body" in output["description"]
    assert output["tags"] == ["AI自动化运营", "tiktok", "专业简洁"]
    assert output["cta"] == "关注我们，获取更多关于AI 自动化运营的自动化运营实践。"
    assert output["raw_response"] == "mock content body"
    assert llm_client.last_request is not None
    assert "AI 自动化运营" in llm_client.last_request.user_prompt
    assert llm_client.last_request.system_prompt is not None


@pytest.mark.asyncio
async def test_content_agent_rejects_invalid_input() -> None:
    """ContentAgent 缺少必填字段时应报错。"""

    agent = ContentAgent(llm_client=FakeLLMClient())

    with pytest.raises(ValueError):
        await agent.run({"topic": "AI 自动化运营"})
