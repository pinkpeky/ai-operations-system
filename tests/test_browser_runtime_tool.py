"""browser_tool Phase 34 runtime action tests."""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.providers.base import BrowserProviderResult
from app.browser.remote.services import BrowserWorkerService
from app.browser.services.browser_runtime_session_service import BrowserRuntimeSessionService
from app.tools.base import ToolExecutionContext
from app.tools.builtin.browser_tool import BrowserTool, BrowserToolInput


class FakeRuntimeProvider:
    provider_name = "remote"

    def __init__(self, worker_id: str) -> None:
        self.worker_id = worker_id

    async def create_session(self, **_: object) -> BrowserProviderResult:
        return BrowserProviderResult(
            success=True,
            message="created",
            data={"worker_id": self.worker_id, "worker_name": "tool-worker", "remote_session_id": "runtime-tool"},
        )

    async def navigate(self, **_: object) -> BrowserProviderResult:
        return BrowserProviderResult(success=True, message="navigated", data={"current_url": "https://example.com"})

    async def screenshot(self, **_: object) -> BrowserProviderResult:
        return BrowserProviderResult(success=True, message="shot", data={"screenshot_path": "storage/browser_screenshots/tool.png"})

    async def get_page(self, **_: object) -> BrowserProviderResult:
        return BrowserProviderResult(success=True, message="page", data={"content": "<h1>Example Domain</h1>"})

    async def close_session(self, **_: object) -> BrowserProviderResult:
        return BrowserProviderResult(success=True, message="closed", data={})


@pytest.mark.asyncio
async def test_browser_tool_can_create_runtime_session(session: AsyncSession) -> None:
    worker = await BrowserWorkerService(session).register_worker(
        workspace_id="workspace-runtime-tool",
        worker_name="tool-worker",
        worker_type="playwright",
        base_url="http://worker",
        capabilities={"browser_runtime": True, "browser": "chromium"},
        metadata={},
    )
    runtime_service = BrowserRuntimeSessionService(session, provider=FakeRuntimeProvider(str(worker.id)))  # type: ignore[arg-type]
    tool = BrowserTool()

    output = await tool._execute_runtime_action(
        request=BrowserToolInput(action_type="create_session"),
        context=ToolExecutionContext(workspace_id="workspace-runtime-tool", session=session),
        runtime_service=runtime_service,
    )

    assert output.success is True
    assert output.session["metadata"]["remote_session_id"] == "runtime-tool"
