"""openclaw_tool tests."""

import pytest

from app.browser.remote.services.browser_worker_repository import BrowserWorkerRepository
from app.openclaw.client import OpenClawWorkerClientResult
from app.tools.base import ToolExecutionContext
from app.tools.builtin.openclaw_tool import OpenClawTool


class FakeOpenClawWorkerClient:
    """测试用 OpenClaw client。"""

    def __init__(self, **_: object) -> None:
        pass

    async def health_check(self) -> OpenClawWorkerClientResult:
        return OpenClawWorkerClientResult(success=True, message="ok", data={"success": True, "provider": "mock", "enabled": True, "reachable": True, "mock": True})

    async def capabilities(self) -> OpenClawWorkerClientResult:
        return OpenClawWorkerClientResult(success=True, message="ok", data={"success": True, "provider": "mock", "mock": True, "capabilities": {"openclaw": True}, "actions": ["execute_action"]})

    async def execute_action(self, *, payload: dict[str, object]) -> OpenClawWorkerClientResult:
        return OpenClawWorkerClientResult(
            success=True,
            message="ok",
            data={
                "success": True,
                "action_type": payload["action_type"],
                "output_payload": {"real_openclaw_called": False, "target": payload.get("target")},
                "duration_ms": 1,
                "provider": "mock",
                "mock": True,
            },
        )


@pytest.mark.asyncio
async def test_openclaw_tool_execute_action(session, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """openclaw_tool 应通过已注册 worker 调用 mock OpenClaw，并写入日志。"""

    from app.openclaw import service as service_module

    monkeypatch.setattr(service_module, "OpenClawWorkerClient", FakeOpenClawWorkerClient)
    worker = await BrowserWorkerRepository(session).register_worker(
        workspace_id="workspace-openclaw-tool",
        worker_name="worker-openclaw",
        worker_type="playwright",
        base_url="http://worker",
        capabilities={"openclaw": True, "browser": "chromium"},
        metadata={},
    )
    await session.commit()

    output = await OpenClawTool().execute(
        OpenClawTool().validate_input(
            {
                "action_type": "execute_action",
                "worker_id": str(worker.id),
                "openclaw_action_type": "mock_inspect",
                "target": "https://example.com",
            }
        ),
        ToolExecutionContext(workspace_id="workspace-openclaw-tool", session=session),
    )

    assert output.success is True
    assert output.worker_id == str(worker.id)
    assert output.result["mock"] is True
