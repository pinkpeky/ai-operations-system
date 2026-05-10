"""中央 Agent 数据模型模块。

该模块定义通用 Agent 请求/响应，以及 ContentAgent 的输入输出结构。
"""

from typing import Any

from pydantic import BaseModel, Field


class AgentRequest(BaseModel):
    """通用 Agent 请求。"""

    agent_type: str = Field(min_length=1, max_length=64, description="Agent 类型")
    input: dict[str, Any] = Field(default_factory=dict, description="Agent 输入")


class AgentResponse(BaseModel):
    """通用 Agent 响应。"""

    agent_name: str
    agent_type: str
    output: dict[str, Any]
    raw_response: str


class ContentAgentRequest(BaseModel):
    """内容生成 Agent 请求。"""

    topic: str = Field(min_length=1, max_length=255, description="内容主题")
    platform: str = Field(min_length=1, max_length=64, description="发布平台")
    style: str = Field(min_length=1, max_length=128, description="内容风格")


class ContentAgentResponse(BaseModel):
    """内容生成 Agent 响应。"""

    title: str
    description: str
    tags: list[str]
    cta: str
    raw_response: str
