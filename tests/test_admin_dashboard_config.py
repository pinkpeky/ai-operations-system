"""Admin Dashboard configuration tests."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADMIN_ROOT = ROOT / "admin_dashboard"


def test_admin_dashboard_env_example_documents_runtime_config() -> None:
    env_example = (ADMIN_ROOT / ".env.example").read_text(encoding="utf-8")

    assert "VITE_AI_SERVER_API=http://127.0.0.1:8000" in env_example
    assert "VITE_WORKSPACE_ID=production-workspace" in env_example
    assert "VITE_USER_ID=production-operator" in env_example


def test_admin_dashboard_settings_use_local_storage_keys() -> None:
    client = (ADMIN_ROOT / "src/api/client.ts").read_text(encoding="utf-8")
    app = (ADMIN_ROOT / "src/main.tsx").read_text(encoding="utf-8")

    for key in ("aiServerUrl", "workspaceId", "userId"):
        assert key in client
        assert key in app
    assert "production-workspace" in client
    assert "production-operator" in client
    assert "refreshIntervalMs" in client
    assert "10000" in client
