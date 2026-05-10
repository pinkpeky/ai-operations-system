"""任务 Handler 基础模块。

Handler 只负责执行具体 task_type 的业务逻辑，不直接管理 Redis Queue 和任务状态流转。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, ClassVar


@dataclass(frozen=True, slots=True)
class TaskExecutionResult:
    """标准任务执行结果。"""

    success: bool
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


class BaseTaskHandler(ABC):
    """任务 Handler 基类。"""

    task_type: ClassVar[str]

    @abstractmethod
    async def handle(self, payload: dict[str, Any]) -> TaskExecutionResult:
        """执行任务并返回标准结果。"""
