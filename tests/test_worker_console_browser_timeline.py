"""Worker Console browser timeline file coverage tests."""

from pathlib import Path


def test_worker_console_contains_browser_timeline_panel() -> None:
    """Web and desktop consoles should expose timeline/snapshot/replay controls."""

    web_main = Path("worker_console/src/main.tsx").read_text(encoding="utf-8")
    desktop_main = Path("worker_console_desktop/src/main.tsx").read_text(encoding="utf-8")
    web_client = Path("worker_console/src/api/browserRuntimeClient.ts").read_text(encoding="utf-8")
    desktop_client = Path("worker_console_desktop/src/api/browserRuntimeClient.ts").read_text(encoding="utf-8")

    for content in (web_main, desktop_main):
        assert "Timeline" in content
        assert "Snapshots" in content
        assert "Replay metadata" in content
        assert "metadata-only" in content
        assert "refreshTimeline" in content

    for content in (web_client, desktop_client):
        assert "/events?limit=200" in content
        assert "/snapshots?limit=200" in content
        assert "/replay" in content
        assert "exportReplay" in content
