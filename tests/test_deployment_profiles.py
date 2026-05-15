import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROFILES = ["local-dev", "server-docker", "client-worker", "desktop-client", "staging", "production-like"]


def test_deployment_profiles_have_required_files() -> None:
    for profile in PROFILES:
        root = ROOT / "deployment/profiles" / profile
        assert (root / "profile.json").exists()
        assert (root / "env.template").exists()
        assert (root / "ports.json").exists()
        assert (root / "services.json").exists()
        assert (root / "healthchecks.json").exists()
        assert (root / "README.md").exists()


def test_deployment_profiles_do_not_contain_real_secrets() -> None:
    forbidden = ["sk-", "ghp_", "xoxb-", "BEGIN PRIVATE KEY"]
    for profile in PROFILES:
        text = "\n".join((ROOT / "deployment/profiles" / profile / name).read_text(encoding="utf-8") for name in ["profile.json", "env.template", "README.md"])
        assert all(item not in text for item in forbidden)
        assert "change_me" in text or "placeholder" in text or "demo-" in text or "replace_with_secret_outside_git" in text


def test_profile_metadata_declares_scenarios() -> None:
    for profile in PROFILES:
        payload = json.loads((ROOT / "deployment/profiles" / profile / "profile.json").read_text(encoding="utf-8"))
        assert payload["profile_key"] == profile
        assert payload["scenario"]
        assert payload["required_env"]

