from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_worker_console_desktop_docs_are_present() -> None:
    """中英文 Worker Console 文档必须说明 Phase 31 桌面壳范围。"""

    docs = [
        ROOT / "docs/PROJECT_OVERVIEW.md",
        ROOT / "docs/CURRENT_RUNTIME.md",
        ROOT / "docs/zh/WORKER_CONSOLE.md",
        ROOT / "docs/en/WORKER_CONSOLE.md",
    ]

    for path in docs:
        text = path.read_text(encoding="utf-8")
        assert "Phase 31" in text, path
        assert "Worker Console Desktop App Foundation" in text, path
        assert "worker_console_desktop" in text, path
        assert "Tauri" in text, path
        assert "npm run tauri dev" in text, path
        assert "VITE_LOCAL_WORKER_API" in text, path
        assert "no exe / dmg" in text or "没有正式安装包" in text, path
        assert "no system tray" in text or "没有系统托盘" in text, path
        assert "no auto update" in text or "没有自动更新" in text, path


def test_desktop_readme_documents_manual_commands() -> None:
    readme = (ROOT / "worker_console_desktop/README.md").read_text(encoding="utf-8")

    for command in [
        "python -m worker_client.cli start",
        "npm install",
        "npm run build",
        "npm run tauri dev",
    ]:
        assert command in readme

    assert "formal exe / dmg installer" in readme
    assert "system tray" in readme
    assert "auto update" in readme
