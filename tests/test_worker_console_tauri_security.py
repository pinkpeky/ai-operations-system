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


def test_tauri_rust_runtime_does_not_execute_arbitrary_commands() -> None:
    main_rs = (DESKTOP_ROOT / "src-tauri/src/main.rs").read_text(encoding="utf-8").lower()

    forbidden_terms = [
        "std::process",
        "command::new",
        "powershell",
        "cmd.exe",
        "bash -c",
        "plugin-shell",
        "remote shell",
    ]

    for term in forbidden_terms:
        assert term not in main_rs

    assert "emit_tray_control" in main_rs
    assert "tray-control" in main_rs
