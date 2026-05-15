from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_deployment_profile_docs_exist_and_cover_boundaries() -> None:
    for relative in ["docs/en/DEPLOYMENT_PROFILES.md", "docs/zh/DEPLOYMENT_PROFILES.md"]:
        path = ROOT / relative
        assert path.exists()
        text = path.read_text(encoding="utf-8")
        assert "local-dev" in text
        assert "server-docker" in text
        assert "client-worker" in text
        assert "desktop-client" in text
        assert "staging" in text
        assert "production-like" in text
        assert "Kubernetes/Helm/Terraform" in text

