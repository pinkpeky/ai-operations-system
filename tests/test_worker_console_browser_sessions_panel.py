"""Worker Console Browser Sessions panel file tests."""

from pathlib import Path


def test_worker_console_browser_sessions_panel_exists() -> None:
    web_main = Path("worker_console/src/main.tsx").read_text(encoding="utf-8")
    desktop_main = Path("worker_console_desktop/src/main.tsx").read_text(encoding="utf-8")

    assert "BrowserSessionsPanel" in web_main
    assert "BrowserSessionsPanel" in desktop_main
    assert "browserRuntimeClient" in web_main
    assert "browserRuntimeClient" in desktop_main
