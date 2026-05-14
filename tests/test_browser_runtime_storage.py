"""Browser runtime screenshot storage tests."""

from __future__ import annotations

import base64
from uuid import uuid4

from app.browser.providers.remote_provider import RemoteBrowserProvider


def test_browser_runtime_screenshot_storage(tmp_path) -> None:
    provider = RemoteBrowserProvider.__new__(RemoteBrowserProvider)
    provider.screenshot_root = tmp_path

    screenshot_path = provider._store_screenshot(  # type: ignore[attr-defined]
        workspace_id="workspace/storage",
        runtime_session_id=uuid4(),
        screenshot_base64=base64.b64encode(b"\x89PNG\r\n\x1a\n").decode("ascii"),
        screenshot_name="phase34",
    )

    assert screenshot_path.exists()
    assert screenshot_path.read_bytes().startswith(b"\x89PNG")
    assert str(screenshot_path).startswith(str(tmp_path.resolve()))
