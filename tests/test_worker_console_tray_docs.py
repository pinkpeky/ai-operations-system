from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_phase32_docs_cover_tray_runtime_scope() -> None:
    docs = [
        ROOT / "docs/PROJECT_OVERVIEW.md",
        ROOT / "docs/CURRENT_RUNTIME.md",
        ROOT / "docs/zh/WORKER_CONSOLE.md",
        ROOT / "docs/en/WORKER_CONSOLE.md",
    ]

    for path in docs:
        text = path.read_text(encoding="utf-8")
        assert "Phase 32" in text, path
        assert "Worker Console System Tray & Desktop Runtime Foundation" in text, path
        assert "System Tray" in text, path
        assert "Minimize To Tray" in text, path
        assert "Tray Runtime Control" in text, path
        assert "Desktop Status Sync" in text, path
        assert "AutoStart Placeholder" in text, path
        assert "no formal installer" in text or "没有正式 installer" in text, path
        assert "no auto-update" in text or "没有自动更新" in text, path


def test_autostart_docs_are_placeholders_only() -> None:
    docs = [
        ROOT / "worker_console_desktop/autostart/README.md",
        ROOT / "worker_console_desktop/autostart/windows_registry_placeholder.md",
        ROOT / "worker_console_desktop/autostart/mac_launch_agent_placeholder.md",
    ]

    for path in docs:
        text = path.read_text(encoding="utf-8")
        assert "Placeholder" in text
        assert "not implemented" in text or "does not" in text
