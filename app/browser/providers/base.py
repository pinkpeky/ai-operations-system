"""Browser Provider 统一接口。

该接口提前约束未来真实浏览器适配器需要支持的动作。Phase 17 只接
MockBrowserProvider，不启动真实浏览器，也不执行平台自动化。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class BrowserProviderResult:
    """Provider 返回的标准结果。"""

    success: bool
    message: str
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    def model_dump(self) -> dict[str, Any]:
        """返回可 JSON 序列化的 provider payload。"""

        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "error": self.error,
        }


class BaseBrowserProvider(ABC):
    """统一浏览器 provider 协议。"""

    provider_name = "base"

    @abstractmethod
    async def create_session(self, *, metadata: dict[str, Any] | None = None) -> BrowserProviderResult:
        """创建 provider 侧 session。"""

    @abstractmethod
    async def close_session(self, *, provider_session_id: str | None = None) -> BrowserProviderResult:
        """关闭 provider 侧 session。"""

    @abstractmethod
    async def navigate(
        self,
        *,
        target: str | None,
        input_payload: dict[str, Any],
        session_metadata: dict[str, Any] | None = None,
    ) -> BrowserProviderResult:
        """导航到 URL 或路由。"""

    @abstractmethod
    async def click(
        self,
        *,
        target: str | None,
        input_payload: dict[str, Any],
        session_metadata: dict[str, Any] | None = None,
    ) -> BrowserProviderResult:
        """点击选择器或语义目标。"""

    @abstractmethod
    async def type_text(
        self,
        *,
        target: str | None,
        input_payload: dict[str, Any],
        session_metadata: dict[str, Any] | None = None,
    ) -> BrowserProviderResult:
        """向目标输入文本。"""

    @abstractmethod
    async def scroll(
        self,
        *,
        target: str | None,
        input_payload: dict[str, Any],
        session_metadata: dict[str, Any] | None = None,
    ) -> BrowserProviderResult:
        """滚动页面或容器。"""

    @abstractmethod
    async def screenshot(
        self,
        *,
        target: str | None,
        input_payload: dict[str, Any],
        session_metadata: dict[str, Any] | None = None,
    ) -> BrowserProviderResult:
        """截取截图占位结果或未来真实截图产物。"""

    @abstractmethod
    async def get_page_content(
        self,
        *,
        target: str | None,
        input_payload: dict[str, Any],
        session_metadata: dict[str, Any] | None = None,
    ) -> BrowserProviderResult:
        """返回当前页面内容。"""
