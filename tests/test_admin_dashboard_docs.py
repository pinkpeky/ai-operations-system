"""Admin Dashboard docs tests."""

from __future__ import annotations

from pathlib import Path


def test_admin_dashboard_docs_describe_scope_and_boundaries() -> None:
    zh = Path("docs/zh/ADMIN_DASHBOARD.md").read_text(encoding="utf-8")
    en = Path("docs/en/ADMIN_DASHBOARD.md").read_text(encoding="utf-8")
    overview = Path("docs/PROJECT_OVERVIEW.md").read_text(encoding="utf-8")

    for text in (zh, en, overview):
        assert "Admin Dashboard Foundation" in text
        assert "admin_dashboard" in text
        assert "VITE_AI_SERVER_API" in text
        assert "read-only" in text
        assert "monitoring" in text
        assert "no login UI" in text
        assert "no permission UI" in text
        assert "no publishing business flow" in text
        assert "no real social platform control" in text


def test_admin_dashboard_docs_list_pages() -> None:
    docs = "\n".join(
        [
            Path("docs/zh/ADMIN_DASHBOARD.md").read_text(encoding="utf-8"),
            Path("docs/en/ADMIN_DASHBOARD.md").read_text(encoding="utf-8"),
        ]
    )

    for page in (
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
        assert page in docs
