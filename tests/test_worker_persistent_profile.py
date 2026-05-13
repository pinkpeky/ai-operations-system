"""Worker persistent profile runtime tests."""

from pathlib import Path

import pytest

from worker.browser_worker.config import WorkerSettings
from worker.browser_worker.playwright_runtime import PlaywrightBrowserWorkerRuntime


@pytest.mark.asyncio
async def test_worker_uses_persistent_context_when_profile_requested(fake_playwright, tmp_path: Path) -> None:  # type: ignore[no-untyped-def]
    """指定 profile_id 时 worker 应使用 launch_persistent_context。"""

    settings = WorkerSettings(
        WORKER_SCREENSHOT_DIR=str(tmp_path / "screenshots"),
        WORKER_PROFILE_DIR=str(tmp_path / "profiles"),
    )
    runtime = PlaywrightBrowserWorkerRuntime(settings=settings)

    session_result = await runtime.create_session(
        workspace_id="workspace-worker-profile",
        local_browser_session_id="local-session-profile",
        metadata={"source": "unit-test"},
        profile_id="profile-001",
        profile_path=None,
        use_persistent_profile=True,
    )
    remote_session_id = str(session_result.remote_session_id)
    navigate = await runtime.execute_action(
        remote_session_id=remote_session_id,
        action_type="navigate",
        target="https://example.com",
        input_payload={},
    )
    closed = await runtime.close_session(remote_session_id=remote_session_id)

    expected_path = tmp_path / "profiles" / "workspace-worker-profile" / "profile-001"
    assert session_result.success is True
    assert session_result.data["persistent_context_enabled"] is True
    assert Path(str(session_result.data["profile_path"])) == expected_path.resolve()
    assert expected_path.exists()
    assert navigate.success is True
    assert closed.success is True
