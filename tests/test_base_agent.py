"""BaseAgent 测试模块。

验证中央 Agent 基类的标准执行流程和错误处理。
"""

from typing import Any

import pytest

from app.agents.base_agent import BaseAgent
from app.schemas.llm import LLMRequest, LLMResponse


class FakeLLMClient:
    """Agent 测试用 LLM Client 替身。"""

    def __init__(self) -> None:
        self.last_request: LLMRequest | None = None

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """返回固定 LLM 响应。"""

        self.last_request = request
        return LLMResponse(provider="mock", model="mock-llm", content="fake raw response")


class DemoAgent(BaseAgent):
    """BaseAgent 测试用示例 Agent。"""

    agent_name = "DemoAgent"
    agent_type = "demo"

    def validate_input(self, agent_input: dict[str, Any]) -> dict[str, Any]:
        """校验输入。"""

        if "value" not in agent_input:
            raise ValueError("value is required")
        return {"value": str(agent_input["value"])}

    def build_prompt(self, validated_input: dict[str, Any]) -> str:
        """构建 Prompt。"""

        return f"Value: {validated_input['value']}"

    def format_output(self, validated_input: dict[str, Any], llm_response: LLMResponse) -> dict[str, Any]:
        """格式化输出。"""

        return {
            "value": validated_input["value"],
            "raw_response": llm_response.content,
        }


@pytest.mark.asyncio
async def test_base_agent_runs_standard_flow() -> None:
    """BaseAgent 应按 validate -> prompt -> llm -> format 顺序执行。"""

    llm_client = FakeLLMClient()
    agent = DemoAgent(llm_client=llm_client)

    output = await agent.run({"value": "hello"})

    assert output["value"] == "hello"
    assert output["raw_response"] == "fake raw response"
    assert llm_client.last_request is not None
    assert llm_client.last_request.user_prompt == "Value: hello"


@pytest.mark.asyncio
async def test_base_agent_raises_validation_error() -> None:
    """输入不合法时应抛出 ValueError。"""

    agent = DemoAgent(llm_client=FakeLLMClient())

    with pytest.raises(ValueError, match="value is required"):
        await agent.run({})
