from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_frontends_show_deployment_profile_help() -> None:
    files = [
        ROOT / "admin_dashboard/src/main.tsx",
        ROOT / "worker_console/src/main.tsx",
        ROOT / "worker_console_desktop/src/main.tsx",
    ]

    for path in files:
        text = path.read_text(encoding="utf-8")
        assert "Deployment Profile Help" in text
        assert "recommended_profile" in text
        assert "profile_bootstrap_docs" in text
        assert "docs/en/DEPLOYMENT_PROFILES.md" in text

