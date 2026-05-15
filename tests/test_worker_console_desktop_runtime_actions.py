from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DESKTOP_ROOT = ROOT / "worker_console_desktop"


def test_button_and_tray_share_runtime_action_handler() -> None:
    app = (DESKTOP_ROOT / "src/main.tsx").read_text(encoding="utf-8")

    assert 'onClick={() => void runControl("startRuntime")}' in app
    assert 'onClick={() => void runControl("stopRuntime")}' in app
    assert 'onClick={() => void runControl("restartRuntime")}' in app
    assert 'if (action === "startRuntime" || action === "stopRuntime" || action === "restartRuntime")' in app
    assert "void runControl(action)" in app


def test_desktop_runtime_start_uses_limited_native_launcher() -> None:
    app = (DESKTOP_ROOT / "src/main.tsx").read_text(encoding="utf-8")
    bridge = (DESKTOP_ROOT / "src/desktopBridge.ts").read_text(encoding="utf-8")
    main_rs = (DESKTOP_ROOT / "src-tauri/src/main.rs").read_text(encoding="utf-8")

    assert "startWorkerClientRuntime" in app
    assert 'invoke<string>("start_worker_client_runtime")' in bridge
    assert "fn start_worker_client_runtime()" in main_rs
    assert "worker_client.cli" in main_rs
    assert "Command::new(executable)" in main_rs
    assert ".arg(\"start\")" in main_rs
    assert "cmd" not in main_rs.lower()
    assert "powershell" not in main_rs.lower()


def test_local_worker_client_uses_expected_local_api_contract() -> None:
    client = (DESKTOP_ROOT / "src/api/localWorkerClient.ts").read_text(encoding="utf-8")

    assert '"/local/runtime/start"' in client
    assert '"/local/runtime/stop"' in client
    assert '"/local/runtime/restart"' in client
    assert '"/local/heartbeat/start"' in client
    assert '"/local/heartbeat/stop"' in client
    assert "Worker API unreachable at" in client

