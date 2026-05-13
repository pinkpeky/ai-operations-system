"""截图清理服务。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from pathlib import Path

from app.core.config import Settings, get_settings

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class ScreenshotCleanupResult:
    """结构化截图清理结果。"""

    workspace_id: str
    root_dir: str
    older_than_days: int
    dry_run: bool
    matched_files: int
    deleted_files: int
    bytes_freed: int


class ScreenshotCleanupService:
    """按 workspace 与文件年龄手动清理截图。"""

    def __init__(self, *, settings: Settings | None = None, roots: list[Path] | None = None) -> None:
        self.settings = settings or get_settings()
        self.roots = roots or [Path(self.settings.browser_screenshot_dir), Path("worker/screenshots")]

    def cleanup(
        self,
        *,
        workspace_id: str,
        older_than_days: int | None = None,
        dry_run: bool = True,
    ) -> ScreenshotCleanupResult:
        """清理单个 workspace 的截图；默认 dry-run，避免误删。"""

        days = older_than_days or self.settings.screenshot_retention_days
        cutoff = datetime.now() - timedelta(days=days)
        matched_files = 0
        deleted_files = 0
        bytes_freed = 0
        root_labels: list[str] = []

        for root in self.roots:
            workspace_dir = (root / workspace_id).resolve()
            root_labels.append(str(root))
            if not workspace_dir.exists():
                continue
            for file_path in workspace_dir.rglob("*.png"):
                try:
                    if not file_path.is_file():
                        continue
                    stat = file_path.stat()
                    if datetime.fromtimestamp(stat.st_mtime) >= cutoff:
                        continue
                    matched_files += 1
                    bytes_freed += stat.st_size
                    if not dry_run:
                        file_path.unlink()
                        deleted_files += 1
                except Exception as exc:
                    logger.warning("Screenshot cleanup skipped file", extra={"path": str(file_path), "error": str(exc)})

        logger.info(
            "Screenshot cleanup completed",
            extra={
                "workspace_id": workspace_id,
                "older_than_days": days,
                "dry_run": dry_run,
                "matched_files": matched_files,
                "deleted_files": deleted_files,
            },
        )
        return ScreenshotCleanupResult(
            workspace_id=workspace_id,
            root_dir=";".join(root_labels),
            older_than_days=days,
            dry_run=dry_run,
            matched_files=matched_files,
            deleted_files=deleted_files,
            bytes_freed=bytes_freed if not dry_run else 0,
        )
