from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DESKTOP_ROOT = ROOT / "worker_console_desktop"


def test_tauri_bundle_icon_is_configured_and_present() -> None:
    """Tauri Windows resource generation needs a real icon file."""

    config = json.loads((DESKTOP_ROOT / "src-tauri/tauri.conf.json").read_text(encoding="utf-8"))
    icons = config["bundle"]["icon"]

    assert icons == ["icons/icon.ico"]
    icon_path = DESKTOP_ROOT / "src-tauri" / icons[0]
    assert icon_path.exists()
    assert icon_path.stat().st_size > 100


def test_tauri_icon_file_is_valid_ico_header() -> None:
    icon = (DESKTOP_ROOT / "src-tauri/icons/icon.ico").read_bytes()

    assert int.from_bytes(icon[0:2], "little") == 0
    assert int.from_bytes(icon[2:4], "little") == 1
    assert int.from_bytes(icon[4:6], "little") >= 1

