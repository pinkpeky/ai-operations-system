"""LLM Provider 抽象基类模块。

Provider 层只描述模型调用能力，任务扫描、入队和状态流转仍由 Scheduler 独立负责。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ClassVar

from app.schemas.llm import LLMHealthResponse, LLMRequest, LLMResponse


@dataclass(frozen=True, slots=True)
class LLMPrompt:
    """渲染后的 Prompt 结构。"""

    system_prompt: str | None
    user_prompt: str
    full_prompt: str


class BaseLLMProvider(ABC):
    """LLM Provider 基类。"""

    provider_name: ClassVar[str] = "base"

    def __init__(self, model: str) -> None:
        self.model = model

    @abstractmethod
    async def generate(self, request: LLMRequest, prompt: LLMPrompt) -> LLMResponse:
        """执行一次 LLM 生成。"""

    async def health_check(self) -> LLMHealthResponse:
        """检查 Provider 是否可用。"""

        return LLMHealthResponse(
            provider=self.provider_name,
            model=self.model,
            reachable=True,
            error=None,
        )
