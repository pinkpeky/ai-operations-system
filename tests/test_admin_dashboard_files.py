"""Admin Dashboard file structure tests."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADMIN_ROOT = ROOT / "admin_dashboard"


def test_admin_dashboard_project_files_exist() -> None:
    """Phase 36 Admin Dashboard should be an independent Vite/React project."""

    required = [
        "package.json",
        "index.html",
        "vite.config.ts",
        "tailwind.config.ts",
        "postcss.config.js",
        ".env.example",
        "README.md",
        "src/main.tsx",
        "src/styles.css",
        "src/api/client.ts",
    ]

    for relative_path in required:
        assert (ADMIN_ROOT / relative_path).exists(), relative_path


def test_admin_dashboard_package_and_sidebar_pages() -> None:
    """Dashboard should include the required monitoring pages and build script."""

    package_json = json.loads((ADMIN_ROOT / "package.json").read_text(encoding="utf-8"))
    app = (ADMIN_ROOT / "src/main.tsx").read_text(encoding="utf-8")

    assert package_json["scripts"]["build"] == "tsc -b && vite build"
    assert package_json["dependencies"]["react"]
    assert package_json["dependencies"]["vite"]

    for label in (
        "Overview",
        "Workers",
        "Browser Runtime",
        "Conversations",
        "Tasks",
        "OpenClaw",
        "Audit Logs",
        "RAG / Documents",
        "Settings",
    ):
        assert label in app


def test_admin_dashboard_is_read_only_foundation() -> None:
    """Phase 36 should not expose destructive worker/task controls."""

    app = (ADMIN_ROOT / "src/main.tsx").read_text(encoding="utf-8")

    assert "Read-only" in app or "read-only" in app
    assert "rotate-secret" not in app
    assert "/revoke" not in app
    assert "/tasks/${taskId}/retry" not in app
    assert "/tasks/${taskId}/cancel" not in app
