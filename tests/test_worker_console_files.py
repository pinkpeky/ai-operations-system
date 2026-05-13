"""Worker Console file structure tests."""

from __future__ import annotations

import json
from pathlib import Path


def test_worker_console_project_files_exist() -> None:
    """Phase 30 Worker Console 应是独立 Vite/React/TypeScript 项目。"""

    required = [
        "worker_console/package.json",
        "worker_console/index.html",
        "worker_console/vite.config.ts",
        "worker_console/tailwind.config.ts",
        "worker_console/postcss.config.js",
        "worker_console/.env.example",
        "worker_console/README.md",
        "worker_console/src/main.tsx",
        "worker_console/src/styles.css",
        "worker_console/src/api/localWorkerClient.ts",
    ]

    for path in required:
        assert Path(path).exists(), path


def test_worker_console_package_scripts_and_local_api_client() -> None:
    """package scripts 与 Local API client 需要覆盖本地控制台接口。"""

    package_json = json.loads(Path("worker_console/package.json").read_text(encoding="utf-8"))
    api_client = Path("worker_console/src/api/localWorkerClient.ts").read_text(encoding="utf-8")
    app = Path("worker_console/src/main.tsx").read_text(encoding="utf-8")

    assert package_json["scripts"]["build"] == "tsc -b && vite build"
    assert "VITE_LOCAL_WORKER_API" in Path("worker_console/.env.example").read_text(encoding="utf-8")
    for route in (
        "/local/status",
        "/local/health",
        "/local/logs",
        "/local/runtime/start",
        "/local/runtime/stop",
        "/local/runtime/restart",
        "/local/heartbeat/start",
        "/local/heartbeat/stop",
    ):
        assert route in api_client
    assert "Worker API unreachable" in app
    assert "请确认 worker_client 是否启动" in app
    assert "请确认端口是否为 9100" in app
