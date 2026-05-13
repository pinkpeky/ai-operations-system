"""Screenshot cleanup service tests."""

import os
import time
from pathlib import Path

from app.browser.services.screenshot_cleanup_service import ScreenshotCleanupService
from app.core.config import Settings


def test_screenshot_cleanup_supports_dry_run_and_delete(tmp_path: Path) -> None:
    """截图清理默认可预览，确认执行后才删除文件。"""

    workspace_id = "workspace-screenshot-cleanup"
    screenshot_root = tmp_path / "screenshots"
    screenshot_file = screenshot_root / workspace_id / "session-1" / "old.png"
    screenshot_file.parent.mkdir(parents=True)
    screenshot_file.write_bytes(b"old screenshot")

    old_timestamp = time.time() - 9 * 24 * 60 * 60
    os.utime(screenshot_file, (old_timestamp, old_timestamp))

    service = ScreenshotCleanupService(
        settings=Settings(SCREENSHOT_RETENTION_DAYS=7),
        roots=[screenshot_root],
    )

    dry_run_result = service.cleanup(workspace_id=workspace_id, dry_run=True)

    assert dry_run_result.matched_files == 1
    assert dry_run_result.deleted_files == 0
    assert screenshot_file.exists()

    delete_result = service.cleanup(workspace_id=workspace_id, dry_run=False)

    assert delete_result.matched_files == 1
    assert delete_result.deleted_files == 1
    assert delete_result.bytes_freed == len(b"old screenshot")
    assert not screenshot_file.exists()


def test_screenshot_cleanup_respects_workspace_boundary(tmp_path: Path) -> None:
    """清理时只能影响当前 workspace 目录。"""

    screenshot_root = tmp_path / "screenshots"
    target_file = screenshot_root / "workspace-a" / "session-1" / "old.png"
    other_file = screenshot_root / "workspace-b" / "session-1" / "old.png"
    target_file.parent.mkdir(parents=True)
    other_file.parent.mkdir(parents=True)
    target_file.write_bytes(b"a")
    other_file.write_bytes(b"b")

    old_timestamp = time.time() - 9 * 24 * 60 * 60
    os.utime(target_file, (old_timestamp, old_timestamp))
    os.utime(other_file, (old_timestamp, old_timestamp))

    service = ScreenshotCleanupService(
        settings=Settings(SCREENSHOT_RETENTION_DAYS=7),
        roots=[screenshot_root],
    )

    result = service.cleanup(workspace_id="workspace-a", dry_run=False)

    assert result.deleted_files == 1
    assert not target_file.exists()
    assert other_file.exists()
