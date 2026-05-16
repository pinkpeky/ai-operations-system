from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DESKTOP_ROOT = ROOT / "worker_console_desktop"


def test_desktop_console_documents_server_client_boundary_in_ui() -> None:
    app = (DESKTOP_ROOT / "src/main.tsx").read_text(encoding="utf-8")

    assert "This desktop console controls the worker runtime on this local machine." in app
    assert "Start Runtime starts a server-local worker, not a remote customer machine." in app
    assert "For real client E2E, run this app on the customer machine." in app
    assert "桌面控制台控制的是当前本机 Worker Runtime" in app
    assert "它启动的是服务器本机 worker，不是远程客户机" in app
    assert "真实客户机 E2E 请在客户机上运行 Desktop Console" in app


def test_desktop_console_diagnostics_surface_local_runtime_context() -> None:
    app = (DESKTOP_ROOT / "src/main.tsx").read_text(encoding="utf-8")

    for label in [
        "Local Worker Diagnostics",
        "status_endpoint",
        "health_endpoint",
        "runtime_reachable",
        "runtime_port",
        "server_url",
        "worker_base_url",
        "last_successful_sync",
    ]:
        assert label in app

