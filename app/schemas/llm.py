"""LLM 接口数据模型模块。

该模块定义 LLM Client Layer 对外暴露的请求、响应和健康检查结构。
"""

from typing import Any, Self

from pydantic import BaseModel, Field, model_validator


class LLMRequest(BaseModel):
    """LLM 调用请求。"""

    system_prompt: str | None = Field(default=None, description="系统提示词")
    user_prompt: str = Field(default="", description="用户提示词")
    template: str | None = Field(default=None, description="可选 Prompt 模板，使用 Python format 语法")
    variables: dict[str, Any] = Field(default_factory=dict, description="模板渲染变量")
    temperature: float | None = Field(default=None, ge=0, le=2, description="采样温度预留字段")
    max_tokens: int | None = Field(default=None, ge=1, le=65536, description="最大输出 token 预留字段")

    @model_validator(mode="after")
    def validate_prompt_source(self) -> Self:
        """确保请求至少包含用户提示词或模板。"""

        has_user_prompt = bool(self.user_prompt.strip())
        has_template = bool(self.template and self.template.strip())
        if not has_user_prompt and not has_template:
            raise ValueError("user_prompt or template is required")
        return self


class LLMResponse(BaseModel):
    """LLM 调用响应。"""

    provider: str = Field(description="实际使用的 Provider 名称")
    model: str = Field(description="实际使用的模型名称")
    content: str = Field(description="模型输出内容")
    usage: dict[str, int] = Field(default_factory=dict, description="用量统计预留字段")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Provider 附加元信息")


class LLMHealthResponse(BaseModel):
    """LLM Provider 健康检查响应。"""

    provider: str
    model: str
    reachable: bool
    error: str | None = None


class LLMResourcePlanRequest(BaseModel):
    """Plan GPU admission for one LLM conversation request."""

    task_type: str = Field(default="planning_chat", max_length=64)
    client_id: str | None = Field(default=None, max_length=128)
    priority: str = Field(default="normal", max_length=32)
    expected_tokens: int | None = Field(default=None, ge=1, le=262144)
    allow_queue: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)


class LLMResourcePlanResponse(BaseModel):
    """GPU and concurrency plan for one LLM request."""

    success: bool = True
    provider: str
    model: str
    workspace_id: str | None = None
    strategy_enabled: bool = True
    mode: str
    admission_status: str
    should_run_now: bool
    recommended_gpu_indexes: list[int] = Field(default_factory=list)
    cuda_visible_devices: str | None = None
    max_concurrent_llm_requests: int
    comfyui_active: bool = False
    comfyui_busy_gpu_indexes: list[int] = Field(default_factory=list)
    available_gpu_indexes: list[int] = Field(default_factory=list)
    ollama_options: dict[str, Any] = Field(default_factory=dict)
    runtime_notes: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)
    comfyui_resource_plan: dict[str, Any] = Field(default_factory=dict)
