from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DESKTOP_ROOT = ROOT / "worker_console_desktop"


def test_tauri_config_is_desktop_shell_foundation() -> None:
    """Tauri 配置只声明桌面壳，不开启正式安装包。"""

    config = json.loads((DESKTOP_ROOT / "src-tauri/tauri.conf.json").read_text(encoding="utf-8"))

    assert config["productName"] == "AI Ops Worker Console"
    assert config["version"] == "32.0.0"
    assert config["identifier"] == "com.aiops.workerconsole"
    assert config["build"]["devUrl"] == "http://127.0.0.1:5174"
    assert config["build"]["frontendDist"] == "../dist"
    assert config["build"]["beforeBuildCommand"] == "npm run build"
    assert config["bundle"]["active"] is False

    [window] = config["app"]["windows"]
    assert window["label"] == "main"
    assert window["title"] == "AI Ops Worker Console"
    assert window["width"] >= 1200
    assert window["minWidth"] >= 900


def test_tauri_rust_shell_is_minimal() -> None:
    """Rust 侧只做最小窗口壳，避免引入托盘/自启/自动更新能力。"""

    main_rs = (DESKTOP_ROOT / "src-tauri/src/main.rs").read_text(encoding="utf-8")
    cargo = (DESKTOP_ROOT / "src-tauri/Cargo.toml").read_text(encoding="utf-8")

    assert "tauri::Builder::default()" in main_rs
    assert "autostart" not in main_rs.lower()
    assert "updater" not in main_rs.lower()
    assert "tauri = { version = \"2\"" in cargo


def test_desktop_env_example_points_to_local_worker_api() -> None:
    env_example = (DESKTOP_ROOT / ".env.example").read_text(encoding="utf-8")

    assert "VITE_LOCAL_WORKER_API=http://127.0.0.1:9100" in env_example
