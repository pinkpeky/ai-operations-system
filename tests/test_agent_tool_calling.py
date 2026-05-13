"""Agent Tool Calling 测试。"""

from typing import Any

import pytest
from pydantic import BaseModel, Field

from app.agents.base_agent import BaseAgent
from app.schemas.llm import LLMRequest, LLMResponse
from app.tools.base import BaseTool, ToolExecutionContext
from app.tools.registry import ToolRegistry


class FakeLLMClient:
    """测试用 LLM Client。"""

    def __init__(self) -> None:
        self.last_request: LLMRequest | None = None

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """返回固定响应。"""

        self.last_request = request
        return LLMResponse(provider="mock", model="mock-llm", content="answer with tools")


class DemoInput(BaseModel):
    """Demo 工具输入。"""

    text: str = Field(min_length=1)


class DemoOutput(BaseModel):
    """Demo 工具输出。"""

    result: str


class DemoTool(BaseTool):
    """Agent 测试用工具。"""

    name = "demo_tool"
    description = "Demo tool"
    input_schema = DemoInput
    output_schema = DemoOutput

    async def execute(self, tool_input: BaseModel, context: ToolExecutionContext) -> BaseModel:
        """返回工具结果。"""

        request = DemoInput.model_validate(tool_input.model_dump())
        return DemoOutput(result=f"{context.workspace_id}:{request.text}")


class DemoAgent(BaseAgent):
    """测试用 Agent。"""

    agent_name = "DemoAgent"
    agent_type = "demo"

    def validate_input(self, agent_input: dict[str, Any]) -> dict[str, Any]:
        if "value" not in agent_input:
            raise ValueError("value is required")
        return {"value": str(agent_input["value"])}

    def build_prompt(self, validated_input: dict[str, Any]) -> str:
        return f"Value: {validated_input['value']}"

    def format_output(self, validated_input: dict[str, Any], llm_response: LLMResponse) -> dict[str, Any]:
        return {"raw_response": llm_response.content}


@pytest.mark.asyncio
async def test_agent_executes_manual_tool_call_before_llm() -> None:
    """Agent 应支持手动指定工具，并把工具结果附加到 prompt。"""

    registry = ToolRegistry()
    registry.register_tool(DemoTool())
    llm_client = FakeLLMClient()
    agent = DemoAgent(
        llm_client=llm_client,
        tool_registry=registry,
        available_tools=["demo_tool"],
    )

    output = await agent.run(
        {
            "value": "hello",
            "tool_context": ToolExecutionContext(workspace_id="workspace-a"),
            "tool_calls": [{"tool_name": "demo_tool", "tool_input": {"text": "search me"}}],
        }
    )

    assert output["raw_response"] == "answer with tools"
    assert output["tool_call_trace"][0]["tool_name"] == "demo_tool"
    assert output["tool_call_trace"][0]["tool_output"]["result"] == "workspace-a:search me"
    assert llm_client.last_request is not None
    assert "demo_tool" in llm_client.last_request.user_prompt
    assert "workspace-a:search me" in llm_client.last_request.user_prompt
