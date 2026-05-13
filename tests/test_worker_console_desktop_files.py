from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DESKTOP_ROOT = ROOT / "worker_console_desktop"


def test_worker_console_desktop_files_exist() -> None:
    """桌面控制台必须包含可独立运行的 Tauri + Vite 基础文件。"""

    required_files = [
        "package.json",
        ".env.example",
        "index.html",
        "vite.config.ts",
        "tailwind.config.ts",
        "postcss.config.js",
        "tsconfig.json",
        "README.md",
        "src/main.tsx",
        "src/styles.css",
        "src/api/localWorkerClient.ts",
        "src-tauri/tauri.conf.json",
        "src-tauri/Cargo.toml",
        "src-tauri/build.rs",
        "src-tauri/src/main.rs",
        "src-tauri/capabilities/default.json",
    ]

    for relative_path in required_files:
        assert (DESKTOP_ROOT / relative_path).exists(), relative_path


def test_worker_console_desktop_package_scripts_and_deps() -> None:
    """package.json 必须暴露前端 build 与 Tauri dev 入口。"""

    package = json.loads((DESKTOP_ROOT / "package.json").read_text(encoding="utf-8"))

    assert package["version"] == "31.0.0"
    assert package["scripts"]["build"] == "tsc -b && vite build"
    assert package["scripts"]["tauri:dev"] == "tauri dev"
    assert package["dependencies"]["@tauri-apps/api"].startswith("^2")
    assert package["devDependencies"]["@tauri-apps/cli"].startswith("^2")


def test_worker_console_desktop_local_api_client_contract() -> None:
    """桌面端继续复用 Phase 29/30 的本地 Worker API 契约。"""

    client = (DESKTOP_ROOT / "src/api/localWorkerClient.ts").read_text(encoding="utf-8")

    for endpoint in [
        "/local/status",
        "/local/health",
        "/local/logs",
        "/local/runtime/start",
        "/local/runtime/stop",
        "/local/runtime/restart",
        "/local/heartbeat/start",
        "/local/heartbeat/stop",
    ]:
        assert endpoint in client

    assert "VITE_LOCAL_WORKER_API" in client
    assert "http://127.0.0.1:9100" in client


def test_worker_console_desktop_unreachable_message() -> None:
    """Worker API 不可达时必须给出清晰的本地启动提示。"""

    app = (DESKTOP_ROOT / "src/main.tsx").read_text(encoding="utf-8")

    assert "Worker API unreachable" in app
    assert "Worker Runtime 未启动" in app
    assert "请先启动 worker_client" in app
    assert "packaging 脚本启动" in app
