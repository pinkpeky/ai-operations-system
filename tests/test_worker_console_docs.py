"""Worker Console docs tests."""

from __future__ import annotations

from pathlib import Path


def test_worker_console_docs_describe_scope_and_boundaries() -> None:
    """Phase 30 docs 必须明确当前只是 Web GUI Foundation。"""

    zh = Path("docs/zh/WORKER_CONSOLE.md").read_text(encoding="utf-8")
    en = Path("docs/en/WORKER_CONSOLE.md").read_text(encoding="utf-8")
    overview = Path("docs/PROJECT_OVERVIEW.md").read_text(encoding="utf-8")

    for text in (zh, en, overview):
        assert "Worker Console GUI Foundation" in text
        assert "worker_console" in text
        assert "VITE_LOCAL_WORKER_API" in text
        assert "http://127.0.0.1:9100" in text
        assert "no exe / dmg" in text or "no exe/dmg" in text
        assert "no system tray" in text
        assert "Tauri" in text
        assert "Electron" in text
