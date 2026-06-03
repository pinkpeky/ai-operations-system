"""Phase 37 frontend config and CORS tests."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_frontend_env_examples_use_server_root_and_workspace_headers() -> None:
    """All frontends should point at the AI Server root and document workspace/user headers."""

    for relative in (
        "admin_dashboard/.env.example",
        "worker_console/.env.example",
        "worker_console_desktop/.env.example",
    ):
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert "VITE_AI_SERVER_API=http://127.0.0.1:8000" in text
        assert "VITE_WORKSPACE_ID=production-workspace" in text
        assert "VITE_USER_ID=production-operator" in text

    for relative in ("worker_console/.env.example", "worker_console_desktop/.env.example"):
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert "VITE_LOCAL_WORKER_API=http://127.0.0.1:9100" in text


def test_backend_cors_allows_development_frontend_origins() -> None:
    """Development CORS must include web, desktop, and Tauri local origins."""

    config = (ROOT / "app" / "core" / "config.py").read_text(encoding="utf-8")
    main = (ROOT / "app" / "main.py").read_text(encoding="utf-8")
    env_example = (ROOT / ".env.example").read_text(encoding="utf-8")
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")

    assert "CORSMiddleware" in main
    assert "cors_allowed_origin_list" in main
    assert "CORS_ALLOWED_ORIGINS" in config
    assert "CORS_ALLOWED_ORIGINS" in env_example
    assert "CORS_ALLOWED_ORIGINS" in compose
    assert "WORKER_CLIENT_OPENCLAW_BASE_URL" in env_example
    assert "WORKER_CLIENT_OPENCLAW_BASE_URL" in compose
    assert "WORKER_CLIENT_OPENCLAW_API_KEY" in env_example
    assert "WORKER_CLIENT_OPENCLAW_API_KEY" in compose

    for origin in (
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5180",
        "http://127.0.0.1:5180",
        "http://localhost:5181",
        "http://127.0.0.1:5181",
        "tauri://localhost",
    ):
        assert origin in config
        assert origin in env_example
        assert origin in compose
