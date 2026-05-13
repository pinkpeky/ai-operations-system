"""OpenClaw provider base interface for customer-machine workers."""

from __future__ import annotations

from abc import ABC, abstractmethod

from worker_client.openclaw.schemas import (
    OpenClawActionRequest,
    OpenClawActionResponse,
    OpenClawCapabilitiesResponse,
    OpenClawHealthResponse,
)


class BaseOpenClawProvider(ABC):
    """OpenClaw 执行器统一接口。

    真实 OpenClaw 尚未接入；该接口只为后续替换 provider 预留稳定协议。
    """

    provider_name = "base"
    mock = False

    @abstractmethod
    async def health_check(self) -> OpenClawHealthResponse:
        """检查 provider 是否可用。"""

    @abstractmethod
    async def execute_action(self, request: OpenClawActionRequest) -> OpenClawActionResponse:
        """执行一个 OpenClaw action。"""

    @abstractmethod
    async def list_capabilities(self) -> OpenClawCapabilitiesResponse:
        """返回 provider 能力声明。"""

    @abstractmethod
    async def get_version(self) -> str:
        """返回 provider 版本。"""
