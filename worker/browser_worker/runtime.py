"""Browser Worker runtime 抽象接口。"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from worker.browser_worker.schemas import WorkerActionResponse, WorkerHumanControlResponse, WorkerSessionResponse


class BaseBrowserWorkerRuntime(ABC):
    """独立 Browser Worker runtime 统一接口。"""

    @abstractmethod
    async def create_session(
        self,
        *,
        workspace_id: str | None,
        local_browser_session_id: str | None,
        metadata: dict[str, Any],
        profile_id: str | None = None,
        profile_path: str | None = None,
        use_persistent_profile: bool = False,
    ) -> WorkerSessionResponse:
        """创建 worker 内部 browser session。"""

    @abstractmethod
    async def close_session(self, *, remote_session_id: str) -> WorkerSessionResponse:
        """关闭 worker 内部 browser session。"""

    @abstractmethod
    async def execute_action(
        self,
        *,
        remote_session_id: str,
        action_type: str,
        target: str | None,
        input_payload: dict[str, Any],
    ) -> WorkerActionResponse:
        """执行 worker browser action。"""

    @abstractmethod
    async def start_human_control(
        self,
        *,
        remote_session_id: str,
        control_session_id: str | None,
        payload: dict[str, Any],
    ) -> WorkerHumanControlResponse:
        """进入 metadata-level 人工接管状态。"""

    @abstractmethod
    async def complete_human_control(
        self,
        *,
        remote_session_id: str,
        control_session_id: str | None,
        note: str | None,
        payload: dict[str, Any],
    ) -> WorkerHumanControlResponse:
        """结束 metadata-level 人工接管状态。"""

    @abstractmethod
    async def get_human_control_status(self, *, remote_session_id: str) -> WorkerHumanControlResponse:
        """查询 metadata-level 人工接管状态。"""

    @abstractmethod
    async def close_all(self) -> None:
        """关闭所有 runtime session。"""
