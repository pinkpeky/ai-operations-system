from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DESKTOP_ROOT = ROOT / "worker_console_desktop"


def test_tauri_security_does_not_enable_shell_or_fs_permissions() -> None:
    capability = json.loads(
        (DESKTOP_ROOT / "src-tauri/capabilities/default.json").read_text(encoding="utf-8")
    )
    permissions = " ".join(capability["permissions"]).lower()
    package = json.loads((DESKTOP_ROOT / "package.json").read_text(encoding="utf-8"))
    all_dependencies = {
        **package.get("dependencies", {}),
        **package.get("devDependencies", {}),
    }

    assert "shell" not in permissions
    assert "fs" not in permissions
    assert "process" not in permissions
    assert "@tauri-apps/plugin-shell" not in all_dependencies
    assert "@tauri-apps/plugin-fs" not in all_dependencies
    assert "@tauri-apps/plugin-process" not in all_dependencies


def test_tauri_rust_runtime_uses_only_limited_worker_launcher() -> None:
    main_rs = (DESKTOP_ROOT / "src-tauri/src/main.rs").read_text(encoding="utf-8").lower()

    forbidden_terms = [
        "powershell",
        "cmd.exe",
        "bash -c",
        "plugin-shell",
        "remote shell",
    ]

    for term in forbidden_terms:
        assert term not in main_rs

    assert "command::new(executable)" in main_rs
    assert "worker_client.cli" in main_rs
    assert '.arg("start")' in main_rs
    assert "worker_config.yaml" in main_rs
    assert "ensure_runtime_port_available" in main_rs
    assert "emit_tray_control" in main_rs
    assert "tray-control" in main_rs
